"""
Test Blender Persistent Server Performance

Measures actual performance improvement vs subprocess approach.
Target: 25-50x faster (5-10s → <200ms)
"""

import time
import requests
import json

# Local DCC agent endpoint
AGENT_URL = "http://127.0.0.1:8003"

def test_blender_operation():
    """Test a simple Blender operation via DCC agent."""

    # Simple Blender operation: create a cube
    operation = {
        "operation_id": "test_blender_cube_001",
        "dcc": "blender",
        "operation_type": "create_cube",
        "parameters": {
            "size": 2.0,
            "location": [0, 0, 0]
        },
        "input_files": [],
        "output_directory": "/tmp/blender_test",
        "timeout": 30
    }

    print("=" * 70)
    print("🧪 BLENDER PERSISTENT SERVER PERFORMANCE TEST")
    print("=" * 70)
    print(f"Operation: {operation['operation_type']}")
    print(f"Parameters: size={operation['parameters']['size']}")
    print()

    # Execute operation
    start_time = time.time()

    try:
        response = requests.post(
            f"{AGENT_URL}/execute",
            json=operation,
            timeout=35
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
                old_time_estimate = 7.0  # seconds (conservative estimate: 5-10s)
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

                if speedup >= 25:
                    print(f"✅ SPEEDUP TARGET ACHIEVED: {speedup:.1f}x ≥ 25x")
                else:
                    print(f"⚠️  Below speedup target: {speedup:.1f}x < 25x")
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

    # Run test
    success, exec_time, used_persistent = test_blender_operation()

    # Summary
    print()
    print("TEST SUMMARY")
    print("=" * 70)
    if success and used_persistent:
        if exec_time < 0.2:
            print("🎉 EXCELLENT: Blender persistent server working perfectly!")
        elif exec_time < 1.0:
            print("✅ GOOD: Blender persistent server working well!")
        else:
            print("⚠️  ACCEPTABLE: Blender persistent server working but slower than target")
    elif success:
        print("⚠️  Fallback mode: Operation succeeded but persistent server not used")
    else:
        print("❌ FAILED: Operation did not complete successfully")
    print("=" * 70)
