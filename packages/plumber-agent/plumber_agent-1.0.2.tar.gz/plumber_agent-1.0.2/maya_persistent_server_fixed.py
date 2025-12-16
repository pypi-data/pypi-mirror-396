"""
Fixed Maya Persistent Server
Uses ThreadingMixIn for proper connection handling on Windows.
"""

import os
import sys
import time
import json
import socket
import threading
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler
from datetime import datetime

# Create log file
log_file = os.path.join(os.path.dirname(__file__), "maya_server_fixed.log")

def log(message):
    """Write to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()

log("=" * 80)
log("FIXED MAYA SERVER STARTING")

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

class MayaHandler(BaseRequestHandler):
    """Request handler for Maya commands."""

    def handle(self):
        """Handle incoming request."""
        try:
            log(f"Connection from {self.client_address}")

            # Read request with timeout
            self.request.settimeout(10.0)

            data = b""
            while True:
                try:
                    chunk = self.request.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                    # Check for end of HTTP request
                    if b"\r\n\r\n" in data:
                        # Check if there's a body
                        if b"Content-Length:" in data:
                            headers = data.split(b"\r\n\r\n")[0].decode('utf-8', errors='ignore')
                            for line in headers.split('\r\n'):
                                if line.startswith('Content-Length:'):
                                    content_length = int(line.split(':')[1].strip())
                                    body_start = data.find(b"\r\n\r\n") + 4
                                    body_received = len(data) - body_start
                                    if body_received >= content_length:
                                        break
                        else:
                            break
                except socket.timeout:
                    log("Socket timeout reading request")
                    break

            # Parse request
            request_str = data.decode('utf-8', errors='ignore')
            request_line = request_str.split('\r\n')[0] if request_str else "EMPTY"
            log(f"Request: {request_line}")

            # Health check
            if "GET /health" in request_str:
                response = {
                    'status': 'ready',
                    'maya_version': maya_version,
                    'active_sessions': len(maya_sessions)
                }
                self.send_response(200, response)
                log("Health check OK")
                return

            # Command execution
            if "POST /" in request_str:
                body_start = request_str.find("\r\n\r\n") + 4
                body = request_str[body_start:]

                if body.strip():
                    request_data = json.loads(body)
                    command = request_data.get('command', '')
                    operation_type = request_data.get('operation_type', 'generic')
                    log(f"Executing: {operation_type}")

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

                    self.send_response(200, result)
                    return

            # Unknown request
            self.send_response(404, {'error': 'Not found'})

        except Exception as e:
            log(f"Handler error: {e}")
            try:
                self.send_response(500, {'error': str(e)})
            except:
                pass

    def send_response(self, status_code, data):
        """Send HTTP response."""
        try:
            body = json.dumps(data).encode('utf-8')

            response = f"HTTP/1.1 {status_code} OK\r\n"
            response += "Content-Type: application/json\r\n"
            response += f"Content-Length: {len(body)}\r\n"
            response += "Connection: close\r\n"
            response += "\r\n"

            self.request.sendall(response.encode('utf-8') + body)
        except Exception as e:
            log(f"Error sending response: {e}")


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """Threaded TCP Server for handling multiple connections."""
    allow_reuse_address = True
    daemon_threads = True

    # Increase socket timeout to prevent premature closures
    timeout = 30


def run_server(host="127.0.0.1", port=8766):
    """Run the Maya TCP server."""
    log(f"Creating threaded TCP server on {host}:{port}...")

    try:
        server = ThreadedTCPServer((host, port), MayaHandler)
        log(f"Server bound to {host}:{port}")

        # Verify socket is actually listening
        server.socket.listen(5)
        log(f"Socket listening (backlog: 5)")

        log("=" * 80)
        log("MAYA SERVER READY")
        log(f"Health: http://{host}:{port}/health")
        log("=" * 80)

        # Start serving - this blocks
        server.serve_forever()

    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        log(f"Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (Fixed)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    log(f"Args: host={args.host}, port={args.port}")
    run_server(args.host, args.port)
