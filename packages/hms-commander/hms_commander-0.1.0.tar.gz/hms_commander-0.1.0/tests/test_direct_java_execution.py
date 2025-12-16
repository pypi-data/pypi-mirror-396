"""
Test Direct Java Execution for HEC-HMS

This script tests the new direct Java invocation approach across multiple
HMS versions, including those affected by the batch file quoting bug (4.0-4.11).
"""

import sys
from pathlib import Path

# Add hms-commander to path
sys.path.insert(0, str(Path(__file__).parent))

from hms_commander import HmsExamples, HmsJython

def test_version_execution(version: str, project_name: str = "tifton"):
    """Test execution for a specific HMS version."""
    print(f"\n{'='*60}")
    print(f"Testing HMS {version}")
    print('='*60)

    # Get paths - check both 64-bit and 32-bit locations
    hms_install = None
    for base in [Path(r"C:\Program Files\HEC\HEC-HMS"),
                 Path(r"C:\Program Files (x86)\HEC\HEC-HMS")]:
        candidate = base / version
        if candidate.exists():
            hms_install = candidate
            break

    if hms_install is None:
        print(f"  SKIP: HMS {version} not installed")
        return None

    # Check for required files - handle both 64-bit (jre) and 32-bit (java) structures
    java_exe = hms_install / "jre" / "bin" / "java.exe"
    if not java_exe.exists():
        java_exe = hms_install / "java" / "bin" / "java.exe"
    hms_jar = hms_install / "hms.jar"

    if not java_exe.exists():
        print(f"  SKIP: Java not found (checked jre/bin and java/bin)")
        return None

    if not hms_jar.exists():
        print(f"  SKIP: hms.jar not found at {hms_jar}")
        return None

    print(f"  Install: {hms_install}")
    print(f"  Java: {java_exe}")

    # Extract project if it exists for this version
    try:
        project_path = HmsExamples.extract_project(
            project_name,
            version=version,
            output_path=Path(__file__).parent / "test_output" / f"test_{version}"
        )
    except Exception as e:
        print(f"  SKIP: Project not available for version {version}: {e}")
        return None

    print(f"  Project: {project_path}")

    # Find the run name (varies by version)
    run_file = list(project_path.glob("*.run"))[0]
    run_content = run_file.read_text()

    # Parse run name from .run file
    run_name = None
    for line in run_content.split('\n'):
        if line.strip().startswith("Run:"):
            run_name = line.split("Run:")[1].strip()
            break

    if not run_name:
        print(f"  ERROR: Could not find run name in {run_file}")
        return False

    print(f"  Run name: {run_name}")

    # Generate and execute script
    script = HmsJython.generate_compute_script(
        project_path=project_path,
        run_name=run_name,
        save_project=True
    )

    print(f"  Executing via direct Java invocation...")
    success, stdout, stderr = HmsJython.execute_script(
        script_content=script,
        hms_exe_path=hms_install,
        working_dir=project_path,
        timeout=120,
        max_memory="2G"  # Smaller memory for test
    )

    # Print results
    if success:
        print(f"  RESULT: SUCCESS")
    else:
        print(f"  RESULT: FAILED")

    if stdout:
        # Print key lines from stdout
        for line in stdout.split('\n'):
            if any(x in line for x in ['Project opened', 'Computation', 'Error', 'completed']):
                print(f"    stdout: {line.strip()}")

    if stderr and "SystemExit: 0" not in stderr:
        print(f"    stderr: {stderr[:200]}")

    return success


def test_version_3_error():
    """Test that HMS 3.x gives a clear error message."""
    print(f"\n{'='*60}")
    print("Testing HMS 3.x Error Message")
    print('='*60)

    # Try with a fake 3.x path
    fake_path = Path(r"C:\Program Files\HEC\HEC-HMS\3.5")

    try:
        version = HmsJython._get_hms_version(fake_path)
        print(f"  Detected version: {version}")

        HmsJython._check_version_supported(version)
        print("  ERROR: Should have raised RuntimeError!")
        return False

    except RuntimeError as e:
        print(f"  Correct error raised: {e}")
        return True


def test_legacy_version_error():
    """Test that HMS 4.0-4.3 gives a clear error message."""
    print(f"\n{'='*60}")
    print("Testing HMS 4.0-4.3 Legacy Error Message")
    print('='*60)

    # Test versions that should raise legacy error
    for version_str in ["4.0", "4.1", "4.2.1", "4.3"]:
        fake_path = Path(f"C:\\Program Files\\HEC\\HEC-HMS\\{version_str}")

        try:
            version = HmsJython._get_hms_version(fake_path)
            print(f"  Testing {version_str} -> {version}")

            HmsJython._check_version_supported(version)
            print(f"  ERROR: {version_str} should have raised RuntimeError!")
            return False

        except RuntimeError as e:
            if "legacy classpath" in str(e):
                print(f"  {version_str}: Correct legacy error raised")
            else:
                print(f"  {version_str}: Wrong error type: {e}")
                return False

    return True


def main():
    print("=" * 70)
    print("HMS Direct Java Execution Test Suite")
    print("Tests the fix for HMS 4.0-4.11 batch file quoting bug")
    print("=" * 70)

    # Test supported 4.x versions (4.4.1+)
    # HMS 4.0-4.3 use a legacy classpath structure that isn't supported
    test_versions = [
        "4.13",
        "4.12",
        "4.11",
        "4.10",
        "4.9",
        "4.8",
        "4.7.1",
        "4.6",
        "4.5",
        "4.4.1",
    ]

    results = {}

    # Test each version
    for version in test_versions:
        result = test_version_execution(version)
        if result is not None:
            results[version] = result

    # Test HMS 3.x error message
    results["3.x error"] = test_version_3_error()

    # Test HMS 4.0-4.3 legacy error message
    results["4.0-4.3 legacy error"] = test_legacy_version_error()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    skipped = 0

    for version, result in results.items():
        if result is None:
            status = "SKIPPED"
            skipped += 1
        elif result:
            status = "PASSED"
            passed += 1
        else:
            status = "FAILED"
            failed += 1
        print(f"  HMS {version}: {status}")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        print("\nFAILED TESTS - Direct Java execution needs debugging!")
        return 1
    else:
        print("\nAll tests passed! Direct Java execution is working.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
