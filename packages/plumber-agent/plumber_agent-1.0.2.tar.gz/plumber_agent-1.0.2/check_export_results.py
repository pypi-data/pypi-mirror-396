#!/usr/bin/env python3
"""Check for exported Houdini files and diagnose export issues."""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

def check_recent_files(directory, extensions, minutes=10):
    """Find files created in the last N minutes."""
    if not os.path.exists(directory):
        print(f"[SKIP] Directory does not exist: {directory}")
        return []

    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    recent_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime > cutoff_time:
                    recent_files.append({
                        'path': filepath,
                        'modified': mtime.isoformat(),
                        'size': os.path.getsize(filepath)
                    })

    return recent_files

def check_houdini_export():
    """Check for exported Houdini files."""
    print("="*80)
    print("HOUDINI EXPORT DIAGNOSTIC")
    print("="*80)
    print()

    # Common export locations
    check_dirs = [
        os.path.expanduser("~/plumber_exports"),
        os.path.expanduser("~"),
        "C:/temp",
        "C:/Users/Public/Documents",
        os.getcwd(),
    ]

    # Check Houdini file extensions
    houdini_extensions = ['.hip', '.hipnc', '.hiplc']

    print("Checking common export locations...")
    print()

    all_recent_files = []

    for directory in check_dirs:
        print(f"Checking: {directory}")
        recent = check_recent_files(directory, houdini_extensions, minutes=15)
        if recent:
            print(f"  [OK] Found {len(recent)} recent Houdini file(s)")
            all_recent_files.extend(recent)
        else:
            print(f"  [--] No recent Houdini files")
        print()

    if all_recent_files:
        print("="*80)
        print(f"[OK] FOUND {len(all_recent_files)} RECENT HOUDINI FILE(S):")
        print("="*80)
        for file_info in all_recent_files:
            print(f"\nFile: {file_info['path']}")
            print(f"   Modified: {file_info['modified']}")
            print(f"   Size: {file_info['size']:,} bytes")
    else:
        print("="*80)
        print("[FAIL] NO RECENT HOUDINI FILES FOUND")
        print("="*80)
        print()
        print("Possible issues:")
        print("  1. Export operation didn't run")
        print("  2. Export path was incorrect")
        print("  3. Export failed silently")
        print("  4. File exported to unexpected location")
        print()
        print("Check:")
        print("  - Railway logs for [WS RESPONSE] showing export operation completed")
        print("  - Agent logs for export operation execution")
        print("  - HoudiniExportSceneNode properties for export_path")

    print()
    print("="*80)
    print("CHECKING HOUDINI SERVER LOGS")
    print("="*80)

    log_file = Path(__file__).parent / "houdini_server_filebased.log"
    if log_file.exists():
        print(f"\n[OK] Found log file: {log_file}")
        print("\nLast 50 lines:")
        print("-"*80)
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.rstrip())
    else:
        print(f"\n[FAIL] Log file not found: {log_file}")

    print()
    print("="*80)
    print("CHECKING COMMAND/RESPONSE FILES")
    print("="*80)

    temp_dir = Path.home() / "AppData" / "Local" / "Temp"
    command_files = list(temp_dir.glob("houdini_command_*.json"))
    response_files = list(temp_dir.glob("houdini_response_*.json"))

    if command_files:
        print(f"\n[OK] Found {len(command_files)} command file(s)")
        for cmd_file in sorted(command_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            mtime = datetime.fromtimestamp(cmd_file.stat().st_mtime)
            print(f"\nFile: {cmd_file.name}")
            print(f"   Modified: {mtime.isoformat()}")
            try:
                with open(cmd_file, 'r') as f:
                    data = json.load(f)
                    print(f"   Operation: {data.get('operation_type', 'unknown')}")
                    print(f"   Command ID: {data.get('command_id', 'unknown')}")
            except Exception as e:
                print(f"   Error reading: {e}")

    if response_files:
        print(f"\n[OK] Found {len(response_files)} response file(s)")
        for resp_file in sorted(response_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            mtime = datetime.fromtimestamp(resp_file.stat().st_mtime)
            print(f"\nFile: {resp_file.name}")
            print(f"   Modified: {mtime.isoformat()}")
            try:
                with open(resp_file, 'r') as f:
                    data = json.load(f)
                    print(f"   Success: {data.get('success', 'unknown')}")
                    print(f"   Result: {data.get('result', 'no result')[:200]}")
            except Exception as e:
                print(f"   Error reading: {e}")

if __name__ == "__main__":
    try:
        check_houdini_export()
    except Exception as e:
        print(f"\n[ERROR] Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
