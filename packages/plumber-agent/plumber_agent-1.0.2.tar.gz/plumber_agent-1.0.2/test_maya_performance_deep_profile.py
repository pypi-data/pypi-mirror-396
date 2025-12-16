"""
Deep Performance Profiling for Maya Session Creation
This script measures exactly where the 16+ seconds are being spent.
"""

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path

# Profiling results
profiling_data = {}

def measure_step(step_name, func):
    """Execute a function and measure its execution time."""
    start = time.time()
    result = func()
    duration = time.time() - start
    profiling_data[step_name] = duration
    print(f"⏱️  {step_name}: {duration:.3f}s")
    return result

def test_maya_python_import_speed():
    """Test 1: How long does it take to import maya.standalone?"""
    print("\n" + "="*60)
    print("TEST 1: Maya Python Import Speed")
    print("="*60)

    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

    test_script = '''
import time
import sys

start = time.time()
import maya.standalone
import_time = time.time() - start
print(f"IMPORT_TIME:{import_time:.3f}")
sys.exit(0)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name

    try:
        result = subprocess.run(
            [mayapy_path, temp_script],
            capture_output=True,
            text=True,
            timeout=60
        )

        for line in result.stdout.split('\n'):
            if line.startswith('IMPORT_TIME:'):
                import_time = float(line.split(':')[1])
                profiling_data['maya_import_time'] = import_time
                print(f"   maya.standalone import: {import_time:.3f}s")
    finally:
        os.unlink(temp_script)

def test_maya_initialize_speed():
    """Test 2: How long does maya.standalone.initialize() take?"""
    print("\n" + "="*60)
    print("TEST 2: Maya Standalone Initialize Speed")
    print("="*60)

    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

    test_script = '''
import time
import os

# Set environment variables to disable plugins
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

import maya.standalone

start = time.time()
maya.standalone.initialize(name='python')
init_time = time.time() - start

print(f"INIT_TIME:{init_time:.3f}")

# Quick cmds import
start = time.time()
import maya.cmds
cmds_time = time.time() - start
print(f"CMDS_TIME:{cmds_time:.3f}")

maya.standalone.uninitialize()
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name

    try:
        start_total = time.time()
        result = subprocess.run(
            [mayapy_path, temp_script],
            capture_output=True,
            text=True,
            timeout=120
        )
        total_time = time.time() - start_total

        print(f"   Total execution time: {total_time:.3f}s")

        for line in result.stdout.split('\n'):
            if line.startswith('INIT_TIME:'):
                init_time = float(line.split(':')[1])
                profiling_data['maya_initialize_time'] = init_time
                print(f"   maya.standalone.initialize(): {init_time:.3f}s")
            elif line.startswith('CMDS_TIME:'):
                cmds_time = float(line.split(':')[1])
                profiling_data['maya_cmds_import_time'] = cmds_time
                print(f"   maya.cmds import: {cmds_time:.3f}s")

        overhead = total_time - profiling_data.get('maya_initialize_time', 0) - profiling_data.get('maya_cmds_import_time', 0)
        print(f"   Process overhead: {overhead:.3f}s")
        profiling_data['process_overhead'] = overhead

    finally:
        os.unlink(temp_script)

def test_file_write_speed():
    """Test 3: How long does it take to write session info files?"""
    print("\n" + "="*60)
    print("TEST 3: File I/O Speed")
    print("="*60)

    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

    test_script = '''
import time
import os
import json
import tempfile

# Set environment variables to disable plugins
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

# Time file writing operations
output_dir = tempfile.mkdtemp()
session_id = "test_session"

start = time.time()

# Create session files
command_queue_file = os.path.join(output_dir, f"maya_session_{session_id}_queue.txt")
response_queue_file = os.path.join(output_dir, f"maya_session_{session_id}_response.txt")
status_file = os.path.join(output_dir, f"maya_session_{session_id}_status.txt")
session_info_file = os.path.join(output_dir, f"maya_session_{session_id}_info.txt")

open(command_queue_file, 'w').close()
open(response_queue_file, 'w').close()

with open(status_file, 'w') as f:
    f.write('listening')

session_data = {
    "session_id": session_id,
    "status": "listening",
    "command_queue": command_queue_file,
    "response_queue": response_queue_file,
    "maya_version": cmds.about(version=True)
}

with open(session_info_file, 'w') as f:
    json.dump(session_data, f, indent=2)

file_write_time = time.time() - start
print(f"FILE_WRITE_TIME:{file_write_time:.6f}")

maya.standalone.uninitialize()
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name

    try:
        result = subprocess.run(
            [mayapy_path, temp_script],
            capture_output=True,
            text=True,
            timeout=120
        )

        for line in result.stdout.split('\n'):
            if line.startswith('FILE_WRITE_TIME:'):
                file_time = float(line.split(':')[1])
                profiling_data['file_write_time'] = file_time
                print(f"   Session file creation: {file_time:.6f}s")

    finally:
        os.unlink(temp_script)

def test_minimal_session_creation():
    """Test 4: Full minimal session creation (current implementation)"""
    print("\n" + "="*60)
    print("TEST 4: Full Minimal Session Creation (Current Approach)")
    print("="*60)

    mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
    output_dir = tempfile.mkdtemp()

    # Use the exact script from dcc_executor.py (mayapy_simple mode)
    test_script = f'''
import os
import sys
import time
from datetime import datetime

