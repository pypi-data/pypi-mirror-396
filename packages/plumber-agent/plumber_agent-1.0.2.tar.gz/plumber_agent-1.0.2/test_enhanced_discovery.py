#!/usr/bin/env python3
"""
Test Enhanced DCC Discovery System
Tests the new multi-drive and registry-based discovery for alpha tester issue resolution.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from dcc_discovery import get_dcc_discovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_enhanced_discovery():
    """Test the enhanced DCC discovery system."""

    print("\n" + "="*80)
    print("ENHANCED DCC DISCOVERY SYSTEM TEST")
    print("="*80)

    # Get discovery service
    discovery = get_dcc_discovery()

    print(f"\nAvailable drives: {discovery.available_drives}")

    # Test Blender discovery
    print("\n" + "-"*60)
    print("BLENDER DISCOVERY TEST")
    print("-"*60)

    blender_info = discovery.discover_blender()

    print(f"Available: {blender_info['available']}")
    print(f"Selected Version: {blender_info.get('version', 'None')}")
    print(f"Selected Path: {blender_info.get('installation_path', 'None')}")
    print(f"Selected Executable: {blender_info.get('executable', 'None')}")

    print(f"\nAll Found Blender Installations ({len(blender_info.get('versions_found', []))}):")
    for i, version_info in enumerate(blender_info.get('versions_found', []), 1):
        print(f"  {i}. Version: {version_info.get('version', 'Unknown')}")
        print(f"     Path: {version_info.get('path', 'Unknown')}")
        print(f"     Executable: {version_info.get('executable', 'Unknown')}")
        print(f"     Source: {version_info.get('source', 'Unknown')}")
        print()

    # Test Maya discovery
    print("\n" + "-"*60)
    print("MAYA DISCOVERY TEST")
    print("-"*60)

    maya_info = discovery.discover_maya()

    print(f"Available: {maya_info['available']}")
    print(f"Selected Version: {maya_info.get('version', 'None')}")
    print(f"Selected Path: {maya_info.get('installation_path', 'None')}")
    print(f"Selected Executable: {maya_info.get('executable', 'None')}")
    print(f"Selected Python Executable: {maya_info.get('python_executable', 'None')}")

    print(f"\nAll Found Maya Installations ({len(maya_info.get('versions_found', []))}):")
    for i, version_info in enumerate(maya_info.get('versions_found', []), 1):
        print(f"  {i}. Version: {version_info.get('version', 'Unknown')}")
        print(f"     Path: {version_info.get('path', 'Unknown')}")
        print(f"     Executable: {version_info.get('executable', 'Unknown')}")
        print(f"     Python Executable: {version_info.get('python_executable', 'Unknown')}")
        print(f"     Source: {version_info.get('source', 'Unknown')}")
        print()

    # Test Houdini discovery
    print("\n" + "-"*60)
    print("HOUDINI DISCOVERY TEST")
    print("-"*60)

    houdini_info = discovery.discover_houdini()

    print(f"Available: {houdini_info['available']}")
    print(f"Selected Version: {houdini_info.get('version', 'None')}")
    print(f"Selected Path: {houdini_info.get('installation_path', 'None')}")
    print(f"Selected Executable: {houdini_info.get('executable', 'None')}")
    print(f"Selected Python Executable: {houdini_info.get('python_executable', 'None')}")
    print(f"License Type: {houdini_info.get('license_type', 'None')}")

    print(f"\nAll Found Houdini Installations ({len(houdini_info.get('versions_found', []))}):")
    for i, version_info in enumerate(houdini_info.get('versions_found', []), 1):
        print(f"  {i}. Version: {version_info.get('version', 'Unknown')}")
        print(f"     Path: {version_info.get('path', 'Unknown')}")
        print(f"     Executable: {version_info.get('executable', 'Unknown')}")
        print(f"     Python Executable: {version_info.get('python_executable', 'Unknown')}")
        print(f"     License Type: {version_info.get('license_type', 'Unknown')}")
        print(f"     Source: {version_info.get('source', 'Unknown')}")
        print()

    # Summary
    print("\n" + "="*80)
    print("DISCOVERY SUMMARY")
    print("="*80)

    total_found = (
        len(blender_info.get('versions_found', [])) +
        len(maya_info.get('versions_found', [])) +
        len(houdini_info.get('versions_found', []))
    )

    available_count = sum([
        blender_info['available'],
        maya_info['available'],
        houdini_info['available']
    ])

    print(f"Total DCC installations found: {total_found}")
    print(f"Available DCCs: {available_count}/3")
    print(f"Blender: {'Available' if blender_info['available'] else 'Not Available'} ({len(blender_info.get('versions_found', []))} installations)")
    print(f"Maya: {'Available' if maya_info['available'] else 'Not Available'} ({len(maya_info.get('versions_found', []))} installations)")
    print(f"Houdini: {'Available' if houdini_info['available'] else 'Not Available'} ({len(houdini_info.get('versions_found', []))} installations)")

    # Alpha tester specific test
    print(f"\nALPHA TESTER SCENARIO TEST")
    print(f"Multiple Blender versions found: {'YES' if len(blender_info.get('versions_found', [])) > 1 else 'NO'}")

    if len(blender_info.get('versions_found', [])) > 1:
        print("SUCCESS: Enhanced discovery should resolve alpha tester issue!")
        print("SUCCESS: Agent will now find ALL Blender installations across all drives")
        print("SUCCESS: User can choose between versions instead of uninstalling")
    else:
        print("INFO: Only one Blender installation found (expected for most users)")

    print("\n" + "="*80)
    print("ENHANCED DISCOVERY TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_enhanced_discovery()