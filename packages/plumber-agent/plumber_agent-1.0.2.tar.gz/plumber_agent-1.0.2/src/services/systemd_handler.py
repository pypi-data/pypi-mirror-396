"""
Linux systemd service handler for Plumber Agent.

Manages the agent as a systemd service on Linux systems.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, List


class SystemdHandler:
    """Handles systemd service management on Linux."""

    SERVICE_NAME = "plumber-agent"
    SERVICE_FILE = f"/etc/systemd/system/{SERVICE_NAME}.service"
    LOG_FILE = f"/var/log/{SERVICE_NAME}.log"

    def __init__(self):
        """Initialize systemd handler."""
        self.python_executable = sys.executable
        self.plumber_agent_executable = self._find_plumber_agent_executable()

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

    def _generate_service_file(self, host: str, port: int) -> str:
        """
        Generate systemd service file content.

        Args:
            host: Host to bind to
            port: Port to bind to

        Returns:
            Service file content as string
        """
        service_content = f"""[Unit]
Description=Plumber Agent - Local DCC Agent for Maya, Blender, and Houdini
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'nobody')}
WorkingDirectory=/tmp
ExecStart={self.plumber_agent_executable} --host {host} --port {port}
Restart=on-failure
RestartSec=10
StandardOutput=append:{self.LOG_FILE}
StandardError=append:{self.LOG_FILE}

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
"""
        return service_content

    def install(self, host: str = '127.0.0.1', port: int = 8001, auto_start: bool = True) -> bool:
        """
        Install the agent as a systemd service.

        Args:
            host: Host to bind to
            port: Port to bind to
            auto_start: Enable auto-start on boot

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if running as root
            if os.geteuid() != 0:
                print("Error: Installing systemd service requires root privileges.")
                print("Please run with sudo: sudo plumber-agent install-service")
                return False

            # Generate service file
            service_content = self._generate_service_file(host, port)

            # Write service file
            with open(self.SERVICE_FILE, 'w') as f:
                f.write(service_content)

            print(f"✓ Service file created: {self.SERVICE_FILE}")

            # Create log file with proper permissions
            Path(self.LOG_FILE).touch(exist_ok=True)
            os.chmod(self.LOG_FILE, 0o644)

            # Reload systemd daemon
            subprocess.run(
                ["systemctl", "daemon-reload"],
                check=True,
                capture_output=True
            )
            print("✓ Systemd daemon reloaded")

            # Enable service if auto_start
            if auto_start:
                subprocess.run(
                    ["systemctl", "enable", self.SERVICE_NAME],
                    check=True,
                    capture_output=True
                )
                print(f"✓ Service enabled (auto-start on boot)")

            return True

        except subprocess.CalledProcessError as e:
            print(f"Error running systemctl: {e}")
            return False
        except Exception as e:
            print(f"Error installing service: {e}")
            return False

    def uninstall(self) -> bool:
        """
        Uninstall the systemd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if running as root
            if os.geteuid() != 0:
                print("Error: Uninstalling systemd service requires root privileges.")
                print("Please run with sudo: sudo plumber-agent uninstall-service")
                return False

            # Stop service if running
            self.stop()

            # Disable service
            subprocess.run(
                ["systemctl", "disable", self.SERVICE_NAME],
                check=False,
                capture_output=True
            )

            # Remove service file
            if os.path.exists(self.SERVICE_FILE):
                os.remove(self.SERVICE_FILE)
                print(f"✓ Service file removed: {self.SERVICE_FILE}")

            # Reload systemd daemon
            subprocess.run(
                ["systemctl", "daemon-reload"],
                check=True,
                capture_output=True
            )
            print("✓ Systemd daemon reloaded")

            return True

        except Exception as e:
            print(f"Error uninstalling service: {e}")
            return False

    def start(self) -> bool:
        """
        Start the systemd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ["systemctl", "start", self.SERVICE_NAME],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def stop(self) -> bool:
        """
        Stop the systemd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ["systemctl", "stop", self.SERVICE_NAME],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def restart(self) -> bool:
        """
        Restart the systemd service.

        Returns:
            True if successful, False otherwise
        """
        try:
            subprocess.run(
                ["systemctl", "restart", self.SERVICE_NAME],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def status(self) -> Dict[str, any]:
        """
        Get the service status.

        Returns:
            Dictionary with status information
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-active", self.SERVICE_NAME],
                capture_output=True,
                text=True,
                check=False
            )

            is_running = result.stdout.strip() == "active"

            status_info = {
                'is_running': is_running,
                'service_name': self.SERVICE_NAME,
                'platform': 'Linux (systemd)'
            }

            if is_running:
                # Get additional info
                try:
                    show_result = subprocess.run(
                        ["systemctl", "show", self.SERVICE_NAME, "--property=MainPID"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    pid_line = show_result.stdout.strip()
                    if pid_line.startswith("MainPID="):
                        pid = int(pid_line.split("=")[1])
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
                except Exception:
                    pass

            return status_info

        except Exception as e:
            return {
                'is_running': False,
                'service_name': self.SERVICE_NAME,
                'platform': 'Linux (systemd)',
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
        try:
            result = subprocess.run(
                ["journalctl", "-u", self.SERVICE_NAME, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.splitlines()
        except subprocess.CalledProcessError:
            # Fallback to log file
            if os.path.exists(self.LOG_FILE):
                with open(self.LOG_FILE, 'r') as f:
                    all_lines = f.readlines()
                    return [line.rstrip() for line in all_lines[-lines:]]
            return []

    def follow_logs(self):
        """
        Follow service logs in real-time (blocking).
        """
        try:
            subprocess.run(
                ["journalctl", "-u", self.SERVICE_NAME, "-f"],
                check=True
            )
        except subprocess.CalledProcessError:
            # Fallback to tail -f on log file
            if os.path.exists(self.LOG_FILE):
                subprocess.run(
                    ["tail", "-f", self.LOG_FILE],
                    check=True
                )
        except KeyboardInterrupt:
            pass
