"""
Maya DCC Plugin
Provides Maya-specific functionality for the universal DCC system.
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

class MayaPlugin(BaseDCCPlugin):
    """Maya plugin implementation."""

    def __init__(self):
        super().__init__("maya")
        self.capabilities = [
            DCCCapability.RENDERING,
            DCCCapability.MODELING,
            DCCCapability.ANIMATION,
            DCCCapability.SIMULATION,
            DCCCapability.SCRIPTING,
            DCCCapability.IMPORT_EXPORT,
            DCCCapability.MATERIAL_EDITING
        ]
        self.max_sessions = 2  # Maya is resource-intensive
        self.session_timeout = 1800  # 30 minutes

    async def discover(self) -> Dict[str, Any]:
        """Discover Maya installation using enhanced multi-drive search."""
        # Import the enhanced discovery from main discovery module
        from ..dcc_discovery import get_dcc_discovery

        discovery_service = get_dcc_discovery()

        # Use the enhanced Maya discovery
        maya_info = discovery_service.discover_maya()

        # Convert to plugin format and return
        return {
            'available': maya_info['available'],
            'version': maya_info.get('version'),
            'executable': maya_info.get('executable'),
            'python_executable': maya_info.get('python_executable'),
            'installation_path': maya_info.get('installation_path'),
            'versions_found': maya_info.get('versions_found', [])
        }

    async def create_session(self, session_id: Optional[str] = None) -> DCCSession:
        """Create new Maya session."""
        if not session_id:
            session_id = self._generate_session_id()

        logger.info(f"🚀 Creating Maya session: {session_id}")

        session = DCCSession(
            session_id=session_id,
            dcc_type=self.dcc_type,
            version=self.version,
            executable_path=self.executable_path
        )

        try:
            # Create session temp directory
            session.temp_directory = self._create_temp_directory(session_id)

            # Start Maya in batch mode for better stability
            session.state = DCCSessionState.STARTING

            # For now, we'll use mayapy for script execution
            # In future versions, we can implement persistent Maya sessions
            session.state = DCCSessionState.ACTIVE
            self.sessions[session_id] = session

            logger.info(f"✅ Maya session created: {session_id}")
            return session

        except Exception as e:
            logger.error(f"❌ Failed to create Maya session {session_id}: {e}")
            session.state = DCCSessionState.ERROR
            raise

    async def execute_operation(self, session: DCCSession, operation: DCCOperation,
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute operation in Maya session."""
        self._log_operation_start(operation)

        if progress_callback:
            await progress_callback(10, f"Preparing Maya {operation.operation_type}")

        result = DCCOperationResult(operation.operation_id, False)

        try:
            # Route to specific operation handler
            if operation.operation_type == "render":
                result = await self._execute_render(session, operation, progress_callback)
            elif operation.operation_type == "export":
                result = await self._execute_export(session, operation, progress_callback)
            elif operation.operation_type == "import":
                result = await self._execute_import(session, operation, progress_callback)
            elif operation.operation_type == "script":
                result = await self._execute_script(session, operation, progress_callback)
            elif operation.operation_type == "scene_info":
                result = await self._execute_scene_info(session, operation, progress_callback)
            else:
                raise ValueError(f"Unsupported Maya operation: {operation.operation_type}")

            self._log_operation_complete(operation, result.success)
            return result

        except Exception as e:
            logger.error(f"❌ Maya operation {operation.operation_id} failed: {e}")
            result.error_message = str(e)
            result.success = False
            return result

    async def _execute_render(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Maya render operation."""
        params = operation.parameters
        scene_file = params.get('scene_file')
        output_path = params.get('output_path')
        start_frame = params.get('start_frame', 1)
        end_frame = params.get('end_frame', 1)
        renderer = params.get('renderer', 'mayaSoftware')

        if not scene_file or not output_path:
            raise ValueError("scene_file and output_path are required for render operation")

        if progress_callback:
            await progress_callback(30, "Preparing Maya render")

        # Generate Maya Python script for rendering
        script_content = self._generate_render_script(
            scene_file, output_path, start_frame, end_frame, renderer
        )

        # Execute script
        result = await self._execute_maya_script(session, script_content, progress_callback)

        if result.success:
            # Check for output files
            if os.path.exists(output_path):
                result.output_files.append(output_path)
            result.metadata['renderer'] = renderer
            result.metadata['frame_range'] = f"{start_frame}-{end_frame}"

        return result

    async def _execute_export(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Maya export operation."""
        params = operation.parameters
        scene_file = params.get('scene_file')
        output_path = params.get('output_path')
        export_format = params.get('format', 'obj')
        selection_only = params.get('selection_only', False)

        if not scene_file or not output_path:
            raise ValueError("scene_file and output_path are required for export operation")

        if progress_callback:
            await progress_callback(30, f"Exporting to {export_format}")

        script_content = self._generate_export_script(
            scene_file, output_path, export_format, selection_only
        )

        result = await self._execute_maya_script(session, script_content, progress_callback)

        if result.success and os.path.exists(output_path):
            result.output_files.append(output_path)
            result.metadata['export_format'] = export_format

        return result

    async def _execute_import(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Maya import operation."""
        params = operation.parameters
        input_file = params.get('input_file')
        scene_file = params.get('scene_file')
        import_namespace = params.get('namespace', '')

        if not input_file:
            raise ValueError("input_file is required for import operation")

        if progress_callback:
            await progress_callback(30, "Importing asset into Maya")

        script_content = self._generate_import_script(
            input_file, scene_file, import_namespace
        )

        result = await self._execute_maya_script(session, script_content, progress_callback)
        return result

    async def _execute_script(self, session: DCCSession, operation: DCCOperation,
                            progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute custom Maya script."""
        params = operation.parameters
        script_code = params.get('script_code')
        script_file = params.get('script_file')

        if not script_code and not script_file:
            raise ValueError("Either script_code or script_file is required")

        if progress_callback:
            await progress_callback(30, "Executing Maya script")

        if script_file and os.path.exists(script_file):
            with open(script_file, 'r') as f:
                script_code = f.read()

        result = await self._execute_maya_script(session, script_code, progress_callback)
        return result

    async def _execute_scene_info(self, session: DCCSession, operation: DCCOperation,
                                progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Get Maya scene information."""
        params = operation.parameters
        scene_file = params.get('scene_file')

        if not scene_file:
            raise ValueError("scene_file is required for scene_info operation")

        if progress_callback:
            await progress_callback(30, "Analyzing Maya scene")

        script_content = self._generate_scene_info_script(scene_file)
        result = await self._execute_maya_script(session, script_content, progress_callback)
        return result

    async def _execute_maya_script(self, session: DCCSession, script_content: str,
                                 progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute Maya Python script using mayapy."""
        script_file = os.path.join(session.temp_directory, f"maya_script_{int(time.time())}.py")

        try:
            # Write script to file
            with open(script_file, 'w') as f:
                f.write(script_content)

            if progress_callback:
                await progress_callback(50, "Executing Maya script")

            # Convert Windows paths for Maya compatibility
            script_path_maya = script_file.replace('\\', '/')

            # Execute using mayapy
            cmd = [self.python_executable, script_path_maya]

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
                result.error_message = stderr.decode('utf-8') if stderr else "Maya script execution failed"

            if progress_callback:
                await progress_callback(90, "Maya script completed")

            return result

        except Exception as e:
            logger.error(f"Maya script execution error: {e}")
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

    def _generate_render_script(self, scene_file: str, output_path: str,
                              start_frame: int, end_frame: int, renderer: str) -> str:
        """Generate Maya render script."""
        return f'''
import maya.standalone
import maya.cmds as cmds
import os

try:
    # Initialize Maya standalone
    maya.standalone.initialize()

    # Open scene
    cmds.file("{scene_file.replace("\\", "/")}", open=True, force=True)

    # Set renderer
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "{renderer}", type="string")

    # Set output path
    output_dir = os.path.dirname("{output_path.replace("\\", "/")}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Set frame range
    cmds.setAttr("defaultRenderGlobals.startFrame", {start_frame})
    cmds.setAttr("defaultRenderGlobals.endFrame", {end_frame})

    # Render
    for frame in range({start_frame}, {end_frame} + 1):
        cmds.currentTime(frame)
        result = cmds.render(camera="persp")
        print(f"Rendered frame {{frame}}: {{result}}")

    print("Render completed successfully")

except Exception as e:
    print(f"Render failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    def _generate_export_script(self, scene_file: str, output_path: str,
                              export_format: str, selection_only: bool) -> str:
        """Generate Maya export script."""
        return f'''
import maya.standalone
import maya.cmds as cmds
import os

try:
    # Initialize Maya standalone
    maya.standalone.initialize()

    # Open scene
    cmds.file("{scene_file.replace("\\", "/")}", open=True, force=True)

    # Ensure output directory exists
    output_dir = os.path.dirname("{output_path.replace("\\", "/")}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Export based on format
    if "{export_format}" == "obj":
        cmds.file("{output_path.replace("\\", "/")}", force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", typ="OBJexport", es=True)
    elif "{export_format}" == "fbx":
        cmds.loadPlugin("fbxmaya", quiet=True)
        cmds.file("{output_path.replace("\\", "/")}", force=True, options="v=0", typ="FBX export", es=True)
    elif "{export_format}" == "ma":
        cmds.file("{output_path.replace("\\", "/")}", force=True, type="mayaAscii", es=True)
    elif "{export_format}" == "mb":
        cmds.file("{output_path.replace("\\", "/")}", force=True, type="mayaBinary", es=True)
    else:
        raise ValueError(f"Unsupported export format: {export_format}")

    print("Export completed successfully")

except Exception as e:
    print(f"Export failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    def _generate_import_script(self, input_file: str, scene_file: Optional[str],
                              namespace: str) -> str:
        """Generate Maya import script."""
        scene_code = ""
        if scene_file:
            scene_code = f'cmds.file("{scene_file.replace("\\", "/")}", open=True, force=True)'
        else:
            scene_code = 'cmds.file(new=True, force=True)'

        return f'''
import maya.standalone
import maya.cmds as cmds

try:
    # Initialize Maya standalone
    maya.standalone.initialize()

    # Open or create scene
    {scene_code}

    # Import file
    namespace_option = ":{namespace}" if "{namespace}" else ""
    cmds.file("{input_file.replace("\\", "/")}", i=True, namespace=namespace_option)

    print("Import completed successfully")

except Exception as e:
    print(f"Import failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    def _generate_scene_info_script(self, scene_file: str) -> str:
        """Generate Maya scene info script."""
        return f'''
import maya.standalone
import maya.cmds as cmds
import json

try:
    # Initialize Maya standalone
    maya.standalone.initialize()

    # Open scene
    cmds.file("{scene_file.replace("\\", "/")}", open=True, force=True)

    # Gather scene information
    scene_info = {{
        "scene_file": "{scene_file}",
        "frame_range": [cmds.playbackOptions(query=True, min=True), cmds.playbackOptions(query=True, max=True)],
        "current_frame": cmds.currentTime(query=True),
        "render_resolution": [cmds.getAttr("defaultResolution.width"), cmds.getAttr("defaultResolution.height")],
        "renderer": cmds.getAttr("defaultRenderGlobals.currentRenderer"),
        "object_count": len(cmds.ls(dag=True, shapes=True)),
        "camera_count": len(cmds.ls(type="camera")),
        "light_count": len(cmds.ls(type="light")),
        "material_count": len(cmds.ls(materials=True))
    }}

    print("Scene Info:", json.dumps(scene_info, indent=2))

except Exception as e:
    print(f"Scene info failed: {{e}}")
    import traceback
    traceback.print_exc()
'''

    async def close_session(self, session: DCCSession) -> bool:
        """Close Maya session."""
        logger.info(f"🛑 Closing Maya session: {session.session_id}")

        try:
            session.state = DCCSessionState.STOPPING

            # Terminate process if running
            if session.process and session.process.poll() is None:
                session.process.terminate()
                try:
                    session.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    session.process.kill()

            # Clean up temp directory
            if session.temp_directory:
                self._cleanup_temp_directory(session.temp_directory)

            session.state = DCCSessionState.INACTIVE
            return True

        except Exception as e:
            logger.error(f"❌ Failed to close Maya session {session.session_id}: {e}")
            session.state = DCCSessionState.ERROR
            return False

    def get_supported_operations(self) -> List[str]:
        """Get list of supported Maya operations."""
        return [
            "render",
            "export",
            "import",
            "script",
            "scene_info"
        ]

    def validate_operation(self, operation: DCCOperation) -> bool:
        """Validate Maya operation."""
        if operation.operation_type not in self.get_supported_operations():
            return False

        # Validate required parameters based on operation type
        params = operation.parameters

        if operation.operation_type == "render":
            return 'scene_file' in params and 'output_path' in params

        elif operation.operation_type in ["export", "scene_info"]:
            return 'scene_file' in params

        elif operation.operation_type == "import":
            return 'input_file' in params

        elif operation.operation_type == "script":
            return 'script_code' in params or 'script_file' in params

        return True