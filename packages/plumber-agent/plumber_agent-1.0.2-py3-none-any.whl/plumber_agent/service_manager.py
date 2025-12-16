"""
Cross-platform service manager for Plumber Agent.

Automatically detects the operating system and delegates service management
to the appropriate platform-specific handler:
- Linux: systemd
- macOS: launchd
- Windows: Windows Service

This provides a unified API for service management across all platforms.
"""

import platform
import sys
from typing import Dict, Optional, List


class ServiceManager:
    """
    Cross-platform service manager.

    Automatically detects OS and delegates to appropriate handler.
    """

    def __init__(self):
        """Initialize service manager with platform detection."""
        self.platform = platform.system().lower()
        self.handler = self._get_platform_handler()

    def _get_platform_handler(self):
        """
        Get the appropriate service handler for the current platform.

        Returns:
            Platform-specific service handler instance

        Raises:
            RuntimeError: If platform is not supported
        """
        if self.platform == 'linux':
            from .services.systemd_handler import SystemdHandler
            return SystemdHandler()

        elif self.platform == 'darwin':  # macOS
            from .services.launchd_handler import LaunchdHandler
            return LaunchdHandler()

        elif self.platform == 'windows':
            from .services.windows_handler import WindowsHandler
            return WindowsHandler()

        else:
            raise RuntimeError(
                f"Unsupported platform: {self.platform}. "
                "Plumber Agent service management supports Linux, macOS, and Windows."
            )

    def install(self, host: str = '127.0.0.1', port: int = 8001, auto_start: bool = True) -> bool:
        """
        Install the agent as a system service.

        Args:
            host: Host to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 8001)
            auto_start: Enable auto-start on boot (default: True)

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = ServiceManager()
            >>> manager.install(host='0.0.0.0', port=8002, auto_start=True)
            ✓ Service installed successfully!
            True
        """
        return self.handler.install(host=host, port=port, auto_start=auto_start)

    def uninstall(self) -> bool:
        """
        Uninstall the system service.

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = ServiceManager()
            >>> manager.uninstall()
            ✓ Service uninstalled successfully!
            True
        """
        return self.handler.uninstall()

    def start(self) -> bool:
        """
        Start the service.

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = ServiceManager()
            >>> manager.start()
            True
        """
        return self.handler.start()

    def stop(self) -> bool:
        """
        Stop the service.

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = ServiceManager()
            >>> manager.stop()
            True
        """
        return self.handler.stop()

    def restart(self) -> bool:
        """
        Restart the service.

        Returns:
            True if successful, False otherwise

        Example:
            >>> manager = ServiceManager()
            >>> manager.restart()
            True
        """
        return self.handler.restart()

    def status(self) -> Dict[str, any]:
        """
        Get the service status with detailed information.

        Returns:
            Dictionary with status information:
            - is_running: bool - Whether service is running
            - service_name: str - Service name
            - platform: str - Platform info
            - pid: int - Process ID (if running)
            - memory_usage: float - Memory usage in MB (if running)
            - cpu_percent: float - CPU usage percentage (if running)
            - uptime: str - Service uptime (if running)

        Example:
            >>> manager = ServiceManager()
            >>> status = manager.status()
            >>> print(f"Running: {status['is_running']}")
            Running: True
            >>> print(f"PID: {status.get('pid')}")
            PID: 12345
        """
        return self.handler.status()

    def get_logs(self, lines: int = 50) -> List[str]:
        """
        Get service logs.

        Args:
            lines: Number of log lines to retrieve (default: 50)

        Returns:
            List of log lines

        Example:
            >>> manager = ServiceManager()
            >>> logs = manager.get_logs(lines=20)
            >>> for line in logs:
            ...     print(line)
        """
        return self.handler.get_logs(lines=lines)

    def follow_logs(self):
        """
        Follow service logs in real-time (blocking operation).

        Press Ctrl+C to stop following logs.

        Example:
            >>> manager = ServiceManager()
            >>> manager.follow_logs()  # Blocks until Ctrl+C
        """
        return self.handler.follow_logs()

    def get_platform_info(self) -> Dict[str, str]:
        """
        Get platform information.

        Returns:
            Dictionary with platform details:
            - system: Operating system name
            - platform: Platform identifier
            - python_version: Python version
            - handler: Service handler type

        Example:
            >>> manager = ServiceManager()
            >>> info = manager.get_platform_info()
            >>> print(info)
            {
                'system': 'Linux',
                'platform': 'linux',
                'python_version': '3.10.12',
                'handler': 'systemd'
            }
        """
        handler_name = type(self.handler).__name__.replace('Handler', '').lower()

        return {
            'system': platform.system(),
            'platform': self.platform,
            'python_version': platform.python_version(),
            'handler': handler_name
        }

    @staticmethod
    def get_supported_platforms() -> List[str]:
        """
        Get list of supported platforms.

        Returns:
            List of supported platform names

        Example:
            >>> ServiceManager.get_supported_platforms()
            ['Linux', 'macOS', 'Windows']
        """
        return ['Linux', 'macOS', 'Windows']

    @staticmethod
    def is_platform_supported() -> bool:
        """
        Check if current platform is supported.

        Returns:
            True if platform is supported, False otherwise

        Example:
            >>> ServiceManager.is_platform_supported()
            True
        """
        system = platform.system().lower()
        return system in ['linux', 'darwin', 'windows']
