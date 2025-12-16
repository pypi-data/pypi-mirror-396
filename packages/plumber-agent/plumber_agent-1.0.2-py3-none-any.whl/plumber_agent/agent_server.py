"""
Local DCC Agent Server
FastAPI server running on user's local machine to handle DCC operations delegated from Railway.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psutil
import websockets
import uvicorn

from .dcc_discovery import get_dcc_discovery
from .dcc_executor import DCCExecutor
from .connection_manager import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple heartbeat function for long operations
async def simple_heartbeat(connection_manager, operation_id: str):
    """Send periodic heartbeat during long DCC operations."""
    interval = 10  # Send heartbeat every 10 seconds
    counter = 0

    while True:
        try:
            await asyncio.sleep(interval)
            counter += 1

            # Send heartbeat progress message
            heartbeat_msg = {
                "type": "dcc_operation_progress",
                "operation_id": operation_id,
                "progress": 0.5,  # Keep progress at 50% during heartbeat
                "message": f"DCC operation in progress... ({counter * interval}s)",
                "timestamp": datetime.now().isoformat(),
                "heartbeat": True
            }

            # Try to send heartbeat message
            await connection_manager.send_operation_progress(
                operation_id, 0.5, f"DCC operation in progress... ({counter * interval}s)"
            )

            logger.debug(f"💓 Heartbeat sent for operation {operation_id} (#{counter})")

        except asyncio.CancelledError:
            logger.debug(f"💓 Heartbeat stopped for operation {operation_id}")
            break
        except Exception as e:
            logger.warning(f"💓 Heartbeat failed for operation {operation_id}: {e}")
            # Continue trying

app = FastAPI(
    title="Plumber Local DCC Agent",
    description="Local agent for executing DCC operations on user's machine",
    version="2.0.0"
)

# Enable CORS for Railway backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://plumber-production-446f.up.railway.app",
        "http://localhost:8000",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
connected_clients: Dict[str, WebSocket] = {}
active_jobs: Dict[str, Dict] = {}
dcc_discovery = get_dcc_discovery()
dcc_executor = DCCExecutor()

# Connection manager - replaces old railway connection logic
connection_manager: Optional[ConnectionManager] = None

# Pydantic models
class DCCOperation(BaseModel):
    """DCC operation request model."""
    operation_id: str = Field(..., description="Unique operation ID")
    dcc_type: str = Field(..., description="DCC type (maya, blender, houdini)")
    operation_type: str = Field(..., description="Operation type (render, export, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    input_files: List[str] = Field(default_factory=list, description="Input file paths")
    output_directory: str = Field(..., description="Output directory path")
    timeout: int = Field(default=300, description="Timeout in seconds")
    user_id: Optional[str] = Field(None, description="User ID for authentication")

class AgentStatus(BaseModel):
    """Agent status model."""
    agent_id: str
    status: str
    uptime: float
    dcc_status: Dict[str, Dict]
    active_jobs: int
    system_resources: Dict[str, Any]

class OperationResult(BaseModel):
    """Operation result model."""
    operation_id: str
    success: bool
    output_files: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    execution_time: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Agent ID - unique identifier for this agent instance
AGENT_ID = str(uuid.uuid4())
START_TIME = datetime.now()

# Railway backend configuration
RAILWAY_BACKEND_URL = "https://plumber-production-446f.up.railway.app"

async def process_dcc_operation(operation_data: dict):
    """Process DCC operation received via connection manager."""
    try:
        operation_id = operation_data.get('operation_id')
        logger.info(f"🎬 Processing DCC operation: {operation_id}")

        # Convert dict to DCCOperation object
        operation = DCCOperation(**operation_data)

        # Send operation start notification
        await connection_manager.send_operation_response(operation_id, "started", {
            "message": f"Starting {operation.dcc_type} operation",
            "progress": 0
        })

        # Check if DCC is available
        dcc_status = dcc_discovery.get_dcc_status()
        if not dcc_status.get(operation.dcc_type, {}).get('available'):
            error_msg = f"{operation.dcc_type.title()} is not available on this system"
            logger.error(f"❌ {error_msg}")
            await connection_manager.send_operation_response(operation_id, "failed", {
                "error": error_msg
            })
            return

        # Add to active jobs
        active_jobs[operation_id] = {
            "operation": operation.dict(),
            "status": "running",
            "start_time": datetime.now(),
            "progress": 0
        }

        # Execute the operation with progress callback and heartbeat support
        async def progress_callback(progress: int, message: str):
            logger.info(f"📊 [PROGRESS] {operation_id}: {progress}% - {message}")
            await connection_manager.send_operation_progress(operation_id, progress / 100.0, message)
            await connection_manager.send_operation_response(operation_id, "progress", {
                "progress": progress,
                "message": message
            })
            active_jobs[operation_id]["progress"] = progress

        # Execute operation with simple heartbeat approach
        heartbeat_task = None
        try:
            # Start simple heartbeat during operation
            heartbeat_task = asyncio.create_task(
                simple_heartbeat(connection_manager, operation_id)
            )

            # Execute the actual operation
            result = await dcc_executor.execute_operation(operation, progress_callback)

        finally:
            # Stop heartbeat
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

        # Update job status
        active_jobs[operation_id]["status"] = "completed"
        active_jobs[operation_id]["result"] = result.dict()

        # DEBUG: Log result details
        logger.info(f"[AGENT RESULT DEBUG] Operation {operation_id} result.dict() keys: {list(result.dict().keys())}")
        logger.info(f"[AGENT RESULT DEBUG] result.metadata: {result.metadata}")
        logger.info(f"[AGENT RESULT DEBUG] Full result.dict(): {result.dict()}")

        # Send success response
        await connection_manager.send_operation_response(operation_id, "completed", {
            "result": result.dict(),
            "execution_time": result.execution_time,
            "success": result.success
        })

        logger.info(f"✅ Operation {operation_id} completed successfully")

        # Schedule cleanup after 5 minutes
        asyncio.create_task(cleanup_job_delayed(operation_id, 300))

    except Exception as e:
        operation_id = operation_data.get('operation_id', 'unknown')
        error_msg = str(e)
        logger.error(f"❌ Operation {operation_id} failed: {error_msg}")

        # Update job status
        if operation_id in active_jobs:
            active_jobs[operation_id]["status"] = "failed"
            active_jobs[operation_id]["error"] = error_msg

        # Send error response
        await connection_manager.send_operation_response(operation_id, "failed", {
            "error": error_msg
        })

async def cleanup_job_delayed(operation_id: str, delay: int):
    """Clean up job after delay."""
    await asyncio.sleep(delay)
    if operation_id in active_jobs:
        del active_jobs[operation_id]
        logger.debug(f"🧹 Cleaned up job: {operation_id}")

async def handle_dcc_operation_message(data: Dict[str, Any]):
    """Handle DCC operation message from Railway backend."""
    operation_data = data.get('data', {})
    operation_id = operation_data.get('operation_id')
    logger.info(f"📨 Received DCC operation request: {operation_id}")

    # Process DCC operation asynchronously
    asyncio.create_task(process_dcc_operation(operation_data))

@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup."""
    global connection_manager

    logger.info(f"[START] Local DCC Agent v2.0.0 starting up (ID: {AGENT_ID})")
    logger.info("[INFO] Features: Enhanced connection stability, Exponential backoff, Multi-path communication")
    logger.info("[INFO] Compatible with Railway backend v2.2.0+")

    # Discover DCC installations
    discovery_results = dcc_discovery.discover_all()
    logger.info("[DISCOVERY] DCC Discovery completed:")
    for dcc_name, dcc_info in discovery_results.items():
        if dcc_info['available']:
            logger.info(f"  ✅ {dcc_name.title()}: {dcc_info['version']}")
        else:
            logger.info(f"  ❌ {dcc_name.title()}: Not found")

    # Initialize DCC executor
    await dcc_executor.initialize()

    # Format DCC applications data for backend
    dcc_applications = {}
    for dcc_name, dcc_info in discovery_results.items():
        dcc_applications[dcc_name] = {
            "available": dcc_info.get('available', False),
            "version": dcc_info.get('version'),
            "executable": dcc_info.get('executable'),
            "python_executable": dcc_info.get('python_executable')
        }

    # System info
    system_info = {
        "agent_version": "2.0.0",
        "platform": "windows",
        "enhanced_features": True,
        "supported_operations": ["render", "export", "import", "script", "scene_info"]
    }

    # Initialize enhanced connection manager
    connection_manager = ConnectionManager(
        agent_id=AGENT_ID,
        railway_url=RAILWAY_BACKEND_URL,
        dcc_applications=dcc_applications,
        system_info=system_info
    )

    # Register message handlers
    connection_manager.register_message_handler("dcc_operation", handle_dcc_operation_message)

    # Start connection manager
    await connection_manager.start()
    logger.info("✅ Enhanced Connection Manager initialized")

