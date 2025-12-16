"""
Base DCC Plugin Class
Defines the interface and common functionality for all DCC plugins.
"""

import asyncio
import logging
import os
import subprocess
import tempfile
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum

logger = logging.getLogger(__name__)

class DCCSessionState(Enum):
    """DCC session state enumeration."""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    STOPPING = "stopping"

class DCCCapability(Enum):
    """DCC capability enumeration."""
    RENDERING = "rendering"
    MODELING = "modeling"
    ANIMATION = "animation"
    SIMULATION = "simulation"
    COMPOSITING = "compositing"
    SCRIPTING = "scripting"
    IMPORT_EXPORT = "import_export"
    MATERIAL_EDITING = "material_editing"

class DCCOperation:
    """DCC operation data structure."""

    def __init__(self, operation_id: str, operation_type: str, parameters: Dict[str, Any] = None,
                 timeout: int = 300, priority: int = 1):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.parameters = parameters or {}
        self.timeout = timeout
        self.priority = priority
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.progress = 0
        self.status = "pending"
        self.result_data: Optional[Dict] = None
        self.error_message: Optional[str] = None

class DCCOperationResult:
    """DCC operation result."""

    def __init__(self, operation_id: str, success: bool, execution_time: float = 0):
        self.operation_id = operation_id
        self.success = success
        self.execution_time = execution_time
        self.output_files: List[str] = []
        self.logs: List[str] = []
        self.error_message: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

class DCCSession:
    """Represents a DCC application session."""

    def __init__(self, session_id: str, dcc_type: str, version: str, executable_path: str):
        self.session_id = session_id
        self.dcc_type = dcc_type
        self.version = version
        self.executable_path = executable_path
        self.state = DCCSessionState.INACTIVE
        self.process: Optional[subprocess.Popen] = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.active_operations: Dict[str, DCCOperation] = {}
        self.temp_directory: Optional[str] = None
        self.session_data: Dict[str, Any] = {}

