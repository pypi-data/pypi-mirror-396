"""
Maya Persistent Server using http.server
More reliable than socketserver on Windows.
"""

import os
import sys
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Create log file
log_file = os.path.join(os.path.dirname(__file__), "maya_server_http.log")

def log(message):
    """Write to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()

log("=" * 80)
log("HTTP MAYA SERVER STARTING")

# Set environment BEFORE importing Maya
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

log("Initializing Maya...")
start_init = time.time()

try:
    import maya.standalone
    maya.standalone.initialize(name='python')
    import maya.cmds as cmds

    maya_version = cmds.about(version=True)
    init_time = time.time() - start_init
    log(f"Maya {maya_version} initialized in {init_time:.2f}s")

except Exception as e:
    log(f"ERROR during Maya initialization: {e}")
    import traceback
    log(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

# Session management
maya_sessions = {}


class MayaHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Maya commands."""

    def log_message(self, format, *args):
        """Override to use our log function."""
        log(f"HTTP: {format % args}")

    def do_GET(self):
        """Handle GET requests (health check)."""
        log(f"GET request: {self.path}")

        if self.path == '/health' or self.path == '/health/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response = {
                'status': 'ready',
                'maya_version': maya_version,
                'active_sessions': len(maya_sessions)
            }

            self.wfile.write(json.dumps(response).encode('utf-8'))
            log("Health check response sent")
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests (command execution)."""
        log(f"POST request: {self.path}")

        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')

            if not body.strip():
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Empty request'}).encode('utf-8'))
                return

            request_data = json.loads(body)
            command = request_data.get('command', '')
            operation_type = request_data.get('operation_type', 'generic')
            log(f"Executing: {operation_type}")

            # Execute Maya command
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
                    'execution_time': exec_time
                }
                log(f"Success in {exec_time*1000:.1f}ms")

            except Exception as e:
                exec_time = time.time() - exec_start
                result = {
                    'success': False,
                    'error': str(e),
                    'execution_time': exec_time
                }
                log(f"Error: {e}")

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        except Exception as e:
            log(f"POST error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def run_server(host="127.0.0.1", port=8766):
    """Run the Maya HTTP server."""
    log(f"Creating HTTP server on {host}:{port}...")

    try:
        server = HTTPServer((host, port), MayaHTTPHandler)
        log(f"Server created and bound to {host}:{port}")

        log("=" * 80)
        log("MAYA SERVER READY")
        log(f"Health: http://{host}:{port}/health")
        log("=" * 80)

        # Start serving
        log("Starting server.serve_forever()...")
        server.serve_forever()

    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        log(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (HTTP)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    log(f"Args: host={args.host}, port={args.port}")
    run_server(args.host, args.port)
