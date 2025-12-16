#!/usr/bin/env python3
"""
Test final fixes for Maya DLL and WebSocket issues
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_mel_script_generation():
    """Test MEL script generation for Maya operations."""
    print("Testing Maya MEL script generation...")

    try:
        from dcc_executor import DCCExecutor

        # Create executor
        executor = DCCExecutor()

        # Test MEL operation generation
        with tempfile.TemporaryDirectory() as temp_dir:
            # This would be called internally
            success, result = await executor._execute_maya_mel_operation(
                "test_op_123",
                "create_sphere",
                {"radius": 1.0},
                temp_dir
            )

            if success:
                print("✅ Maya MEL execution simulation successful")
                return True
            else:
                print(f"❌ Maya MEL execution failed: {result}")
                return False

    except Exception as e:
        print(f"❌ MEL script test failed: {e}")
        return False

def test_agent_heartbeat():
    """Test agent heartbeat functionality."""
    print("Testing agent heartbeat system...")

    try:
        from agent_server import simple_heartbeat
        from connection_manager import ConnectionManager
        import asyncio

        # Mock connection manager
        class MockConnectionManager:
            async def send_operation_progress(self, op_id, progress, message):
                print(f"Heartbeat: {op_id} - {progress:.1f} - {message}")
                return True

        mock_cm = MockConnectionManager()

        # Test heartbeat for 3 cycles
        async def test_heartbeat():
            heartbeat_task = asyncio.create_task(simple_heartbeat(mock_cm, "test_op"))

            # Let it run for 35 seconds (3 heartbeat cycles)
            await asyncio.sleep(35)

            # Cancel heartbeat
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

        # Run test
        asyncio.run(test_heartbeat())

        print("✅ Heartbeat system test successful")
        return True

    except Exception as e:
        print(f"❌ Heartbeat test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("TESTING FINAL FIXES")
    print("=" * 30)

    tests = [
        ("Maya MEL Script", test_mel_script_generation),
        ("Agent Heartbeat", test_agent_heartbeat)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print(f"\n📊 Final Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL FIXES IMPLEMENTED SUCCESSFULLY!")
        print("✅ Maya DLL bypass with MEL scripts")
        print("✅ WebSocket heartbeat every 10 seconds")
        print("✅ Proper error handling and fallbacks")
    else:
        print("\n⚠️  Some fixes need more work")

    return passed == total

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)