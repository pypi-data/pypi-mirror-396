"""
Optimized Maya Persistent Server using FastAPI
This is the production-ready solution for instant Maya operations.

Expected Performance:
- Initial startup: ~8 seconds (one-time cost at agent start)
- Subsequent operations: <50ms (near-instant!)

Usage:
1. Agent starts Maya persistent server on startup (8s one-time cost)
2. All Maya operations route through this server (< 50ms each)
3. Result: ALL Maya workflows become near-instant after initial startup
"""

import os
import sys
import time
import json
import asyncio
from pathlib import Path

# Set environment BEFORE importing Maya
os.environ["MAYA_DISABLE_CLIC_IPM"] = "1"
os.environ["MAYA_DISABLE_CIP"] = "1"
os.environ["MAYA_SKIP_USERSETUP_PY"] = "1"
os.environ["MAYA_PLUG_IN_PATH"] = ""
os.environ["MAYA_MODULE_PATH"] = ""

print("[MAYA SERVER] Initializing Maya standalone...")
start_init = time.time()

import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds

init_time = time.time() - start_init
maya_version = cmds.about(version=True)
print(f"[MAYA SERVER] Maya {maya_version} initialized in {init_time:.2f}s")

# Now import FastAPI
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("[ERROR] FastAPI not installed. Install with: pip install fastapi uvicorn")
    sys.exit(1)

app = FastAPI(title="Maya Persistent Server", version="1.0.0")

class MayaCommand(BaseModel):
    """Maya command request model."""
    command: str
    operation_type: str = "generic"
    session_id: str = "default"

class MayaResponse(BaseModel):
    """Maya command response model."""
    success: bool
    result: str = ""
    error: str = ""
    execution_time: float

# Session management
maya_sessions = {}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ready",
        "maya_version": cmds.about(version=True),
        "active_sessions": len(maya_sessions)
    }

@app.post("/execute", response_model=MayaResponse)
async def execute_command(command_request: MayaCommand):
    """Execute Maya command and return result."""
    start_time = time.time()

    try:
        # Prepare execution context
        exec_globals = {
            'cmds': cmds,
            'maya': sys.modules['maya'],
            'result': None
        }

        # Execute command
        exec(command_request.command, exec_globals)

        execution_time = time.time() - start_time

        return MayaResponse(
            success=True,
            result=str(exec_globals.get('result', 'OK')),
            execution_time=execution_time
        )

    except Exception as e:
        execution_time = time.time() - start_time
        return MayaResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )

@app.post("/session/create")
async def create_session(session_id: str = "default"):
    """Create a new Maya session (just registers it, Maya is already running)."""
    if session_id in maya_sessions:
        return {"status": "exists", "session_id": session_id}

    maya_sessions[session_id] = {
        "created_at": time.time(),
        "status": "listening"
    }

    return {
        "status": "created",
        "session_id": session_id,
        "maya_version": cmds.about(version=True)
    }

@app.post("/session/close")
async def close_session(session_id: str):
    """Close a Maya session."""
    if session_id in maya_sessions:
        del maya_sessions[session_id]
        return {"status": "closed", "session_id": session_id}
    else:
        return {"status": "not_found", "session_id": session_id}

@app.get("/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"sessions": list(maya_sessions.keys())}

def run_server(host="127.0.0.1", port=8766):
    """Run the Maya FastAPI server."""
    print(f"[MAYA SERVER] Starting FastAPI server on {host}:{port}...")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False  # Disable access logs for performance
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Maya Persistent Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8766, help="Port to bind")
    args = parser.parse_args()

    print("="*60)
    print("Maya Persistent Server")
    print("="*60)
    print(f"Maya Version: {maya_version}")
    print(f"Server: http://{args.host}:{args.port}")
    print(f"Health Check: http://{args.host}:{args.port}/health")
    print(f"Execute Command: POST http://{args.host}:{args.port}/execute")
    print("="*60)

    run_server(args.host, args.port)
