"""
Debug Maya Command Port Startup
Check what's happening when we try to start the command port.
"""

import subprocess
import time
import os

mayapy_path = r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"

startup_script = '''
import os
import time
import sys

# Disable problematic plugins
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

print("[STARTUP] Step 1: Importing Maya standalone...", flush=True)
sys.stdout.flush()

import maya.standalone

print("[STARTUP] Step 2: Initializing Maya standalone...", flush=True)
sys.stdout.flush()

maya.standalone.initialize(name='python')

print("[STARTUP] Step 3: Importing Maya cmds...", flush=True)
sys.stdout.flush()

import maya.cmds as cmds

print("[STARTUP] Step 4: Attempting to open command port...", flush=True)
sys.stdout.flush()

try:
    result = cmds.commandPort(name=":7001", sourceType="python")
    print(f"[STARTUP] Command port result: {result}", flush=True)
    print("[STARTUP] SUCCESS - Maya command port ready on port 7001", flush=True)
except Exception as e:
    print(f"[STARTUP] ERROR opening command port: {e}", flush=True)
    import traceback
    traceback.print_exc()

sys.stdout.flush()

print("[STARTUP] Waiting 10 seconds before exit...", flush=True)
for i in range(10):
    print(f"[STARTUP] Alive: {i+1}/10", flush=True)
    sys.stdout.flush()
    time.sleep(1)

print("[STARTUP] Exiting...", flush=True)
'''

print("Starting Maya with command port...")
print("=" * 60)

process = subprocess.Popen(
    [mayapy_path, "-c", startup_script],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,  # Line buffered
    universal_newlines=True
)

print("\nMaya stdout:")
print("-" * 60)

# Read output in real-time
import threading

def read_output(pipe, prefix):
    for line in iter(pipe.readline, ''):
        if line:
            print(f"{prefix}: {line.rstrip()}")

stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "STDOUT"))
stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "STDERR"))

stdout_thread.daemon = True
stderr_thread.daemon = True

stdout_thread.start()
stderr_thread.start()

# Wait for process with timeout
try:
    process.wait(timeout=30)
    print(f"\nProcess exited with code: {process.returncode}")
except subprocess.TimeoutExpired:
    print("\nProcess still running after 30s (this is actually good!)")
    process.terminate()
    print("Terminated process")

print("=" * 60)