def log_timestamp(message):
    """Log message with precise timestamp for profiling."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{{timestamp}}] {{message}}")

log_timestamp("PROFILING START: Script execution began")

# Simple Maya standalone initialization (no Qt/GUI)
# CRITICAL: Set environment variables BEFORE importing Maya to disable problematic plugins
import os
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""
log_timestamp("STEP 0: Environment variables set")

log_timestamp("STEP 1: About to import maya.standalone")
import maya.standalone
log_timestamp("STEP 2: maya.standalone imported")

log_timestamp("STEP 3: About to call maya.standalone.initialize()")
start_init = time.time()
maya.standalone.initialize(name='python')
init_duration = time.time() - start_init
log_timestamp(f"STEP 4: maya.standalone.initialize() completed in {{init_duration:.2f}}s")

log_timestamp("STEP 5: About to import maya.cmds")
import maya.cmds as cmds
log_timestamp("STEP 6: maya.cmds imported")

maya_version = cmds.about(version=True)
log_timestamp(f"STEP 7: Maya {{maya_version}} fully initialized")

output_dir = "{output_dir.replace(chr(92), '/')}"
log_timestamp(f"STEP 8: Starting session creation")

try:
    # Session configuration
    log_timestamp("STEP 9: Creating session configuration")
    session_id = "test_session"
    output_path = output_dir
    log_timestamp(f"STEP 10: Output path = {{output_path}}")

    os.makedirs(output_path, exist_ok=True)
    log_timestamp("STEP 11: Directory created")

    # Session communication files
    command_queue_file = os.path.join(output_path, f"maya_session_{{session_id}}_queue.txt")
    response_queue_file = os.path.join(output_path, f"maya_session_{{session_id}}_response.txt")
    status_file = os.path.join(output_path, f"maya_session_{{session_id}}_status.txt")
    session_info_file = os.path.join(output_path, f"maya_session_{{session_id}}_info.txt")
    log_timestamp("STEP 12: File paths configured")

    # Initialize communication files
    log_timestamp("STEP 13: Creating empty queue files")
    open(command_queue_file, 'w').close()
    open(response_queue_file, 'w').close()
    log_timestamp("STEP 14: Queue files created")

    # Write session status
    log_timestamp("STEP 15: Writing status file")
    with open(status_file, 'w') as f:
        f.write('listening')
    log_timestamp("STEP 16: Status file written")

    # Write session info (for client to retrieve session_id)
    log_timestamp("STEP 17: Writing session info file")
    import json
    session_data = {{
        "session_id": session_id,
        "status": "listening",
        "command_queue": command_queue_file,
        "response_queue": response_queue_file,
        "maya_version": cmds.about(version=True)
    }}
    with open(session_info_file, 'w') as f:
        json.dump(session_data, f, indent=2)
    log_timestamp("STEP 18: Session info file written - EXITING FOR TEST")

    print(f"Maya session {{session_id}} ready")

    # Exit immediately for testing (don't wait for commands)
    sys.exit(0)

except Exception as e:
    print(f"Session creation failed: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        temp_script = f.name

    try:
        print(f"   Running full session creation test...")
        start_total = time.time()

        result = subprocess.run(
            [mayapy_path, temp_script],
            capture_output=True,
            text=True,
            timeout=120
        )

        total_time = time.time() - start_total
        print(f"\n   Total session creation time: {total_time:.3f}s")
        profiling_data['full_session_creation_time'] = total_time

        print("\n   Step-by-step breakdown:")
        for line in result.stdout.split('\n'):
            if 'STEP' in line or 'PROFILING' in line:
                print(f"      {line}")

    finally:
        os.unlink(temp_script)
        # Clean up temp directory
        import shutil
        try:
            shutil.rmtree(output_dir)
        except:
            pass

def print_summary():
    """Print summary of all profiling results."""
    print("\n" + "="*60)
    print("PERFORMANCE ANALYSIS SUMMARY")
    print("="*60)

    if 'maya_import_time' in profiling_data:
        print(f"Maya Import Time:          {profiling_data['maya_import_time']:.3f}s")

    if 'maya_initialize_time' in profiling_data:
        print(f"Maya Initialize Time:      {profiling_data['maya_initialize_time']:.3f}s")

    if 'maya_cmds_import_time' in profiling_data:
        print(f"Maya cmds Import Time:     {profiling_data['maya_cmds_import_time']:.3f}s")

    if 'file_write_time' in profiling_data:
        print(f"File Write Time:           {profiling_data['file_write_time']:.6f}s")

    if 'process_overhead' in profiling_data:
        print(f"Process Overhead:          {profiling_data['process_overhead']:.3f}s")

    if 'full_session_creation_time' in profiling_data:
        print(f"\nFull Session Creation:     {profiling_data['full_session_creation_time']:.3f}s")

    print("\n" + "="*60)
    print("BOTTLENECK IDENTIFICATION")
    print("="*60)

    if profiling_data:
        max_time = max(profiling_data.items(), key=lambda x: x[1])
        print(f"Largest bottleneck: {max_time[0]} ({max_time[1]:.3f}s)")

        # Calculate where time is spent
        if 'maya_initialize_time' in profiling_data:
            init_pct = (profiling_data['maya_initialize_time'] / profiling_data.get('full_session_creation_time', 1)) * 100
            print(f"Maya initialization accounts for: {init_pct:.1f}% of total time")

if __name__ == "__main__":
    print("Maya Session Creation Performance Deep Profiling")
    print("=" * 60)
    print("This test will measure exactly where the time is spent during Maya session creation.")
    print()

    try:
        test_maya_python_import_speed()
        test_maya_initialize_speed()
        test_file_write_speed()
        test_minimal_session_creation()
        print_summary()

        print("\n✅ Performance profiling complete!")

    except Exception as e:
        print(f"\n❌ Profiling failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
