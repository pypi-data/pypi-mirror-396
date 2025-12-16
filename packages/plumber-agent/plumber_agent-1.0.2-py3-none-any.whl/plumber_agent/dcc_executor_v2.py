"""
Enhanced DCC Executor v2.0
Uses the new universal DCC plugin system for improved reliability and extensibility.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from .dcc_plugins import DCCPluginManager
from .dcc_plugins.base_plugin import DCCOperation, DCCOperationResult

logger = logging.getLogger(__name__)

class EnhancedDCCExecutor:
    """Enhanced DCC Executor using the universal plugin system."""

    def __init__(self):
        self.plugin_manager = DCCPluginManager()
        self.initialized = False
        self.initialization_results: Dict[str, Any] = {}

    async def initialize(self):
        """Initialize the enhanced DCC executor."""
        logger.info("🚀 Initializing Enhanced DCC Executor v2.0")

        try:
            # Initialize plugin manager
            self.initialization_results = await self.plugin_manager.initialize()
            self.initialized = True

            # Log initialization summary
            available_dccs = [dcc for dcc, info in self.initialization_results.items()
                            if info.get('initialized', False) and info.get('available', False)]

            logger.info(f"✅ Enhanced DCC Executor initialized: {len(available_dccs)} DCCs available")
            for dcc in available_dccs:
                info = self.initialization_results[dcc]
                logger.info(f"   ✅ {dcc.title()}: {info.get('version', 'unknown')} ({len(info.get('supported_operations', []))} operations)")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced DCC Executor: {e}")
            return False

    async def execute_operation(self, operation_data: Dict[str, Any],
                              progress_callback: Optional[Callable] = None) -> DCCOperationResult:
        """Execute DCC operation using the plugin system."""
        if not self.initialized:
            raise RuntimeError("DCC Executor not initialized")

        # Extract operation parameters
        dcc_type = operation_data.get('dcc_type')
        operation_type = operation_data.get('operation_type')
        parameters = operation_data.get('parameters', {})
        timeout = operation_data.get('timeout', 300)
        operation_id = operation_data.get('operation_id') or str(uuid.uuid4())

        if not dcc_type or not operation_type:
            raise ValueError("dcc_type and operation_type are required")

        logger.info(f"🎬 Executing {dcc_type} operation: {operation_type} ({operation_id})")

        try:
            # Execute operation through plugin manager
            result = await self.plugin_manager.execute_operation(
                dcc_type=dcc_type,
                operation_type=operation_type,
                parameters=parameters,
                timeout=timeout,
                progress_callback=progress_callback
            )

            logger.info(f"{'✅' if result.success else '❌'} Operation {operation_id} completed: {result.success}")
            return result

        except Exception as e:
            logger.error(f"❌ Operation {operation_id} failed: {e}")
            result = DCCOperationResult(operation_id, False)
            result.error_message = str(e)
            return result

    async def execute_batch_operations(self, operations: List[Dict[str, Any]],
                                     max_concurrent: int = 3) -> List[DCCOperationResult]:
        """Execute multiple DCC operations concurrently."""
        if not self.initialized:
            raise RuntimeError("DCC Executor not initialized")

        logger.info(f"🔄 Executing batch of {len(operations)} operations")

        # Prepare operations for plugin manager
        plugin_operations = []
        for op in operations:
            plugin_op = {
                'dcc_type': op.get('dcc_type'),
                'operation_type': op.get('operation_type'),
                'parameters': op.get('parameters', {}),
                'timeout': op.get('timeout', 300),
                'priority': op.get('priority', 1)
            }
            plugin_operations.append(plugin_op)

        # Execute through plugin manager
        results = await self.plugin_manager.execute_batch_operations(
            plugin_operations, max_concurrent
        )

        successful = sum(1 for r in results if r.success)
        logger.info(f"✅ Batch execution completed: {successful}/{len(operations)} successful")

        return results

    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running operation."""
        logger.info(f"🚫 Cancelling operation: {operation_id}")
        # TODO: Implement operation cancellation in plugin manager
        # For now, return False as cancellation is not yet implemented
        return False

    def get_available_dccs(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available DCCs."""
        if not self.initialized:
            return {}

        return asyncio.run(self.plugin_manager.get_available_dccs())

    def get_dcc_status(self, dcc_type: str) -> Dict[str, Any]:
        """Get status of specific DCC."""
        if not self.initialized:
            return {"error": "Executor not initialized"}

        return asyncio.run(self.plugin_manager.get_plugin_status(dcc_type))

    def get_supported_operations(self, dcc_type: str) -> List[str]:
        """Get supported operations for specific DCC."""
        if not self.initialized:
            return []

        status = self.get_dcc_status(dcc_type)
        return status.get('supported_operations', [])

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.initialized:
            return {}

        base_stats = self.plugin_manager.get_statistics()

        # Add executor-specific stats
        base_stats.update({
            "executor_version": "2.0",
            "plugin_system": True,
            "initialization_results": self.initialization_results,
            "executor_initialized": self.initialized
        })

        return base_stats

    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent operation history."""
        if not self.initialized:
            return []

        return self.plugin_manager.get_operation_history(limit)

    async def close_session(self, dcc_type: str, session_id: str) -> bool:
        """Close specific DCC session."""
        if not self.initialized:
            return False

        return await self.plugin_manager.close_session(dcc_type, session_id)

    async def close_all_sessions(self, dcc_type: Optional[str] = None):
        """Close all sessions for specific DCC or all DCCs."""
        if not self.initialized:
            return

        await self.plugin_manager.close_all_sessions(dcc_type)

    def validate_operation(self, dcc_type: str, operation_type: str,
                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if operation can be executed."""
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }

        if not self.initialized:
            validation_result["errors"].append("Executor not initialized")
            return validation_result

        # Check if DCC is available
        available_dccs = asyncio.run(self.plugin_manager.get_available_dccs())
        if dcc_type not in available_dccs:
            validation_result["errors"].append(f"DCC {dcc_type} is not available")
            return validation_result

        dcc_info = available_dccs[dcc_type]

        # Check if operation is supported
        if operation_type not in dcc_info.get('supported_operations', []):
            validation_result["errors"].append(f"Operation {operation_type} not supported by {dcc_type}")
            return validation_result

        # Check session capacity
        session_stats = dcc_info.get('session_stats', {})
        if session_stats.get('total_sessions', 0) >= session_stats.get('max_sessions', 1):
            validation_result["warnings"].append(f"{dcc_type} is at session capacity")

        # If we get here, basic validation passed
        validation_result["valid"] = True
        return validation_result

    async def cleanup(self):
        """Clean up and shutdown the executor."""
        logger.info("🛑 Shutting down Enhanced DCC Executor")

        if self.initialized:
            await self.plugin_manager.shutdown()
            self.initialized = False

        logger.info("✅ Enhanced DCC Executor shutdown complete")