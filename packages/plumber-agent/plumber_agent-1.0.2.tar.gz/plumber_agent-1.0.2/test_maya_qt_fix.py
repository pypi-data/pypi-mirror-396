#!/usr/bin/env python3
"""
Test script to verify Maya Qt WebEngine fixes work locally
"""
import os
import sys
import tempfile
import subprocess

def test_maya_qt_fix():
    """Test Maya script execution with Qt WebEngine suppression"""

    # Create a test Maya script with our fixes
    test_script_content = '''
import os
import sys

# Set Qt attributes before Maya initialization to suppress WebEngine warnings
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = ""
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"

print("Starting Maya with Qt WebEngine suppression...")

import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds

print("Maya operation starting: test_session")

try:
    print("Maya initialized successfully!")
    print("Creating basic scene...")

    # Create a simple cube
    cube = cmds.polyCube(name="test_cube")[0]
    print(f"Created cube: {cube}")

    # Get scene info
    objects = cmds.ls(dag=True, long=True)
    print(f"Scene contains {len(objects)} objects")

    print("Maya operation completed successfully")

except Exception as e:
    print(f"Maya operation failed: {e}")
    sys.exit(1)
finally:
    maya.standalone.uninitialize()
    print("Maya uninitialized")
'''

    # Write test script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script_content)
        script_path = f.name

    try:
        # Get Maya Python path
        mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
        if not os.path.exists(mayapy_path):
            print(f"[ERROR] Maya not found at: {mayapy_path}")
            return False

        print(f"[TEST] Testing Maya Qt WebEngine fixes...")
        print(f"[SCRIPT] Script: {script_path}")
        print(f"[MAYA] Maya: {mayapy_path}")
        print()

        # Execute Maya script
        cmd = [mayapy_path, script_path]
        print(f"[RUN] Running: {' '.join(cmd)}")

        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        print("=" * 50)
        print("STDOUT:")
        print(process.stdout)
        print("=" * 50)
        print("STDERR:")
        print(process.stderr)
        print("=" * 50)
        print(f"Exit Code: {process.returncode}")

        if process.returncode == 0:
            print("[SUCCESS] Maya Qt WebEngine fixes working!")
            return True
        else:
            print("[FAILED] Maya execution failed")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(script_path)
        except:
            pass

if __name__ == "__main__":
    success = test_maya_qt_fix()
    sys.exit(0 if success else 1)