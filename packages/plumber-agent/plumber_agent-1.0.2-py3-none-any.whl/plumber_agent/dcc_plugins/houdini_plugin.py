"""
Houdini DCC Plugin
Provides Houdini-specific functionality for the universal DCC system.
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

class HoudiniPlugin(BaseDCCPlugin):
    """Houdini plugin implementation."""

    def __init__(self):
        super().__init__("houdini")
        self.capabilities = [
            DCCCapability.RENDERING,
            DCCCapability.MODELING,
            DCCCapability.ANIMATION,
            DCCCapability.SIMULATION,
            DCCCapability.SCRIPTING,
            DCCCapability.IMPORT_EXPORT
        ]
        self.max_sessions = 2  # Houdini is very resource-intensive
        self.session_timeout = 2400  # 40 minutes

    async def discover(self) -> Dict[str, Any]:
        """Discover Houdini installation using enhanced multi-drive search."""
        # Import the enhanced discovery from main discovery module
        from ..dcc_discovery import get_dcc_discovery

        discovery_service = get_dcc_discovery()

        # Use the enhanced Houdini discovery
        houdini_info = discovery_service.discover_houdini()

        # Convert to plugin format and return
        return {
            'available': houdini_info['available'],
            'version': houdini_info.get('version'),
            'executable': houdini_info.get('executable'),
            'python_executable': houdini_info.get('python_executable'),
            'installation_path': houdini_info.get('installation_path'),
            'license_type': houdini_info.get('license_type'),
            'versions_found': houdini_info.get('versions_found', [])
        }

    async def create_session(self, session_id: Optional[str] = None) -> DCCSession:
        """Create new Houdini session."""
        if not session_id:
            session_id = self._generate_session_id()

        logger.info(f"🚀 Creating Houdini session: {session_id}")

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

            logger.info(f"✅ Houdini session created: {session_id}")
            return session

        except Exception as e:
            logger.error(f"❌ Failed to create Houdini session {session_id}: {e}")
            session.state = DCCSessionState.ERROR
            raise

    async def execute_operation(self, session: DCCSession, operation: DCCOperation,
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute operation in Houdini session."""
        self._log_operation_start(operation)

        if progress_callback:
            await progress_callback(10, f"Preparing Houdini {operation.operation_type}")

        result = DCCOperationResult(operation.operation_id, False)

        try:
            # Route to specific operation handler
            if operation.operation_type == "render":
                result = await self._execute_render(session, operation, progress_callback)
            elif operation.operation_type == "script":
                result = await self._execute_script(session, operation, progress_callback)
            elif operation.operation_type == "sim":
                result = await self._execute_simulation(session, operation, progress_callback)
            else:
                raise ValueError(f"Unsupported Houdini operation: {operation.operation_type}")

            self._log_operation_complete(operation, result.success)
            return result

        except Exception as e:
            logger.error(f"❌ Houdini operation {operation.operation_id} failed: {e}")
            result.error_message = str(e)
            result.success = False
            return result

    async def _execute_render(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Houdini render operation."""
        params = operation.parameters
        hip_file = params.get('hip_file')
        output_path = params.get('output_path')
        rop_node = params.get('rop_node', '/out/mantra1')
        start_frame = params.get('start_frame', 1)
        end_frame = params.get('end_frame', 1)

        if not hip_file or not output_path:
            raise ValueError("hip_file and output_path are required for render operation")

        if progress_callback:
            await progress_callback(30, "Rendering with Houdini")

        # Generate Houdini Python script for rendering
        script_content = self._generate_render_script(
            hip_file, output_path, rop_node, start_frame, end_frame
        )

        result = await self._execute_hython_script(session, script_content, progress_callback)

        if result.success:
            result.metadata['rop_node'] = rop_node
            result.metadata['frame_range'] = f"{start_frame}-{end_frame}"

        return result

    async def _execute_script(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Houdini Python script."""
        params = operation.parameters
        script_code = params.get('script_code')
        script_file = params.get('script_file')

        if not script_code and not script_file:
            raise ValueError("Either script_code or script_file is required")

        if progress_callback:
            await progress_callback(30, "Executing Houdini script")

        if script_file and os.path.exists(script_file):
            with open(script_file, 'r') as f:
                script_code = f.read()

        result = await self._execute_hython_script(session, script_code, progress_callback)
        return result

    async def _execute_simulation(self, session: DCCSession, operation: DCCOperation,
                                progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Houdini simulation."""
        params = operation.parameters
        hip_file = params.get('hip_file')
        sim_node = params.get('sim_node', '/obj/dopnet1')
        start_frame = params.get('start_frame', 1)
        end_frame = params.get('end_frame', 240)

        if not hip_file:
            raise ValueError("hip_file is required for simulation operation")

        if progress_callback:
            await progress_callback(30, "Running Houdini simulation")

        script_content = self._generate_simulation_script(
            hip_file, sim_node, start_frame, end_frame
        )

        result = await self._execute_hython_script(session, script_content, progress_callback)

        if result.success:
            result.metadata['sim_node'] = sim_node
            result.metadata['frame_range'] = f"{start_frame}-{end_frame}"

        return result

    async def _execute_hython_script(self, session: DCCSession, script_content: str,
                                   progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Houdini Python script using hython."""
        script_file = os.path.join(session.temp_directory, f"houdini_script_{int(time.time())}.py")

        try:
            # Write script to file
            with open(script_file, 'w') as f:
                f.write(script_content)

            if progress_callback:
                await progress_callback(50, "Executing Houdini script")

            # Execute using hython
            cmd = [self.python_executable, script_file]

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
                result.error_message = stderr.decode('utf-8') if stderr else "Houdini script execution failed"

            if progress_callback:
                await progress_callback(90, "Houdini script completed")

            return result

        except Exception as e:
            logger.error(f"Houdini script execution error: {e}")
            result = DCCOperationResult(session.session_id, False)
            result.error_message = str(e)
            return result

        finally:
            # Clean up script file
            if os.path.exists(script_file):
                try:
                    os.remove(script_file)
                except:
                    pass

    def _generate_render_script(self, hip_file: str, output_path: str, rop_node: str,
                              start_frame: int, end_frame: int) -> str:
        """Generate Houdini render script."""
        return f'''
import hou
import os

try:
    # Load the HIP file
    hou.hipFile.load("{hip_file.replace("\\", "/")}")

    # Get the ROP node
    rop = hou.node("{rop_node}")
    if not rop:
        raise Exception(f"ROP node not found: {rop_node}")

    # Set output path
    output_dir = os.path.dirname("{output_path.replace("\\", "/")}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    rop.parm("vm_picture").set("{output_path.replace("\\", "/")}")

    # Set frame range
    rop.parm("f1").set({start_frame})
    rop.parm("f2").set({end_frame})
    rop.parm("f3").set(1)  # Frame increment

    # Render
    rop.render()

    print("Render completed successfully")

except Exception as e:
    print(f"Render failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    def _generate_simulation_script(self, hip_file: str, sim_node: str,
                                  start_frame: int, end_frame: int) -> str:
        """Generate Houdini simulation script."""
        return f'''
import hou

try:
    # Load the HIP file
    hou.hipFile.load("{hip_file.replace("\\", "/")}")

    # Get the simulation node
    sim = hou.node("{sim_node}")
    if not sim:
        raise Exception(f"Simulation node not found: {sim_node}")

    # Set frame range
    hou.setFrame({start_frame})
    hou.playbar.setFrameRange({start_frame}, {end_frame})

    # Run simulation
    for frame in range({start_frame}, {end_frame} + 1):
        hou.setFrame(frame)
        sim.cook()
        print(f"Simulated frame {{frame}}")

    print("Simulation completed successfully")

except Exception as e:
    print(f"Simulation failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    async def close_session(self, session: DCCSession) -> bool:
        """Close Houdini session."""
        logger.info(f"🛑 Closing Houdini session: {session.session_id}")

        try:
            session.state = DCCSessionState.STOPPING

            # Clean up temp directory
            if session.temp_directory:
                self._cleanup_temp_directory(session.temp_directory)

            session.state = DCCSessionState.INACTIVE
            return True

        except Exception as e:
            logger.error(f"❌ Failed to close Houdini session {session.session_id}: {e}")
            session.state = DCCSessionState.ERROR
            return False

    def get_supported_operations(self) -> List[str]:
        """Get list of supported Houdini operations."""
        return [
            "render",
            "script",
            "sim"
        ]

    def validate_operation(self, operation: DCCOperation) -> bool:
        """Validate Houdini operation."""
        if operation.operation_type not in self.get_supported_operations():
            return False

        params = operation.parameters

        if operation.operation_type == "render":
            return 'hip_file' in params and 'output_path' in params

        elif operation.operation_type == "sim":
            return 'hip_file' in params

        elif operation.operation_type == "script":
            return 'script_code' in params or 'script_file' in params

        return True