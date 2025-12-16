#!/usr/bin/env python3
"""
Show generated Maya script content to verify fixes
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from dcc_executor import DCCExecutor

def main():
    """Show the Maya script with our fixes."""
    print("GENERATED MAYA SCRIPT CONTENT")
    print("=" * 50)

    executor = DCCExecutor()

    # Generate Maya script
    script_content = executor._generate_maya_script(
        "test_maya_operation",
        {"test_param": "test_value"},
        "/tmp/test_output",
        "mayapy"
    )

    print(script_content[:2000])  # First 2000 characters
    print("\n[... script continues ...]")

    # Check for key fixes
    print("\n" + "=" * 50)
    print("CHECKING FOR KEY FIXES:")

    checks = [
        ("Maya Environment Setup", "setup_maya_environment()"),
        ("Maya Location", "MAYA_LOCATION"),
        ("DLL Environment", "MAYA_DISABLE_CIP"),
        ("Path Setup", "maya_bin + os.pathsep"),
        ("Qt Fixes", "QT_WEBENGINE_DISABLE_SANDBOX")
    ]

    for check_name, check_string in checks:
        if check_string in script_content:
            print(f"✓ {check_name}: FOUND")
        else:
            print(f"✗ {check_name}: MISSING")

if __name__ == "__main__":
    main()