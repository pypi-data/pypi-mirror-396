"""
Blender DCC Plugin
Provides Blender-specific functionality for the universal DCC system.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from .base_plugin import BaseDCCPlugin, DCCOperation, DCCOperationResult, DCCSession, DCCSessionState, DCCCapability

logger = logging.getLogger(__name__)

class BlenderPlugin(BaseDCCPlugin):
    """Blender plugin implementation."""

    def __init__(self):
        super().__init__("blender")
        self.capabilities = [
            DCCCapability.RENDERING,
            DCCCapability.MODELING,
            DCCCapability.ANIMATION,
            DCCCapability.SIMULATION,
            DCCCapability.SCRIPTING,
            DCCCapability.IMPORT_EXPORT,
            DCCCapability.MATERIAL_EDITING
        ]
        self.max_sessions = 4  # Blender is lighter than Maya
        self.session_timeout = 1200  # 20 minutes

    async def discover(self) -> Dict[str, Any]:
        """Discover Blender installation using enhanced multi-drive search."""
        # Import the enhanced discovery from main discovery module
        from ..dcc_discovery import get_dcc_discovery

        discovery_service = get_dcc_discovery()

        # Use the enhanced Blender discovery
        blender_info = discovery_service.discover_blender()

        # Convert to plugin format and return
        return {
            'available': blender_info['available'],
            'version': blender_info.get('version'),
            'executable': blender_info.get('executable'),
            'python_executable': blender_info.get('executable'),  # Blender has built-in Python
            'installation_path': blender_info.get('installation_path'),
            'versions_found': blender_info.get('versions_found', [])
        }

    async def create_session(self, session_id: Optional[str] = None) -> DCCSession:
        """Create new Blender session."""
        if not session_id:
            session_id = self._generate_session_id()

        logger.info(f"🚀 Creating Blender session: {session_id}")

        session = DCCSession(
            session_id=session_id,
            dcc_type=self.dcc_type,
            version=self.version,
            executable_path=self.executable_path
        )

        try:
            # Create session temp directory
            session.temp_directory = self._create_temp_directory(session_id)
            session.state = DCCSessionState.ACTIVE
            self.sessions[session_id] = session

            logger.info(f"✅ Blender session created: {session_id}")
            return session

        except Exception as e:
            logger.error(f"❌ Failed to create Blender session {session_id}: {e}")
            session.state = DCCSessionState.ERROR
            raise

    async def execute_operation(self, session: DCCSession, operation: DCCOperation,
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute operation in Blender session."""
        self._log_operation_start(operation)

        if progress_callback:
            await progress_callback(10, f"Preparing Blender {operation.operation_type}")

        result = DCCOperationResult(operation.operation_id, False)

        try:
            # Route to specific operation handler
            if operation.operation_type == "render":
                result = await self._execute_render(session, operation, progress_callback)
            elif operation.operation_type == "script":
                result = await self._execute_script(session, operation, progress_callback)
            else:
                raise ValueError(f"Unsupported Blender operation: {operation.operation_type}")

            self._log_operation_complete(operation, result.success)
            return result

        except Exception as e:
            logger.error(f"❌ Blender operation {operation.operation_id} failed: {e}")
            result.error_message = str(e)
            result.success = False
            return result

    async def _execute_render(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Blender render operation."""
        params = operation.parameters
        blend_file = params.get('blend_file')
        output_path = params.get('output_path')
        start_frame = params.get('start_frame', 1)
        end_frame = params.get('end_frame', 1)
        engine = params.get('engine', 'CYCLES')

        if not blend_file or not output_path:
            raise ValueError("blend_file and output_path are required for render operation")

        if progress_callback:
            await progress_callback(30, f"Rendering with {engine}")

        # Build Blender command
        cmd = [
            self.executable_path,
            '--background',
            blend_file,
            '--render-output', output_path,
            '--engine', engine,
            '--frame-start', str(start_frame),
            '--frame-end', str(end_frame),
            '--render-anim' if start_frame != end_frame else '--render-frame', str(start_frame)
        ]

        result = await self._execute_blender_command(session, cmd, progress_callback)

        if result.success and os.path.exists(output_path):
            result.output_files.append(output_path)
            result.metadata['engine'] = engine
            result.metadata['frame_range'] = f"{start_frame}-{end_frame}"

        return result

    async def _execute_script(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Blender Python script."""
        params = operation.parameters
        script_code = params.get('script_code')
        script_file = params.get('script_file')
        blend_file = params.get('blend_file')

        if not script_code and not script_file:
            raise ValueError("Either script_code or script_file is required")

        if progress_callback:
            await progress_callback(30, "Executing Blender script")

        # Create temp script file if code provided
        temp_script = None
        if script_code:
            temp_script = os.path.join(session.temp_directory, f"blender_script_{int(time.time())}.py")
            with open(temp_script, 'w') as f:
                f.write(script_code)
            script_to_run = temp_script
        else:
            script_to_run = script_file

        # Build Blender command
        cmd = [self.executable_path, '--background']

        if blend_file:
            cmd.append(blend_file)

        cmd.extend(['--python', script_to_run])

        try:
            result = await self._execute_blender_command(session, cmd, progress_callback)
            return result
        finally:
            # Clean up temp script
            if temp_script and os.path.exists(temp_script):
                try:
                    os.remove(temp_script)
                except:
                    pass

    async def _execute_blender_command(self, session: DCCSession, cmd: List[str],
                                     progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Blender command."""
        try:
            if progress_callback:
                await progress_callback(50, "Executing Blender command")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.temp_directory
            )

            stdout, stderr = await process.communicate()

            result = DCCOperationResult(session.session_id, process.returncode == 0)

            if stdout:
                result.logs.append(stdout.decode('utf-8'))
            if stderr:
                result.logs.append(stderr.decode('utf-8'))

            if process.returncode != 0:
                result.error_message = stderr.decode('utf-8') if stderr else "Blender command execution failed"

            if progress_callback:
                await progress_callback(90, "Blender command completed")

            return result

        except Exception as e:
            logger.error(f"Blender command execution error: {e}")
            result = DCCOperationResult(session.session_id, False)
            result.error_message = str(e)
            return result

    async def close_session(self, session: DCCSession) -> bool:
        """Close Blender session."""
        logger.info(f"🛑 Closing Blender session: {session.session_id}")

        try:
            session.state = DCCSessionState.STOPPING

            # Clean up temp directory
            if session.temp_directory:
                self._cleanup_temp_directory(session.temp_directory)

            session.state = DCCSessionState.INACTIVE
            return True

        except Exception as e:
            logger.error(f"❌ Failed to close Blender session {session.session_id}: {e}")
            session.state = DCCSessionState.ERROR
            return False

    def get_supported_operations(self) -> List[str]:
        """Get list of supported Blender operations."""
        return [
            "render",
            "script"
        ]

    def validate_operation(self, operation: DCCOperation) -> bool:
        """Validate Blender operation."""
        if operation.operation_type not in self.get_supported_operations():
            return False

        params = operation.parameters

        if operation.operation_type == "render":
            return 'blend_file' in params and 'output_path' in params

        elif operation.operation_type == "script":
            return 'script_code' in params or 'script_file' in params

        return True