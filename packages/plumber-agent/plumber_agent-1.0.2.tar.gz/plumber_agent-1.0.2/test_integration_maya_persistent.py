"""
Test Maya Persistent Server Integration

This test validates that the persistent server integration works correctly
in the local-dcc-agent.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_integration():
    """Test Maya persistent server integration."""
    from dcc_executor import DCCExecutor
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("\n" + "="*60)
    print("Maya Persistent Server Integration Test")
    print("="*60)

    # Create executor
    print("\n[STEP 1] Creating DCC Executor...")
    executor = DCCExecutor()

    # Initialize executor (this will start Maya server)
    print("\n[STEP 2] Initializing DCC Executor (this will start Maya server)...")
    init_start = time.time()
    await executor.initialize()
    init_time = time.time() - init_start

    print(f"\n✓ Initialization complete in {init_time:.2f}s")

    if executor.maya_server and executor.maya_server.is_ready:
        print(f"✓ Maya persistent server is READY")
        print(f"  Startup time: {executor.maya_server.server_startup_time:.2f}s")

        server_info = executor.maya_server.get_server_info()
        if server_info:
            print(f"  Maya version: {server_info.get('maya_version')}")
            print(f"  Status: {server_info.get('status')}")

        # Test a simple operation
        print("\n[STEP 3] Testing Maya operation...")

        try:
            op_start = time.time()

            result = await executor.maya_server.execute_command(
                "import maya.cmds as cmds; result = cmds.polySphere(name='test_sphere')",
                "test_operation"
            )

            op_time = time.time() - op_start

            if result.get('success'):
                print(f"✓ Operation completed in {op_time*1000:.1f}ms")
                print(f"  Result: {result.get('result')}")
                print(f"  Execution time: {result.get('execution_time', 0)*1000:.1f}ms")

                # Compare to expected performance
                if op_time < 1.0:  # Less than 1 second
                    print("\n✅ SUCCESS - Operation was near-instant (<1s)")
                    print(f"   Expected improvement: {6000/op_time/1000:.0f}x faster than old approach")
                else:
                    print(f"\n⚠️  Warning: Operation took {op_time:.2f}s (expected <1s)")

            else:
                print(f"✗ Operation failed: {result.get('error')}")

        except Exception as e:
            print(f"✗ Operation error: {e}")

    else:
        print("✗ Maya persistent server NOT ready")
        if executor.maya_server:
            print("  Server object exists but not ready")
        else:
            print("  Server object is None")

    # Cleanup
    print("\n[STEP 4] Cleanup...")
    executor.cleanup()

    print("\n" + "="*60)
    print("Test Complete")
    print("="*60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_integration())
