#!/usr/bin/env python3
"""
Plumber Local DCC Agent Packaging Script
Creates distributable packages for alpha testers and users.
"""

import os
import sys
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path

# Package configuration
AGENT_VERSION = "2.0.0"
PACKAGE_NAME = f"plumber-local-dcc-agent-v{AGENT_VERSION}"
DIST_DIR = Path("dist")
PACKAGE_DIR = Path("package_temp")

# Files and directories to include in package
INCLUDE_FILES = [
    "src/",
    "config/",
    "requirements.txt",
    "requirements-simple.txt",
    "install.bat",
    "start_agent.bat",
    "check_version.bat",
    "check_version.py",
    "README.md",
    "MAYA_SCENE_EXPORT_SOLUTION.md",
    "MAYA_WORKFLOW_ANALYSIS.md"
]

# Files to exclude (testing, development, etc.)
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "venv/",
    "test_*.py",
    "verify_fixes.py",
    "fix_maya_dll_issues.py",
    "maya_dll_bypass.py",
    "simple_verify.py",
    "show_maya_script.py",
    "connection_state.pkl",
    "plumber_agent.log",
    ".git",
    ".gitignore"
]

def should_exclude(filepath):
    """Check if a file should be excluded from the package."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(filepath):
            return True
    return False

def create_package_info():
    """Create package information file."""
    package_info = {
        "name": "Plumber Local DCC Agent",
        "version": AGENT_VERSION,
        "description": "Local DCC Agent for hybrid cloud-local workflow execution",
        "build_date": datetime.now().isoformat(),
        "supported_dccs": ["Maya", "Blender", "Houdini"],
        "requirements": {
            "python": ">=3.8",
            "platforms": ["Windows", "macOS", "Linux"]
        },
        "installation": {
            "windows": "Run install.bat as Administrator",
            "macos": "Run: chmod +x install.sh && ./install.sh",
            "linux": "Run: chmod +x install.sh && ./install.sh"
        },
        "startup": {
            "windows": "Run start_agent.bat",
            "macos": "Run: ./start_agent.sh",
            "linux": "Run: ./start_agent.sh"
        }
    }
    return package_info

def create_unix_scripts():
    """Create Unix-compatible scripts (macOS/Linux)."""

    # install.sh
    install_script = """#!/bin/bash
# Plumber Local DCC Agent Installer (Unix)

echo "=============================================="
echo "🚀 Plumber Local DCC Agent Installer"
echo "=============================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python found:"
python3 --version
echo

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run DCC discovery
echo "🔍 Running DCC discovery..."
python src/main.py --discover-only

echo
echo "=============================================="
echo "✅ Installation completed successfully!"
echo "=============================================="
echo
echo "To start the agent:"
echo "  1. Run: ./start_agent.sh"
echo "  2. Or manually: source venv/bin/activate && python src/main.py"
echo
echo "The agent will run on: http://127.0.0.1:8001"
echo "WebSocket endpoint: ws://127.0.0.1:8001/ws"
echo
"""

    # start_agent.sh
    start_script = """#!/bin/bash
# Start Plumber Local DCC Agent (Unix)

echo "=============================================="
echo "🚀 Starting Plumber Local DCC Agent"
echo "=============================================="
echo

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the agent
echo "🌐 Starting agent server..."
echo
echo "🔗 Agent will be available at:"
echo "   HTTP API: http://127.0.0.1:8001"
echo "   WebSocket: ws://127.0.0.1:8001/ws"
echo "   Health Check: http://127.0.0.1:8001/health"
echo
echo "🛑 Press Ctrl+C to stop the agent"
echo

python src/main.py

echo
echo "🛑 Agent stopped"
"""

    return install_script, start_script

def create_package():
    """Create the distributable package."""
    print(f"📦 Creating Plumber Local DCC Agent v{AGENT_VERSION} package...")

    # Create directories
    DIST_DIR.mkdir(exist_ok=True)
    PACKAGE_DIR.mkdir(exist_ok=True)

    try:
        # Copy included files
        print("📂 Copying files...")
        for item in INCLUDE_FILES:
            src_path = Path(item)
            if not src_path.exists():
                print(f"⚠️  Warning: {item} not found, skipping")
                continue

            dst_path = PACKAGE_DIR / item

            if src_path.is_dir():
                # Copy directory
                shutil.copytree(src_path, dst_path,
                              ignore=shutil.ignore_patterns(*[p for p in EXCLUDE_PATTERNS if '*' in p]))
            else:
                # Copy file
                if not should_exclude(src_path):
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)

        # Create package info
        print("📋 Creating package information...")
        package_info = create_package_info()
        with open(PACKAGE_DIR / "package_info.json", "w") as f:
            json.dump(package_info, f, indent=2)

        # Create Unix scripts
        print("🐧 Creating Unix scripts...")
        install_script, start_script = create_unix_scripts()

        with open(PACKAGE_DIR / "install.sh", "w") as f:
            f.write(install_script)
        os.chmod(PACKAGE_DIR / "install.sh", 0o755)

        with open(PACKAGE_DIR / "start_agent.sh", "w") as f:
            f.write(start_script)
        os.chmod(PACKAGE_DIR / "start_agent.sh", 0o755)

        # Create ZIP package
        print("🗜️  Creating ZIP package...")
        zip_path = DIST_DIR / f"{PACKAGE_NAME}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(PACKAGE_DIR):
                # Remove excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

                for file in files:
                    file_path = Path(root) / file
                    if not should_exclude(file_path):
                        arcname = str(file_path.relative_to(PACKAGE_DIR))
                        zipf.write(file_path, f"{PACKAGE_NAME}/{arcname}")

        # Create package metadata
        print("📊 Creating package metadata...")
        metadata = {
            **package_info,
            "package_file": f"{PACKAGE_NAME}.zip",
            "package_size": zip_path.stat().st_size,
            "download_url": f"https://github.com/damnvfx/plumber-editor/releases/download/v{AGENT_VERSION}/{PACKAGE_NAME}.zip",
            "checksums": {
                "md5": "TODO: Generate MD5 checksum",
                "sha256": "TODO: Generate SHA256 checksum"
            }
        }

        with open(DIST_DIR / f"{PACKAGE_NAME}-metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Cleanup
        print("🧹 Cleaning up...")
        shutil.rmtree(PACKAGE_DIR)

        print(f"✅ Package created successfully!")
        print(f"   📦 Package: {zip_path}")
        print(f"   📊 Metadata: {DIST_DIR / f'{PACKAGE_NAME}-metadata.json'}")
        print(f"   📏 Size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

        return True

    except Exception as e:
        print(f"❌ Error creating package: {e}")
        # Cleanup on error
        if PACKAGE_DIR.exists():
            shutil.rmtree(PACKAGE_DIR)
        return False

def main():
    """Main packaging function."""
    print("🚀 Plumber Local DCC Agent Packager")
    print("="*50)

    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Error: Must run from local-dcc-agent directory")
        sys.exit(1)

    success = create_package()

    if success:
        print("\n🎉 Packaging completed successfully!")
        print("\n📋 Next steps for distribution:")
        print("1. Test the package on a clean system")
        print("2. Upload to GitHub releases")
        print("3. Update frontend download URLs")
        print("4. Test alpha tester workflow end-to-end")
    else:
        print("\n❌ Packaging failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()