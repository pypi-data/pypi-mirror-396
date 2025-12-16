"""
Plumber Local DCC Agent - System Tray Application

Provides user-friendly control over the Plumber agent without command line.

Features:
- Visual status indicator (green/yellow/red icon)
- Start/Stop/Restart agent
- View agent status (uptime, DCCs, memory)
- Open web dashboard
- View logs
- Auto-start configuration
- Graceful shutdown

Dependencies:
    pip install pystray pillow psutil

Usage:
    python system_tray.py
    # Or as bundled .exe:
    plumber_tray.exe
"""

import os
import sys
import time
import subprocess
import webbrowser
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Missing dependencies. Install with: pip install pystray pillow psutil")
    sys.exit(1)


class PlumberAgentTray:
    """System tray application for Plumber Local DCC Agent."""

    def __init__(self):
        """Initialize system tray application."""
        # Determine base path (different when bundled with PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running as bundled .exe
            self.base_path = Path(sys._MEIPASS)
            self.install_path = Path(sys.executable).parent
        else:
            # Running as script
            self.base_path = Path(__file__).parent.parent
            self.install_path = self.base_path

        # Agent executable paths
        self.agent_exe = self.install_path / "plumber_agent.exe"
        self.agent_script = self.install_path / "src" / "main.py"

        # Configuration
        self.agent_process = None
        self.agent_start_time = None
        self.check_interval = 5  # seconds
        self.icon = None
        self.monitoring_thread = None
        self.running = True

        # Dashboard URL
        self.dashboard_url = "https://app.plumber.damnltd.com"

    def create_icon_image(self, color):
        """
        Create a simple colored circle icon for system tray.

        Args:
            color: RGB tuple (r, g, b) for icon color

        Returns:
            PIL Image object
        """
        # Create 64x64 image with transparency
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw circle
        draw.ellipse([8, 8, 56, 56], fill=color, outline=(255, 255, 255, 255), width=2)

        # Draw "P" in center (for Plumber)
        # This is simplified - ideally load actual .ico files
        draw.text((20, 15), "P", fill=(255, 255, 255, 255))

        return img

    def get_icon_image(self):
        """Get current icon based on agent status."""
        if self.is_agent_running():
            # Green - Agent running
            return self.create_icon_image((34, 197, 94))  # green-500
        elif self.agent_process and not self.is_agent_running():
            # Yellow - Agent starting/stopping
            return self.create_icon_image((234, 179, 8))  # yellow-500
        else:
            # Red - Agent stopped
            return self.create_icon_image((239, 68, 68))  # red-500

    def is_agent_running(self):
        """
        Check if agent process is running.

        Returns:
            bool: True if agent is running, False otherwise
        """
        # Check if we have a process handle
        if self.agent_process and self.agent_process.poll() is None:
            return True

        # Check if any plumber_agent.exe is running
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] in ['plumber_agent.exe', 'python.exe', 'pythonw.exe']:
                    # Check command line to verify it's our agent
                    if self.agent_exe.exists():
                        if str(self.agent_exe) in ' '.join(proc.cmdline()):
                            return True
                    elif 'main.py' in ' '.join(proc.cmdline()):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    def get_agent_pid(self):
        """Get PID of running agent process."""
        for proc in psutil.process_iter(['name', 'exe', 'pid']):
            try:
                if proc.info['name'] in ['plumber_agent.exe', 'python.exe', 'pythonw.exe']:
                    if self.agent_exe.exists():
                        if str(self.agent_exe) in ' '.join(proc.cmdline()):
                            return proc.info['pid']
                    elif 'main.py' in ' '.join(proc.cmdline()):
                        return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None

    def start_agent(self, icon=None, item=None):
        """Start the Plumber agent."""
        if self.is_agent_running():
            self.show_notification("Agent Already Running", "The Plumber agent is already running.")
            return

        try:
            # Try to start bundled .exe first
            if self.agent_exe.exists():
                # Start agent as subprocess without console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

                self.agent_process = subprocess.Popen(
                    [str(self.agent_exe)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            elif self.agent_script.exists():
                # Fallback to Python script
                self.agent_process = subprocess.Popen(
                    [sys.executable, str(self.agent_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.show_notification("Error", "Agent executable not found!")
                return

            self.agent_start_time = datetime.now()
            self.show_notification("Agent Starting", "Plumber agent is starting...")
            self.update_icon()

            # Wait a moment and verify agent started
            time.sleep(2)
            if self.is_agent_running():
                self.show_notification("Agent Started", "Plumber agent is now running.")
            else:
                self.show_notification("Error", "Agent failed to start. Check logs for details.")

        except Exception as e:
            self.show_notification("Error", f"Failed to start agent: {str(e)}")

    def stop_agent(self, icon=None, item=None):
        """Stop the Plumber agent gracefully."""
        if not self.is_agent_running():
            self.show_notification("Agent Not Running", "The agent is not currently running.")
            return

        try:
            pid = self.get_agent_pid()
            if pid:
                # Try graceful shutdown first
                proc = psutil.Process(pid)
                proc.terminate()

                # Wait up to 10 seconds for graceful shutdown
                try:
                    proc.wait(timeout=10)
                    self.show_notification("Agent Stopped", "Plumber agent has been stopped.")
                except psutil.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    proc.kill()
                    self.show_notification("Agent Stopped", "Agent was forcefully terminated.")

                self.agent_process = None
                self.agent_start_time = None
                self.update_icon()
            else:
                self.show_notification("Error", "Could not find agent process.")

        except Exception as e:
            self.show_notification("Error", f"Failed to stop agent: {str(e)}")

    def restart_agent(self, icon=None, item=None):
        """Restart the agent."""
        self.show_notification("Restarting Agent", "Stopping agent...")
        self.stop_agent()
        time.sleep(2)
        self.show_notification("Restarting Agent", "Starting agent...")
        self.start_agent()

    def show_status(self, icon=None, item=None):
        """Show detailed agent status."""
        if not self.is_agent_running():
            self.show_notification("Agent Status", "Agent is not running.")
            return

        try:
            pid = self.get_agent_pid()
            if not pid:
                return

            proc = psutil.Process(pid)

            # Calculate uptime
            if self.agent_start_time:
                uptime = datetime.now() - self.agent_start_time
                uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            else:
                uptime_str = "Unknown"

            # Get memory usage
            memory_mb = proc.memory_info().rss / 1024 / 1024

            # Get CPU usage (average over 1 second)
            cpu_percent = proc.cpu_percent(interval=1.0)

            status_msg = (
                f"Status: Running\n"
                f"PID: {pid}\n"
                f"Uptime: {uptime_str}\n"
                f"Memory: {memory_mb:.1f} MB\n"
                f"CPU: {cpu_percent:.1f}%"
            )

            self.show_notification("Agent Status", status_msg)

        except Exception as e:
            self.show_notification("Error", f"Failed to get status: {str(e)}")

    def open_dashboard(self, icon=None, item=None):
        """Open Plumber web dashboard in browser."""
        try:
            webbrowser.open(self.dashboard_url)
        except Exception as e:
            self.show_notification("Error", f"Failed to open dashboard: {str(e)}")

    def open_logs(self, icon=None, item=None):
        """Open agent log file."""
        log_file = self.install_path / "agent_logs.txt"
        if log_file.exists():
            try:
                # Open with default text editor
                os.startfile(str(log_file))
            except Exception as e:
                self.show_notification("Error", f"Failed to open logs: {str(e)}")
        else:
            self.show_notification("No Logs", "Log file not found.")

    def show_about(self, icon=None, item=None):
        """Show about information."""
        about_msg = (
            "Plumber Local DCC Agent\n"
            "Version 1.0.0\n\n"
            "Connects local DCC applications\n"
            "(Maya, Blender, Houdini) to\n"
            "the Plumber cloud platform.\n\n"
            "© 2025 DamnVFX"
        )
        self.show_notification("About Plumber Agent", about_msg)

    def exit_tray(self, icon=None, item=None):
        """Exit system tray application (agent keeps running)."""
        self.running = False
        if icon:
            icon.stop()

    def show_notification(self, title, message):
        """
        Show system tray notification.

        Args:
            title: Notification title
            message: Notification message
        """
        if self.icon:
            self.icon.notify(title=title, message=message)

    def update_icon(self):
        """Update system tray icon based on current status."""
        if self.icon:
            self.icon.icon = self.get_icon_image()

    def monitor_agent(self):
        """Background thread to monitor agent status and update icon."""
        while self.running:
            try:
                # Update icon based on current status
                self.update_icon()

                # Check if agent crashed and restart if needed
                if self.agent_start_time and not self.is_agent_running():
                    # Agent was running but is now stopped - may have crashed
                    self.show_notification(
                        "Agent Stopped",
                        "Agent has stopped unexpectedly. Click to restart."
                    )
                    self.agent_start_time = None

                time.sleep(self.check_interval)

            except Exception as e:
                print(f"Monitor thread error: {e}")
                time.sleep(self.check_interval)

    def create_menu(self):
        """Create system tray menu."""
        return pystray.Menu(
            pystray.MenuItem("Start Agent", self.start_agent, enabled=lambda item: not self.is_agent_running()),
            pystray.MenuItem("Stop Agent", self.stop_agent, enabled=lambda item: self.is_agent_running()),
            pystray.MenuItem("Restart Agent", self.restart_agent, enabled=lambda item: self.is_agent_running()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Agent Status", self.show_status),
            pystray.MenuItem("Open Dashboard", self.open_dashboard),
            pystray.MenuItem("View Logs", self.open_logs),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("About", self.show_about),
            pystray.MenuItem("Exit", self.exit_tray)
        )

    def run(self):
        """Run the system tray application."""
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitor_agent, daemon=True)
        self.monitoring_thread.start()

        # Check if agent is already running, if not start it
        if not self.is_agent_running():
            print("Agent not running, starting...")
            self.start_agent()

        # Create and run system tray icon
        self.icon = pystray.Icon(
            name="Plumber Agent",
            icon=self.get_icon_image(),
            title="Plumber Local DCC Agent",
            menu=self.create_menu()
        )

        print("System tray started. Right-click icon for menu.")
        self.icon.run()


def main():
    """Main entry point."""
    print("Plumber Local DCC Agent - System Tray")
    print("=" * 50)

    # Create and run tray application
    tray = PlumberAgentTray()
    try:
        tray.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        tray.running = False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
