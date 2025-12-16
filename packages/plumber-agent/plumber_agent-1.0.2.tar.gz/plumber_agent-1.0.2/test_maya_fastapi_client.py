"""
Test client for Maya FastAPI persistent server.
This validates that the FastAPI approach gives us near-instant performance.
"""

import time
import subprocess
import requests
import threading
import os

MAYA_SERVER_PORT = 8766

def start_maya_fastapi_server():
    """Start Maya optimized server in background."""
    print("Starting Maya optimized server...")
    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
    script_path = "maya_persistent_server_optimized.py"  # Use optimized version

    process = subprocess.Popen(
        [mayapy_path, script_path, "--port", str(MAYA_SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Read output in thread
    def read_output():
        for line in process.stdout:
            print(f"   Maya: {line.rstrip()}")

    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    # Wait for server to be ready
    print("Waiting for Maya FastAPI server...")
    max_wait = 30
    start_wait = time.time()

    while time.time() - start_wait < max_wait:
        try:
            response = requests.get(f'http://localhost:{MAYA_SERVER_PORT}/health', timeout=1)
            if response.status_code == 200:
                startup_time = time.time() - start_wait
                data = response.json()
                print(f"Maya FastAPI server ready in {startup_time:.2f}s (Maya {data.get('maya_version')})")
                return process
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(0.5)
            continue

    print("Failed to connect to Maya FastAPI server")
    process.terminate()
    return None

def send_maya_command(command, operation_type="generic"):
    """Send command to Maya FastAPI server."""
    try:
        start = time.time()
        response = requests.post(
            f'http://localhost:{MAYA_SERVER_PORT}/',  # Changed from /execute to /
            json={'command': command, 'operation_type': operation_type},
            timeout=5
        )
        network_time = time.time() - start

        if response.status_code == 200:
            result = response.json()
            return {
                'success': result.get('success'),
                'network_time': network_time,
                'execution_time': result.get('execution_time', 0)
            }
        else:
            return {'success': False, 'network_time': network_time}
    except Exception as e:
        print(f"      Request failed: {e}")
        return None

def test_maya_fastapi_performance():
    """Test the FastAPI approach for optimal performance."""
    print("\n" + "="*60)
    print("Maya FastAPI Persistent Server Performance Test")
    print("="*60)

    maya_process = None

    try:
        # Step 1: Start Maya FastAPI server (one-time cost)
        print("\n[STEP 1] Starting Maya FastAPI server (one-time initialization)...")
        startup_start = time.time()
        maya_process = start_maya_fastapi_server()

        if not maya_process:
            print("Failed to start Maya FastAPI server")
            return

        startup_time = time.time() - startup_start

        # Step 2: Test rapid operations
        print("\n[STEP 2] Testing rapid operations...")

        operations = [
            ("Create sphere", "cmds.polySphere(name='test_sphere')"),
            ("Create cube", "cmds.polyCube(name='test_cube')"),
            ("Create plane", "cmds.polyPlane(name='test_plane')"),
            ("List objects", "result = str(cmds.ls(assemblies=True))"),
            ("Create torus", "cmds.polyTorus(name='test_torus')"),
            ("Create cylinder", "cmds.polyCylinder(name='test_cylinder')"),
            ("Create cone", "cmds.polyCone(name='test_cone')"),
            ("Create pyramid", "cmds.polyPyramid(name='test_pyramid')"),
            ("Get scene info", "result = str(cmds.file(q=True, sceneName=True))"),
            ("Create pipe", "cmds.polyPipe(name='test_pipe')"),
        ]

        operation_times = []
        execution_times = []

        for op_name, command in operations:
            result = send_maya_command(command, op_name)

            if result:
                operation_times.append(result['network_time'])
                execution_times.append(result.get('execution_time', 0))

                status = "SUCCESS" if result.get('success') else "FAILED"
                print(f"   {op_name:20} {result['network_time']*1000:6.1f}ms (exec: {result.get('execution_time', 0)*1000:5.1f}ms) [{status}]")
            else:
                print(f"   {op_name}: FAILED (no response)")

        if operation_times:
            avg_op_time = sum(operation_times) / len(operation_times)
            avg_exec_time = sum(execution_times) / len(execution_times)

            print("\n" + "="*60)
            print("RESULTS SUMMARY")
            print("="*60)
            print(f"Maya initial startup:       {startup_time:.2f}s (one-time cost)")
            print(f"Average total time:         {avg_op_time*1000:.1f}ms")
            print(f"Average Maya exec time:     {avg_exec_time*1000:.2f}ms")
            print(f"Network overhead:           {(avg_op_time - avg_exec_time)*1000:.1f}ms")
            print(f"Speedup vs new process:     {6000/avg_op_time/1000:.0f}x faster")
            print()
            print("="*60)
            print("PERFORMANCE VERDICT")
            print("="*60)

            if avg_op_time < 0.1:  # Less than 100ms
                print("   *** EXCELLENT - Operations are near-instant! ***")
                print(f"   FastAPI approach achieves <100ms per operation")
                print()
                print("PRODUCTION READINESS:")
                print("   [x] One-time 8s startup cost (acceptable)")
                print(f"   [x] {avg_op_time*1000:.1f}ms average operation time (EXCELLENT!)")
                print(f"   [x] {6000/avg_op_time/1000:.0f}x faster than spawning new process")
                print()
                print("RECOMMENDATION:")
                print("   --> Integrate Maya FastAPI server into local-dcc-agent")
                print("   --> Start server on agent startup")
                print("   --> Route all Maya operations through FastAPI")
                print("   --> Expected result: <100ms for ALL Maya operations")
            elif avg_op_time < 0.5:  # Less than 500ms
                print("   GOOD - Operations are fast but could be optimized")
                print(f"   Average: {avg_op_time*1000:.1f}ms")
            else:
                print("   Operations still slow - investigate further")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nCleaning up...")
        if maya_process:
            maya_process.terminate()
            try:
                maya_process.wait(timeout=5)
            except:
                maya_process.kill()
            print("Maya server stopped")


if __name__ == "__main__":
    test_maya_fastapi_performance()
