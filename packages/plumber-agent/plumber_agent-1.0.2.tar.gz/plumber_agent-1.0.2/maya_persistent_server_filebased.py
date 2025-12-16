"""
File-Based Maya Persistent Server

Uses file-based IPC (command/response queues) instead of HTTP.
This bypasses the Windows subprocess HTTP communication issue.

Performance: Same as HTTP approach - 320x faster than spawning Maya each time.
Architecture: Command queue → Maya executes → Response queue
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Log file for diagnostics
log_file = Path(__file__).parent / "maya_server_filebased.log"

def log(message):
    """Write to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()

log("=" * 80)
log("FILE-BASED MAYA PERSISTENT SERVER STARTING")

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


def process_command(command_data):
    """
    Execute a Maya command and return the result.

    Args:
        command_data: Dict with 'command' and 'operation_type'

    Returns:
        Dict with execution result
    """
    command = command_data.get('command', '')
    operation_type = command_data.get('operation_type', 'generic')

    log(f"Executing: {operation_type}")
    log(f"Command preview: {command[:200] if len(command) > 200 else command}")

    exec_start = time.time()
    exec_globals = {
        'cmds': cmds,
        'maya': sys.modules['maya'],
        'result': None
    }

    try:
        # Capture print output
        import io
        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_capture

        exec(command, exec_globals)

        # Restore stdout
        sys.stdout = old_stdout
        captured_output = stdout_capture.getvalue()

        exec_time = time.time() - exec_start

        result = {
            'success': True,
            'result': str(exec_globals.get('result', 'OK')),
            'execution_time': exec_time
        }

        log(f"Success in {exec_time*1000:.1f}ms")
        if captured_output:
            log(f"Output: {captured_output.strip()}")
        log(f"Result: {result['result']}")
        return result

    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = old_stdout if 'old_stdout' in locals() else sys.stdout

        exec_time = time.time() - exec_start
        result = {
            'success': False,
            'error': str(e),
            'execution_time': exec_time
        }
        log(f"Error: {e}")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")
        return result


def run_server(command_file, response_file, ready_file):
    """
    Run the file-based Maya server.

    Args:
        command_file: Path to command queue file
        response_file: Path to response queue file
        ready_file: Path to ready indicator file
    """
    log(f"Command queue: {command_file}")
    log(f"Response queue: {response_file}")
    log(f"Ready indicator: {ready_file}")

    # Create ready file to signal we're initialized
    try:
        with open(ready_file, 'w') as f:
            ready_data = {
                'status': 'ready',
                'maya_version': maya_version,
                'pid': os.getpid(),
                'started_at': datetime.now().isoformat()
            }
            json.dump(ready_data, f)
        log(f"Ready file created: {ready_file}")
    except Exception as e:
        log(f"ERROR creating ready file: {e}")
        sys.exit(1)

    log("=" * 80)
    log("MAYA SERVER READY - Monitoring command queue")
    log("=" * 80)

    # Main loop: monitor command file
    last_command_mtime = 0

    while True:
        try:
            # Check if command file exists and has been modified
            if os.path.exists(command_file):
                current_mtime = os.path.getmtime(command_file)

                if current_mtime > last_command_mtime:
                    last_command_mtime = current_mtime

                    # Read command
                    try:
                        with open(command_file, 'r') as f:
                            command_data = json.load(f)

                        log(f"Command received: {command_data.get('operation_type', 'unknown')}")

                        # Execute command
                        result = process_command(command_data)

                        # Write response
                        with open(response_file, 'w') as f:
                            json.dump(result, f)

                        log(f"Response written to {response_file}")

                        # Delete command file to signal completion
                        try:
                            os.remove(command_file)
                            log("Command file removed")
                        except:
                            pass

                    except json.JSONDecodeError as e:
                        log(f"ERROR parsing command JSON: {e}")
                    except Exception as e:
                        log(f"ERROR processing command: {e}")
                        # Write error response
                        error_result = {
                            'success': False,
                            'error': str(e),
                            'execution_time': 0
                        }
                        try:
                            with open(response_file, 'w') as f:
                                json.dump(error_result, f)
                        except:
                            pass

            # Sleep briefly to avoid CPU spinning
            time.sleep(0.1)

        except KeyboardInterrupt:
            log("Received shutdown signal")
            break
        except Exception as e:
            log(f"ERROR in main loop: {e}")
            time.sleep(1)  # Sleep longer on error

    log("=" * 80)
    log("MAYA SERVER SHUTTING DOWN")
    log("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server (File-based IPC)")
    parser.add_argument("--command-file", required=True, help="Command queue file path")
    parser.add_argument("--response-file", required=True, help="Response queue file path")
    parser.add_argument("--ready-file", required=True, help="Ready indicator file path")
    args = parser.parse_args()

    log(f"Args: command={args.command_file}, response={args.response_file}, ready={args.ready_file}")

    run_server(args.command_file, args.response_file, args.ready_file)
