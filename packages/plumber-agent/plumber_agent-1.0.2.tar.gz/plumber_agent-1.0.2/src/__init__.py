"""
Plumber Agent - Local DCC Agent for Plumber Workflow Editor

This package enables local execution of DCC operations (Maya, Blender, Houdini)
while workflows run on the cloud platform.
"""

__version__ = "1.0.2"
__author__ = "Damn Ltd"
__email__ = "info@damnltd.com"

# Lazy imports - only import heavy modules when actually accessed
# This prevents slow CLI startup for --help and other quick commands
def __getattr__(name):
    """Lazy import heavy modules to speed up CLI."""
    if name == "app":
        from .agent_server import app
        return app
    elif name == "DCCDiscovery":
        from .dcc_discovery import DCCDiscovery
        return DCCDiscovery
    elif name == "DCCExecutor":
        from .dcc_executor import DCCExecutor
        return DCCExecutor
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "__version__",
    "app",
    "DCCDiscovery",
    "DCCExecutor",
]
