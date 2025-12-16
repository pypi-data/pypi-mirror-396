"""
Test Houdini Persistent Server Performance

Measures actual performance improvement vs subprocess approach.
Target: 150-200x faster (30-40s → <200ms)
"""

import time
import requests
import json

# Local DCC agent endpoint
AGENT_URL = "http://127.0.0.1:8003"

def test_houdini_operation():
    """Test a simple Houdini operation via DCC agent."""

    # Simple Houdini operation: create a sphere
    operation = {
        "operation_id": "test_houdini_sphere_001",
        "dcc": "houdini",
        "operation_type": "create_sphere",
        "parameters": {
            "name": "test_sphere",
            "radius": 2.0
        },
        "input_files": [],
        "output_directory": "/tmp/houdini_test",
        "timeout": 45
    }

    print("=" * 70)
    print("🧪 HOUDINI PERSISTENT SERVER PERFORMANCE TEST")
    print("=" * 70)
    print(f"Operation: {operation['operation_type']}")
    print(f"Parameters: name={operation['parameters']['name']}, radius={operation['parameters']['radius']}")
    print()

    # Execute operation
    start_time = time.time()

    try:
        response = requests.post(
            f"{AGENT_URL}/execute",
            json=operation,
            timeout=50
        )

        execution_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print("✅ OPERATION SUCCESSFUL")
            print(f"   Execution time: {execution_time*1000:.1f}ms ({execution_time:.3f}s)")
            print()

            # Check if persistent server was used
            metadata = result.get('metadata', {})
            via_persistent = metadata.get('via_persistent_server', False)
            server_exec_time = metadata.get('server_execution_time', 0)

            if via_persistent:
                print("🎯 PERSISTENT SERVER USED")
                print(f"   Server execution time: {server_exec_time*1000:.1f}ms")
                print(f"   Total time (including network): {execution_time*1000:.1f}ms")
                print()

                # Calculate speedup vs old approach
                old_time_estimate = 35.0  # seconds (conservative estimate: 30-40s)
                speedup = old_time_estimate / execution_time

                print("📊 PERFORMANCE ANALYSIS")
                print(f"   Old approach (estimated): ~{old_time_estimate:.1f}s")
                print(f"   New approach (measured): {execution_time:.3f}s")
                print(f"   Speedup: {speedup:.1f}x faster")
                print(f"   Time saved: {(old_time_estimate - execution_time):.2f}s ({((old_time_estimate - execution_time) / old_time_estimate * 100):.1f}%)")
                print()

                # Target check
                target_time = 0.2  # 200ms target
                if execution_time <= target_time:
                    print(f"✅ TARGET ACHIEVED: {execution_time*1000:.0f}ms ≤ {target_time*1000:.0f}ms")
                else:
                    print(f"⚠️  Above target: {execution_time*1000:.0f}ms > {target_time*1000:.0f}ms")
                    print(f"   (Still {speedup:.1f}x faster than subprocess approach)")

                if speedup >= 150:
                    print(f"✅ SPEEDUP TARGET ACHIEVED: {speedup:.1f}x ≥ 150x")
                elif speedup >= 100:
                    print(f"✅ EXCELLENT SPEEDUP: {speedup:.1f}x ≥ 100x")
                elif speedup >= 50:
                    print(f"✅ GOOD SPEEDUP: {speedup:.1f}x ≥ 50x")
                else:
                    print(f"⚠️  Below speedup target: {speedup:.1f}x < 50x")
                    print(f"   (But still significant improvement)")
            else:
                print("⚠️  FALLBACK: Subprocess approach used")
                print(f"   Execution time: {execution_time:.2f}s")
                print("   (Persistent server may not be available)")

            print()
            print("=" * 70)
            return True, execution_time, via_persistent

        else:
            print(f"❌ OPERATION FAILED")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, execution_time, False

    except requests.exceptions.Timeout:
        execution_time = time.time() - start_time
        print(f"❌ TIMEOUT after {execution_time:.1f}s")
        return False, execution_time, False
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ ERROR: {e}")
        return False, execution_time, False


