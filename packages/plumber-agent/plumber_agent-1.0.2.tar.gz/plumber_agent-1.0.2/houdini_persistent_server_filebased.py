"""
File-Based Houdini Persistent Server

Uses file-based IPC (command/response queues) for communication.
Keeps Houdini running in the background to avoid initialization overhead.

Performance: 25-50x faster than spawning Houdini each time.
Architecture: Command queue → Houdini executes → Response queue

Based on: blender_persistent_server_filebased.py
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Log file for diagnostics
log_file = Path(__file__).parent / "houdini_server_filebased.log"

def log(message):
    """Write to log file with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
        f.flush()

log("=" * 80)
log("FILE-BASED HOUDINI PERSISTENT SERVER STARTING")

log("Initializing Houdini...")
start_init = time.time()

try:
    import hou

    # Get Houdini version
    houdini_version_tuple = hou.applicationVersion()
    houdini_version = f"{houdini_version_tuple[0]}.{houdini_version_tuple[1]}.{houdini_version_tuple[2]}"
    init_time = time.time() - start_init
    log(f"Houdini {houdini_version} initialized in {init_time:.2f}s")

    # Clear default scene for clean state
    hou.hipFile.clear(suppress_save_prompt=True)
    log("Default scene cleared")

except Exception as e:
    log(f"ERROR during Houdini initialization: {e}")
    import traceback
    log(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)


def process_command(command_data):
    """
    Execute a Houdini command and return the result.

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
        'hou': hou,
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

        if captured_output:
            result['output'] = captured_output
            log(f"Command output: {captured_output[:200]}")

        log(f"Success in {exec_time*1000:.1f}ms")
        return result

    except Exception as e:
        exec_time = time.time() - exec_start
        error_msg = str(e)
        log(f"ERROR: {error_msg}")

        import traceback
        log(f"Traceback:\n{traceback.format_exc()}")

        return {
            'success': False,
            'result': None,
            'error': error_msg,
            'execution_time': exec_time
        }


def can_import(module_name):
    """Check if module can be imported."""
    try:
        __import__(module_name)
        return True
    except:
        return False


def run_server(command_file: Path, response_file: Path, ready_file: Path):
    """
    Main server loop - monitor command file and execute commands.

    Args:
        command_file: Path to command JSON file
        response_file: Path to response JSON file
        ready_file: Path to ready signal file
    """
    log("=" * 80)
    log("HOUDINI SERVER READY - Monitoring command queue")
    log(f"Command file: {command_file}")
    log(f"Response file: {response_file}")
    log(f"Ready file: {ready_file}")

    # Write ready file to signal server is initialized
    houdini_version_tuple = hou.applicationVersion()
    ready_data = {
        'status': 'ready',
        'houdini_version': f"{houdini_version_tuple[0]}.{houdini_version_tuple[1]}",
        'pid': os.getpid(),
        'started_at': datetime.now().isoformat()
    }

    with open(ready_file, 'w') as f:
        json.dump(ready_data, f, indent=2)

    log(f"Ready file written - Server PID: {os.getpid()}")

    # Main monitoring loop
    last_command_time = None

    while True:
        try:
            # Check if command file exists
            if command_file.exists():
                # Check if this is a new command (modified time changed)
                current_mtime = command_file.stat().st_mtime

                if last_command_time is None or current_mtime != last_command_time:
                    last_command_time = current_mtime

                    log("Command file detected")

                    # Read command
                    try:
                        with open(command_file, 'r') as f:
                            command_data = json.load(f)

                        log(f"Command received: {command_data.get('operation_type', 'unknown')}")

                        # Execute command
                        result = process_command(command_data)

                        # Write response
                        with open(response_file, 'w') as f:
                            json.dump(result, f, indent=2)

                        log("Response written to response.json")

                        # Delete command file to signal completion
                        try:
                            command_file.unlink()
                            log("Command file deleted (execution complete)")
                        except Exception as e:
                            log(f"Warning: Could not delete command file: {e}")

                    except (json.JSONDecodeError, IOError) as e:
                        log(f"Error reading command file: {e}")
                        # Write error response
                        error_result = {
                            'success': False,
                            'error': f'Failed to read command: {str(e)}',
                            'execution_time': 0.0
                        }
                        with open(response_file, 'w') as f:
                            json.dump(error_result, f, indent=2)

            # Small sleep to prevent busy waiting
            time.sleep(0.05)  # Check every 50ms

        except KeyboardInterrupt:
            log("Server shutdown requested (Ctrl+C)")
            break

        except Exception as e:
            log(f"ERROR in main loop: {e}")
            import traceback
            log(f"Traceback:\n{traceback.format_exc()}")
            time.sleep(1)  # Longer sleep after error

    log("=" * 80)
    log("HOUDINI SERVER SHUTDOWN")


if __name__ == "__main__":
    # Manual argument parsing for Houdini's sys.argv
    log(f"sys.argv: {sys.argv}")

    command_file_path = None
    response_file_path = None
    ready_file_path = None

    # Parse arguments manually
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--command-file" and i + 1 < len(sys.argv):
            command_file_path = sys.argv[i + 1]
            i += 2
        elif arg == "--response-file" and i + 1 < len(sys.argv):
            response_file_path = sys.argv[i + 1]
            i += 2
        elif arg == "--ready-file" and i + 1 < len(sys.argv):
            ready_file_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not all([command_file_path, response_file_path, ready_file_path]):
        log(f"ERROR: Missing required arguments")
        log(f"  command-file: {command_file_path}")
        log(f"  response-file: {response_file_path}")
        log(f"  ready-file: {ready_file_path}")
        sys.exit(1)

    # Convert to Path objects
    command_file = Path(command_file_path)
    response_file = Path(response_file_path)
    ready_file = Path(ready_file_path)

    log(f"Starting server with:")
    log(f"  Command file: {command_file}")
    log(f"  Response file: {response_file}")
    log(f"  Ready file: {ready_file}")

    # Run server
    run_server(command_file, response_file, ready_file)
