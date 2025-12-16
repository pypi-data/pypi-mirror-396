#!/usr/bin/env python3
"""
Test WebSocket heartbeat system
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

async def test_heartbeat():
    """Test the heartbeat system with a mock long operation."""
    print("Testing WebSocket heartbeat system...")

    try:
        from connection_manager import ConnectionManager

        # Create connection manager
        cm = ConnectionManager("wss://plumber-production-446f.up.railway.app/ws/dcc-agent", "test_agent")

        # Mock long operation
        async def mock_long_operation():
            print("Starting mock long operation...")
            for i in range(12):  # 12 x 10 = 120 seconds
                await asyncio.sleep(10)  # Simulate 10 seconds of work
                print(f"Mock operation progress: {i+1}/12 ({(i+1)*10} seconds)")
            print("Mock long operation completed")
            return {"status": "success", "duration": "120 seconds"}

        # Test heartbeat wrapper
        print("Starting operation with heartbeat...")
        result = await cm.send_operation_with_heartbeat("test_op_123", mock_long_operation)

        print(f"Operation result: {result}")
        return True

    except Exception as e:
        print(f"Heartbeat test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("TESTING WEBSOCKET HEARTBEAT SYSTEM")
    print("=" * 40)

    success = await test_heartbeat()

    if success:
        print("\nHeartbeat system test PASSED!")
    else:
        print("\nHeartbeat system test FAILED")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)