def test_houdini_session_workflow():
    """Test a complete Houdini workflow: session → command → export."""

    print("\n" + "=" * 70)
    print("🧪 HOUDINI WORKFLOW TEST: Session → Command → Export")
    print("=" * 70)

    workflow_start = time.time()
    results = []

    # Test 1: Session creation
    print("\n📝 Test 1/3: Creating Houdini session...")
    session_op = {
        "operation_id": "test_houdini_session_001",
        "dcc": "houdini",
        "operation_type": "session",
        "parameters": {"session_id": "test_session"},
        "input_files": [],
        "output_directory": "/tmp/houdini_test",
        "timeout": 45
    }

    try:
        start = time.time()
        response = requests.post(f"{AGENT_URL}/execute", json=session_op, timeout=50)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"   ✅ Session created in {elapsed*1000:.1f}ms")
            results.append(("session", elapsed, True))
        else:
            print(f"   ❌ Session creation failed")
            results.append(("session", elapsed, False))
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: Execute command
    print("\n📝 Test 2/3: Executing Houdini command...")
    command_op = {
        "operation_id": "test_houdini_command_001",
        "dcc": "houdini",
        "operation_type": "command",
        "parameters": {
            "command": "print(f'Houdini version: {hou.applicationVersionString()}')"
        },
        "input_files": [],
        "output_directory": "/tmp/houdini_test",
        "timeout": 30
    }

    try:
        start = time.time()
        response = requests.post(f"{AGENT_URL}/execute", json=command_op, timeout=35)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"   ✅ Command executed in {elapsed*1000:.1f}ms")
            results.append(("command", elapsed, True))
        else:
            print(f"   ❌ Command execution failed")
            results.append(("command", elapsed, False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("command", 0, False))

    # Test 3: Export scene
    print("\n📝 Test 3/3: Exporting Houdini scene...")
    export_op = {
        "operation_id": "test_houdini_export_001",
        "dcc": "houdini",
        "operation_type": "export",
        "parameters": {
            "export_path": "/tmp/houdini_test/test_scene.hip"
        },
        "input_files": [],
        "output_directory": "/tmp/houdini_test",
        "timeout": 30
    }

    try:
        start = time.time()
        response = requests.post(f"{AGENT_URL}/execute", json=export_op, timeout=35)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"   ✅ Scene exported in {elapsed*1000:.1f}ms")
            results.append(("export", elapsed, True))
        else:
            print(f"   ❌ Export failed")
            results.append(("export", elapsed, False))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("export", 0, False))

    # Summary
    total_time = time.time() - workflow_start
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)

    for op_type, elapsed, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {op_type:12s}: {elapsed*1000:6.1f}ms")

    print(f"\n  Total workflow time: {total_time*1000:.1f}ms ({total_time:.2f}s)")

    # Old approach estimate
    old_total = 35.0 * 3  # ~35s per operation × 3 operations
    speedup = old_total / total_time if total_time > 0 else 0

    print(f"\n  Old approach (estimated): ~{old_total:.0f}s")
    print(f"  Speedup: {speedup:.1f}x faster")
    print(f"  Time saved: {old_total - total_time:.1f}s")

    all_success = all(success for _, _, success in results)

    if all_success and speedup >= 150:
        print("\n  🎉 EXCELLENT: All operations succeeded with 150x+ speedup!")
    elif all_success and speedup >= 50:
        print("\n  ✅ GOOD: All operations succeeded with significant speedup!")
    elif all_success:
        print("\n  ✅ OK: All operations succeeded")
    else:
        print("\n  ⚠️  Some operations failed")

    print("=" * 70)
    return all_success


if __name__ == "__main__":
    # Force UTF-8 encoding for Windows
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Check if agent is running
    try:
        health_response = requests.get(f"{AGENT_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ DCC Agent is running")
            print()
        else:
            print("⚠️  DCC Agent health check failed")
            print()
    except:
        print("❌ DCC Agent is not responding at", AGENT_URL)
        print("   Please ensure the agent is running:")
        print("   cd local-dcc-agent && ./venv/Scripts/python.exe src/main.py --host 127.0.0.1 --port 8003")
        exit(1)

    # Run single operation test
    print("\n" + "🔷" * 35)
    print(" TEST 1: SINGLE OPERATION")
    print("🔷" * 35)
    success, exec_time, used_persistent = test_houdini_operation()

    # Run workflow test
    print("\n" + "🔷" * 35)
    print(" TEST 2: COMPLETE WORKFLOW")
    print("🔷" * 35)
    workflow_success = test_houdini_session_workflow()

    # Final summary
    print()
    print("\n" + "=" * 70)
    print("FINAL TEST SUMMARY")
    print("=" * 70)

    if success and used_persistent:
        if exec_time < 0.2:
            print("🎉 EXCELLENT: Houdini persistent server working perfectly!")
        elif exec_time < 1.0:
            print("✅ GOOD: Houdini persistent server working well!")
        else:
            print("⚠️  ACCEPTABLE: Houdini persistent server working but slower than target")
    elif success:
        print("⚠️  Fallback mode: Operation succeeded but persistent server not used")
    else:
        print("❌ FAILED: Operation did not complete successfully")

    if workflow_success:
        print("✅ WORKFLOW TEST: All operations succeeded")
    else:
        print("⚠️  WORKFLOW TEST: Some operations failed")

    print("=" * 70)
