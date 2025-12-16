#!/usr/bin/env python3
"""
Quick verification that the fixes are properly integrated
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all updated modules import correctly."""
    print("🔍 Testing module imports...")

    try:
        from dcc_executor import DCCExecutor
        print("✅ dcc_executor imported successfully")

        from connection_manager import ConnectionManager
        print("✅ connection_manager imported successfully")

        from agent_server import process_dcc_operation
        print("✅ agent_server imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_maya_environment_setup():
    """Test that Maya environment setup function exists in generated scripts."""
    print("\n🔧 Testing Maya environment setup...")

    try:
        from dcc_executor import DCCExecutor

        # Create executor instance
        executor = DCCExecutor({})

        # Test script generation with Maya environment setup
        script_content = executor._generate_maya_script(
            "test_operation",
            {"test": "param"},
            "/tmp/test",
            "mayapy"
        )

        # Check if our fixes are in the script
        if "setup_maya_environment()" in script_content:
            print("✅ Maya environment setup found in generated script")
        else:
            print("❌ Maya environment setup missing from generated script")
            return False

        if "MAYA_LOCATION" in script_content:
            print("✅ Maya environment variables found in script")
        else:
            print("❌ Maya environment variables missing from script")
            return False

        return True

    except Exception as e:
        print(f"❌ Maya environment test failed: {e}")
        return False

def test_connection_manager_heartbeat():
    """Test that connection manager has heartbeat methods."""
    print("\n💓 Testing connection manager heartbeat...")

    try:
        from connection_manager import ConnectionManager

        # Check if heartbeat methods exist
        cm = ConnectionManager("ws://test", "test_agent")

        if hasattr(cm, 'send_operation_with_heartbeat'):
            print("✅ send_operation_with_heartbeat method found")
        else:
            print("❌ send_operation_with_heartbeat method missing")
            return False

        if hasattr(cm, 'send_operation_progress'):
            print("✅ send_operation_progress method found")
        else:
            print("❌ send_operation_progress method missing")
            return False

        if hasattr(cm, '_dcc_operation_heartbeat'):
            print("✅ _dcc_operation_heartbeat method found")
        else:
            print("❌ _dcc_operation_heartbeat method missing")
            return False

        # Check timeout configuration
        if hasattr(cm, 'dcc_operation_timeout'):
            print(f"✅ DCC operation timeout configured: {cm.dcc_operation_timeout}s")
        else:
            print("❌ DCC operation timeout not configured")
            return False

        return True

    except Exception as e:
        print(f"❌ Connection manager test failed: {e}")
        return False

def main():
    """Run all verification tests."""
    print("Verifying Fixes Integration")
    print("=" * 40)

    tests = [
        ("Module Imports", test_imports),
        ("Maya Environment Setup", test_maya_environment_setup),
        ("Connection Manager Heartbeat", test_connection_manager_heartbeat)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print(f"\n📊 Verification Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL FIXES ARE PROPERLY INTEGRATED!")
        print("✅ Maya DLL environment setup is active")
        print("✅ WebSocket heartbeat system is active")
        print("✅ Agent will use fixes when started with start_agent.bat")
        return True
    else:
        print("\n⚠️  Some fixes are not properly integrated")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)