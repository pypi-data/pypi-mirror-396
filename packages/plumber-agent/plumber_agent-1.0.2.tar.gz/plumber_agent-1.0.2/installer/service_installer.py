"""
Plumber Local DCC Agent - Cross-Platform Service Installer

Installs the Plumber agent as a native system service on Windows, Linux, and macOS.

Supported platforms:
- Windows: Windows Service using NSSM (Non-Sucking Service Manager)
- Linux: systemd service
- macOS: launchd service

Dependencies:
    No external dependencies - uses only Python stdlib

Usage:
    python service_installer.py install
    python service_installer.py uninstall
    python service_installer.py start
    python service_installer.py stop
    python service_installer.py restart
    python service_installer.py status
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


class ServiceInstaller:
    """Cross-platform service installer for Plumber Local DCC Agent."""

    def __init__(self):
        """Initialize service installer."""
        self.platform = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)
        self.service_name = "PlumberAgent"
        self.service_display_name = "Plumber Local DCC Agent"
        self.service_description = "Connects local DCC applications (Maya, Blender, Houdini) to Plumber cloud platform"

        # Determine installation paths
        if getattr(sys, 'frozen', False):
            # Running as bundled executable
            self.install_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.install_dir = Path(__file__).parent.parent

        self.agent_executable = self.install_dir / ("plumber_agent.exe" if self.platform == "Windows" else "plumber_agent")

        # Platform-specific paths
        if self.platform == "Windows":
            self.nssm_exe = self.install_dir / "nssm.exe"
        elif self.platform == "Linux":
            self.service_file = f"/etc/systemd/system/{self.service_name.lower()}.service"
            self.user_service_file = Path.home() / f".config/systemd/user/{self.service_name.lower()}.service"
        elif self.platform == "Darwin":  # macOS
            self.plist_file = Path.home() / f"Library/LaunchAgents/com.plumber.{self.service_name.lower()}.plist"

    def install(self, user_level=False):
        """
        Install agent as system service.

        Args:
            user_level: If True, install as user-level service (no admin required)
        """
        print(f"Installing {self.service_display_name} on {self.platform}...")

        if self.platform == "Windows":
            return self._install_windows_service(user_level)
        elif self.platform == "Linux":
            return self._install_systemd_service(user_level)
        elif self.platform == "Darwin":
            return self._install_launchd_service()
        else:
            print(f"❌ Unsupported platform: {self.platform}")
            return False

    def uninstall(self):
        """Uninstall agent service."""
        print(f"Uninstalling {self.service_display_name}...")

        # Stop service first
        self.stop()

        if self.platform == "Windows":
            return self._uninstall_windows_service()
        elif self.platform == "Linux":
            return self._uninstall_systemd_service()
        elif self.platform == "Darwin":
            return self._uninstall_launchd_service()
        else:
            print(f"❌ Unsupported platform: {self.platform}")
            return False

    def start(self):
        """Start agent service."""
        print(f"Starting {self.service_display_name}...")

        if self.platform == "Windows":
            return self._run_command([str(self.nssm_exe), "start", self.service_name])
        elif self.platform == "Linux":
            # Try user service first, then system service
            result = self._run_command(["systemctl", "--user", "start", f"{self.service_name.lower()}.service"])
            if not result:
                result = self._run_command(["sudo", "systemctl", "start", f"{self.service_name.lower()}.service"])
            return result
        elif self.platform == "Darwin":
            return self._run_command(["launchctl", "start", f"com.plumber.{self.service_name.lower()}"])
        else:
            print(f"❌ Unsupported platform: {self.platform}")
            return False

    def stop(self):
        """Stop agent service."""
        print(f"Stopping {self.service_display_name}...")

        if self.platform == "Windows":
            return self._run_command([str(self.nssm_exe), "stop", self.service_name])
        elif self.platform == "Linux":
            # Try user service first, then system service
            result = self._run_command(["systemctl", "--user", "stop", f"{self.service_name.lower()}.service"])
            if not result:
                result = self._run_command(["sudo", "systemctl", "stop", f"{self.service_name.lower()}.service"])
            return result
        elif self.platform == "Darwin":
            return self._run_command(["launchctl", "stop", f"com.plumber.{self.service_name.lower()}"])
        else:
            print(f"❌ Unsupported platform: {self.platform}")
            return False

    def restart(self):
        """Restart agent service."""
        print(f"Restarting {self.service_display_name}...")
        self.stop()
        import time
        time.sleep(2)
        return self.start()

    def status(self):
        """Check agent service status."""
        print(f"Checking status of {self.service_display_name}...")

        if self.platform == "Windows":
            result = self._run_command([str(self.nssm_exe), "status", self.service_name], capture=True)
            if result:
                status = result.stdout.decode().strip()
                print(f"Status: {status}")
                return status == "SERVICE_RUNNING"
        elif self.platform == "Linux":
            # Try user service first, then system service
            result = self._run_command(["systemctl", "--user", "is-active", f"{self.service_name.lower()}.service"], capture=True)
            if not result or result.returncode != 0:
                result = self._run_command(["systemctl", "is-active", f"{self.service_name.lower()}.service"], capture=True)

            if result and result.returncode == 0:
                status = result.stdout.decode().strip()
                print(f"Status: {status}")
                return status == "active"
            return False
        elif self.platform == "Darwin":
            result = self._run_command(["launchctl", "list", f"com.plumber.{self.service_name.lower()}"], capture=True)
            if result and result.returncode == 0:
                print("Status: running")
                return True
            else:
                print("Status: stopped")
                return False
        else:
            print(f"❌ Unsupported platform: {self.platform}")
            return False

    # Windows-specific methods

    def _install_windows_service(self, user_level=False):
        """Install Windows Service using NSSM."""
        if not self.nssm_exe.exists():
            print(f"❌ NSSM not found at {self.nssm_exe}")
            print("   Download NSSM from https://nssm.cc/download")
            return False

        if not self.agent_executable.exists():
            print(f"❌ Agent executable not found at {self.agent_executable}")
            return False

        # Install service using NSSM
        commands = [
            [str(self.nssm_exe), "install", self.service_name, str(self.agent_executable)],
            [str(self.nssm_exe), "set", self.service_name, "DisplayName", self.service_display_name],
            [str(self.nssm_exe), "set", self.service_name, "Description", self.service_description],
            [str(self.nssm_exe), "set", self.service_name, "Start", "SERVICE_AUTO_START"],
            [str(self.nssm_exe), "set", self.service_name, "AppDirectory", str(self.install_dir)],
            [str(self.nssm_exe), "set", self.service_name, "AppStdout", str(self.install_dir / "agent_stdout.log")],
            [str(self.nssm_exe), "set", self.service_name, "AppStderr", str(self.install_dir / "agent_stderr.log")],
        ]

        for cmd in commands:
            if not self._run_command(cmd):
                print(f"❌ Failed to configure service: {' '.join(cmd)}")
                return False

        print(f"✅ Windows Service installed successfully")
        print(f"   Service name: {self.service_name}")
        print(f"   Display name: {self.service_display_name}")
        return True

    def _uninstall_windows_service(self):
        """Uninstall Windows Service."""
        if not self.nssm_exe.exists():
            print(f"❌ NSSM not found at {self.nssm_exe}")
            return False

        if self._run_command([str(self.nssm_exe), "remove", self.service_name, "confirm"]):
            print(f"✅ Windows Service uninstalled successfully")
            return True
        return False

    # Linux-specific methods

    def _install_systemd_service(self, user_level=False):
        """Install systemd service on Linux."""
        if not self.agent_executable.exists():
            print(f"❌ Agent executable not found at {self.agent_executable}")
            return False

        # Create service file content
        service_content = f"""[Unit]
