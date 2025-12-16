"""
Quick test script for HmsGeo extraction

Run this to verify the HmsGeo class works with your HEC-HMS model files.
Update the file paths below to point to your actual model files.
"""

import logging
from pathlib import Path
from HmsGeo import HmsGeo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_basin_parsing():
    """Test parsing a .basin file."""
    print("\n" + "="*70)
    print("TEST 1: Basin File Parsing")
    print("="*70)

    # UPDATE THIS PATH to your .basin file
    basin_path = "C:/HCFCD/Models/A100_B100/Ph1_1PCT.basin"

    if not Path(basin_path).exists():
        print(f"❌ SKIP: File not found: {basin_path}")
        print("   Please update the path in test_extraction.py")
        return False

    try:
        subbasins, junctions, reaches = HmsGeo.parse_basin_file(basin_path)

        print(f"✓ Parsed successfully")
        print(f"  - Subbasins: {len(subbasins)}")
        print(f"  - Junctions: {len(junctions)}")
        print(f"  - Reaches: {len(reaches)}")

        # Check first subbasin
        if subbasins:
            first_name = list(subbasins.keys())[0]
            first_sub = subbasins[first_name]
            print(f"\n  First subbasin: {first_name}")
            print(f"    Coordinates: ({first_sub.get('x')}, {first_sub.get('y')})")
            print(f"    Area: {first_sub.get('area')} sq mi")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_geo_parsing():
    """Test parsing a .geo file."""
    print("\n" + "="*70)
    print("TEST 2: GEO File Parsing")
    print("="*70)

    # UPDATE THIS PATH to your .geo file
    geo_path = "C:/HCFCD/Models/A100_B100/A100-GEO.geo"

    if not Path(geo_path).exists():
        print(f"❌ SKIP: File not found: {geo_path}")
        print("   Please update the path in test_extraction.py")
        return False

    try:
        coords = HmsGeo.parse_geo_file(geo_path)

        print(f"✓ Parsed successfully")
        print(f"  - Subbasins: {len(coords)}")

        # Check first coordinate
        if coords:
            first_name = list(coords.keys())[0]
            first_coord = coords[first_name]
            print(f"\n  First subbasin: {first_name}")
            print(f"    X: {first_coord['x']}")
            print(f"    Y: {first_coord['y']}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_map_parsing():
    """Test parsing a .map file."""
    print("\n" + "="*70)
    print("TEST 3: MAP File Parsing")
    print("="*70)

    # UPDATE THIS PATH to your .map file
    map_path = "C:/HCFCD/Models/A100_B100/A100-MAP.map"

    if not Path(map_path).exists():
        print(f"❌ SKIP: File not found: {map_path}")
        print("   Please update the path in test_extraction.py")
        return False

    try:
        map_data = HmsGeo.parse_map_file(map_path)

        boundaries = map_data['boundaries']
        rivers = map_data['rivers']

        print(f"✓ Parsed successfully")
        print(f"  - Boundary features: {len(boundaries)}")
        print(f"  - River features: {len(rivers)}")

        # Calculate detail level
        if boundaries:
            total_vertices = sum(len(b['coordinates']) for b in boundaries)
            avg_vertices = total_vertices / len(boundaries)
            print(f"\n  Boundary detail:")
            print(f"    Total vertices: {total_vertices:,}")
            print(f"    Avg per feature: {avg_vertices:.1f}")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_geojson_export():
    """Test exporting to GeoJSON."""
    print("\n" + "="*70)
    print("TEST 4: GeoJSON Export")
    print("="*70)

    # UPDATE THIS PATH
    basin_path = "C:/HCFCD/Models/A100_B100/Ph1_1PCT.basin"
    output_dir = Path("C:/GH/hms-commander/test_output")

    if not Path(basin_path).exists():
        print(f"❌ SKIP: File not found: {basin_path}")
        return False

    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Parse
        subbasins, junctions, reaches = HmsGeo.parse_basin_file(basin_path)

        # Export
        output_subs = output_dir / "test_subbasins.geojson"
        HmsGeo.create_geojson_subbasins(subbasins, output_subs)

        output_juncs = output_dir / "test_junctions.geojson"
        HmsGeo.create_geojson_junctions(junctions, output_juncs)

        output_reachs = output_dir / "test_reaches.geojson"
        HmsGeo.create_geojson_reaches(reaches, output_reachs)

        # Check files exist
        if output_subs.exists() and output_juncs.exists() and output_reachs.exists():
            print(f"✓ Exported successfully to: {output_dir}")
            print(f"  - {output_subs.name}")
            print(f"  - {output_juncs.name}")
            print(f"  - {output_reachs.name}")

            # Check file sizes
            total_size = sum(f.stat().st_size for f in [output_subs, output_juncs, output_reachs])
            print(f"\n  Total size: {total_size / 1024:.1f} KB")

            return True
        else:
            print(f"❌ FAILED: Output files not created")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extract_all():
    """Test the convenience method extract_all_gis."""
    print("\n" + "="*70)
    print("TEST 5: Extract All GIS Data")
    print("="*70)

    # UPDATE THESE PATHS
    basin_path = "C:/HCFCD/Models/A100_B100/Ph1_1PCT.basin"
    geo_path = "C:/HCFCD/Models/A100_B100/A100-GEO.geo"
    map_path = "C:/HCFCD/Models/A100_B100/A100-MAP.map"
    output_dir = Path("C:/GH/hms-commander/test_output")

    if not Path(basin_path).exists():
        print(f"❌ SKIP: File not found: {basin_path}")
        return False

    try:
        # Extract all
        outputs = HmsGeo.extract_all_gis(
            basin_path=basin_path,
            geo_path=geo_path if Path(geo_path).exists() else None,
            map_path=map_path if Path(map_path).exists() else None,
            output_dir=output_dir
        )

        print(f"\n✓ Extraction complete!")
        print(f"  Generated {len(outputs)} GeoJSON files:")
        for key, path in outputs.items():
            size_kb = Path(path).stat().st_size / 1024
            print(f"    {key}: {path.name} ({size_kb:.1f} KB)")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("HmsGeo Test Suite")
    print("="*70)
    print("\n⚠️  Before running: Update file paths in test_extraction.py")
    print()

    results = []

    # Run tests
    results.append(("Basin Parsing", test_basin_parsing()))
    results.append(("GEO Parsing", test_geo_parsing()))
    results.append(("MAP Parsing", test_map_parsing()))
    results.append(("GeoJSON Export", test_geojson_export()))
    results.append(("Extract All", test_extract_all()))

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL/SKIP"
        print(f"  {status}: {test_name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed or were skipped.")
        print("     Check file paths and error messages above.")


if __name__ == "__main__":
    main()
