"""
Maya HTTP Server Approach for Instant Session Creation

This approach launches ONE persistent Maya instance with a simple HTTP server,
then all operations are sent via HTTP POST (instant, no new process).

Expected performance:
- Initial Maya startup: ~6 seconds (one-time cost)
- Subsequent operations: <100ms (near-instant)
"""

import time
import subprocess
import os
import tempfile
import requests
import threading

MAYA_SERVER_PORT = 8765

def start_maya_http_server():
    """Start Maya with embedded HTTP server."""
    print("Starting Maya with HTTP server...")
    start_time = time.time()

    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

    # Script to start Maya with HTTP server
    startup_script = f'''
import os
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Disable problematic plugins
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

print("[STARTUP] Importing Maya...", flush=True)
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
print(f"[STARTUP] Maya {{cmds.about(version=True)}} initialized", flush=True)

class MayaRequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests and execute Maya commands."""

    def do_POST(self):
        """Handle POST request with Maya command."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))

            command = request.get('command', '')
            operation_type = request.get('operation_type', 'generic')

            print(f"[REQUEST] Executing: {{operation_type}}", flush=True)

            # Execute command in Maya context
            exec_globals = {{'cmds': cmds, 'maya': __import__('maya')}}
            exec_result = {{}}

            try:
                exec(command, exec_globals, exec_result)
                result = {{
                    'success': True,
                    'message': f'Operation {{operation_type}} completed',
                    'result': str(exec_result.get('result', 'OK'))
                }}
            except Exception as e:
                result = {{
                    'success': False,
                    'error': str(e)
                }}

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] Request failed: {{e}}", flush=True)
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        """Handle GET request (health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {{
                'status': 'ready',
                'maya_version': cmds.about(version=True)
            }}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

# Start HTTP server
server_address = ('localhost', {MAYA_SERVER_PORT})
httpd = HTTPServer(server_address, MayaRequestHandler)
print(f"[STARTUP] Maya HTTP server ready on port {MAYA_SERVER_PORT}", flush=True)

# Run server (this blocks)
httpd.serve_forever()
'''

    # Write startup script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(startup_script)
        temp_script = f.name

    # Launch Maya as background process
    maya_process = subprocess.Popen(
        [mayapy_path, temp_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

    # Read output in separate thread
    def read_output():
        for line in maya_process.stdout:
            print(f"   Maya: {line.rstrip()}")

    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    # Wait for Maya to be ready
    print("Waiting for Maya HTTP server...")
    max_wait = 30
    start_wait = time.time()

    while time.time() - start_wait < max_wait:
        try:
            response = requests.get(f'http://localhost:{MAYA_SERVER_PORT}/health', timeout=1)
            if response.status_code == 200:
                data = response.json()
                startup_time = time.time() - start_time
                print(f"Maya HTTP server ready in {startup_time:.2f}s (Maya {data.get('maya_version')})")
                return maya_process
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            time.sleep(0.5)
            continue

    print("Failed to connect to Maya HTTP server")
    maya_process.terminate()
    return None


def send_maya_command(command, operation_type="generic"):
    """Send command to Maya HTTP server."""
    try:
        start = time.time()
        response = requests.post(
            f'http://localhost:{MAYA_SERVER_PORT}/',
            json={'command': command, 'operation_type': operation_type},
            timeout=0.5  # Shorter timeout to detect if it's hanging
        )
        network_time = time.time() - start
        print(f"      Network time: {network_time*1000:.1f}ms")
        return response.json()
    except requests.exceptions.Timeout:
        print(f"      Request timed out after 500ms!")
        return None
    except Exception as e:
        print(f"      Request failed: {e}")
        return None


def test_maya_http_performance():
    """Test the HTTP server approach for performance."""
    print("\n" + "="*60)
    print("Maya HTTP Server Performance Test")
    print("="*60)

    maya_process = None

    try:
        # Step 1: Start Maya (one-time cost)
        print("\n[STEP 1] Starting Maya HTTP server (one-time initialization)...")
        startup_start = time.time()
        maya_process = start_maya_http_server()

        if not maya_process:
            print("Failed to start Maya HTTP server")
            return

        startup_time = time.time() - startup_start

        # Step 2: Test rapid operations (simulating multiple sessions)
        print("\n[STEP 2] Testing rapid operations...")

        operations = [
            ("Create sphere", "cmds.polySphere(name='test_sphere')"),
            ("Create cube", "cmds.polyCube(name='test_cube')"),
            ("Create plane", "cmds.polyPlane(name='test_plane')"),
            ("List objects", "result = str(cmds.ls(assemblies=True))"),
            ("Create sphere 2", "cmds.polySphere(name='test_sphere2')"),
        ]

        operation_times = []

        for op_name, command in operations:
            op_start = time.time()
            result = send_maya_command(command, op_name)
            op_time = time.time() - op_start
            operation_times.append(op_time)

            status = "SUCCESS" if result and result.get('success') else "FAILED"
            print(f"   {op_name}: {op_time*1000:.1f}ms [{status}]")

        avg_op_time = sum(operation_times) / len(operation_times)

        print("\n" + "="*60)
        print("RESULTS SUMMARY")
        print("="*60)
        print(f"Maya initial startup:     {startup_time:.2f}s (one-time cost)")
        print(f"Average operation time:   {avg_op_time*1000:.1f}ms")
        print(f"Speedup vs new process:   {6000/avg_op_time/1000:.0f}x faster")
        print()
        print("CONCLUSION:")
        if avg_op_time < 0.5:  # Less than 500ms
            print("   *** SUCCESS - HTTP server approach is MUCH faster! ***")
            print("   Recommendation: Implement this for production")
            print()
            print("NEXT STEPS:")
            print("   1. Integrate HTTP server into local-dcc-agent")
            print("   2. Start Maya HTTP server on agent startup")
            print("   3. Route all Maya operations through HTTP API")
            print("   4. Expected result: <1 second for ALL Maya operations")
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
            maya_process.wait(timeout=5)
            print("Maya server stopped")


if __name__ == "__main__":
    test_maya_http_performance()
