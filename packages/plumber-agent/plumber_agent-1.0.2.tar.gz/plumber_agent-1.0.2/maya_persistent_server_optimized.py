"""
Optimized Maya Persistent Server using ThreadingHTTPServer
This removes the 500ms latency from single-threaded HTTP server.

Expected Performance:
- Initial startup: ~8 seconds (one-time cost at agent start)
- Subsequent operations: <10ms (near-instant!)
"""

import os
import sys
import time
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Set environment BEFORE importing Maya
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

print("[MAYA SERVER] Initializing Maya standalone...", flush=True)
start_init = time.time()

import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

init_time = time.time() - start_init
maya_version = cmds.about(version=True)
print(f"[MAYA SERVER] Maya {maya_version} initialized in {init_time:.2f}s", flush=True)

# Session management
maya_sessions = {}

class MayaRequestHandler(BaseHTTPRequestHandler):
    """Optimized handler for Maya commands."""

    def do_POST(self):
        """Handle POST request with Maya command."""
        request_start = time.time()

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))

            command = request.get('command', '')
            operation_type = request.get('operation_type', 'generic')

            # Execute command in Maya context
            exec_start = time.time()
            exec_globals = {
                'cmds': cmds,
                'maya': sys.modules['maya'],
                'result': None
            }

            try:
                exec(command, exec_globals)
                exec_time = time.time() - exec_start

                result = {
                    'success': True,
                    'result': str(exec_globals.get('result', 'OK')),
                    'execution_time': exec_time,
                    'total_time': time.time() - request_start
                }
            except Exception as e:
                exec_time = time.time() - exec_start
                result = {
                    'success': False,
                    'error': str(e),
                    'execution_time': exec_time,
                    'total_time': time.time() - request_start
                }

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Connection', 'keep-alive')  # Keep connection open for performance
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_result = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_result).encode('utf-8'))

    def do_GET(self):
        """Handle GET request (health check and session management)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            response = {
                'status': 'ready',
                'maya_version': cmds.about(version=True),
                'active_sessions': len(maya_sessions)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/sessions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            response = {'sessions': list(maya_sessions.keys())}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress HTTP request logging for performance."""
        pass

def run_server(host="127.0.0.1", port=8766):
    """Run the Maya Threading HTTP server."""
    server_address = (host, port)

    # Use ThreadingHTTPServer for concurrent request handling
    httpd = ThreadingHTTPServer(server_address, MayaRequestHandler)

    print(f"[MAYA SERVER] Server ready on http://{host}:{port}", flush=True)
    print("="*60, flush=True)
    print("Maya Persistent Server (Optimized)", flush=True)
    print("="*60, flush=True)
    print(f"Maya Version: {maya_version}", flush=True)
    print(f"Health Check: http://{host}:{port}/health", flush=True)
    print(f"Execute Command: POST http://{host}:{port}/", flush=True)
    print("="*60, flush=True)

    # Run server (blocks)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[MAYA SERVER] Shutting down...")
        httpd.shutdown()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (Optimized)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    run_server(args.host, args.port)
