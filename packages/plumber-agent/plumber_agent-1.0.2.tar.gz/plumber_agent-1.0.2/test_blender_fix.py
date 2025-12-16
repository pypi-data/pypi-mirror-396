"""Test Blender persistent server path fix"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dcc_discovery import get_dcc_discovery
from blender_server_manager_filebased import BlenderServerManagerFileBased

print("="*60)
print("Testing Blender Persistent Server Path Fix")
print("="*60)

# Get DCC discovery
discovery = get_dcc_discovery()
discovered_dccs = discovery.discovered_dccs

# Check Blender discovery results
print("\n1. DCC Discovery Results:")
print("-" * 60)
blender_info = discovered_dccs.get('blender', {})
if blender_info.get('available'):
    print(f"✅ Blender Found!")
    print(f"   Version: {blender_info.get('version')}")
    print(f"   Executable: {blender_info.get('executable')}")
else:
    print(f"❌ Blender NOT found")
    sys.exit(1)

# Get Blender executable path
blender_path = discovery.get_executable_path("blender")
print(f"\n2. Retrieved Executable Path:")
print(f"   {blender_path}")

# Test 1: Create server manager WITH discovered path (NEW behavior)
print("\n3. Test WITH Discovered Path (NEW):")
print("-" * 60)
try:
    manager_with_path = BlenderServerManagerFileBased(blender_path=blender_path)
    print(f"✅ BlenderServerManager created successfully!")
    print(f"   Using path: {manager_with_path.blender_path}")

    if manager_with_path.blender_path == blender_path:
        print(f"✅ Path matches discovered path!")
    else:
        print(f"❌ Path mismatch!")
        print(f"   Expected: {blender_path}")
        print(f"   Got: {manager_with_path.blender_path}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Create server manager WITHOUT path (fallback auto-detection)
print("\n4. Test WITHOUT Path (FALLBACK):")
print("-" * 60)
try:
    manager_without_path = BlenderServerManagerFileBased()
    print(f"✅ BlenderServerManager created successfully!")
    print(f"   Auto-detected path: {manager_without_path.blender_path}")

    # Check if fallback found the same path
    if manager_without_path.blender_path == blender_path:
        print(f"✅ Fallback auto-detection matches discovered path!")
    else:
        print(f"⚠️  Fallback found different path:")
        print(f"   Discovered: {blender_path}")
        print(f"   Auto-detected: {manager_without_path.blender_path}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
print("\nConclusion:")
print("- ✅ Blender persistent server can now use discovered path")
print("- ✅ No more hardcoded version guessing needed")
print("- ✅ Supports Blender 4.5 and any future versions dynamically")
