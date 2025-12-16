"""
Simple Maya Persistent Server with Socket Server
More reliable than ThreadingHTTPServer for Windows/Maya environment.
"""

import os
import sys
import time
import json
import socket
import threading
from socketserver import TCPServer, BaseRequestHandler

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

class SimpleMayaHandler(BaseRequestHandler):
    """Simple request handler for Maya commands."""

    def handle(self):
        """Handle incoming request."""
        try:
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

            # Health check
            if "GET /health" in request_str:
                response = {
                    'status': 'ready',
                    'maya_version': maya_version,
                    'active_sessions': len(maya_sessions)
                }
                self.send_http_response(200, response)
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
                    except Exception as e:
                        exec_time = time.time() - exec_start
                        result = {
                            'success': False,
                            'error': str(e),
                            'execution_time': exec_time
                        }

                    self.send_http_response(200, result)
                    return

            # Unknown request
            self.send_http_response(404, {'error': 'Not found'})

        except Exception as e:
            print(f"[MAYA SERVER ERROR] {e}", flush=True)
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
    print(f"[MAYA SERVER] Starting server on {host}:{port}...", flush=True)

    server = ReusableTCPServer((host, port), SimpleMayaHandler)

    print(f"[MAYA SERVER] Server ready on http://{host}:{port}", flush=True)
    print("="*60, flush=True)
    print("Maya Persistent Server (Simple)", flush=True)
    print("="*60, flush=True)
    print(f"Maya Version: {maya_version}", flush=True)
    print(f"Health Check: http://{host}:{port}/health", flush=True)
    print(f"Execute Command: POST http://{host}:{port}/", flush=True)
    print("="*60, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[MAYA SERVER] Shutting down...", flush=True)
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (Simple)")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    run_server(args.host, args.port)
