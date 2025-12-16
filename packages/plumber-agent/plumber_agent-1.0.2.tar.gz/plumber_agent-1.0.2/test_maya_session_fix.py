"""Test Maya session management implementation."""
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dcc_executor import DCCExecutor, OperationResult
from dcc_discovery import DCCDiscovery


class MockOperation:
    """Mock operation for testing."""
    def __init__(self, operation_id, operation_type, dcc_type, parameters, output_directory):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.dcc_type = dcc_type
        self.parameters = parameters
        self.output_directory = output_directory


async def test_maya_session_workflow():
    """Test complete Maya session workflow."""
    print("\n🧪 Testing Maya Session Management Implementation")
    print("=" * 70)

    # Initialize executor
    discovery = DCCDiscovery()
    executor = DCCExecutor(discovery)

    # Check Maya availability
    maya_available = discovery.get_executable_path("maya", "python") is not None
    print(f"\n📋 Maya available: {maya_available}")

    if not maya_available:
        print("❌ Maya not found - skipping tests")
        return

    # Create temp output directory
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="maya_session_test_")
    print(f"📁 Temp directory: {temp_dir}")

    try:
        # Test 1: Create Maya session
        print("\n" + "="*70)
        print("Test 1: Create Maya Session")
        print("="*70)

        session_op = MockOperation(
            operation_id="test_session_001",
            operation_type="session",
            dcc_type="maya",
            parameters={"session_id": "test_session_001"},
            output_directory=temp_dir
        )

        print("📝 Creating Maya session...")
        session_result = await executor.execute_operation(session_op)

        print(f"\n✅ Result: {session_result.success}")
        print(f"📊 Metadata: {session_result.metadata}")

        if session_result.success:
            session_id = session_result.metadata.get("session_id")
            print(f"🎉 Session created: {session_id}")
            print(f"📋 Status: {session_result.metadata.get('session_status')}")
            print(f"📝 Command queue: {session_result.metadata.get('command_queue')}")
        else:
            print(f"❌ Session creation failed: {session_result.error_message}")
            return

        # Test 2: Send command to session
        print("\n" + "="*70)
        print("Test 2: Send Command to Session")
        print("="*70)

        command = """
import maya.cmds as cmds
sphere_name = cmds.polySphere(name='test_sphere', radius=5)[0]
print(f'Created sphere: {sphere_name}')
"""

        command_op = MockOperation(
            operation_id="test_command_001",
            operation_type="command",
            dcc_type="maya",
            parameters={
                "session_id": session_id,
                "command": command,
                "timeout": 30
            },
            output_directory=temp_dir
        )

        print("📝 Sending command to Maya session...")
        print(f"Command: {command.strip()}")

        command_result = await executor.execute_operation(command_op)

        print(f"\n✅ Result: {command_result.success}")
        print(f"📊 Logs: {command_result.logs}")

        if not command_result.success:
            print(f"❌ Command failed: {command_result.error_message}")

        # Test 3: Close session
        print("\n" + "="*70)
        print("Test 3: Close Maya Session")
        print("="*70)

        close_op = MockOperation(
            operation_id="test_close_001",
            operation_type="session_close",
            dcc_type="maya",
            parameters={"session_id": session_id},
            output_directory=temp_dir
        )

        print("📝 Closing Maya session...")
        close_result = await executor.execute_operation(close_op)

        print(f"\n✅ Result: {close_result.success}")
        print(f"📊 Session closed: {close_result.metadata.get('closed')}")

        # Summary
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)

        tests = [
            ("Create Session", session_result.success),
            ("Send Command", command_result.success),
            ("Close Session", close_result.success)
        ]

        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")

        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temp directory: {temp_dir}")
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_maya_session_workflow())
