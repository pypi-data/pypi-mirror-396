#!/usr/bin/env python3
"""
Cross-Platform Utilities
Provides cross-platform compatibility for paths, processes, and system operations.
"""

import os
import platform
import subprocess
import shutil
from pathlib import Path, PurePath, PureWindowsPath, PurePosixPath
from typing import List, Optional, Dict, Union, Any
import logging

logger = logging.getLogger(__name__)

class CrossPlatformPathHandler:
    """Handles path operations across Windows, Linux, and macOS."""

    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == 'Windows'
        self.is_linux = self.system == 'Linux'
        self.is_macos = self.system == 'Darwin'

    def normalize_path(self, path: Union[str, Path]) -> Path:
        """Normalize path for current platform."""
        if isinstance(path, str):
            path = Path(path)

        # Convert to absolute path and resolve
        return path.resolve()

    def to_platform_path(self, path: Union[str, Path], target_platform: str = None) -> str:
        """Convert path to target platform format."""
        if target_platform is None:
            target_platform = self.system

        path_str = str(path)

        if target_platform == 'Windows':
            # Convert forward slashes to backslashes for Windows
            return path_str.replace('/', '\\')
        else:
            # Convert backslashes to forward slashes for Unix-like systems
            return path_str.replace('\\', '/')

    def get_executable_extension(self) -> str:
        """Get platform-specific executable extension."""
        return '.exe' if self.is_windows else ''

    def find_executable_variants(self, base_name: str, search_paths: List[str]) -> List[str]:
        """Find executable variants across platforms."""
        variants = []
        extensions = ['.exe'] if self.is_windows else ['']

        for search_path in search_paths:
            for ext in extensions:
                exe_path = os.path.join(search_path, f"{base_name}{ext}")
                if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
                    variants.append(exe_path)

        return variants

    def get_app_data_dir(self, app_name: str) -> Path:
        """Get platform-specific application data directory."""
        if self.is_windows:
            # Windows: %APPDATA%/app_name
            base = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
        elif self.is_macos:
            # macOS: ~/Library/Application Support/app_name
            base = str(Path.home() / 'Library' / 'Application Support')
        else:
            # Linux: ~/.config/app_name
            base = os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))

        return Path(base) / app_name

    def get_temp_dir(self) -> Path:
        """Get platform-specific temporary directory."""
        import tempfile
        return Path(tempfile.gettempdir())

    def create_safe_filename(self, filename: str) -> str:
        """Create a safe filename for current platform."""
        # Remove/replace characters that are invalid on various platforms
        invalid_chars = '<>:"|?*' if self.is_windows else ''

        safe_name = filename
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')

        # Remove leading/trailing spaces and dots (problematic on Windows)
        safe_name = safe_name.strip(' .')

        # Limit length
        max_length = 255 if not self.is_windows else 260  # Windows has path length limits
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]

        return safe_name

