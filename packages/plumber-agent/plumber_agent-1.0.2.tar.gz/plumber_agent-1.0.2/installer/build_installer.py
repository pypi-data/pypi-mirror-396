#!/usr/bin/env python3
"""
Plumber Local DCC Agent - Cross-Platform Installer Builder
Detects platform and builds appropriate installer package.

Supports:
- Windows: Inno Setup (.exe installer)
- Linux: Debian package (.deb)
- macOS: Package (.pkg)

Usage:
    python build_installer.py
    python build_installer.py --platform windows
    python build_installer.py --platform linux
    python build_installer.py --platform macos
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path


class InstallerBuilder:
    """Cross-platform installer builder."""

    def __init__(self, target_platform=None):
        self.current_platform = platform.system()
        self.target_platform = target_platform or self.current_platform

        self.installer_dir = Path(__file__).parent
        self.agent_dir = self.installer_dir.parent
        self.dist_dir = self.installer_dir / "dist"
        self.output_dir = self.installer_dir / "output"

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

    def build_pyinstaller_executable(self):
        """Build standalone executable with PyInstaller."""
        print("🔧 Building PyInstaller executable...")

        # Check if dist already exists
        if (self.dist_dir / "plumber_agent.exe").exists() or \
           (self.dist_dir / "plumber_agent").exists():
            print("✅ PyInstaller executable already exists. Skipping build.")
            return True

        # Check virtual environment
        venv_dir = self.agent_dir / "venv"
        if not venv_dir.exists():
            print("❌ Virtual environment not found!")
            print("Please create venv and install dependencies:")
            print("  python -m venv venv")
            if self.current_platform == "Windows":
                print("  venv\\Scripts\\activate")
            else:
                print("  source venv/bin/activate")
            print("  pip install -r requirements.txt")
            print("  pip install pyinstaller")
            return False

        # Activate venv and build
        if self.current_platform == "Windows":
            python_exe = venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = venv_dir / "bin" / "python"

        if not python_exe.exists():
            print(f"❌ Python executable not found: {python_exe}")
            return False

        # PyInstaller command
        cmd = [
            str(python_exe), "-m", "PyInstaller",
            "--onefile",
            "--name", "plumber_agent",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.installer_dir / "build_pyinstaller"),
            "--specpath", str(self.installer_dir),
            str(self.agent_dir / "src" / "main.py")
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=str(self.agent_dir))

        if result.returncode != 0:
            print("❌ PyInstaller build failed!")
            return False

        print("✅ PyInstaller build complete.")
        return True

    def build_windows_installer(self):
        """Build Windows Inno Setup installer."""
        print("\n🪟 Building Windows installer with Inno Setup...")

        # Check if Inno Setup is installed
        inno_paths = [
            Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
            Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        ]

        iscc_exe = None
        for path in inno_paths:
            if path.exists():
                iscc_exe = path
                break

        if not iscc_exe:
            print("❌ Inno Setup not found!")
            print("Please install Inno Setup 6 from: https://jrsoftware.org/isinfo.php")
            print("Or manually run: iscc installer/setup.iss")
            return False

        # Run Inno Setup compiler
        setup_script = self.installer_dir / "setup.iss"
        cmd = [str(iscc_exe), str(setup_script)]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print("❌ Inno Setup build failed!")
            return False

        print("✅ Windows installer built successfully!")
        print(f"Output: {self.output_dir / 'PlumberAgentSetup.exe'}")
        return True

    def build_linux_deb(self):
        """Build Linux .deb package."""
        print("\n🐧 Building Linux .deb package...")

        build_script = self.installer_dir / "linux" / "build_deb.sh"

        if not build_script.exists():
            print(f"❌ Build script not found: {build_script}")
            return False

        # Make script executable
        build_script.chmod(0o755)

        # Run build script
        cmd = ["bash", str(build_script)]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print("❌ Debian package build failed!")
            return False

        print("✅ Linux .deb package built successfully!")
        return True

    def build_macos_pkg(self):
        """Build macOS .pkg installer."""
        print("\n🍎 Building macOS .pkg installer...")

        build_script = self.installer_dir / "macos" / "build_pkg.sh"

        if not build_script.exists():
            print(f"❌ Build script not found: {build_script}")
            return False

        # Make script executable
        build_script.chmod(0o755)

        # Run build script
        cmd = ["bash", str(build_script)]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print("❌ macOS package build failed!")
            return False

        print("✅ macOS .pkg installer built successfully!")
        return True

    def build(self):
        """Build installer for target platform."""
        print(f"🚀 Building installer for {self.target_platform}...")
        print(f"Current platform: {self.current_platform}")
        print()

        # Build PyInstaller executable first
        if not self.build_pyinstaller_executable():
            return False

        # Build platform-specific installer
        if self.target_platform == "Windows":
            return self.build_windows_installer()
        elif self.target_platform == "Linux":
            return self.build_linux_deb()
        elif self.target_platform == "Darwin":
            return self.build_macos_pkg()
        else:
            print(f"❌ Unsupported platform: {self.target_platform}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build Plumber Local DCC Agent installer for target platform"
    )
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos"],
        help="Target platform (default: current platform)"
    )

    args = parser.parse_args()

    # Map platform names
    platform_map = {
        "windows": "Windows",
        "linux": "Linux",
        "macos": "Darwin"
    }

    target = platform_map.get(args.platform) if args.platform else None

    # Build installer
    builder = InstallerBuilder(target_platform=target)
    success = builder.build()

    if success:
        print("\n✅ Installer build complete!")
        print(f"Output directory: {builder.output_dir}")
        sys.exit(0)
    else:
        print("\n❌ Installer build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
