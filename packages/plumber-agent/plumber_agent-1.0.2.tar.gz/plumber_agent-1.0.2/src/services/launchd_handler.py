"""
macOS launchd service handler for Plumber Agent.

Manages the agent as a launchd service on macOS systems.
"""

import os
import subprocess
import sys
import plistlib
from pathlib import Path
from typing import Dict, Optional, List


class LaunchdHandler:
    """Handles launchd service management on macOS."""

    SERVICE_NAME = "com.damnltd.plumber-agent"
    PLIST_FILE = Path.home() / "Library" / "LaunchAgents" / f"{SERVICE_NAME}.plist"
    LOG_DIR = Path.home() / "Library" / "Logs"
    LOG_FILE = LOG_DIR / "plumber-agent.log"
    ERR_LOG_FILE = LOG_DIR / "plumber-agent-error.log"

    def __init__(self):
        """Initialize launchd handler."""
        self.python_executable = sys.executable
        self.plumber_agent_executable = self._find_plumber_agent_executable()

        # Ensure log directory exists
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _find_plumber_agent_executable(self) -> str:
        """Find the plumber-agent executable path."""
        # Try to find in PATH
        try:
            result = subprocess.run(
                ["which", "plumber-agent"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Fallback: construct path from Python executable
        python_dir = Path(self.python_executable).parent
        plumber_agent_path = python_dir / "plumber-agent"
        return str(plumber_agent_path)

    def _generate_plist(self, host: str, port: int, auto_start: bool) -> Dict:
        """
        Generate launchd plist configuration.

        Args:
            host: Host to bind to
            port: Port to bind to
            auto_start: Enable auto-start on boot

        Returns:
            Plist dictionary
        """
        plist = {
            'Label': self.SERVICE_NAME,
            'ProgramArguments': [
                self.plumber_agent_executable,
                '--host', host,
                '--port', str(port)
            ],
            'RunAtLoad': auto_start,
            'KeepAlive': {
                'SuccessfulExit': False,  # Restart on failure
                'Crashed': True
            },
            'StandardOutPath': str(self.LOG_FILE),
            'StandardErrorPath': str(self.ERR_LOG_FILE),
            'WorkingDirectory': str(Path.home()),
            'EnvironmentVariables': {
                'PATH': os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin'),
            }
        }

        return plist

    def install(self, host: str = '127.0.0.1', port: int = 8001, auto_start: bool = True) -> bool:
        """
        Install the agent as a launchd service.

        Args:
            host: Host to bind to
            port: Port to bind to
            auto_start: Enable auto-start on boot

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure LaunchAgents directory exists
            self.PLIST_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Generate plist
            plist_content = self._generate_plist(host, port, auto_start)

            # Write plist file
            with open(self.PLIST_FILE, 'wb') as f:
                plistlib.dump(plist_content, f)

            print(f"✓ Plist file created: {self.PLIST_FILE}")

            # Create log files
            self.LOG_FILE.touch(exist_ok=True)
            self.ERR_LOG_FILE.touch(exist_ok=True)

            # Load service (registers it with launchd)
            subprocess.run(
                ["launchctl", "load", str(self.PLIST_FILE)],
                check=True,
                capture_output=True
            )
            print(f"✓ Service loaded with launchd")

            if auto_start:
                print(f"✓ Service will start automatically on login")

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error loading service: {e}")
            if e.stderr:
                print(f"Details: {e.stderr.decode()}")
            return False
        except Exception as e:
            print(f"Error installing service: {e}")
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the launchd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Unload service if loaded
            if self._is_loaded():
                subprocess.run(
                    ["launchctl", "unload", str(self.PLIST_FILE)],
                    check=False,
                    capture_output=True
                )
                print(f"✓ Service unloaded from launchd")

            # Remove plist file
            if self.PLIST_FILE.exists():
                self.PLIST_FILE.unlink()
                print(f"✓ Plist file removed: {self.PLIST_FILE}")

            return True

        except Exception as e:
            print(f"Error uninstalling service: {e}")
            return False

    def _is_loaded(self) -> bool:
        """
        Check if service is loaded with launchd.

        Returns:
            True if loaded, False otherwise
        """
        try:
            result = subprocess.run(
                ["launchctl", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            return self.SERVICE_NAME in result.stdout
        except subprocess.CalledProcessError:
            return False

    def start(self) -> bool:
        """
        Start the launchd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._is_loaded():
                # Load if not loaded
                subprocess.run(
                    ["launchctl", "load", str(self.PLIST_FILE)],
                    check=True,
                    capture_output=True
                )
            else:
                # Kickstart if already loaded
                subprocess.run(
                    ["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/{self.SERVICE_NAME}"],
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError:
            return False

    def stop(self) -> bool:
        """
        Stop the launchd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self._is_loaded():
                subprocess.run(
                    ["launchctl", "stop", self.SERVICE_NAME],
                    check=True,
                    capture_output=True
                )
            return True
        except subprocess.CalledProcessError:
            return False

    def restart(self) -> bool:
        """
        Restart the launchd service.

        Returns:
            True if successful, False otherwise
        """
        self.stop()
        import time
        time.sleep(1)
        return self.start()

    def status(self) -> Dict[str, any]:
        """
        Get the service status.

        Returns:
            Dictionary with status information
        """
        try:
            result = subprocess.run(
                ["launchctl", "list", self.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=False
            )

            is_running = result.returncode == 0

            status_info = {
                'is_running': is_running,
                'service_name': self.SERVICE_NAME,
                'platform': 'macOS (launchd)'
            }

            if is_running and result.stdout:
                # Parse launchctl output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if '"PID"' in line or 'PID' in line:
                        try:
                            # Extract PID from output like: "PID" = 12345;
                            pid = int(line.split('=')[1].strip().rstrip(';'))
                            if pid > 0:
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
                'platform': 'macOS (launchd)',
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
        logs = []

        # Read stdout log
        if self.LOG_FILE.exists():
            with open(self.LOG_FILE, 'r') as f:
                stdout_lines = f.readlines()
                logs.extend([f"[OUT] {line.rstrip()}" for line in stdout_lines[-lines:]])

        # Read stderr log
        if self.ERR_LOG_FILE.exists():
            with open(self.ERR_LOG_FILE, 'r') as f:
                stderr_lines = f.readlines()
                logs.extend([f"[ERR] {line.rstrip()}" for line in stderr_lines[-lines:]])

        # Sort by timestamp if possible, otherwise just return last N lines
        return logs[-lines:]

    def follow_logs(self):
        """
        Follow service logs in real-time (blocking).
        """
        try:
            # Use tail -f on both log files
            subprocess.run(
                ["tail", "-f", str(self.LOG_FILE), str(self.ERR_LOG_FILE)],
                check=True
            )
        except KeyboardInterrupt:
            pass
        except subprocess.CalledProcessError:
            print(f"Error following logs. Log files:")
            print(f"  {self.LOG_FILE}")
            print(f"  {self.ERR_LOG_FILE}")
