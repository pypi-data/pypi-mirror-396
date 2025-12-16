"""
DCC Installation Discovery System
Automatically detects Maya, Blender, and Houdini installations on Windows systems.
Enhanced with multi-drive search and registry detection.
"""

import os
import platform
import subprocess
import json
import string
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Windows-specific imports (conditional)
if platform.system() == 'Windows':
    import winreg
else:
    winreg = None  # Not available on Linux/macOS

logger = logging.getLogger(__name__)

class DCCDiscovery:
    """Discovers and validates DCC application installations."""

    def __init__(self):
        self.system = platform.system()
        self.discovered_dccs = {}
        self.available_drives = self._get_available_drives()

    def _get_available_drives(self) -> List[str]:
        """Get all available drives on Windows system."""
        if self.system != 'Windows':
            return []

        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
                logger.debug(f"Found drive: {drive}")

        return drives

    def _search_registry_for_app(self, app_name: str, registry_paths: List[str]) -> List[str]:
        """Search Windows Registry for application installation paths."""
        found_paths = []

        if self.system != 'Windows':
            return found_paths

        for registry_path in registry_paths:
            try:
                # Check both HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER
                for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                    try:
                        with winreg.OpenKey(hkey, registry_path) as key:
                            # Get InstallLocation or similar
                            for value_name in ['InstallLocation', 'InstallDir', 'Path', 'InstallPath']:
                                try:
                                    install_path, _ = winreg.QueryValueEx(key, value_name)
                                    if install_path and os.path.exists(install_path):
                                        found_paths.append(install_path)
                                        logger.info(f"Found {app_name} in registry: {install_path}")
                                except FileNotFoundError:
                                    continue
                    except FileNotFoundError:
                        continue
            except Exception as e:
                logger.debug(f"Registry search error for {app_name}: {e}")

        return found_paths

    def _search_all_drives_for_app(self, app_folder_patterns: List[str]) -> List[str]:
        """Search all available drives for application folders."""
        found_paths = []

        for drive in self.available_drives:
            logger.debug(f"Searching drive {drive} for DCC installations...")

            # Common installation root directories
            search_roots = [
                os.path.join(drive, "Program Files"),
                os.path.join(drive, "Program Files (x86)"),
                drive  # Root of drive for portable installations
            ]

            for root in search_roots:
                if not os.path.exists(root):
                    continue

                try:
                    for item in os.listdir(root):
                        for pattern in app_folder_patterns:
                            if pattern.lower() in item.lower():
                                full_path = os.path.join(root, item)
                                if os.path.isdir(full_path):
                                    found_paths.append(full_path)
                                    logger.debug(f"Found potential installation: {full_path}")
                except (PermissionError, OSError) as e:
                    logger.debug(f"Cannot access {root}: {e}")

        return found_paths

    def _get_linux_search_paths(self) -> List[str]:
        """Get standard Linux paths for DCC application search."""
        return [
            '/usr/bin',
            '/usr/local/bin',
            '/opt',
            '/snap',  # Snap package installations (e.g., /snap/blender/current/)
            '/snap/bin',  # Snap binary symlinks
            '/usr/share/applications',
            f"{Path.home()}/Applications",
            f"{Path.home()}/.local/bin",
            f"{Path.home()}/.local/share/applications",
            '/usr/autodesk',
            '/usr/local/autodesk',
            f"{Path.home()}/autodesk"
        ]

    def _search_linux_for_app(self, app_patterns: List[str], executable_names: List[str]) -> List[Dict[str, str]]:
        """Search Linux standard paths for DCC applications."""
        if self.system != 'Linux':
            return []

        installations = []
        search_paths = self._get_linux_search_paths()

        logger.debug(f"[Linux Search] Patterns: {app_patterns}, Executables: {executable_names}")
        logger.debug(f"[Linux Search] Search paths: {search_paths}")

        for base_path in search_paths:
            if not os.path.exists(base_path):
                logger.debug(f"[Linux Search] Path does not exist: {base_path}")
                continue

            logger.debug(f"[Linux Search] Searching in: {base_path}")
            try:
                # Direct executable search
                for exe_name in executable_names:
                    exe_path = os.path.join(base_path, exe_name)
                    if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
                        installations.append({
                            'path': os.path.dirname(exe_path),
                            'executable': exe_path,
                            'source': 'linux_standard'
                        })

                # Directory pattern search
                if os.path.isdir(base_path):
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path):
                            for pattern in app_patterns:
                                if pattern.lower() in item.lower():
                                    logger.debug(f"[Linux Search] Pattern '{pattern}' matched directory: {item_path}")
                                    # Look for executables in this directory
                                    for exe_name in executable_names:
                                        exe_path = os.path.join(item_path, exe_name)
                                        if os.path.exists(exe_path) and os.access(exe_path, os.X_OK):
                                            installations.append({
                                                'path': item_path,
                                                'executable': exe_path,
                                                'source': 'linux_pattern'
                                            })
                                        # Also check bin subdirectory
                                        bin_exe_path = os.path.join(item_path, 'bin', exe_name)
                                        if os.path.exists(bin_exe_path) and os.access(bin_exe_path, os.X_OK):
                                            installations.append({
                                                'path': item_path,
                                                'executable': bin_exe_path,
                                                'source': 'linux_pattern_bin'
                                            })

                                        # Check Snap-specific structure: /snap/app/current/executable
                                        if base_path == '/snap':
                                            snap_current_exe = os.path.join(item_path, 'current', exe_name)
                                            logger.debug(f"[Linux Search] Checking Snap path: {snap_current_exe}")
                                            if os.path.exists(snap_current_exe):
                                                logger.debug(f"[Linux Search] Snap executable exists: {snap_current_exe}")
                                                if os.access(snap_current_exe, os.X_OK):
                                                    logger.debug(f"[Linux Search] Snap executable is executable: {snap_current_exe}")
                                                    installations.append({
                                                        'path': item_path,
                                                        'executable': snap_current_exe,
                                                        'source': 'snap'
                                                    })
                                                else:
                                                    logger.debug(f"[Linux Search] Snap executable not executable: {snap_current_exe}")
                                            else:
                                                logger.debug(f"[Linux Search] Snap path does not exist: {snap_current_exe}")

            except (PermissionError, OSError):
                continue

        return installations

    def _get_macos_search_paths(self) -> List[str]:
        """Get standard macOS paths for DCC application search."""
        return [
            '/Applications',
            f"{Path.home()}/Applications",
            '/usr/local/bin',
            '/opt',
            '/opt/homebrew/bin',
            '/usr/local/Cellar',
            f"{Path.home()}/Library/Application Support"
        ]

    def _search_macos_for_app(self, app_patterns: List[str], app_bundle_names: List[str]) -> List[Dict[str, str]]:
        """Search macOS standard paths for DCC applications."""
        if self.system != 'Darwin':
            return []

        installations = []
        search_paths = self._get_macos_search_paths()

        for base_path in search_paths:
            if not os.path.exists(base_path):
                continue

            try:
                if os.path.isdir(base_path):
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)

                        # Check for .app bundles
                        if item.endswith('.app'):
                            for bundle_name in app_bundle_names:
                                if bundle_name.lower() in item.lower():
                                    # Look for executable inside bundle
                                    contents_path = os.path.join(item_path, 'Contents', 'MacOS')
                                    if os.path.exists(contents_path):
                                        for exe_item in os.listdir(contents_path):
                                            exe_path = os.path.join(contents_path, exe_item)
                                            if os.access(exe_path, os.X_OK):
                                                installations.append({
                                                    'path': item_path,
                                                    'executable': exe_path,
                                                    'source': 'macos_bundle'
                                                })
                                                break

                        # Check for directory pattern matches
                        elif os.path.isdir(item_path):
                            for pattern in app_patterns:
                                if pattern.lower() in item.lower():
                                    # Look for bin subdirectory
                                    bin_path = os.path.join(item_path, 'bin')
                                    if os.path.exists(bin_path):
                                        for bin_item in os.listdir(bin_path):
                                            if any(pattern.lower() in bin_item.lower() for pattern in app_patterns):
                                                exe_path = os.path.join(bin_path, bin_item)
                                                if os.access(exe_path, os.X_OK):
                                                    installations.append({
                                                        'path': item_path,
                                                        'executable': exe_path,
                                                        'source': 'macos_pattern'
                                                    })

            except (PermissionError, OSError):
                continue

        return installations

    def _parse_version_from_path(self, path: str, app_name: str) -> Optional[str]:
        """Extract version number from installation path."""
        try:
            # Common version patterns
            import re

            # Look for version patterns in the path
            version_patterns = [
                r'(\d{4})',  # Year-based versions like 2026, 2024
                r'(\d+\.\d+\.\d+)',  # Semantic versions like 4.4.0
                r'(\d+\.\d+)',  # Major.minor versions like 4.4
                r'(\d+)',  # Single digit versions
            ]

            path_lower = path.lower()

            for pattern in version_patterns:
                matches = re.findall(pattern, path)
                if matches:
                    # Return the last match (usually the most specific version)
                    version = matches[-1]
                    logger.debug(f"Extracted version '{version}' from path: {path}")
                    return version

            # Fallback: try to extract from folder name
            folder_name = os.path.basename(path)
            for pattern in version_patterns:
                matches = re.findall(pattern, folder_name)
                if matches:
                    return matches[-1]

        except Exception as e:
            logger.debug(f"Version parsing error for {path}: {e}")

        return "Unknown"

    def _sort_versions(self, versions: List[Dict]) -> List[Dict]:
        """Sort versions by preference (newest first)."""
        def version_sort_key(version_info):
            try:
                version = version_info.get('version', '0')

                # Handle year-based versions (Maya)
                if version.isdigit() and len(version) == 4:
                    return (int(version), 0, 0)

                # Handle semantic versions (Blender, Houdini)
                if '.' in version:
                    parts = version.split('.')
                    major = int(parts[0]) if parts[0].isdigit() else 0
                    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                    return (major, minor, patch)

                # Handle single number versions
                if version.isdigit():
                    return (int(version), 0, 0)

                return (0, 0, 0)  # Unknown versions go last

            except (ValueError, TypeError):
                return (0, 0, 0)

        return sorted(versions, key=version_sort_key, reverse=True)

    def discover_all(self) -> Dict[str, Dict]:
        """Discover all available DCC applications."""
        logger.info("Starting DCC discovery process...")

        self.discovered_dccs = {
            'maya': self.discover_maya(),
            'blender': self.discover_blender(),
            'houdini': self.discover_houdini(),
            'nuke': self.discover_nuke(),
            'natron': self.discover_natron(),
            'vectorworks': self.discover_vectorworks()
        }

        # Log discovery results
        for dcc_name, dcc_info in self.discovered_dccs.items():
            if dcc_info['available']:
                logger.info(f"✅ {dcc_name.title()} found: {dcc_info['version']} at {dcc_info['executable']}")
            else:
                logger.warning(f"❌ {dcc_name.title()} not found")

        return self.discovered_dccs

    def discover_maya(self) -> Dict:
        """Discover Maya installations using enhanced multi-drive search."""
        maya_info = {
            'available': False,
            'version': None,
            'executable': None,
            'python_executable': None,
            'installation_path': None,
            'versions_found': []
        }

        try:
            logger.info("Starting enhanced Maya discovery...")
            maya_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Step 1: Search Windows Registry for official installations
                registry_paths = [
                    r"SOFTWARE\Autodesk\Maya",
                    r"SOFTWARE\Classes\Applications\maya.exe",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Autodesk Maya"
                ]

                registry_installations = self._search_registry_for_app("Maya", registry_paths)
                for reg_path in registry_installations:
                    maya_exe = os.path.join(reg_path, 'bin', 'maya.exe')
                    mayapy_exe = os.path.join(reg_path, 'bin', 'mayapy.exe')
                    if os.path.exists(maya_exe) and os.path.exists(mayapy_exe):
                        version = self._parse_version_from_path(reg_path, 'Maya')
                        if version:
                            maya_versions.append({
                                'version': version,
                                'path': reg_path,
                                'executable': maya_exe,
                                'python_executable': mayapy_exe,
                                'source': 'registry'
                            })

                # Step 2: Multi-drive search for all Maya installations
                folder_patterns = ['Autodesk', 'Maya']
                drive_installations = self._search_all_drives_for_app(folder_patterns)

            elif self.system == 'Linux':
                # Linux-specific discovery
                app_patterns = ['maya', 'Maya', 'autodesk']
                executable_names = ['maya', 'mayapy']
                drive_installations = self._search_linux_for_app(app_patterns, executable_names)
                # Process Linux installations
                for install in drive_installations:
                    if 'maya' in install['executable'].lower():
                        # Find corresponding mayapy
                        maya_exe = install['executable']
                        mayapy_exe = maya_exe.replace('maya', 'mayapy') if 'mayapy' not in maya_exe else maya_exe
                        if maya_exe != mayapy_exe or 'mayapy' in maya_exe:
                            # Try to find version
                            version = self._parse_version_from_path(install['path'], 'Maya')
                            if not version:
                                version = self._get_maya_version_linux(maya_exe)
                            if version:
                                maya_versions.append({
                                    'version': version,
                                    'path': install['path'],
                                    'executable': maya_exe,
                                    'python_executable': mayapy_exe,
                                    'source': install['source']
                                })
                drive_installations = []

            elif self.system == 'Darwin':  # macOS
                # macOS-specific discovery
                app_patterns = ['maya', 'Maya', 'Autodesk']
                bundle_names = ['Maya', 'Autodesk Maya']
                drive_installations = self._search_macos_for_app(app_patterns, bundle_names)
                # Process macOS installations
                for install in drive_installations:
                    maya_exe = install['executable']
                    # Look for mayapy in the same directory
                    mayapy_exe = os.path.join(os.path.dirname(maya_exe), 'mayapy')
                    if not os.path.exists(mayapy_exe):
                        # Try alternative paths
                        mayapy_exe = maya_exe.replace('maya', 'mayapy')
                    if os.path.exists(mayapy_exe):
                        version = self._parse_version_from_path(install['path'], 'Maya')
                        if not version:
                            version = self._get_maya_version_macos(maya_exe)
                        if version:
                            maya_versions.append({
                                'version': version,
                                'path': install['path'],
                                'executable': maya_exe,
                                'python_executable': mayapy_exe,
                                'source': install['source']
                            })
                drive_installations = []

            else:
                drive_installations = []

            for maya_path in drive_installations:
                # Check if this is an Autodesk folder or direct Maya installation
                if 'Autodesk' in maya_path and 'Maya' not in os.path.basename(maya_path):
                    # Look inside Autodesk folder for Maya installations
                    if os.path.exists(maya_path):
                        try:
                            for item in os.listdir(maya_path):
                                if item.startswith('Maya'):
                                    version_path = os.path.join(maya_path, item)
                                    if os.path.isdir(version_path):
                                        maya_exe = os.path.join(version_path, 'bin', 'maya.exe')
                                        mayapy_exe = os.path.join(version_path, 'bin', 'mayapy.exe')
                                        if os.path.exists(maya_exe) and os.path.exists(mayapy_exe):
                                            version = self._parse_version_from_path(version_path, 'Maya')
                                            if version:
                                                maya_versions.append({
                                                    'version': version,
                                                    'path': version_path,
                                                    'executable': maya_exe,
                                                    'python_executable': mayapy_exe,
                                                    'source': 'filesystem'
                                                })
                        except (PermissionError, OSError):
                            continue
                elif 'Maya' in maya_path:
                    # Direct Maya installation folder
                    maya_exe = os.path.join(maya_path, 'bin', 'maya.exe')
                    mayapy_exe = os.path.join(maya_path, 'bin', 'mayapy.exe')
                    if os.path.exists(maya_exe) and os.path.exists(mayapy_exe):
                        version = self._parse_version_from_path(maya_path, 'Maya')
                        if version:
                            maya_versions.append({
                                'version': version,
                                'path': maya_path,
                                'executable': maya_exe,
                                'python_executable': mayapy_exe,
                                'source': 'filesystem'
                            })

            # Step 3: Remove duplicates based on installation path and sort by version
            unique_versions = {}
            for version_info in maya_versions:
                key = version_info['path']
                if key not in unique_versions:
                    unique_versions[key] = version_info

            maya_versions = list(unique_versions.values())
            maya_versions = self._sort_versions(maya_versions)
            maya_info['versions_found'] = maya_versions

            logger.info(f"Found {len(maya_versions)} Maya installations:")
            for version_info in maya_versions:
                logger.info(f"  ✅ Maya {version_info['version']} at {version_info['path']} (via {version_info.get('source', 'unknown')})")

            if maya_versions:
                # Use the newest version as default
                latest = maya_versions[0]
                maya_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'python_executable': latest['python_executable'],
                    'installation_path': latest['path']
                })

                # Validate executable works
                if self._validate_maya_executable(latest['python_executable']):
                    logger.info(f"Maya {latest['version']} validated successfully")
                else:
                    logger.warning(f"Maya {latest['version']} found but failed validation")

        except Exception as e:
            logger.error(f"Error discovering Maya: {e}")

        return maya_info

    def discover_blender(self) -> Dict:
        """Discover Blender installations using enhanced multi-drive search."""
        blender_info = {
            'available': False,
            'version': None,
            'executable': None,
            'installation_path': None,
            'versions_found': []
        }

        try:
            logger.info("Starting enhanced Blender discovery...")
            blender_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Step 1: Search Windows Registry for official installations
                registry_paths = [
                    r"SOFTWARE\Blender Foundation\Blender",
                    r"SOFTWARE\Classes\blendfile\shell\open\command",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Blender"
                ]

                registry_installations = self._search_registry_for_app("Blender", registry_paths)
                for reg_path in registry_installations:
                    blender_exe = os.path.join(reg_path, 'blender.exe')
                    if os.path.exists(blender_exe):
                        version = self._get_blender_version(blender_exe)
                        if version:
                            blender_versions.append({
                                'version': version,
                                'path': reg_path,
                                'executable': blender_exe,
                                'source': 'registry'
                            })

                # Step 2: Multi-drive search for all Blender installations
                folder_patterns = ['Blender Foundation', 'Blender']
                drive_installations = self._search_all_drives_for_app(folder_patterns)

            elif self.system == 'Linux':
                # Linux-specific discovery
                app_patterns = ['blender', 'Blender']
                executable_names = ['blender']
                drive_installations = self._search_linux_for_app(app_patterns, executable_names)
                # Convert format to match Windows structure
                for install in drive_installations:
                    version = self._get_blender_version(install['executable'])
                    if version:
                        blender_versions.append({
                            'version': version,
                            'path': install['path'],
                            'executable': install['executable'],
                            'source': install['source']
                        })
                drive_installations = []  # Prevent duplicate processing below

            elif self.system == 'Darwin':  # macOS
                # macOS-specific discovery
                app_patterns = ['blender', 'Blender']
                bundle_names = ['Blender']
                drive_installations = self._search_macos_for_app(app_patterns, bundle_names)
                # Convert format to match Windows structure
                for install in drive_installations:
                    version = self._get_blender_version(install['executable'])
                    if version:
                        blender_versions.append({
                            'version': version,
                            'path': install['path'],
                            'executable': install['executable'],
                            'source': install['source']
                        })
                drive_installations = []  # Prevent duplicate processing below

            else:
                drive_installations = []

            for blender_path in drive_installations:
                # Check if this is a Blender Foundation folder or direct Blender installation
                if 'Blender Foundation' in blender_path:
                    # Look inside for Blender version folders
                    if os.path.exists(blender_path):
                        try:
                            for item in os.listdir(blender_path):
                                if item.startswith('Blender'):
                                    version_path = os.path.join(blender_path, item)
                                    if os.path.isdir(version_path):
                                        blender_exe = os.path.join(version_path, 'blender.exe')
                                        if os.path.exists(blender_exe):
                                            # ALWAYS use executable version for Blender (fixes OctaneBlender detection)
                                            version = self._get_blender_version(blender_exe)
                                            if not version:
                                                # Fallback to path parsing only if executable check fails
                                                version = self._parse_version_from_path(version_path, 'Blender')
                                            if version and version != "Unknown":
                                                blender_versions.append({
                                                    'version': version,
                                                    'path': version_path,
                                                    'executable': blender_exe,
                                                    'source': 'filesystem'
                                                })
                        except (PermissionError, OSError):
                            continue
                else:
                    # Direct Blender installation folder
                    blender_exe = os.path.join(blender_path, 'blender.exe')
                    if os.path.exists(blender_exe):
                        # ALWAYS use executable version for Blender (fixes OctaneBlender detection)
                        version = self._get_blender_version(blender_exe)
                        if not version:
                            # Fallback to path parsing only if executable check fails
                            version = self._parse_version_from_path(blender_path, 'Blender')
                        if version and version != "Unknown":
                            blender_versions.append({
                                'version': version,
                                'path': blender_path,
                                'executable': blender_exe,
                                'source': 'filesystem'
                            })

            # Step 3: Check PATH environment variable
            try:
                result = subprocess.run(['blender', '--version'],
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = self._parse_blender_version_output(result.stdout)
                    if version:
                        blender_versions.append({
                            'version': version,
                            'path': 'PATH',
                            'executable': 'blender',
                            'source': 'environment'
                        })
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            # Step 4: Remove duplicates based on executable path and sort by version
            unique_versions = {}
            for version_info in blender_versions:
                key = version_info['executable']
                if key not in unique_versions:
                    unique_versions[key] = version_info

            blender_versions = list(unique_versions.values())
            blender_versions = self._sort_versions(blender_versions)
            blender_info['versions_found'] = blender_versions

            logger.info(f"Found {len(blender_versions)} Blender installations:")
            for version_info in blender_versions:
                logger.info(f"  ✅ Blender {version_info['version']} at {version_info['path']} (via {version_info.get('source', 'unknown')})")

            if blender_versions:
                latest = blender_versions[0]
                blender_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'installation_path': latest['path']
                })

        except Exception as e:
            logger.error(f"Error discovering Blender: {e}")

        return blender_info

    def discover_houdini(self) -> Dict:
        """Discover Houdini installations using enhanced multi-drive search."""
        houdini_info = {
            'available': False,
            'version': None,
            'executable': None,
            'python_executable': None,
            'installation_path': None,
            'license_type': None,
            'versions_found': []
        }

        try:
            logger.info("Starting enhanced Houdini discovery...")
            houdini_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Step 1: Search Windows Registry for official installations
                registry_paths = [
                    r"SOFTWARE\Side Effects Software\Houdini",
                    r"SOFTWARE\Classes\Applications\houdini.exe",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Houdini"
                ]

                registry_installations = self._search_registry_for_app("Houdini", registry_paths)
                for reg_path in registry_installations:
                    houdini_exe = os.path.join(reg_path, 'bin', 'houdini.exe')
                    hython_exe = os.path.join(reg_path, 'bin', 'hython.exe')
                    if os.path.exists(houdini_exe) and os.path.exists(hython_exe):
                        version = self._parse_version_from_path(reg_path, 'Houdini')
                        license_type = self._detect_houdini_license(reg_path)
                        if version:
                            houdini_versions.append({
                                'version': version,
                                'path': reg_path,
                                'executable': houdini_exe,
                                'python_executable': hython_exe,
                                'license_type': license_type,
                                'source': 'registry'
                            })

                # Step 2: Multi-drive search for all Houdini installations
                folder_patterns = ['Side Effects Software', 'Houdini']
                drive_installations = self._search_all_drives_for_app(folder_patterns)

            elif self.system == 'Linux':
                # Linux-specific discovery
                app_patterns = ['houdini', 'Houdini', 'hfs']
                executable_names = ['houdini', 'hython']
                drive_installations = self._search_linux_for_app(app_patterns, executable_names)
                # Process Linux installations
                for install in drive_installations:
                    if 'houdini' in install['executable'].lower():
                        houdini_exe = install['executable']
                        # Find corresponding hython
                        hython_exe = os.path.join(os.path.dirname(houdini_exe), 'hython')
                        if not os.path.exists(hython_exe):
                            # Try alternative patterns
                            hython_exe = houdini_exe.replace('houdini', 'hython')
                        if os.path.exists(hython_exe):
                            version = self._parse_version_from_path(install['path'], 'Houdini')
                            if not version:
                                version = self._get_houdini_version_linux(houdini_exe)
                            license_type = self._detect_houdini_license_linux(install['path'])
                            if version:
                                houdini_versions.append({
                                    'version': version,
                                    'path': install['path'],
                                    'executable': houdini_exe,
                                    'python_executable': hython_exe,
                                    'license_type': license_type,
                                    'source': install['source']
                                })
                drive_installations = []

            elif self.system == 'Darwin':  # macOS
                # macOS-specific discovery
                app_patterns = ['houdini', 'Houdini']
                bundle_names = ['Houdini', 'Houdini Apprentice', 'Houdini Indie']
                drive_installations = self._search_macos_for_app(app_patterns, bundle_names)
                # Process macOS installations
                for install in drive_installations:
                    houdini_exe = install['executable']
                    # Look for hython in same directory or Frameworks
                    hython_exe = os.path.join(os.path.dirname(houdini_exe), 'hython')
                    if not os.path.exists(hython_exe):
                        # Try in Frameworks directory for app bundles
                        frameworks_path = os.path.join(install['path'], 'Contents', 'Frameworks', 'Houdini.framework', 'Versions', 'Current', 'bin', 'hython')
                        if os.path.exists(frameworks_path):
                            hython_exe = frameworks_path
                    if os.path.exists(hython_exe):
                        version = self._parse_version_from_path(install['path'], 'Houdini')
                        if not version:
                            version = self._get_houdini_version_macos(houdini_exe)
                        license_type = self._detect_houdini_license_macos(install['path'])
                        if version:
                            houdini_versions.append({
                                'version': version,
                                'path': install['path'],
                                'executable': houdini_exe,
                                'python_executable': hython_exe,
                                'license_type': license_type,
                                'source': install['source']
                            })
                drive_installations = []

            else:
                drive_installations = []

            for houdini_path in drive_installations:
                # Check if this is a Side Effects Software folder or direct Houdini installation
                if 'Side Effects Software' in houdini_path and 'Houdini' not in os.path.basename(houdini_path):
                    # Look inside Side Effects Software folder for Houdini installations
                    if os.path.exists(houdini_path):
                        try:
                            for item in os.listdir(houdini_path):
                                if item.startswith('Houdini'):
                                    version_path = os.path.join(houdini_path, item)
                                    if os.path.isdir(version_path):
                                        houdini_exe = os.path.join(version_path, 'bin', 'houdini.exe')
                                        hython_exe = os.path.join(version_path, 'bin', 'hython.exe')
                                        if os.path.exists(houdini_exe) and os.path.exists(hython_exe):
                                            version = self._parse_version_from_path(version_path, 'Houdini')
                                            license_type = self._detect_houdini_license(version_path)
                                            if version:
                                                houdini_versions.append({
                                                    'version': version,
                                                    'path': version_path,
                                                    'executable': houdini_exe,
                                                    'python_executable': hython_exe,
                                                    'license_type': license_type,
                                                    'source': 'filesystem'
                                                })
                        except (PermissionError, OSError):
                            continue
                elif 'Houdini' in houdini_path:
                    # Direct Houdini installation folder
                    houdini_exe = os.path.join(houdini_path, 'bin', 'houdini.exe')
                    hython_exe = os.path.join(houdini_path, 'bin', 'hython.exe')
                    if os.path.exists(houdini_exe) and os.path.exists(hython_exe):
                        version = self._parse_version_from_path(houdini_path, 'Houdini')
                        license_type = self._detect_houdini_license(houdini_path)
                        if version:
                            houdini_versions.append({
                                'version': version,
                                'path': houdini_path,
                                'executable': houdini_exe,
                                'python_executable': hython_exe,
                                'license_type': license_type,
                                'source': 'filesystem'
                            })

            # Step 3: Remove duplicates based on installation path and sort by version
            unique_versions = {}
            for version_info in houdini_versions:
                key = version_info['path']
                if key not in unique_versions:
                    unique_versions[key] = version_info

            houdini_versions = list(unique_versions.values())
            houdini_versions = self._sort_versions(houdini_versions)
            houdini_info['versions_found'] = houdini_versions

            logger.info(f"Found {len(houdini_versions)} Houdini installations:")
            for version_info in houdini_versions:
                logger.info(f"  ✅ Houdini {version_info['version']} at {version_info['path']} (via {version_info.get('source', 'unknown')})")

            if houdini_versions:
                latest = houdini_versions[0]
                houdini_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'python_executable': latest['python_executable'],
                    'installation_path': latest['path'],
                    'license_type': latest['license_type']
                })

        except Exception as e:
            logger.error(f"Error discovering Houdini: {e}")

        return houdini_info

    def _validate_maya_executable(self, mayapy_path: str) -> bool:
        """Validate Maya Python executable works."""
        try:
            # Simple test command
            result = subprocess.run([
                mayapy_path, '-c', 'import maya.standalone; print("Maya Python OK")'
            ], capture_output=True, text=True, timeout=30)

            return result.returncode == 0 and "Maya Python OK" in result.stdout

        except Exception as e:
            logger.error(f"Maya validation failed: {e}")
            return False

    def _get_maya_version_linux(self, maya_exe: str) -> Optional[str]:
        """Get Maya version on Linux by running maya -v."""
        try:
            result = subprocess.run([maya_exe, '-v'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse Maya version from output like "Maya 2024.1"
                import re
                match = re.search(r'Maya\s+(\d+(?:\.\d+)?)', result.stdout)
                if match:
                    return match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    def _get_maya_version_macos(self, maya_exe: str) -> Optional[str]:
        """Get Maya version on macOS by running maya -v."""
        try:
            result = subprocess.run([maya_exe, '-v'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse Maya version from output
                import re
                match = re.search(r'Maya\s+(\d+(?:\.\d+)?)', result.stdout)
                if match:
                    return match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    def _get_houdini_version_linux(self, houdini_exe: str) -> Optional[str]:
        """Get Houdini version on Linux."""
        try:
            result = subprocess.run([houdini_exe, '-version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                import re
                match = re.search(r'Houdini\s+(\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    def _get_houdini_version_macos(self, houdini_exe: str) -> Optional[str]:
        """Get Houdini version on macOS."""
        try:
            result = subprocess.run([houdini_exe, '-version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                import re
                match = re.search(r'Houdini\s+(\d+\.\d+\.\d+)', result.stdout)
                if match:
                    return match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    def _detect_houdini_license_linux(self, install_path: str) -> str:
        """Detect Houdini license type on Linux."""
        # Check for license indicators in path or environment
        if 'apprentice' in install_path.lower():
            return 'Apprentice'
        elif 'indie' in install_path.lower():
            return 'Indie'
        else:
            return 'Commercial'

    def _detect_houdini_license_macos(self, install_path: str) -> str:
        """Detect Houdini license type on macOS."""
        # Check bundle name for license type
        bundle_name = os.path.basename(install_path).lower()
        if 'apprentice' in bundle_name:
            return 'Apprentice'
        elif 'indie' in bundle_name:
            return 'Indie'
        else:
            return 'Commercial'

    def _get_blender_version(self, blender_exe: str) -> Optional[str]:
        """Get Blender version from executable."""
        try:
            result = subprocess.run([blender_exe, '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return self._parse_blender_version_output(result.stdout)
        except Exception:
            pass
        return None

    def _parse_blender_version_output(self, output: str) -> Optional[str]:
        """Parse version from Blender --version output."""
        try:
            for line in output.split('\n'):
                if 'Blender' in line and '.' in line:
                    # Extract version like "3.6.5" from "Blender 3.6.5"
                    parts = line.split()
                    for part in parts:
                        if '.' in part and part.replace('.', '').isdigit():
                            return part
        except Exception:
            pass
        return None

    def _detect_houdini_license(self, houdini_path: str) -> str:
        """Detect Houdini license type."""
        try:
            # Check for license files or registry entries
            # This is a simplified detection - real implementation would be more thorough
            if 'Apprentice' in houdini_path:
                return 'Apprentice'
            elif 'Indie' in houdini_path:
                return 'Indie'
            else:
                return 'Commercial'
        except Exception:
            return 'Unknown'

    def get_dcc_status(self) -> Dict:
        """Get current status of all DCC applications."""
        if not self.discovered_dccs:
            self.discover_all()

        status = {}
        for dcc_name, dcc_info in self.discovered_dccs.items():
            status[dcc_name] = {
                'available': dcc_info['available'],
                'version': dcc_info.get('version'),
                'ready': dcc_info['available'] and dcc_info.get('executable') is not None
            }

        return status

    def get_executable_path(self, dcc_name: str, executable_type: str = 'main') -> Optional[str]:
        """Get executable path for specific DCC."""
        if dcc_name not in self.discovered_dccs:
            return None

        dcc_info = self.discovered_dccs[dcc_name]
        if not dcc_info['available']:
            return None

        if executable_type == 'python' and 'python_executable' in dcc_info:
            return dcc_info['python_executable']
        else:
            return dcc_info.get('executable')

    def discover_nuke(self) -> Dict:
        """Discover Nuke installations using enhanced multi-drive search."""
        nuke_info = {
            'available': False,
            'version': None,
            'executable': None,
            'python_executable': None,
            'installation_path': None,
            'versions_found': []
        }

        try:
            logger.info("Starting enhanced Nuke discovery...")
            nuke_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Step 1: Search Windows Registry for official installations
                registry_paths = [
                    r"SOFTWARE\The Foundry\Nuke",
                    r"SOFTWARE\Classes\Applications\Nuke*.exe",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Nuke"
                ]

                registry_installations = self._search_registry_for_app("Nuke", registry_paths)
                for reg_path in registry_installations:
                    # Search for Nuke executable in bin directory
                    potential_executables = []
                    bin_dir = os.path.join(reg_path, 'bin')
                    if os.path.exists(bin_dir):
                        for file in os.listdir(bin_dir):
                            if file.startswith('Nuke') and file.endswith('.exe'):
                                potential_executables.append(os.path.join(bin_dir, file))
                    else:
                        # Sometimes Nuke is directly in the installation directory
                        for file in os.listdir(reg_path):
                            if file.startswith('Nuke') and file.endswith('.exe'):
                                potential_executables.append(os.path.join(reg_path, file))

                    for nuke_exe in potential_executables:
                        if os.path.exists(nuke_exe):
                            version = self._parse_version_from_path(reg_path, 'Nuke')
                            if version:
                                nuke_versions.append({
                                    'version': version,
                                    'path': reg_path,
                                    'executable': nuke_exe,
                                    'python_executable': nuke_exe,  # Nuke has built-in Python
                                    'source': 'registry'
                                })

                # Step 2: Search all drives for Nuke installations
                for drive in self.available_drives:
                    logger.debug(f"Searching {drive} for Nuke installations...")

                    # Common installation paths
                    search_paths = [
                        os.path.join(drive, "Program Files", "Nuke*"),
                        os.path.join(drive, "Program Files (x86)", "Nuke*"),
                        os.path.join(drive, "Nuke*"),
                        os.path.join(drive, "Applications", "Nuke*")
                    ]

                    for search_pattern in search_paths:
                        import glob
                        for install_dir in glob.glob(search_pattern):
                            if os.path.isdir(install_dir):
                                # Look for Nuke executable
                                potential_executables = []

                                # Check for executables in bin directory
                                bin_dir = os.path.join(install_dir, 'bin')
                                if os.path.exists(bin_dir):
                                    for file in os.listdir(bin_dir):
                                        if file.startswith('Nuke') and file.endswith('.exe'):
                                            potential_executables.append(os.path.join(bin_dir, file))

                                # Check for executables in root directory
                                for file in os.listdir(install_dir):
                                    if file.startswith('Nuke') and file.endswith('.exe'):
                                        potential_executables.append(os.path.join(install_dir, file))

                                for nuke_exe in potential_executables:
                                    if os.path.exists(nuke_exe):
                                        version = self._parse_version_from_path(install_dir, 'Nuke')
                                        if version and not any(v['executable'] == nuke_exe for v in nuke_versions):
                                            nuke_versions.append({
                                                'version': version,
                                                'path': install_dir,
                                                'executable': nuke_exe,
                                                'python_executable': nuke_exe,
                                                'source': 'filesystem'
                                            })

            elif self.system == 'Linux':
                # Linux search paths
                search_paths = self._get_linux_search_paths()
                nuke_versions.extend(self._search_linux_for_app("Nuke", search_paths))

            elif self.system == 'Darwin':
                # macOS search paths
                search_paths = self._get_macos_search_paths()
                nuke_versions.extend(self._search_macos_for_app("Nuke", search_paths))

            # Sort versions and select the latest
            if nuke_versions:
                sorted_versions = self._sort_versions(nuke_versions)
                latest = sorted_versions[0]

                nuke_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'python_executable': latest.get('python_executable', latest['executable']),
                    'installation_path': latest['path'],
                    'versions_found': sorted_versions
                })

                logger.info(f"✅ Found Nuke {latest['version']} at {latest['executable']}")
                logger.info(f"   Installation path: {latest['path']}")
                logger.info(f"   Found {len(sorted_versions)} total installations")
            else:
                logger.warning("❌ No Nuke installations found")

        except Exception as e:
            logger.error(f"Error discovering Nuke: {e}")

        return nuke_info

    def discover_natron(self) -> Dict:
        """Discover Natron installations using standard directory search."""
        natron_info = {
            'available': False,
            'version': None,
            'executable': None,
            'python_executable': None,
            'installation_path': None,
            'versions_found': []
        }

        try:
            logger.info("Starting Natron discovery...")
            natron_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Search all drives for Natron installations
                for drive in self.available_drives:
                    logger.debug(f"Searching {drive} for Natron installations...")

                    search_paths = [
                        os.path.join(drive, "Program Files", "Natron*"),
                        os.path.join(drive, "Program Files (x86)", "Natron*"),
                        os.path.join(drive, "Natron*"),
                        os.path.join(drive, "Applications", "Natron*")
                    ]

                    for search_pattern in search_paths:
                        import glob
                        for install_dir in glob.glob(search_pattern):
                            if os.path.isdir(install_dir):
                                # Look for Natron executable
                                natron_exe = None
                                natron_renderer_exe = None

                                # Check for executables in bin directory
                                bin_dir = os.path.join(install_dir, 'bin')
                                if os.path.exists(bin_dir):
                                    natron_exe = os.path.join(bin_dir, 'Natron.exe')
                                    natron_renderer_exe = os.path.join(bin_dir, 'NatronRenderer.exe')

                                # Check for executables in root directory
                                if not natron_exe:
                                    natron_exe = os.path.join(install_dir, 'Natron.exe')
                                if not natron_renderer_exe:
                                    natron_renderer_exe = os.path.join(install_dir, 'NatronRenderer.exe')

                                # Prefer NatronRenderer for command-line operations
                                executable = natron_renderer_exe if os.path.exists(natron_renderer_exe) else natron_exe

                                if executable and os.path.exists(executable):
                                    version = self._parse_version_from_path(install_dir, 'Natron')
                                    if version and not any(v['executable'] == executable for v in natron_versions):
                                        natron_versions.append({
                                            'version': version,
                                            'path': install_dir,
                                            'executable': executable,
                                            'python_executable': executable,  # Natron has built-in Python
                                            'source': 'filesystem'
                                        })

            elif self.system == 'Linux':
                # Linux search paths for Natron
                search_paths = [
                    '/usr/bin',
                    '/usr/local/bin',
                    '/opt/Natron*',
                    '/opt/natron*',
                    os.path.expanduser('~/Applications'),
                    '/Applications'
                ]

                for search_path in search_paths:
                    if '*' in search_path:
                        import glob
                        for path in glob.glob(search_path):
                            if os.path.isdir(path):
                                natron_exe = os.path.join(path, 'bin', 'Natron')
                                natron_renderer = os.path.join(path, 'bin', 'NatronRenderer')
                                executable = natron_renderer if os.path.exists(natron_renderer) else natron_exe

                                if os.path.exists(executable):
                                    version = self._parse_version_from_path(path, 'Natron')
                                    natron_versions.append({
                                        'version': version or 'Unknown',
                                        'path': path,
                                        'executable': executable,
                                        'python_executable': executable,
                                        'source': 'filesystem'
                                    })
                    else:
                        natron_exe = os.path.join(search_path, 'natron')
                        natron_renderer = os.path.join(search_path, 'natronrenderer')
                        executable = natron_renderer if os.path.exists(natron_renderer) else natron_exe

                        if os.path.exists(executable):
                            natron_versions.append({
                                'version': 'System',
                                'path': search_path,
                                'executable': executable,
                                'python_executable': executable,
                                'source': 'system'
                            })

            elif self.system == 'Darwin':
                # macOS search paths for Natron
                search_paths = [
                    '/Applications/Natron.app',
                    '/Applications/Natron*/Natron.app',
                    os.path.expanduser('~/Applications/Natron.app'),
                    os.path.expanduser('~/Applications/Natron*/Natron.app')
                ]

                for search_pattern in search_paths:
                    import glob
                    for app_path in glob.glob(search_pattern):
                        if os.path.isdir(app_path):
                            natron_exe = os.path.join(app_path, 'Contents', 'MacOS', 'Natron')
                            natron_renderer = os.path.join(app_path, 'Contents', 'MacOS', 'NatronRenderer')
                            executable = natron_renderer if os.path.exists(natron_renderer) else natron_exe

                            if os.path.exists(executable):
                                version = self._parse_version_from_path(app_path, 'Natron')
                                natron_versions.append({
                                    'version': version or 'Unknown',
                                    'path': app_path,
                                    'executable': executable,
                                    'python_executable': executable,
                                    'source': 'filesystem'
                                })

            # Sort versions and select the latest
            if natron_versions:
                sorted_versions = self._sort_versions(natron_versions)
                latest = sorted_versions[0]

                natron_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'python_executable': latest.get('python_executable', latest['executable']),
                    'installation_path': latest['path'],
                    'versions_found': sorted_versions
                })

                logger.info(f"✅ Found Natron {latest['version']} at {latest['executable']}")
                logger.info(f"   Installation path: {latest['path']}")
                logger.info(f"   Found {len(sorted_versions)} total installations")
            else:
                logger.warning("❌ No Natron installations found")

        except Exception as e:
            logger.error(f"Error discovering Natron: {e}")

        return natron_info

    def discover_vectorworks(self) -> Dict:
        """Discover Vectorworks installations using enhanced registry and path search."""
        vectorworks_info = {
            'available': False,
            'version': None,
            'executable': None,
            'python_executable': None,
            'installation_path': None,
            'versions_found': []
        }

        try:
            logger.info("Starting enhanced Vectorworks discovery...")
            vectorworks_versions = []

            # Cross-platform discovery based on OS
            if self.system == 'Windows':
                # Step 1: Search Windows Registry for official installations
                registry_paths = [
                    r"SOFTWARE\Nemetschek\Vectorworks",
                    r"SOFTWARE\Classes\Applications\Vectorworks*.exe",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Vectorworks"
                ]

                registry_installations = self._search_registry_for_app("Vectorworks", registry_paths)
                for reg_path in registry_installations:
                    # Search for Vectorworks executable
                    vectorworks_exe = None

                    # Common executable names for different versions
                    exe_names = ['Vectorworks.exe', 'VectorworksViewer.exe']
                    for exe_name in exe_names:
                        exe_path = os.path.join(reg_path, exe_name)
                        if os.path.exists(exe_path):
                            vectorworks_exe = exe_path
                            break

                    if vectorworks_exe:
                        version = self._parse_version_from_path(reg_path, 'Vectorworks')
                        if version:
                            vectorworks_versions.append({
                                'version': version,
                                'path': reg_path,
                                'executable': vectorworks_exe,
                                'python_executable': vectorworks_exe,  # Vectorworks has embedded Python
                                'source': 'registry'
                            })

                # Step 2: Search all drives for Vectorworks installations
                for drive in self.available_drives:
                    logger.debug(f"Searching {drive} for Vectorworks installations...")

                    search_paths = [
                        os.path.join(drive, "Program Files", "Vectorworks*"),
                        os.path.join(drive, "Program Files (x86)", "Vectorworks*"),
                        os.path.join(drive, "Vectorworks*"),
                        os.path.join(drive, "Applications", "Vectorworks*")
                    ]

                    for search_pattern in search_paths:
                        import glob
                        for install_dir in glob.glob(search_pattern):
                            if os.path.isdir(install_dir):
                                # Look for Vectorworks executable
                                exe_names = ['Vectorworks.exe', 'VectorworksViewer.exe']
                                vectorworks_exe = None

                                for exe_name in exe_names:
                                    exe_path = os.path.join(install_dir, exe_name)
                                    if os.path.exists(exe_path):
                                        vectorworks_exe = exe_path
                                        break

                                if vectorworks_exe:
                                    version = self._parse_version_from_path(install_dir, 'Vectorworks')
                                    if version and not any(v['executable'] == vectorworks_exe for v in vectorworks_versions):
                                        vectorworks_versions.append({
                                            'version': version,
                                            'path': install_dir,
                                            'executable': vectorworks_exe,
                                            'python_executable': vectorworks_exe,
                                            'source': 'filesystem'
                                        })

            elif self.system == 'Darwin':
                # macOS search paths for Vectorworks
                search_paths = [
                    '/Applications/Vectorworks*.app',
                    os.path.expanduser('~/Applications/Vectorworks*.app')
                ]

                for search_pattern in search_paths:
                    import glob
                    for app_path in glob.glob(search_pattern):
                        if os.path.isdir(app_path):
                            vectorworks_exe = os.path.join(app_path, 'Contents', 'MacOS', 'Vectorworks')

                            if os.path.exists(vectorworks_exe):
                                version = self._parse_version_from_path(app_path, 'Vectorworks')
                                vectorworks_versions.append({
                                    'version': version or 'Unknown',
                                    'path': app_path,
                                    'executable': vectorworks_exe,
                                    'python_executable': vectorworks_exe,
                                    'source': 'filesystem'
                                })

            # Note: Vectorworks has limited Linux support
            # Most installations are Windows/macOS only

            # Sort versions and select the latest
            if vectorworks_versions:
                sorted_versions = self._sort_versions(vectorworks_versions)
                latest = sorted_versions[0]

                vectorworks_info.update({
                    'available': True,
                    'version': latest['version'],
                    'executable': latest['executable'],
                    'python_executable': latest.get('python_executable', latest['executable']),
                    'installation_path': latest['path'],
                    'versions_found': sorted_versions
                })

                logger.info(f"✅ Found Vectorworks {latest['version']} at {latest['executable']}")
                logger.info(f"   Installation path: {latest['path']}")
                logger.info(f"   Found {len(sorted_versions)} total installations")
            else:
                logger.warning("❌ No Vectorworks installations found")

        except Exception as e:
            logger.error(f"Error discovering Vectorworks: {e}")

        return vectorworks_info


# Global discovery instance
discovery = DCCDiscovery()

def get_dcc_discovery() -> DCCDiscovery:
    """Get the global DCC discovery instance."""
    return discovery