class BaseDCCPlugin(ABC):
    """Abstract base class for DCC plugins."""

    def __init__(self, dcc_type: str, version: str = "unknown"):
        self.dcc_type = dcc_type
        self.version = version
        self.capabilities: List[DCCCapability] = []
        self.sessions: Dict[str, DCCSession] = {}
        self.max_sessions = 3
        self.session_timeout = 3600  # 1 hour
        self.discovery_data: Dict[str, Any] = {}
        self.is_available = False
        self.executable_path: Optional[str] = None
        self.python_executable: Optional[str] = None
        self.installation_path: Optional[str] = None

    @abstractmethod
    async def discover(self) -> Dict[str, Any]:
        """Discover DCC installation and capabilities."""
        pass

    @abstractmethod
    async def create_session(self, session_id: Optional[str] = None) -> DCCSession:
        """Create a new DCC session."""
        pass

    @abstractmethod
    async def execute_operation(self, session: DCCSession, operation: DCCOperation,
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute an operation in the DCC session."""
        pass

    @abstractmethod
    async def close_session(self, session: DCCSession) -> bool:
        """Close a DCC session."""
        pass

    @abstractmethod
    def get_supported_operations(self) -> List[str]:
        """Get list of supported operations."""
        pass

    @abstractmethod
    def validate_operation(self, operation: DCCOperation) -> bool:
        """Validate if operation is supported and properly formatted."""
        pass

    # Common implementation methods

    async def initialize(self) -> bool:
        """Initialize the DCC plugin."""
        logger.info(f"🔧 Initializing {self.dcc_type} plugin...")

        try:
            # Discover DCC installation
            self.discovery_data = await self.discover()
            self.is_available = self.discovery_data.get('available', False)

            if self.is_available:
                self.executable_path = self.discovery_data.get('executable')
                self.python_executable = self.discovery_data.get('python_executable')
                self.installation_path = self.discovery_data.get('installation_path')
                self.version = self.discovery_data.get('version', self.version)

                logger.info(f"✅ {self.dcc_type} plugin initialized: {self.version}")
                return True
            else:
                logger.warning(f"❌ {self.dcc_type} not available")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize {self.dcc_type} plugin: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[DCCSession]:
        """Get existing session by ID."""
        return self.sessions.get(session_id)

    async def get_or_create_session(self, preferred_session_id: Optional[str] = None) -> DCCSession:
        """Get existing session or create new one."""
        # Try to reuse existing session
        for session in self.sessions.values():
            if session.state == DCCSessionState.ACTIVE and len(session.active_operations) == 0:
                session.last_activity = datetime.now()
                return session

        # Create new session if under limit
        if len(self.sessions) < self.max_sessions:
            return await self.create_session(preferred_session_id)

        # Wait for session to become available
        logger.warning(f"Max sessions ({self.max_sessions}) reached for {self.dcc_type}, waiting...")
        await asyncio.sleep(1)
        return await self.get_or_create_session(preferred_session_id)

    async def cleanup_sessions(self) -> int:
        """Clean up inactive or timed-out sessions."""
        cleaned_count = 0
        current_time = datetime.now()

        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            # Check for timeout
            inactive_time = (current_time - session.last_activity).total_seconds()

            if (inactive_time > self.session_timeout or
                session.state == DCCSessionState.ERROR or
                (session.state == DCCSessionState.ACTIVE and len(session.active_operations) == 0 and inactive_time > 300)):

                logger.info(f"🧹 Cleaning up {self.dcc_type} session: {session_id}")
                await self.close_session(session)
                sessions_to_remove.append(session_id)
                cleaned_count += 1

        # Remove sessions from dictionary
        for session_id in sessions_to_remove:
            del self.sessions[session_id]

        return cleaned_count

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        active_sessions = len([s for s in self.sessions.values() if s.state == DCCSessionState.ACTIVE])
        busy_sessions = len([s for s in self.sessions.values() if s.state == DCCSessionState.BUSY])
        total_operations = sum(len(s.active_operations) for s in self.sessions.values())

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "busy_sessions": busy_sessions,
            "total_operations": total_operations,
            "max_sessions": self.max_sessions,
            "is_available": self.is_available
        }

    def get_capabilities(self) -> List[str]:
        """Get DCC capabilities as string list."""
        return [cap.value for cap in self.capabilities]

    def supports_operation(self, operation_type: str) -> bool:
        """Check if operation type is supported."""
        return operation_type in self.get_supported_operations()

    async def execute_with_timeout(self, session: DCCSession, operation: DCCOperation,
                                 progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute operation with timeout handling."""
        try:
            # Mark operation as started
            operation.started_at = datetime.now()
            operation.status = "running"
            session.active_operations[operation.operation_id] = operation
            session.state = DCCSessionState.BUSY
            session.last_activity = datetime.now()

            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute_operation(session, operation, progress_callback),
                timeout=operation.timeout
            )

            # Mark as completed
            operation.completed_at = datetime.now()
            operation.status = "completed"
            result.execution_time = (operation.completed_at - operation.started_at).total_seconds()

            return result

        except asyncio.TimeoutError:
            logger.error(f"❌ Operation {operation.operation_id} timed out after {operation.timeout}s")
            operation.status = "timeout"
            operation.error_message = f"Operation timed out after {operation.timeout} seconds"

            result = DCCOperationResult(operation.operation_id, False)
            result.error_message = operation.error_message
            return result

        except Exception as e:
            logger.error(f"❌ Operation {operation.operation_id} failed: {e}")
            operation.status = "failed"
            operation.error_message = str(e)

            result = DCCOperationResult(operation.operation_id, False)
            result.error_message = str(e)
            return result

        finally:
            # Clean up operation
            if operation.operation_id in session.active_operations:
                del session.active_operations[operation.operation_id]

            # Update session state
            if len(session.active_operations) == 0:
                session.state = DCCSessionState.ACTIVE

            session.last_activity = datetime.now()

    def _create_temp_directory(self, operation_id: str) -> str:
        """Create temporary directory for operation."""
        temp_base = tempfile.gettempdir()
        temp_dir = os.path.join(temp_base, f"plumber_dcc_{self.dcc_type}", operation_id)
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def _cleanup_temp_directory(self, temp_dir: str):
        """Clean up temporary directory."""
        try:
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug(f"🧹 Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return f"{self.dcc_type}_{uuid.uuid4().hex[:8]}"

    def _log_operation_start(self, operation: DCCOperation):
        """Log operation start."""
        logger.info(f"🎬 Starting {self.dcc_type} operation: {operation.operation_type} ({operation.operation_id})")

    def _log_operation_complete(self, operation: DCCOperation, success: bool):
        """Log operation completion."""
        duration = 0
        if operation.started_at and operation.completed_at:
            duration = (operation.completed_at - operation.started_at).total_seconds()

        status = "✅" if success else "❌"
        logger.info(f"{status} {self.dcc_type} operation {operation.operation_id} completed in {duration:.2f}s")

    async def shutdown(self):
        """Shutdown plugin and clean up all sessions."""
        logger.info(f"🛑 Shutting down {self.dcc_type} plugin...")

        # Close all sessions
        for session in list(self.sessions.values()):
            await self.close_session(session)

        self.sessions.clear()
        logger.info(f"✅ {self.dcc_type} plugin shutdown complete")