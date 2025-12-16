"""
Windows Service handler for Plumber Agent.

Manages the agent as a Windows Service.
Uses pywin32 for native Windows Service API.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Dict, Optional, List


class WindowsHandler:
    """Handles Windows Service management."""

    SERVICE_NAME = "PlumberAgent"
    DISPLAY_NAME = "Plumber Agent - Local DCC Agent"
    DESCRIPTION = "Local DCC Agent for Plumber Workflow Editor (Maya, Blender, Houdini)"
    # Use APPDATA on Windows, fallback to home directory on other platforms
    # (This handler won't be used on non-Windows, but needs to be importable)
    LOG_DIR = Path(os.getenv('APPDATA', str(Path.home()))) / "plumber-agent"
    LOG_FILE = LOG_DIR / "agent.log"

    def __init__(self):
        """Initialize Windows handler."""
        self.python_executable = sys.executable
        self.plumber_agent_executable = self._find_plumber_agent_executable()

        # Ensure log directory exists
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Check if pywin32 is available
        self.has_pywin32 = self._check_pywin32()

    def _check_pywin32(self) -> bool:
        """Check if pywin32 is available."""
        try:
            import win32serviceutil
            return True
        except ImportError:
            return False

    def _find_plumber_agent_executable(self) -> str:
        """Find the plumber-agent executable path."""
        # Try to find in PATH
        try:
            result = subprocess.run(
                ["where", "plumber-agent"],
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass

        # Fallback: construct path from Python executable
        python_dir = Path(self.python_executable).parent
        plumber_agent_path = python_dir / "Scripts" / "plumber-agent.exe"
        if not plumber_agent_path.exists():
            plumber_agent_path = python_dir / "plumber-agent.exe"
        return str(plumber_agent_path)

    def install(self, host: str = '127.0.0.1', port: int = 8001, auto_start: bool = True) -> bool:
        """
        Install the agent as a Windows Service.

        Args:
            host: Host to bind to
            port: Port to bind to
            auto_start: Enable auto-start on boot

        Returns:
            True if successful, False otherwise
        """
        if self.has_pywin32:
            return self._install_with_pywin32(host, port, auto_start)
        else:
            return self._install_with_sc(host, port, auto_start)

    def _install_with_pywin32(self, host: str, port: int, auto_start: bool) -> bool:
        """Install service using pywin32."""
        try:
            import win32serviceutil
            import win32service

            # Create service command
            service_cmd = f'"{self.plumber_agent_executable}" --host {host} --port {port}'

            # Install service
            win32serviceutil.InstallService(
                None,  # No class (we're using executable directly)
                self.SERVICE_NAME,
                self.DISPLAY_NAME,
                startType=win32service.SERVICE_AUTO_START if auto_start else win32service.SERVICE_DEMAND_START,
                description=self.DESCRIPTION,
                exeName=self.python_executable,
                exeArgs=f'-m plumber_agent.cli --host {host} --port {port}'
            )

            print(f"✓ Service installed: {self.DISPLAY_NAME}")

            # Configure service to restart on failure
            subprocess.run(
                ["sc", "failure", self.SERVICE_NAME, "reset=", "86400", "actions=", "restart/60000/restart/60000//1000"],
                check=False,
                capture_output=True,
                shell=True
            )

            if auto_start:
                print(f"✓ Service set to auto-start on boot")

            return True

        except Exception as e:
            print(f"Error installing service with pywin32: {e}")
            return False

    def _install_with_sc(self, host: str, port: int, auto_start: bool) -> bool:
        """Install service using sc.exe command (fallback)."""
        try:
            # Build service command
            service_cmd = f'"{self.python_executable}" -m plumber_agent.cli --host {host} --port {port}'

            # Create service
            start_type = "auto" if auto_start else "demand"

            result = subprocess.run(
                [
                    "sc", "create", self.SERVICE_NAME,
                    f"binPath= {service_cmd}",
                    f"start= {start_type}",
                    f"DisplayName= {self.DISPLAY_NAME}"
                ],
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )

            if result.returncode != 0:
                print(f"Error creating service: {result.stderr}")
                return False

            print(f"✓ Service installed: {self.DISPLAY_NAME}")

            # Set description
            subprocess.run(
                ["sc", "description", self.SERVICE_NAME, self.DESCRIPTION],
                check=False,
                capture_output=True,
                shell=True
            )

            # Configure failure actions
            subprocess.run(
                ["sc", "failure", self.SERVICE_NAME, "reset=", "86400", "actions=", "restart/60000"],
                check=False,
                capture_output=True,
                shell=True
            )

            if auto_start:
                print(f"✓ Service set to auto-start on boot")

            print("\nNote: Windows Service requires pywin32 for optimal functionality.")
            print("Install with: pip install pywin32")

            return True

        except Exception as e:
            print(f"Error installing service: {e}")
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the Windows Service.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Stop service first
            self.stop()

            if self.has_pywin32:
                import win32serviceutil
                win32serviceutil.RemoveService(self.SERVICE_NAME)
            else:
                subprocess.run(
                    ["sc", "delete", self.SERVICE_NAME],
                    check=True,
                    capture_output=True,
                    shell=True
                )

            print(f"✓ Service uninstalled: {self.DISPLAY_NAME}")
            return True

        except Exception as e:
            print(f"Error uninstalling service: {e}")
            return False

    def start(self) -> bool:
        """
        Start the Windows Service.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.has_pywin32:
                import win32serviceutil
                win32serviceutil.StartService(self.SERVICE_NAME)
            else:
                subprocess.run(
                    ["sc", "start", self.SERVICE_NAME],
                    check=True,
                    capture_output=True,
                    shell=True
                )
            return True
        except Exception:
            return False

    def stop(self) -> bool:
        """
        Stop the Windows Service.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.has_pywin32:
                import win32serviceutil
                win32serviceutil.StopService(self.SERVICE_NAME)
            else:
                subprocess.run(
                    ["sc", "stop", self.SERVICE_NAME],
                    check=False,
                    capture_output=True,
                    shell=True
                )
            return True
        except Exception:
            return False

    def restart(self) -> bool:
        """
        Restart the Windows Service.

        Returns:
            True if successful, False otherwise
        """
        self.stop()
        import time
        time.sleep(2)
        return self.start()

    def status(self) -> Dict[str, any]:
        """
        Get the service status.

        Returns:
            Dictionary with status information
        """
        try:
            result = subprocess.run(
                ["sc", "query", self.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=False,
                shell=True
            )

            is_running = "RUNNING" in result.stdout

            status_info = {
                'is_running': is_running,
                'service_name': self.SERVICE_NAME,
                'platform': 'Windows (Service)'
            }

            if is_running:
                # Try to extract PID from sc query output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'PID' in line:
                        try:
                            pid = int(line.split(':')[1].strip())
                            status_info['pid'] = pid

                            # Get process info using psutil if available
                            try:
                                import psutil
                                process = psutil.Process(pid)
                                status_info['memory_usage'] = round(process.memory_info().rss / 1024 / 1024, 2)
                                status_info['cpu_percent'] = round(process.cpu_percent(interval=0.1), 2)

                                # Calculate uptime
                                create_time = process.create_time()
                                import time
                                uptime_seconds = int(time.time() - create_time)
                                hours = uptime_seconds // 3600
                                minutes = (uptime_seconds % 3600) // 60
                                status_info['uptime'] = f"{hours}h {minutes}m"
                            except ImportError:
                                pass
                        except (ValueError, IndexError):
                            pass

            return status_info

        except Exception as e:
            return {
                'is_running': False,
                'service_name': self.SERVICE_NAME,
                'platform': 'Windows (Service)',
                'error': str(e)
            }

    def get_logs(self, lines: int = 50) -> List[str]:
        """
        Get service logs.

        Args:
            lines: Number of lines to retrieve

        Returns:
            List of log lines
        """
        if self.LOG_FILE.exists():
            with open(self.LOG_FILE, 'r') as f:
                all_lines = f.readlines()
                return [line.rstrip() for line in all_lines[-lines:]]
        return []

    def follow_logs(self):
        """
        Follow service logs in real-time (blocking).
        """
        print(f"Following logs: {self.LOG_FILE}")
        print("Press Ctrl+C to stop\n")

        try:
            # Simple tail -f implementation for Windows
            if self.LOG_FILE.exists():
                with open(self.LOG_FILE, 'r') as f:
                    # Go to end of file
                    f.seek(0, 2)

                    while True:
                        line = f.readline()
                        if line:
                            print(line.rstrip())
                        else:
                            import time
                            time.sleep(0.1)
        except KeyboardInterrupt:
            pass
