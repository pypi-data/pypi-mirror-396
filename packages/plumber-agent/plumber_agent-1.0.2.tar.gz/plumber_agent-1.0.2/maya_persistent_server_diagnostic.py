"""
Diagnostic Maya Persistent Server
Writes detailed logs to file to diagnose startup issues.
"""

import os
import sys
import time
import json
import socket
import threading
from socketserver import TCPServer, BaseRequestHandler
from datetime import datetime

# Create log file
log_file = os.path.join(os.path.dirname(__file__), "maya_server_diagnostic.log")

def log(message):
    """Write to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()

log("=" * 80)
log("DIAGNOSTIC MAYA SERVER STARTING")
log(f"Python: {sys.version}")
log(f"Python executable: {sys.executable}")
log(f"Working directory: {os.getcwd()}")
log(f"Script path: {__file__}")

# Set environment BEFORE importing Maya
log("Setting Maya environment variables...")
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""
log("Environment variables set")

log("Importing Maya standalone...")
start_init = time.time()

try:
    import maya.standalone
    log(f"Maya standalone imported in {time.time() - start_init:.2f}s")

    log("Calling maya.standalone.initialize()...")
    init_start = time.time()
    maya.standalone.initialize(name='python')
    log(f"Maya standalone initialized in {time.time() - init_start:.2f}s")

    log("Importing maya.cmds...")
    import maya.cmds as cmds
    log("maya.cmds imported")

    maya_version = cmds.about(version=True)
    init_time = time.time() - start_init
    log(f"Maya {maya_version} fully initialized in {init_time:.2f}s")

except Exception as e:
    log(f"ERROR during Maya initialization: {e}")
    import traceback
    log(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)

# Session management
maya_sessions = {}

class SimpleMayaHandler(BaseRequestHandler):
    """Simple request handler for Maya commands."""

    def handle(self):
        """Handle incoming request."""
        try:
            log(f"Received connection from {self.client_address}")

            # Read request
            data = b""
            while True:
                chunk = self.request.recv(4096)
                if not chunk:
                    break
                data += chunk
                # Simple check for end of HTTP request
                if b"\r\n\r\n" in data:
                    # Check if there's a body
                    if b"Content-Length:" in data:
                        headers = data.split(b"\r\n\r\n")[0].decode('utf-8')
                        for line in headers.split('\r\n'):
                            if line.startswith('Content-Length:'):
                                content_length = int(line.split(':')[1].strip())
                                body_start = data.find(b"\r\n\r\n") + 4
                                body_received = len(data) - body_start
                                if body_received >= content_length:
                                    break
                    else:
                        break

            # Parse request
            request_str = data.decode('utf-8')
            log(f"Request: {request_str.split()[0:2] if request_str else 'EMPTY'}")

            # Health check
            if "GET /health" in request_str:
                log("Health check request")
                response = {
                    'status': 'ready',
                    'maya_version': maya_version,
                    'active_sessions': len(maya_sessions)
                }
                self.send_http_response(200, response)
                log("Health check response sent")
                return

            # Command execution
            if "POST /" in request_str:
                # Extract JSON body
                body_start = request_str.find("\r\n\r\n") + 4
                body = request_str[body_start:]

                if body.strip():
                    request_data = json.loads(body)
                    command = request_data.get('command', '')
                    operation_type = request_data.get('operation_type', 'generic')
                    log(f"Executing command: {operation_type}")

                    # Execute command
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
                        log(f"Command executed successfully in {exec_time*1000:.1f}ms")
                    except Exception as e:
                        exec_time = time.time() - exec_start
                        result = {
                            'success': False,
                            'error': str(e),
                            'execution_time': exec_time
                        }
                        log(f"Command failed: {e}")

                    self.send_http_response(200, result)
                    return

            # Unknown request
            log("Unknown request type")
            self.send_http_response(404, {'error': 'Not found'})

        except Exception as e:
            log(f"Handler error: {e}")
            import traceback
            log(f"Traceback:\n{traceback.format_exc()}")
            try:
                self.send_http_response(500, {'error': str(e)})
            except:
                pass

    def send_http_response(self, status_code, data):
        """Send HTTP response."""
        body = json.dumps(data).encode('utf-8')

        response = f"HTTP/1.1 {status_code} OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"

        self.request.sendall(response.encode('utf-8') + body)


class ReusableTCPServer(TCPServer):
    """TCP Server that allows address reuse."""
    allow_reuse_address = True


def run_server(host="127.0.0.1", port=8766):
    """Run the Maya TCP server."""
    log(f"Creating TCP server on {host}:{port}...")

    try:
        server = ReusableTCPServer((host, port), SimpleMayaHandler)
        log(f"Server created successfully")
        log(f"Server bound to {host}:{port}")
        log(f"Server listening...")
        log("=" * 80)
        log("MAYA SERVER READY - Waiting for connections")
        log("=" * 80)

        # Server is ready - this is what we're waiting for!
        server.serve_forever()

    except Exception as e:
        log(f"ERROR creating/starting server: {e}")
        import traceback
        log(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (Diagnostic)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    log(f"Command line args: host={args.host}, port={args.port}")
    run_server(args.host, args.port)
