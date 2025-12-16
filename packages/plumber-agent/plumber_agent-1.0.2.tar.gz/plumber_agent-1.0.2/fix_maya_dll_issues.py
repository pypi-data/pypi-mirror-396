#!/usr/bin/env python3
"""
Maya DLL Import Fix - Diagnostic and Repair Tool
Fixes Maya 2026 standalone initialization issues in Windows environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def diagnose_maya_environment():
    """Comprehensive Maya environment diagnosis."""
    print("🔍 Maya Environment Diagnosis")
    print("=" * 50)

    # Check Maya installation
    maya_paths = [
        r"C:\Program Files\Autodesk\Maya2026\bin\maya.exe",
        r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"
    ]

    for path in maya_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Missing: {path}")

    # Check environment variables
    maya_vars = [
        'MAYA_LOCATION',
        'PYTHONPATH',
        'PATH'
    ]

    print("\n🌍 Environment Variables:")
    for var in maya_vars:
        value = os.environ.get(var, "Not set")
        if len(value) > 100:
            value = value[:100] + "..."
        print(f"  {var}: {value}")

    # Check Python path for Maya modules
    print("\n🐍 Python Module Check:")
    try:
        # Add Maya Python path
        maya_python_path = r"C:\Program Files\Autodesk\Maya2026\Python\Lib\site-packages"
        if os.path.exists(maya_python_path):
            sys.path.insert(0, maya_python_path)
            print(f"✅ Added Maya Python path: {maya_python_path}")

        # Try importing Maya modules
        import maya.standalone
        print("✅ maya.standalone imported successfully")
    except ImportError as e:
        print(f"❌ maya.standalone import failed: {e}")

    # Check DLL dependencies
    print("\n🔧 DLL Dependency Check:")
    maya_bin = r"C:\Program Files\Autodesk\Maya2026\bin"
    if os.path.exists(maya_bin):
        dlls = [f for f in os.listdir(maya_bin) if f.endswith('.dll')]
        print(f"✅ Found {len(dlls)} DLL files in Maya bin directory")

        # Check critical DLLs
        critical_dlls = ['Foundation.dll', 'OpenMaya.dll', 'OpenMayaAnim.dll']
        for dll in critical_dlls:
            dll_path = os.path.join(maya_bin, dll)
            if os.path.exists(dll_path):
                print(f"  ✅ {dll}")
            else:
                print(f"  ❌ {dll} (MISSING)")

def create_maya_environment_setup():
    """Create comprehensive Maya environment setup script."""
    setup_script = '''
import os
import sys
import platform

def setup_maya_environment():
    """Setup complete Maya environment for standalone execution."""

    # Maya 2026 installation paths
    maya_location = r"C:\\Program Files\\Autodesk\\Maya2026"
    maya_bin = os.path.join(maya_location, "bin")
    maya_python = os.path.join(maya_location, "Python")

    # Critical environment variables for Maya 2026
    maya_env = {
        "MAYA_LOCATION": maya_location,
        "MAYA_APP_DIR": os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "maya"),
        "MAYA_DISABLE_CIP": "1",
        "MAYA_DISABLE_CLIC_IPM": "1",
        "MAYA_DISABLE_ADLMPIT_POPUP": "1",
        "MAYA_DISABLE_ADP": "1",
        "MAYA_CM_DISABLE_ERROR_POPUPS": "1",

        # Qt WebEngine fixes for Maya 2026
        "QT_QPA_PLATFORM_PLUGIN_PATH": "",
        "QT_WEBENGINE_DISABLE_SANDBOX": "1",
        "QTWEBENGINE_DISABLE_SANDBOX": "1",
        "QT_LOGGING_RULES": "qt.webenginecontext.debug=false",
        "QT_WEBENGINE_CHROMIUM_FLAGS": "--disable-web-security --disable-features=VizDisplayCompositor",
        "QTWEBENGINE_CHROMIUM_FLAGS": "--disable-web-security --disable-gpu",

        # DLL loading fixes
        "MAYA_NO_CONSOLE_WINDOW": "1",
        "MAYA_DEBUG_NO_DIALOGS": "1"
    }

    # Apply environment variables
    for key, value in maya_env.items():
        os.environ[key] = value

    # Update PATH to include Maya bin directory
    current_path = os.environ.get("PATH", "")
    if maya_bin not in current_path:
        os.environ["PATH"] = maya_bin + os.pathsep + current_path

    # Update PYTHONPATH for Maya Python modules
    maya_python_paths = [
        os.path.join(maya_python, "Lib", "site-packages"),
        os.path.join(maya_location, "devkit", "other", "python", "2.7", "lib"),
        maya_bin
    ]

    current_pythonpath = os.environ.get("PYTHONPATH", "")
    for path in maya_python_paths:
        if os.path.exists(path) and path not in current_pythonpath:
            if current_pythonpath:
                current_pythonpath += os.pathsep + path
            else:
                current_pythonpath = path

            # Also add to sys.path for immediate use
            if path not in sys.path:
                sys.path.insert(0, path)

    os.environ["PYTHONPATH"] = current_pythonpath

    print("🔧 Maya environment setup completed")
    return True

def safe_maya_import():
    """Safely import Maya standalone with comprehensive error handling."""
    try:
        # Setup environment first
        setup_maya_environment()

        # Import Maya modules
        import maya.standalone

        # Initialize Maya standalone
        maya.standalone.initialize(name='python')

        # Import Maya commands
        import maya.cmds as cmds

        print("✅ Maya standalone initialized successfully")
        return True, cmds

    except ImportError as e:
        print(f"❌ Maya import failed: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Maya initialization failed: {e}")
        return False, None

if __name__ == "__main__":
    setup_maya_environment()
'''

    return setup_script

def create_websocket_timeout_fix():
    """Create WebSocket timeout fix for long operations."""
    timeout_fix = '''
"""
WebSocket Timeout Fix for Long DCC Operations
Implements heartbeat and extended timeout handling
"""

import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ExtendedWebSocketManager:
    """Enhanced WebSocket manager for long-running DCC operations."""

    def __init__(self, websocket, operation_id: str):
        self.websocket = websocket
        self.operation_id = operation_id
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.is_active = True

    async def start_heartbeat(self, interval: int = 30):
        """Start heartbeat messages during long operations."""
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval))

    async def _heartbeat_loop(self, interval: int):
        """Send periodic heartbeat messages."""
        while self.is_active:
            try:
                await asyncio.sleep(interval)
                if self.is_active:
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "operation_id": self.operation_id,
                        "timestamp": time.time()
                    }
                    await self.send_message(heartbeat_msg)
                    logger.debug(f"💓 Sent heartbeat for operation {self.operation_id}")
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                break

    async def send_progress(self, progress: float, message: str):
        """Send progress update with heartbeat."""
        try:
            progress_msg = {
                "type": "progress",
                "operation_id": self.operation_id,
                "progress": progress,
                "message": message,
                "timestamp": time.time()
            }
            await self.send_message(progress_msg)
        except Exception as e:
            logger.warning(f"Failed to send progress: {e}")

    async def send_message(self, message: dict):
        """Send message with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await self.websocket.send(json.dumps(message))
                return
            except Exception as e:
                logger.warning(f"Send attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    raise

    def stop_heartbeat(self):
        """Stop heartbeat and cleanup."""
        self.is_active = False
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()

async def execute_with_heartbeat(websocket, operation_id: str, operation_func, *args, **kwargs):
    """Execute long operation with WebSocket heartbeat."""
    manager = ExtendedWebSocketManager(websocket, operation_id)

    try:
        # Start heartbeat
        await manager.start_heartbeat(interval=20)  # Every 20 seconds

        # Execute operation
        result = await operation_func(*args, **kwargs)

        return result

    finally:
        # Stop heartbeat
        manager.stop_heartbeat()
'''

    return timeout_fix

def main():
    """Main fix application."""
    print("🔧 Maya DLL and WebSocket Fix Tool")
    print("=" * 50)

    # Run diagnosis
    diagnose_maya_environment()

    # Create fix files
    print("\n📝 Creating Fix Files:")

    # Maya environment setup
    maya_setup = create_maya_environment_setup()
    with open("maya_environment_fix.py", "w") as f:
        f.write(maya_setup)
    print("✅ Created: maya_environment_fix.py")

    # WebSocket timeout fix
    websocket_fix = create_websocket_timeout_fix()
    with open("websocket_timeout_fix.py", "w") as f:
        f.write(websocket_fix)
    print("✅ Created: websocket_timeout_fix.py")

    print("\n🎯 Next Steps:")
    print("1. Run: python maya_environment_fix.py (test Maya setup)")
    print("2. Apply websocket_timeout_fix.py to connection_manager.py")
    print("3. Test Maya execution with new environment setup")

if __name__ == "__main__":
    main()