class CrossPlatformProcessManager:
    """Manages process operations across platforms."""

    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == 'Windows'

    def run_command(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        timeout: Optional[float] = None,
        capture_output: bool = True,
        **kwargs
    ) -> subprocess.CompletedProcess:
        """Run command with platform-specific optimizations."""

        # Platform-specific environment setup
        env = kwargs.pop('env', os.environ.copy())

        if self.is_windows:
            # Windows-specific optimizations
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                env=env,
                **kwargs
            )
            return result

        except subprocess.TimeoutExpired as e:
            logger.warning(f"Command timed out after {timeout}s: {' '.join(command)}")
            raise
        except FileNotFoundError as e:
            logger.error(f"Executable not found: {command[0]}")
            raise

    def find_process_by_name(self, process_name: str) -> List[Dict[str, Any]]:
        """Find processes by name across platforms."""
        processes = []

        try:
            if self.is_windows:
                # Windows: use tasklist
                result = subprocess.run(
                    ['tasklist', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    import csv
                    reader = csv.reader(result.stdout.strip().split('\n'))
                    for row in reader:
                        if len(row) >= 5 and process_name.lower() in row[0].lower():
                            processes.append({
                                'name': row[0],
                                'pid': int(row[1]),
                                'memory': row[4]
                            })
            else:
                # Unix-like: use ps
                result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n')[1:]:  # Skip header
                        if process_name.lower() in line.lower():
                            parts = line.split()
                            if len(parts) >= 11:
                                processes.append({
                                    'name': ' '.join(parts[10:]),
                                    'pid': int(parts[1]),
                                    'cpu': parts[2],
                                    'memory': parts[3]
                                })

        except (subprocess.TimeoutExpired, ValueError, IndexError) as e:
            logger.error(f"Failed to find processes: {e}")

        return processes

    def kill_process_by_pid(self, pid: int, force: bool = False) -> bool:
        """Kill process by PID across platforms."""
        try:
            if self.is_windows:
                # Windows: use taskkill
                command = ['taskkill', '/PID', str(pid)]
                if force:
                    command.append('/F')
            else:
                # Unix-like: use kill
                import signal
                signal_type = signal.SIGKILL if force else signal.SIGTERM
                os.kill(pid, signal_type)
                return True

            result = subprocess.run(command, capture_output=True, timeout=10)
            return result.returncode == 0

        except (subprocess.TimeoutExpired, OSError, ProcessLookupError) as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False

class CrossPlatformSystemInfo:
    """Provides cross-platform system information."""

    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        import psutil

        info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count(),
        }

        # Add memory information if psutil available
        try:
            memory = psutil.virtual_memory()
            info.update({
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent
            })
        except ImportError:
            logger.debug("psutil not available, skipping memory info")

        return info

    @staticmethod
    def get_environment_paths() -> List[str]:
        """Get PATH environment variable as list."""
        path_env = os.environ.get('PATH', '')
        if platform.system() == 'Windows':
            return path_env.split(';')
        else:
            return path_env.split(':')

    @staticmethod
    def get_library_paths() -> List[str]:
        """Get library search paths for current platform."""
        if platform.system() == 'Windows':
            # Windows DLL search paths
            return [
                os.environ.get('SystemRoot', r'C:\Windows'),
                os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32'),
                os.environ.get('ProgramFiles', r'C:\Program Files'),
                os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')
            ]
        elif platform.system() == 'Darwin':
            # macOS library paths
            return [
                '/usr/lib',
                '/usr/local/lib',
                '/opt/homebrew/lib',
                '/Library/Frameworks',
                '/System/Library/Frameworks'
            ]
        else:
            # Linux library paths
            return [
                '/usr/lib',
                '/usr/local/lib',
                '/lib',
                '/usr/lib64',
                '/usr/local/lib64',
                '/lib64'
            ]

def get_cross_platform_handler() -> CrossPlatformPathHandler:
    """Get platform handler singleton."""
    if not hasattr(get_cross_platform_handler, '_instance'):
        get_cross_platform_handler._instance = CrossPlatformPathHandler()
    return get_cross_platform_handler._instance

def get_process_manager() -> CrossPlatformProcessManager:
    """Get process manager singleton."""
    if not hasattr(get_process_manager, '_instance'):
        get_process_manager._instance = CrossPlatformProcessManager()
    return get_process_manager._instance

# Convenience functions
def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize path for current platform."""
    return get_cross_platform_handler().normalize_path(path)

def to_platform_path(path: Union[str, Path], target_platform: str = None) -> str:
    """Convert path to target platform format."""
    return get_cross_platform_handler().to_platform_path(path, target_platform)

def run_cross_platform_command(
    command: List[str],
    timeout: Optional[float] = None,
    **kwargs
) -> subprocess.CompletedProcess:
    """Run command with cross-platform optimizations."""
    return get_process_manager().run_command(command, timeout=timeout, **kwargs)