Description={self.service_description}
After=network.target

[Service]
Type=simple
ExecStart={self.agent_executable}
Restart=always
RestartSec=10
WorkingDirectory={self.install_dir}

[Install]
WantedBy={"default.target" if user_level else "multi-user.target"}
"""

        # Determine service file path
        if user_level:
            service_file = self.user_service_file
            service_file.parent.mkdir(parents=True, exist_ok=True)
            reload_cmd = ["systemctl", "--user", "daemon-reload"]
            enable_cmd = ["systemctl", "--user", "enable", f"{self.service_name.lower()}.service"]
        else:
            service_file = Path(self.service_file)
            reload_cmd = ["sudo", "systemctl", "daemon-reload"]
            enable_cmd = ["sudo", "systemctl", "enable", f"{self.service_name.lower()}.service"]

        try:
            # Write service file
            if user_level:
                service_file.write_text(service_content)
            else:
                # Need sudo to write to /etc/systemd/system/
                with open("/tmp/plumber_agent.service", "w") as f:
                    f.write(service_content)
                if not self._run_command(["sudo", "mv", "/tmp/plumber_agent.service", str(service_file)]):
                    return False

            # Reload systemd and enable service
            if not self._run_command(reload_cmd):
                return False
            if not self._run_command(enable_cmd):
                return False

            print(f"✅ systemd service installed successfully")
            print(f"   Service file: {service_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to install systemd service: {e}")
            return False

    def _uninstall_systemd_service(self):
        """Uninstall systemd service."""
        # Try user service first
        user_file = self.user_service_file
        system_file = Path(self.service_file)

        removed = False
        if user_file.exists():
            self._run_command(["systemctl", "--user", "disable", f"{self.service_name.lower()}.service"])
            user_file.unlink()
            self._run_command(["systemctl", "--user", "daemon-reload"])
            removed = True

        if system_file.exists():
            self._run_command(["sudo", "systemctl", "disable", f"{self.service_name.lower()}.service"])
            self._run_command(["sudo", "rm", str(system_file)])
            self._run_command(["sudo", "systemctl", "daemon-reload"])
            removed = True

        if removed:
            print(f"✅ systemd service uninstalled successfully")
        return removed

    # macOS-specific methods

    def _install_launchd_service(self):
        """Install launchd service on macOS."""
        if not self.agent_executable.exists():
            print(f"❌ Agent executable not found at {self.agent_executable}")
            return False

        # Create plist content
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.plumber.{self.service_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{self.agent_executable}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{self.install_dir}</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{self.install_dir}/agent_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{self.install_dir}/agent_stderr.log</string>
</dict>
</plist>
"""

        try:
            # Create LaunchAgents directory if it doesn't exist
            self.plist_file.parent.mkdir(parents=True, exist_ok=True)

            # Write plist file
            self.plist_file.write_text(plist_content)

            # Load service
            if self._run_command(["launchctl", "load", str(self.plist_file)]):
                print(f"✅ launchd service installed successfully")
                print(f"   Plist file: {self.plist_file}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to install launchd service: {e}")
            return False

    def _uninstall_launchd_service(self):
        """Uninstall launchd service."""
        if self.plist_file.exists():
            self._run_command(["launchctl", "unload", str(self.plist_file)])
            self.plist_file.unlink()
            print(f"✅ launchd service uninstalled successfully")
            return True
        return False

    # Helper methods

    def _run_command(self, cmd, capture=False):
        """
        Run shell command with error handling.

        Args:
            cmd: Command list to execute
            capture: If True, return CompletedProcess object instead of bool

        Returns:
            bool or CompletedProcess
        """
        try:
            if capture:
                result = subprocess.run(cmd, capture_output=True)
                return result
            else:
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    return True
                else:
                    error = result.stderr.decode().strip()
                    if error:
                        print(f"   Error: {error}")
                    return False
        except Exception as e:
            print(f"   Exception: {e}")
            return False if not capture else None


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Plumber Local DCC Agent - Service Installer")
    parser.add_argument("action", choices=["install", "uninstall", "start", "stop", "restart", "status"],
                        help="Action to perform")
    parser.add_argument("--user", action="store_true",
                        help="Install as user-level service (no admin required)")

    args = parser.parse_args()

    installer = ServiceInstaller()

    if args.action == "install":
        success = installer.install(user_level=args.user)
    elif args.action == "uninstall":
        success = installer.uninstall()
    elif args.action == "start":
        success = installer.start()
    elif args.action == "stop":
        success = installer.stop()
    elif args.action == "restart":
        success = installer.restart()
    elif args.action == "status":
        success = installer.status()
    else:
        print(f"❌ Unknown action: {args.action}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
