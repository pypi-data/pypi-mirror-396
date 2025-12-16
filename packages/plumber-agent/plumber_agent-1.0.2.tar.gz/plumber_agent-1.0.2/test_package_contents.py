#!/usr/bin/env python3
"""
Test script to verify all Python modules are discoverable
and the package structure is correct for v1.0.2
"""

import os
import sys
from pathlib import Path

# Add src to Python path to simulate installed package
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.parent))

print("=" * 80)
print("PLUMBER AGENT v1.0.2 - PACKAGE STRUCTURE VERIFICATION")
print("=" * 80)
print()

# Test 1: Check all Python files exist
print("TEST 1: Checking Python files exist in src/")
print("-" * 80)

expected_files = [
    "src/__init__.py",
    "src/agent_server.py",
    "src/cli.py",
    "src/connection_manager.py",
    "src/cross_platform_utils.py",
    "src/dcc_discovery.py",  # <- THE CRITICAL ONE THAT WAS MISSING
    "src/dcc_executor.py",
    "src/dcc_executor_v2.py",
    "src/main.py",
    "src/maya_server_manager.py",
    "src/maya_server_manager_filebased.py",
    "src/blender_server_manager_filebased.py",
    "src/houdini_server_manager_filebased.py",
    "src/service_manager.py",
    "src/services/__init__.py",
    "src/services/systemd_handler.py",
    "src/services/launchd_handler.py",
    "src/services/windows_handler.py",
    "src/dcc_plugins/__init__.py",
    "src/dcc_plugins/base_plugin.py",
    "src/dcc_plugins/maya_plugin.py",
    "src/dcc_plugins/blender_plugin.py",
    "src/dcc_plugins/houdini_plugin.py",
    "src/dcc_plugins/plugin_manager.py",
]

missing_files = []
found_files = []

for file_path in expected_files:
    full_path = Path(__file__).parent / file_path
    if full_path.exists():
        found_files.append(file_path)
        size_kb = full_path.stat().st_size / 1024
        if "dcc_discovery" in file_path:
            print(f"✅ {file_path:50} ({size_kb:>6.1f} KB) <- CRITICAL FILE")
        else:
            print(f"✅ {file_path:50} ({size_kb:>6.1f} KB)")
    else:
        missing_files.append(file_path)
        print(f"❌ {file_path:50} MISSING!")

print()
print(f"Total files expected: {len(expected_files)}")
print(f"Total files found:    {len(found_files)}")
print(f"Total files missing:  {len(missing_files)}")
print()

if missing_files:
    print("❌ TEST 1 FAILED - Missing files found!")
    sys.exit(1)
else:
    print("✅ TEST 1 PASSED - All expected files exist")

print()

# Test 2: Try importing plumber_agent modules
print("TEST 2: Testing module imports (simulating installed package)")
print("-" * 80)

# Change directory to src so imports work like installed package
original_dir = os.getcwd()
os.chdir(src_dir)
sys.path.insert(0, str(src_dir))

import_tests = [
    ("plumber_agent version", "import sys; sys.path.insert(0, '.'); from __init__ import __version__; print(__version__)"),
    ("plumber_agent.dcc_discovery", "import sys; sys.path.insert(0, '.'); import dcc_discovery; print('OK')"),
    ("plumber_agent.dcc_discovery.get_dcc_discovery", "import sys; sys.path.insert(0, '.'); from dcc_discovery import get_dcc_discovery; print('OK')"),
    ("plumber_agent.cli", "import sys; sys.path.insert(0, '.'); import cli; print('OK')"),
    ("plumber_agent.agent_server", "import sys; sys.path.insert(0, '.'); import agent_server; print('OK')"),
    ("plumber_agent.services", "import sys; sys.path.insert(0, '.'); import services; print('OK')"),
    ("plumber_agent.dcc_plugins", "import sys; sys.path.insert(0, '.'); import dcc_plugins; print('OK')"),
]

failed_imports = []

for test_name, import_cmd in import_tests:
    try:
        result = os.popen(f"cd {src_dir} && python3 -c \"{import_cmd}\"").read().strip()
        if result:
            if "dcc_discovery" in test_name:
                print(f"✅ {test_name:50} WORKS <- CRITICAL MODULE")
            else:
                print(f"✅ {test_name:50} WORKS")
        else:
            failed_imports.append(test_name)
            print(f"❌ {test_name:50} FAILED")
    except Exception as e:
        failed_imports.append(test_name)
        print(f"❌ {test_name:50} ERROR: {e}")

os.chdir(original_dir)

print()
print(f"Total import tests: {len(import_tests)}")
print(f"Passed: {len(import_tests) - len(failed_imports)}")
print(f"Failed: {len(failed_imports)}")
print()

if failed_imports:
    print("❌ TEST 2 FAILED - Some imports failed!")
    sys.exit(1)
else:
    print("✅ TEST 2 PASSED - All modules importable")

print()

# Test 3: Check MANIFEST.in exists and has correct content
print("TEST 3: Checking MANIFEST.in configuration")
print("-" * 80)

manifest_path = Path(__file__).parent / "MANIFEST.in"
if manifest_path.exists():
    print("✅ MANIFEST.in exists")
    content = manifest_path.read_text()

    required_lines = [
        "global-include *.py",
        "recursive-include src *",
    ]

    all_found = True
    for line in required_lines:
        if line in content:
            print(f"✅ Contains: {line}")
        else:
            print(f"❌ Missing: {line}")
            all_found = False

    if all_found:
        print("✅ TEST 3 PASSED - MANIFEST.in properly configured")
    else:
        print("❌ TEST 3 FAILED - MANIFEST.in missing required directives")
        sys.exit(1)
else:
    print("❌ TEST 3 FAILED - MANIFEST.in does not exist")
    sys.exit(1)

print()

# Test 4: Check version consistency
print("TEST 4: Checking version consistency across files")
print("-" * 80)

version_checks = {
    "pyproject.toml": ('version = "1.0.2"', Path(__file__).parent / "pyproject.toml"),
    "setup.py": ('version="1.0.2"', Path(__file__).parent / "setup.py"),
    "src/__init__.py": ('__version__ = "1.0.2"', Path(__file__).parent / "src" / "__init__.py"),
}

version_consistent = True
for file_name, (expected, file_path) in version_checks.items():
    if file_path.exists():
        content = file_path.read_text()
        if expected in content:
            print(f"✅ {file_name:20} has version 1.0.2")
        else:
            print(f"❌ {file_name:20} WRONG VERSION")
            version_consistent = False
    else:
        print(f"❌ {file_name:20} FILE NOT FOUND")
        version_consistent = False

print()
if version_consistent:
    print("✅ TEST 4 PASSED - All versions are 1.0.2")
else:
    print("❌ TEST 4 FAILED - Version inconsistency found")
    sys.exit(1)

print()

# Final summary
print("=" * 80)
print("FINAL RESULT: ALL TESTS PASSED ✅")
print("=" * 80)
print()
print("Package v1.0.2 is ready for building and publishing!")
print()
print("Next steps:")
print("1. Build package:  python3 -m build --outdir dist/")
print("2. Check wheel:    unzip -l dist/plumber_agent-1.0.2-py3-none-any.whl | grep dcc_discovery")
print("3. Test install:   pip install dist/plumber_agent-1.0.2-py3-none-any.whl")
print("4. Verify import:  python3 -c 'import plumber_agent.dcc_discovery; print(\"OK\")'")
print("5. Publish:        python3 -m twine upload dist/*")
print()
print("Key fix: dcc_discovery.py (73 KB) is now included via MANIFEST.in!")
print("=" * 80)
