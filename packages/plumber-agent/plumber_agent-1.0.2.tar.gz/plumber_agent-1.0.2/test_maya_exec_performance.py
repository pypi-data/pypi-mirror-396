"""
Test what's causing the 500ms delay in Maya command execution.
Is it exec()? Is it Maya cmds? Is it something else?
"""

import os
import time

# Disable problematic plugins
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

print("Initializing Maya...")
start = time.time()
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
init_time = time.time() - start
print(f"Maya initialized in {init_time:.2f}s")

print("\n" + "="*60)
print("Testing Maya Command Performance")
print("="*60)

# Test 1: Direct Maya command
print("\nTest 1: Direct Maya commands (no exec)")
times = []
for i in range(5):
    start = time.time()
    cmds.polySphere(name=f'direct_sphere_{i}')
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"   Sphere {i+1}: {elapsed*1000:.2f}ms")
print(f"   Average: {sum(times)/len(times)*1000:.2f}ms")

# Test 2: exec() with Maya commands
print("\nTest 2: exec() with Maya commands")
exec_times = []
for i in range(5):
    command = f"cmds.polySphere(name='exec_sphere_{i}')"
    exec_globals = {'cmds': cmds}
    start = time.time()
    exec(command, exec_globals)
    elapsed = time.time() - start
    exec_times.append(elapsed)
    print(f"   Sphere {i+1}: {elapsed*1000:.2f}ms")
print(f"   Average: {sum(exec_times)/len(exec_times)*1000:.2f}ms")

# Test 3: Simple Python exec (no Maya)
print("\nTest 3: Pure Python exec (no Maya commands)")
pure_exec_times = []
for i in range(5):
    command = f"result = 2 + 2 * {i}"
    exec_globals = {}
    start = time.time()
    exec(command, exec_globals)
    elapsed = time.time() - start
    pure_exec_times.append(elapsed)
    print(f"   Calculation {i+1}: {elapsed*1000:.6f}ms")
print(f"   Average: {sum(pure_exec_times)/len(pure_exec_times)*1000:.6f}ms")

print("\n" + "="*60)
print("ANALYSIS")
print("="*60)
print(f"Direct Maya command:  {sum(times)/len(times)*1000:.2f}ms")
print(f"exec() with Maya:     {sum(exec_times)/len(exec_times)*1000:.2f}ms")
print(f"Pure Python exec():   {sum(pure_exec_times)/len(pure_exec_times)*1000:.6f}ms")
print()

if sum(times)/len(times) > 0.1:  # More than 100ms
    print("CONCLUSION: Maya commands themselves are slow (~100-500ms each)")
    print("This is normal for Maya geometry creation operations.")
    print("HTTP server approach is working optimally!")
else:
    print("CONCLUSION: Maya commands are fast, something else is the bottleneck")

maya.standalone.uninitialize()