@app.get("/")
async def root():
    """Root endpoint with agent information."""
    connection_status = connection_manager.get_connection_status() if connection_manager else {"state": "initializing"}

    return {
        "message": "Plumber Local DCC Agent v2.0.0",
        "agent_id": AGENT_ID,
        "status": "running",
        "uptime": (datetime.now() - START_TIME).total_seconds(),
        "version": "2.0.0",
        "enhanced_features": True,
        "connection_status": connection_status
    }

@app.get("/version")
async def get_version():
    """Get detailed version information."""
    connection_status = connection_manager.get_connection_status() if connection_manager else {"state": "initializing"}

    return {
        "agent_version": "2.0.0",
        "agent_id": AGENT_ID,
        "enhanced_features": True,
        "features": [
            "Exponential backoff reconnection",
            "Connection state persistence",
            "Bidirectional heartbeat system",
            "Multi-path communication (WebSocket + HTTP)",
            "Circuit breaker pattern",
            "Real-time connection quality monitoring",
            "Message queuing during disconnections",
            "Maya/Blender/Houdini support"
        ],
        "connection_status": connection_status,
        "compatible_backend_version": "2.2.0+",
        "last_updated": "2025-09-23",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version/check")
async def check_latest_version():
    """Check if this agent is the latest version by comparing with Railway backend."""
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Check Railway backend version
            async with session.get("https://plumber-production-446f.up.railway.app/api/version") as response:
                if response.status == 200:
                    backend_info = await response.json()
                    backend_version = backend_info.get("version", "unknown")

                    # Simple version comparison (you can make this more sophisticated)
                    current_version = "2.0.0"
                    is_latest = True  # For now, assume latest until we have version server

                    return {
                        "current_version": current_version,
                        "backend_version": backend_version,
                        "is_latest": is_latest,
                        "status": "up-to-date" if is_latest else "update-available",
                        "heartbeat_compatible": True,
                        "check_time": datetime.now().isoformat()
                    }
                else:
                    return {
                        "current_version": "2.0.0",
                        "status": "check-failed",
                        "error": f"Backend check failed: {response.status}",
                        "check_time": datetime.now().isoformat()
                    }
    except Exception as e:
        return {
            "current_version": "2.0.0",
            "status": "check-failed",
            "error": str(e),
            "check_time": datetime.now().isoformat()
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    system_resources = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }

    connection_status = connection_manager.get_connection_status() if connection_manager else {"state": "initializing"}

    return {
        "status": "healthy",
        "agent_id": AGENT_ID,
        "uptime": (datetime.now() - START_TIME).total_seconds(),
        "active_jobs": len(active_jobs),
        "system_resources": system_resources,
        "connection_status": connection_status,
        "connection_quality": connection_status.get("quality", 0.0),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status", response_model=AgentStatus)
async def get_agent_status():
    """Get detailed agent status."""
    uptime = (datetime.now() - START_TIME).total_seconds()

    system_resources = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "percent": psutil.virtual_memory().percent,
            "available_gb": psutil.virtual_memory().available / (1024**3),
            "total_gb": psutil.virtual_memory().total / (1024**3)
        },
        "disk": {
            "percent": psutil.disk_usage('C:').percent if os.name == 'nt' else psutil.disk_usage('/').percent,
        }
    }

    return AgentStatus(
        agent_id=AGENT_ID,
        status="running",
        uptime=uptime,
        dcc_status=dcc_discovery.get_dcc_status(),
        active_jobs=len(active_jobs),
        system_resources=system_resources
    )

