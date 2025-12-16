"""
Command Line Interface for Plumber Agent

Provides CLI commands for managing the local DCC agent:
- plumber-agent: Start the agent server
- plumber-agent install-service: Install as system service
- plumber-agent uninstall-service: Remove system service
- plumber-agent start: Start service
- plumber-agent stop: Stop service
- plumber-agent restart: Restart service
- plumber-agent status: Check service status
- plumber-agent version: Show version
"""

import sys
import click
import asyncio
from pathlib import Path

# Import version
from . import __version__

# Import main components (will be loaded when needed)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--host', default='127.0.0.1', help='Host to bind the agent server')
@click.option('--port', default=8001, help='Port to bind the agent server', type=int)
@click.option('--reload', is_flag=True, help='Enable auto-reload on code changes (development only)')
def main(ctx, host, port, reload):
    """
    Plumber Agent - Local DCC Agent for Maya, Blender, and Houdini operations.

    Run without arguments to start the agent server.
    Use subcommands for service management.
    """
    # If Click is just parsing for help/completion, don't start the server
    if ctx.resilient_parsing:
        return

    # Check if --help was requested (don't start server for help)
    if '--help' in sys.argv or '-h' in sys.argv:
        return

    if ctx.invoked_subcommand is None:
        # No subcommand, start the server
        start_server(host=host, port=port, reload=reload)


@main.command()
@click.option('--host', default='127.0.0.1', help='Host to bind the agent server')
@click.option('--port', default=8001, help='Port to bind the agent server', type=int)
@click.option('--reload', is_flag=True, help='Enable auto-reload on code changes (development only)')
def serve(host, port, reload):
    """Start the agent server (same as running without arguments)."""
    start_server(host=host, port=port, reload=reload)


@main.command()
def version():
    """Show the agent version."""
    click.echo(f"Plumber Agent v{__version__}")


@main.command(name='install-service')
@click.option('--host', default='127.0.0.1', help='Host for the agent service')
@click.option('--port', default=8001, help='Port for the agent service', type=int)
@click.option('--auto-start/--no-auto-start', default=True, help='Enable auto-start on boot')
def install_service(host, port, auto_start):
    """Install the agent as a system service (auto-start on boot)."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    click.echo("Installing Plumber Agent as system service...")
    click.echo(f"  Host: {host}")
    click.echo(f"  Port: {port}")
    click.echo(f"  Auto-start: {'Yes' if auto_start else 'No'}")

    try:
        success = manager.install(host=host, port=port, auto_start=auto_start)
        if success:
            click.secho("[OK] Service installed successfully!", fg='green')
            click.echo("\nNext steps:")
            click.echo("  1. Start the service: plumber-agent start")
            click.echo("  2. Check status: plumber-agent status")
            click.echo("  3. View logs: plumber-agent logs")
        else:
            click.secho("[ERROR] Service installation failed", fg='red')
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command(name='uninstall-service')
def uninstall_service():
    """Remove the system service."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    if not click.confirm("Are you sure you want to uninstall the Plumber Agent service?"):
        click.echo("Cancelled.")
        return

    click.echo("Uninstalling Plumber Agent service...")

    try:
        success = manager.uninstall()
        if success:
            click.secho("[OK] Service uninstalled successfully!", fg='green')
        else:
            click.secho("[ERROR] Service uninstallation failed", fg='red')
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
def start():
    """Start the agent service."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    click.echo("Starting Plumber Agent service...")

    try:
        success = manager.start()
        if success:
            click.secho("[OK] Service started successfully!", fg='green')
            click.echo("Check status with: plumber-agent status")
        else:
            click.secho("[ERROR] Service start failed", fg='red')
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
def stop():
    """Stop the agent service."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    click.echo("Stopping Plumber Agent service...")

    try:
        success = manager.stop()
        if success:
            click.secho("[OK] Service stopped successfully!", fg='green')
        else:
            click.secho("[ERROR] Service stop failed", fg='red')
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
def restart():
    """Restart the agent service."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    click.echo("Restarting Plumber Agent service...")

    try:
        success = manager.restart()
        if success:
            click.secho("[OK] Service restarted successfully!", fg='green')
        else:
            click.secho("[ERROR] Service restart failed", fg='red')
            sys.exit(1)
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
def status():
    """Check the agent service status."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    try:
        status_info = manager.status()

        if status_info['is_running']:
            click.secho("[RUNNING] Plumber Agent is running", fg='green', bold=True)
        else:
            click.secho("[STOPPED] Plumber Agent is stopped", fg='yellow', bold=True)

        click.echo(f"  Service: {status_info.get('service_name', 'N/A')}")
        click.echo(f"  Platform: {status_info.get('platform', 'N/A')}")

        if 'pid' in status_info:
            click.echo(f"  PID: {status_info['pid']}")

        if 'uptime' in status_info:
            click.echo(f"  Uptime: {status_info['uptime']}")

        if 'memory_usage' in status_info:
            click.echo(f"  Memory: {status_info['memory_usage']} MB")

        if 'cpu_percent' in status_info:
            click.echo(f"  CPU: {status_info['cpu_percent']}%")

    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
@click.option('--follow', '-f', is_flag=True, help='Follow log output in real-time')
@click.option('--lines', '-n', default=50, help='Number of lines to show', type=int)
def logs(follow, lines):
    """View agent service logs."""
    from .service_manager import ServiceManager

    manager = ServiceManager()

    try:
        if follow:
            click.echo("Following Plumber Agent logs (Ctrl+C to stop)...")
            manager.follow_logs()
        else:
            log_lines = manager.get_logs(lines=lines)
            for line in log_lines:
                click.echo(line)
    except KeyboardInterrupt:
        click.echo("\nStopped following logs.")
    except Exception as e:
        click.secho(f"[ERROR] {e}", fg='red')
        sys.exit(1)


@main.command()
def discover():
    """Discover installed DCC applications (Maya, Blender, Houdini)."""
    from .dcc_discovery import get_dcc_discovery

    click.echo("Discovering DCC applications...\n")

    discovery_instance = get_dcc_discovery()
    # Actually run discovery! This was missing
    dccs = discovery_instance.discover_all()

    if not dccs or not any(dcc['available'] for dcc in dccs.values()):
        click.secho("No DCC applications found.", fg='yellow')
        return

    for dcc_type, dcc_info in dccs.items():
        if dcc_info.get('available', False):
            click.secho(f"✓ {dcc_type.upper()}", fg='green', bold=True)
            click.echo(f"  Version: {dcc_info.get('version', 'Unknown')}")
            click.echo(f"  Path: {dcc_info.get('executable', 'Unknown')}")
            click.echo()


def start_server(host='127.0.0.1', port=8001, reload=False):
    """
    Start the Plumber Agent FastAPI server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload (development only)
    """
    import uvicorn

    click.echo(f"Starting Plumber Agent v{__version__}...")
    click.echo(f"Server: http://{host}:{port}")
    click.echo("Press Ctrl+C to stop\n")

    try:
        uvicorn.run(
            "plumber_agent.agent_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        click.echo("\nStopping Plumber Agent...")
    except Exception as e:
        click.secho(f"✗ Error starting server: {e}", fg='red')
        sys.exit(1)


if __name__ == '__main__':
    main()
