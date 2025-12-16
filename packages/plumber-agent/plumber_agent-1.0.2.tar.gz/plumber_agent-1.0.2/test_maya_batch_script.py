#!/usr/bin/env python3
"""
Test the Maya batch script generation to verify the fix
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dcc_executor import DCCExecutor

def test_maya_script_generation():
    """Test both batch and mayapy script generation modes"""
    print("Testing Maya script generation modes...")

    executor = DCCExecutor()

    # Test parameters
    operation_type = "export"
    params = {"format": "ma"}
    output_dir = "/tmp/test_output"

    # Test mayapy mode (default)
    mayapy_script = executor._generate_maya_script(operation_type, params, output_dir, execution_mode="mayapy")
    print("\n=== MAYAPY MODE SCRIPT ===")
    print("Should include Qt setup and maya.standalone.initialize():")
    if "Maya 2026 Qt WebEngine Fix" in mayapy_script:
        print("[OK] Qt setup included in mayapy script")
    else:
        print("[FAIL] Qt setup missing in mayapy script")

    if "maya.standalone.initialize()" in mayapy_script:
        print("[OK] Maya standalone initialization included in mayapy script")
    else:
        print("[FAIL] Maya standalone initialization missing in mayapy script")

    # Test batch mode
    batch_script = executor._generate_maya_script(operation_type, params, output_dir, execution_mode="batch")
    print("\n=== BATCH MODE SCRIPT ===")
    print("Should skip Qt setup and maya.standalone.initialize():")
    if "Maya 2026 Qt WebEngine Fix" in batch_script:
        print("[FAIL] Qt setup incorrectly included in batch script")
    else:
        print("[OK] Qt setup correctly skipped in batch script")

    if "maya.standalone.initialize()" in batch_script:
        print("[FAIL] Maya standalone initialization incorrectly included in batch script")
    else:
        print("[OK] Maya standalone initialization correctly skipped in batch script")

    if "Running in Maya batch mode - Maya already initialized" in batch_script:
        print("[OK] Batch mode message included")
    else:
        print("[FAIL] Batch mode message missing")

    if "maya_already_initialized = True" in batch_script:
        print("[OK] maya_already_initialized correctly set to True in batch mode")
    else:
        print("[FAIL] maya_already_initialized not set to True in batch mode")

    print("\n=== SUMMARY ===")
    print("Batch mode script generation: ", end="")
    if ("Maya 2026 Qt WebEngine Fix" not in batch_script and
        "maya.standalone.initialize()" not in batch_script and
        "Running in Maya batch mode" in batch_script and
        "maya_already_initialized = True" in batch_script):
        print("WORKING CORRECTLY")
        return True
    else:
        print("NEEDS FIXES")
        return False

if __name__ == "__main__":
    test_maya_script_generation()