@app.get("/dcc/discovery")
async def get_dcc_discovery_results():
    """Get DCC discovery results."""
    return {
        "agent_id": AGENT_ID,
        "discovery_results": dcc_discovery.discovered_dccs,
        "dcc_status": dcc_discovery.get_dcc_status(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/connection/status")
async def get_connection_status():
    """Get detailed connection status."""
    if not connection_manager:
        return {
            "error": "Connection manager not initialized",
            "timestamp": datetime.now().isoformat()
        }

    connection_status = connection_manager.get_connection_status()

    return {
        "agent_id": AGENT_ID,
        "connection_status": connection_status,
        "railway_backend": RAILWAY_BACKEND_URL,
        "enhanced_features_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/dcc/execute", response_model=OperationResult)
async def execute_dcc_operation(
    operation: DCCOperation,
    background_tasks: BackgroundTasks
):
    """Execute DCC operation."""
    logger.info(f"🎬 Received DCC operation: {operation.operation_id} ({operation.dcc_type})")

    # Check if DCC is available
    dcc_status = dcc_discovery.get_dcc_status()
    if not dcc_status.get(operation.dcc_type, {}).get('available'):
        raise HTTPException(
            status_code=400,
            detail=f"{operation.dcc_type.title()} is not available on this system"
        )

    # Check if operation is already running
    if operation.operation_id in active_jobs:
        raise HTTPException(
            status_code=409,
            detail=f"Operation {operation.operation_id} is already running"
        )

    # Add to active jobs
    active_jobs[operation.operation_id] = {
        "operation": operation.dict(),
        "status": "running",
        "start_time": datetime.now(),
        "progress": 0
    }

    try:
        # Execute the operation
        result = await dcc_executor.execute_operation(operation)

        # Update job status
        active_jobs[operation.operation_id]["status"] = "completed"
        active_jobs[operation.operation_id]["result"] = result.dict()

        # Schedule cleanup after 5 minutes
        background_tasks.add_task(cleanup_job, operation.operation_id, delay=300)

        logger.info(f"✅ Operation {operation.operation_id} completed successfully")
        return result

    except Exception as e:
        # Update job status
        active_jobs[operation.operation_id]["status"] = "failed"
        active_jobs[operation.operation_id]["error"] = str(e)

        # Schedule cleanup after 1 minute for failed jobs
        background_tasks.add_task(cleanup_job, operation.operation_id, delay=60)

        logger.error(f"❌ Operation {operation.operation_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_active_jobs():
    """Get list of active jobs."""
    return {
        "agent_id": AGENT_ID,
        "active_jobs": active_jobs,
        "job_count": len(active_jobs),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/jobs/{operation_id}")
async def get_job_status(operation_id: str):
    """Get status of specific job."""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "operation_id": operation_id,
        "job_info": active_jobs[operation_id],
        "timestamp": datetime.now().isoformat()
    }

@app.delete("/jobs/{operation_id}")
async def cancel_job(operation_id: str):
    """Cancel running job."""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[operation_id]
    if job["status"] == "running":
        # Cancel the operation
        await dcc_executor.cancel_operation(operation_id)
        job["status"] = "cancelled"
        job["end_time"] = datetime.now()

        logger.info(f"🚫 Operation {operation_id} cancelled")
        return {"message": f"Operation {operation_id} cancelled"}
    else:
        return {"message": f"Operation {operation_id} is not running (status: {job['status']})"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication with Railway."""
    await websocket.accept()
    client_id = str(uuid.uuid4())
    connected_clients[client_id] = websocket

    logger.info(f"🔌 WebSocket client connected: {client_id}")

    try:
        # Send initial status
        await websocket.send_json({
            "type": "agent_status",
            "data": {
                "agent_id": AGENT_ID,
                "status": "connected",
                "dcc_status": dcc_discovery.get_dcc_status(),
                "timestamp": datetime.now().isoformat()
            }
        })

        # Listen for messages
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, data)

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if client_id in connected_clients:
            del connected_clients[client_id]

async def handle_websocket_message(websocket: WebSocket, data: Dict):
    """Handle incoming WebSocket message."""
    message_type = data.get("type")

    if message_type == "ping":
        await websocket.send_json({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })
    elif message_type == "get_status":
        status = await get_agent_status()
        await websocket.send_json({
            "type": "status_response",
            "data": status.dict()
        })
    elif message_type == "dcc_operation":
        operation_data = data.get("data", {})
        try:
            operation = DCCOperation(**operation_data)
            # Handle the operation asynchronously
            asyncio.create_task(handle_websocket_operation(websocket, operation))
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Invalid operation data: {e}"
            })

async def handle_websocket_operation(websocket: WebSocket, operation: DCCOperation):
    """Handle DCC operation via WebSocket with real-time progress updates."""
    try:
        # Add to active jobs
        active_jobs[operation.operation_id] = {
            "operation": operation.dict(),
            "status": "running",
            "start_time": datetime.now(),
            "progress": 0
        }

        # Send operation started message
        await websocket.send_json({
            "type": "operation_started",
            "operation_id": operation.operation_id,
            "timestamp": datetime.now().isoformat()
        })

        # Execute operation with progress callbacks
        async def progress_callback(progress: int, message: str):
            await websocket.send_json({
                "type": "operation_progress",
                "operation_id": operation.operation_id,
                "progress": progress,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            active_jobs[operation.operation_id]["progress"] = progress

        result = await dcc_executor.execute_operation(operation, progress_callback)

        # Update job status
        active_jobs[operation.operation_id]["status"] = "completed"
        active_jobs[operation.operation_id]["result"] = result.dict()

        # Send completion message
        await websocket.send_json({
            "type": "operation_completed",
            "operation_id": operation.operation_id,
            "result": result.dict(),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        # Update job status
        active_jobs[operation.operation_id]["status"] = "failed"
        active_jobs[operation.operation_id]["error"] = str(e)

        # Send error message
        await websocket.send_json({
            "type": "operation_failed",
            "operation_id": operation.operation_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

async def cleanup_job(operation_id: str, delay: int = 0):
    """Clean up completed job after delay."""
    if delay > 0:
        await asyncio.sleep(delay)

    if operation_id in active_jobs:
        del active_jobs[operation_id]
        logger.info(f"🧹 Cleaned up job: {operation_id}")

async def broadcast_to_clients(message: Dict):
    """Broadcast message to all connected WebSocket clients."""
    if not connected_clients:
        return

    disconnected_clients = []
    for client_id, websocket in connected_clients.items():
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send message to client {client_id}: {e}")
            disconnected_clients.append(client_id)

    # Clean up disconnected clients
    for client_id in disconnected_clients:
        if client_id in connected_clients:
            del connected_clients[client_id]

def run_agent(host: str = "127.0.0.1", port: int = 8001):
    """Run the Local DCC Agent server."""
    logger.info(f"[START] Starting Local DCC Agent on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_agent()