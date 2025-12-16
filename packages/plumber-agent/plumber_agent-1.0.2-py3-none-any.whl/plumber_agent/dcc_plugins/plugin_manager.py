"""
DCC Plugin Manager
Manages multiple DCC plugins and provides unified interface for DCC operations.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Type

from .base_plugin import BaseDCCPlugin, DCCOperation, DCCOperationResult, DCCSession, DCCSessionState

logger = logging.getLogger(__name__)

class DCCPluginManager:
    """Manages multiple DCC plugins and provides unified operation interface."""

    def __init__(self):
        self.plugins: Dict[str, BaseDCCPlugin] = {}
        self.available_dccs: List[str] = []
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.operation_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000

        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None

    async def initialize(self) -> Dict[str, Any]:
        """Initialize all DCC plugins."""
        logger.info("🚀 Initializing DCC Plugin Manager...")

        # Import and register plugins
        await self._register_plugins()

        # Initialize each plugin
        initialization_results = {}
        for dcc_type, plugin in self.plugins.items():
            try:
                success = await plugin.initialize()
                initialization_results[dcc_type] = {
                    "initialized": success,
                    "available": plugin.is_available,
                    "version": plugin.version,
                    "capabilities": plugin.get_capabilities(),
                    "supported_operations": plugin.get_supported_operations()
                }

                if success and plugin.is_available:
                    self.available_dccs.append(dcc_type)
                    logger.info(f"✅ {dcc_type} plugin ready: {plugin.version}")
                else:
                    logger.warning(f"❌ {dcc_type} plugin not available")

            except Exception as e:
                logger.error(f"❌ Failed to initialize {dcc_type} plugin: {e}")
                initialization_results[dcc_type] = {
                    "initialized": False,
                    "error": str(e)
                }

        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info(f"🎉 DCC Plugin Manager initialized: {len(self.available_dccs)} DCCs available")
        return initialization_results

    async def _register_plugins(self):
        """Register all available DCC plugins."""
        try:
            # Import plugins dynamically
            from .maya_plugin import MayaPlugin
            from .blender_plugin import BlenderPlugin
            from .houdini_plugin import HoudiniPlugin

            # Register plugins
            self.plugins["maya"] = MayaPlugin()
            self.plugins["blender"] = BlenderPlugin()
            self.plugins["houdini"] = HoudiniPlugin()

            logger.info(f"📦 Registered {len(self.plugins)} DCC plugins")

        except ImportError as e:
            logger.warning(f"Failed to import some DCC plugins: {e}")

    async def execute_operation(self, dcc_type: str, operation_type: str,
                              parameters: Dict[str, Any] = None,
                              timeout: int = 300, priority: int = 1,
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute operation on specified DCC."""
        operation_id = str(uuid.uuid4())

        # Create operation
        operation = DCCOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            parameters=parameters or {},
            timeout=timeout,
            priority=priority
        )

        logger.info(f"🎬 Executing {dcc_type} operation: {operation_type} ({operation_id})")

        try:
            # Check if DCC is available
            if dcc_type not in self.available_dccs:
                raise ValueError(f"{dcc_type} is not available")

            plugin = self.plugins[dcc_type]

            # Validate operation
            if not plugin.validate_operation(operation):
                raise ValueError(f"Invalid operation: {operation_type} for {dcc_type}")

            # Get or create session
            session = await plugin.get_or_create_session()

            # Execute operation with timeout
            result = await plugin.execute_with_timeout(session, operation, progress_callback)

            # Record statistics
            self.total_operations += 1
            if result.success:
                self.successful_operations += 1
            else:
                self.failed_operations += 1

            # Add to history
            self._add_to_history(operation, result)

            return result

        except Exception as e:
            logger.error(f"❌ Operation {operation_id} failed: {e}")

            # Create failed result
            result = DCCOperationResult(operation_id, False)
            result.error_message = str(e)

            self.total_operations += 1
            self.failed_operations += 1
            self._add_to_history(operation, result)

            return result

    async def execute_batch_operations(self, operations: List[Dict[str, Any]],
                                     max_concurrent: int = 3) -> List[DCCOperationResult]:
        """Execute multiple operations concurrently."""
        logger.info(f"🔄 Executing batch of {len(operations)} operations (max concurrent: {max_concurrent})")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_single(op_data):
            async with semaphore:
                return await self.execute_operation(**op_data)

        # Execute all operations
        tasks = [execute_single(op) for op in operations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_result = DCCOperationResult(f"batch_op_{i}", False)
                failed_result.error_message = str(result)
                final_results.append(failed_result)
            else:
                final_results.append(result)

        successful = sum(1 for r in final_results if r.success)
        logger.info(f"✅ Batch operations completed: {successful}/{len(operations)} successful")

        return final_results

    async def get_available_dccs(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available DCCs."""
        dcc_info = {}

        for dcc_type in self.available_dccs:
            plugin = self.plugins[dcc_type]
            dcc_info[dcc_type] = {
                "available": plugin.is_available,
                "version": plugin.version,
                "capabilities": plugin.get_capabilities(),
                "supported_operations": plugin.get_supported_operations(),
                "session_stats": plugin.get_session_stats(),
                "executable_path": plugin.executable_path
            }

        return dcc_info

    async def get_plugin_status(self, dcc_type: str) -> Dict[str, Any]:
        """Get detailed status of specific plugin."""
        if dcc_type not in self.plugins:
            return {"error": f"Plugin {dcc_type} not found"}

        plugin = self.plugins[dcc_type]

        return {
            "dcc_type": dcc_type,
            "available": plugin.is_available,
            "version": plugin.version,
            "capabilities": plugin.get_capabilities(),
            "supported_operations": plugin.get_supported_operations(),
            "session_stats": plugin.get_session_stats(),
            "discovery_data": plugin.discovery_data
        }

    async def get_session_info(self, dcc_type: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about specific session."""
        if dcc_type not in self.plugins:
            return None

        plugin = self.plugins[dcc_type]
        session = await plugin.get_session(session_id)

        if not session:
            return None

        return {
            "session_id": session.session_id,
            "dcc_type": session.dcc_type,
            "version": session.version,
            "state": session.state.value,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "active_operations": list(session.active_operations.keys()),
            "operation_count": len(session.active_operations)
        }

    async def close_session(self, dcc_type: str, session_id: str) -> bool:
        """Close specific session."""
        if dcc_type not in self.plugins:
            return False

        plugin = self.plugins[dcc_type]
        session = await plugin.get_session(session_id)

        if not session:
            return False

        return await plugin.close_session(session)

    async def close_all_sessions(self, dcc_type: Optional[str] = None):
        """Close all sessions for specific DCC or all DCCs."""
        if dcc_type:
            if dcc_type in self.plugins:
                plugin = self.plugins[dcc_type]
                for session in list(plugin.sessions.values()):
                    await plugin.close_session(session)
                plugin.sessions.clear()
        else:
            for plugin in self.plugins.values():
                for session in list(plugin.sessions.values()):
                    await plugin.close_session(session)
                plugin.sessions.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get operation statistics."""
        success_rate = 0
        if self.total_operations > 0:
            success_rate = (self.successful_operations / self.total_operations) * 100

        # Get per-DCC statistics
        dcc_stats = {}
        for dcc_type, plugin in self.plugins.items():
            dcc_stats[dcc_type] = plugin.get_session_stats()

        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": success_rate,
            "available_dccs": len(self.available_dccs),
            "total_plugins": len(self.plugins),
            "dcc_stats": dcc_stats,
            "recent_operations": len([h for h in self.operation_history
                                    if (datetime.now() - datetime.fromisoformat(h['timestamp'])).total_seconds() < 3600])
        }

    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent operation history."""
        return self.operation_history[-limit:] if self.operation_history else []

    async def _cleanup_loop(self):
        """Background task to clean up inactive sessions."""
        while True:
            try:
                total_cleaned = 0
                for plugin in self.plugins.values():
                    cleaned = await plugin.cleanup_sessions()
                    total_cleaned += cleaned

                if total_cleaned > 0:
                    logger.info(f"🧹 Cleaned up {total_cleaned} inactive sessions")

                await asyncio.sleep(300)  # Clean up every 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)

    async def _monitoring_loop(self):
        """Background task to monitor plugin health."""
        while True:
            try:
                # Check plugin health
                for dcc_type, plugin in self.plugins.items():
                    if plugin.is_available:
                        session_stats = plugin.get_session_stats()
                        if session_stats["total_sessions"] > plugin.max_sessions * 0.8:
                            logger.warning(f"⚠️ {dcc_type} approaching session limit: {session_stats['total_sessions']}/{plugin.max_sessions}")

                await asyncio.sleep(60)  # Monitor every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)

    def _add_to_history(self, operation: DCCOperation, result: DCCOperationResult):
        """Add operation to history."""
        history_entry = {
            "operation_id": operation.operation_id,
            "operation_type": operation.operation_type,
            "dcc_type": getattr(operation, 'dcc_type', 'unknown'),
            "success": result.success,
            "execution_time": result.execution_time,
            "timestamp": datetime.now().isoformat(),
            "error_message": result.error_message
        }

        self.operation_history.append(history_entry)

        # Limit history size
        if len(self.operation_history) > self.max_history_size:
            self.operation_history = self.operation_history[-self.max_history_size//2:]

    async def shutdown(self):
        """Shutdown plugin manager and all plugins."""
        logger.info("🛑 Shutting down DCC Plugin Manager...")

        # Cancel background tasks
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()

        # Shutdown all plugins
        for plugin in self.plugins.values():
            await plugin.shutdown()

        logger.info("✅ DCC Plugin Manager shutdown complete")