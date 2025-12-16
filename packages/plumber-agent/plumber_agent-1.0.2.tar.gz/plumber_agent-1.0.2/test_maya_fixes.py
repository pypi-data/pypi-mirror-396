#!/usr/bin/env python3
"""
Maya Fixes Validation Script
Tests the Maya DLL environment setup and execution strategies
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path

def test_maya_environment_setup():
    """Test the Maya environment setup function."""
    print("🔧 Testing Maya Environment Setup")
    print("-" * 40)

    # Create test script that includes our environment setup
    test_script = '''
import os
import sys
import platform

# CRITICAL Maya 2026 DLL Environment Setup - MUST BE FIRST
def setup_maya_environment():
    """Complete Maya environment setup for DLL loading."""
    maya_location = r"C:\\Program Files\\Autodesk\\Maya2026"
    maya_bin = os.path.join(maya_location, "bin")
    maya_python = os.path.join(maya_location, "Python")

    # Critical environment variables for DLL loading
    maya_env = {
        "MAYA_LOCATION": maya_location,
        "MAYA_APP_DIR": os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "maya"),
        "MAYA_DISABLE_CIP": "1",
        "MAYA_DISABLE_CLIC_IPM": "1",
        "MAYA_DISABLE_ADLMPIT_POPUP": "1",
        "MAYA_DISABLE_ADP": "1",
        "MAYA_CM_DISABLE_ERROR_POPUPS": "1",
        "MAYA_NO_CONSOLE_WINDOW": "1",
        "MAYA_DEBUG_NO_DIALOGS": "1",

        # Qt WebEngine fixes for Maya 2026
        "QT_QPA_PLATFORM_PLUGIN_PATH": "",
        "QT_WEBENGINE_DISABLE_SANDBOX": "1",
        "QTWEBENGINE_DISABLE_SANDBOX": "1",
        "QT_LOGGING_RULES": "qt.webenginecontext.debug=false",
        "QT_WEBENGINE_CHROMIUM_FLAGS": "--disable-web-security --disable-features=VizDisplayCompositor",
        "QTWEBENGINE_CHROMIUM_FLAGS": "--disable-web-security --disable-gpu"
    }

    # Apply environment variables
    for key, value in maya_env.items():
        os.environ[key] = value

    # Update PATH to include Maya bin directory FIRST
    current_path = os.environ.get("PATH", "")
    if maya_bin not in current_path:
        os.environ["PATH"] = maya_bin + os.pathsep + current_path

    # Update PYTHONPATH for Maya Python modules
    maya_python_paths = [
        os.path.join(maya_python, "Lib", "site-packages"),
        os.path.join(maya_location, "devkit", "other", "python", "2.7", "lib"),
        maya_bin
    ]

    current_pythonpath = os.environ.get("PYTHONPATH", "")
    for path in maya_python_paths:
        if os.path.exists(path) and path not in current_pythonpath:
            if current_pythonpath:
                current_pythonpath += os.pathsep + path
            else:
                current_pythonpath = path
            # Add to sys.path for immediate use
            if path not in sys.path:
                sys.path.insert(0, path)

    os.environ["PYTHONPATH"] = current_pythonpath
    print("🔧 Maya DLL environment setup completed")

# Setup Maya environment BEFORE any imports
setup_maya_environment()

# Test Maya import
print("Testing Maya import...")
try:
    import maya.standalone
    print("✅ maya.standalone imported successfully")

    # Try initialization
    maya.standalone.initialize(name='python')
    print("✅ maya.standalone initialized successfully")

    # Try importing cmds
    import maya.cmds as cmds
    print("✅ maya.cmds imported successfully")

    # Create a simple cube to test functionality
    cube = cmds.polyCube(name='test_cube')[0]
    print(f"✅ Created test cube: {cube}")

    # Get cube info
    bbox = cmds.exactWorldBoundingBox(cube)
    print(f"✅ Cube bounding box: {bbox}")

    # Clean up
    cmds.delete(cube)
    print("✅ Cleanup completed")

    # Uninitialize
    maya.standalone.uninitialize()
    print("✅ Maya standalone uninitialized successfully")

    print("\\n🎉 ALL MAYA TESTS PASSED!")

except ImportError as e:
    print(f"❌ Maya import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Maya operation failed: {e}")
    sys.exit(1)
'''

    # Write test script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        test_script_path = f.name

    try:
        # Test with mayapy
        mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
        if os.path.exists(mayapy_path):
            print(f"🐍 Testing with mayapy: {mayapy_path}")
            result = subprocess.run([mayapy_path, test_script_path],
                                  capture_output=True, text=True, timeout=60)

            print("STDOUT:")
            print(result.stdout)

            if result.stderr:
                print("STDERR:")
                print(result.stderr)

            if result.returncode == 0:
                print("✅ Maya environment test PASSED")
                return True
            else:
                print(f"❌ Maya environment test FAILED (return code: {result.returncode})")
                return False
        else:
            print(f"❌ Maya not found at {mayapy_path}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Maya test timed out")
        return False
    except Exception as e:
        print(f"❌ Maya test error: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(test_script_path)
        except:
            pass

def test_maya_operation():
    """Test a simple Maya operation like the DCC agent would run."""
    print("\n🎬 Testing Maya Operation")
    print("-" * 40)

    # Create a simple Maya operation script
    maya_operation = '''
import os
import sys
import json
import tempfile

# Setup Maya environment
maya_location = r"C:\\Program Files\\Autodesk\\Maya2026"
maya_bin = os.path.join(maya_location, "bin")
os.environ["PATH"] = maya_bin + os.pathsep + os.environ.get("PATH", "")

# Import and initialize Maya
try:
    import maya.standalone
    maya.standalone.initialize(name='python')
    import maya.cmds as cmds

    print("Maya operation: Creating sphere")

    # Create sphere
    sphere = cmds.polySphere(name='test_sphere', radius=2.0)[0]

    # Get sphere properties
    radius = cmds.getAttr(f"{sphere}.radius")
    translate = cmds.xform(sphere, query=True, translation=True)

    result = {
        "status": "success",
        "object": sphere,
        "radius": radius,
        "position": translate,
        "operation": "create_sphere"
    }

    # Save result to temp file
    temp_dir = tempfile.gettempdir()
    result_file = os.path.join(temp_dir, "maya_operation_result.json")

    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"✅ Maya operation completed successfully")
    print(f"📁 Result saved to: {result_file}")
    print(json.dumps(result, indent=2))

    # Clean up
    cmds.delete(sphere)
    maya.standalone.uninitialize()

except Exception as e:
    result = {
        "status": "error",
        "error": str(e),
        "operation": "create_sphere"
    }

    # Save error result
    temp_dir = tempfile.gettempdir()
    result_file = os.path.join(temp_dir, "maya_operation_result.json")

    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"❌ Maya operation failed: {e}")
    print(f"📁 Error saved to: {result_file}")
'''

    # Write operation script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(maya_operation)
        operation_script_path = f.name

    try:
        # Test operation with mayapy
        mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

        print(f"🐍 Running Maya operation with mayapy")
        result = subprocess.run([mayapy_path, operation_script_path],
                              capture_output=True, text=True, timeout=90)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        # Check for result file
        result_file = os.path.join(tempfile.gettempdir(), "maya_operation_result.json")
        if os.path.exists(result_file):
            with open(result_file, 'r') as f:
                operation_result = json.load(f)

            print("\n📊 Operation Result:")
            print(json.dumps(operation_result, indent=2))

            if operation_result.get("status") == "success":
                print("✅ Maya operation test PASSED")
                return True
            else:
                print("❌ Maya operation test FAILED")
                return False
        else:
            print("❌ No result file found")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Maya operation timed out")
        return False
    except Exception as e:
        print(f"❌ Maya operation error: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(operation_script_path)
        except:
            pass

def main():
    """Main test runner."""
    print("🧪 Maya Fixes Validation Test Suite")
    print("=" * 50)

    # Run tests
    tests = [
        ("Maya Environment Setup", test_maya_environment_setup),
        ("Maya Operation", test_maya_operation)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Maya fixes are working!")
        return True
    else:
        print("⚠️  Some tests failed - Maya fixes need more work")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)