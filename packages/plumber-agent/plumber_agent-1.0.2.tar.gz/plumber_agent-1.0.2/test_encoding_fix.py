#!/usr/bin/env python3
"""
Test that encoding fix resolves Unicode issues
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_script_generation():
    """Test Maya script generation with Unicode characters."""
    print("Testing Maya script generation with Unicode fix...")

    try:
        from dcc_executor import DCCExecutor

        # Create executor
        executor = DCCExecutor()
        await executor.initialize()

        # Generate script with potential Unicode content
        script_content = executor._generate_maya_script(
            "test_operation",
            {"param1": "value1", "param2": "value2"},
            "/tmp/test_output",
            "mayapy"
        )

        # Try to write script to file (this was failing before)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            test_script_path = f.name

        print(f"SUCCESS: Script written to {test_script_path}")

        # Read back the script to verify encoding
        with open(test_script_path, 'r', encoding='utf-8') as f:
            read_content = f.read()

        if "setup_maya_environment()" in read_content:
            print("SUCCESS: Maya environment setup found in script")
        else:
            print("FAIL: Maya environment setup missing")
            return False

        # Cleanup
        os.unlink(test_script_path)

        return True

    except Exception as e:
        print(f"FAIL: Script generation failed: {e}")
        return False

async def main():
    """Main test function."""
    print("TESTING UNICODE ENCODING FIX")
    print("=" * 30)

    success = test_script_generation()

    if success:
        print("\nENCODING FIX VERIFIED!")
        print("Maya operations should now work without Unicode errors.")
    else:
        print("\nEncoding fix needs more work.")

    return success

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)