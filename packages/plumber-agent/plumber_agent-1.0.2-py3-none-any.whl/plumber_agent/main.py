"""
Plumber Local DCC Agent
Main entry point for the Local DCC Agent that runs on user's machine.
"""

import argparse
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from .agent_server import run_agent
from .dcc_discovery import get_dcc_discovery
from .dcc_executor import DCCExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('plumber_agent.log')
    ]
)

logger = logging.getLogger(__name__)

# Global executor for cleanup
executor = None

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"[STOP] Received signal {signum}, shutting down...")

    if executor:
        executor.cleanup()

    sys.exit(0)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Plumber Local DCC Agent")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the agent server (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind the agent server (default: 8001)"
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only run DCC discovery and exit"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("[LOCAL AGENT DEBUG] ====== Starting Plumber Local DCC Agent ======")
    logger.info(f"[LOCAL AGENT DEBUG] Log level: {args.log_level}")
    logger.info(f"[LOCAL AGENT DEBUG] Host: {args.host}, Port: {args.port}")

    # Initialize DCC discovery
    discovery = get_dcc_discovery()
    logger.info("[LOCAL AGENT DEBUG] Running DCC discovery...")

    discovery_results = discovery.discover_all()
    logger.info(f"[LOCAL AGENT DEBUG] Discovery completed, found {len([d for d in discovery_results.values() if d['available']])} available DCCs")

    # Print discovery results
    print("\n" + "="*60)
    print("*** PLUMBER LOCAL DCC AGENT v2.0.0 - DISCOVERY RESULTS ***")
    print("="*60)

    for dcc_name, dcc_info in discovery_results.items():
        if dcc_info['available']:
            print(f"[OK] {dcc_name.upper()}")
            print(f"   Version: {dcc_info['version']}")
            print(f"   Executable: {dcc_info['executable']}")
            if 'python_executable' in dcc_info and dcc_info['python_executable']:
                print(f"   Python: {dcc_info['python_executable']}")
            print()
            logger.info(f"[LOCAL AGENT DEBUG] DCC found: {dcc_name} v{dcc_info['version']}")
        else:
            print(f"[NOT FOUND] {dcc_name.upper()}: Not found")
            print()
            logger.info(f"[LOCAL AGENT DEBUG] DCC not found: {dcc_name}")

    # Check if any DCC is available
    available_dccs = [name for name, info in discovery_results.items() if info['available']]

    if not available_dccs:
        print("*** WARNING: No DCC applications found! ***")
        print("   Please install Maya, Blender, or Houdini before running the agent.")
        print()
        logger.warning("[LOCAL AGENT DEBUG] No DCC applications found!")
    else:
        print(f"*** Found {len(available_dccs)} DCC application(s): {', '.join(available_dccs)} ***")
        print()
        logger.info(f"[LOCAL AGENT DEBUG] Available DCCs: {', '.join(available_dccs)}")

    if args.discover_only:
        print("Discovery complete. Exiting.")
        return

    # Initialize executor
    global executor
    executor = DCCExecutor()
    logger.info("[LOCAL AGENT DEBUG] DCC Executor initialized")

    print("*** Starting agent server... ***")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   WebSocket endpoint: ws://{args.host}:{args.port}/ws")
    print(f"   Health check: http://{args.host}:{args.port}/health")
    print()
    print("*** To connect from Railway backend, use: ***")
    print(f"   Agent URL: http://{args.host}:{args.port}")
    print("="*60)
    print()
    logger.info(f"[LOCAL AGENT DEBUG] Starting agent server on {args.host}:{args.port}")

    try:
        # Run the agent server
        logger.info("[LOCAL AGENT DEBUG] Calling run_agent()...")
        run_agent(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("[LOCAL AGENT DEBUG] Agent stopped by user (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"[LOCAL AGENT DEBUG] Agent failed with exception: {e}")
        import traceback
        logger.error(f"[LOCAL AGENT DEBUG] Traceback: {traceback.format_exc()}")
        sys.exit(1)
    finally:
        if executor:
            logger.info("[LOCAL AGENT DEBUG] Cleaning up DCC Executor...")
            executor.cleanup()
        logger.info("[LOCAL AGENT DEBUG] ====== Agent shutdown complete ======")

if __name__ == "__main__":
    main()