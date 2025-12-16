"""
Enhanced Connection Management System
Provides robust connection handling with exponential backoff, health monitoring, and failover capabilities.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import aiohttp
import websockets
from pathlib import Path
import pickle
from .cross_platform_utils import (
    normalize_path,
    CrossPlatformSystemInfo,
    get_process_manager
)

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Connection state enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"

class ConnectionType(Enum):
    """Connection type enumeration."""
    WEBSOCKET = "websocket"
    HTTP_POLLING = "http_polling"
    HTTP_FALLBACK = "http_fallback"

class ConnectionHealth:
    """Tracks connection health metrics."""

    def __init__(self):
        self.latency_samples: List[float] = []
        self.packet_loss_count = 0
        self.total_packets = 0
        self.last_heartbeat = None
        self.consecutive_failures = 0
        self.total_reconnections = 0
        self.connection_quality = 1.0  # 0.0 = poor, 1.0 = excellent

    def add_latency_sample(self, latency: float):
        """Add latency sample for quality calculation."""
        self.latency_samples.append(latency)
        if len(self.latency_samples) > 50:  # Keep last 50 samples
            self.latency_samples.pop(0)

    def record_packet_loss(self):
        """Record a packet loss event."""
        self.packet_loss_count += 1
        self.total_packets += 1

    def record_failed_packet(self):
        """Record a failed packet event (alias for packet loss)."""
        self.record_packet_loss()

    def record_successful_packet(self):
        """Record a successful packet transmission."""
        self.total_packets += 1

    def calculate_quality(self) -> float:
        """Calculate connection quality score (0.0 - 1.0)."""
        if not self.latency_samples:
            return 0.5

        # Calculate average latency
        avg_latency = sum(self.latency_samples) / len(self.latency_samples)
        latency_score = max(0, 1.0 - (avg_latency / 1000))  # 1s latency = 0 score

        # Calculate packet loss rate
        packet_loss_rate = self.packet_loss_count / max(1, self.total_packets)
        packet_score = 1.0 - packet_loss_rate

        # Calculate failure score
        failure_score = max(0, 1.0 - (self.consecutive_failures / 10))

        # Weighted average
        quality = (latency_score * 0.4 + packet_score * 0.4 + failure_score * 0.2)
        self.connection_quality = max(0.0, min(1.0, quality))
        return self.connection_quality

class ConnectionManager:
    """Enhanced connection manager with reliability features."""

    def __init__(self, agent_id: str, railway_url: str, state_file: str = "connection_state.pkl", dcc_applications: Dict = None, system_info: Dict = None):
        self.agent_id = agent_id
        self.railway_url = railway_url
        self.railway_ws_url = railway_url.replace("https://", "wss://").replace("http://", "ws://") + "/ws/dcc-agent"
        self.state_file = Path(state_file)
        self.dcc_applications = dcc_applications or {}
        self.system_info = system_info or {}

        # Connection state
        self.state = ConnectionState.DISCONNECTED
        self.connection_type = ConnectionType.WEBSOCKET
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.http_session: Optional[aiohttp.ClientSession] = None

        # Health monitoring - NOW USED ONLY FOR QUALITY METRICS, NOT DISCONNECTION
        self.health = ConnectionHealth()
        self.last_heartbeat_sent = None
        self.last_heartbeat_received = None
        self.heartbeat_interval = 25.0  # seconds - Match Railway's 30s expectation (5s buffer)
        self.heartbeat_timeout = 30.0  # seconds - Timeout for individual heartbeat response
        # REMOVED: connection_timeout - NEVER timeout connection, only track health quality
        self.dcc_operation_timeout = 900.0  # 15 minutes for long DCC operations (matches Railway timeout)

        # INFINITE RECONNECTION - Never give up, only exponential backoff
        self.reconnect_delays = [1, 2, 5, 10, 20, 30, 60, 120, 180, 300, 600]  # Up to 10 min delay
        self.current_delay_index = 0
        self.max_reconnect_attempts = None  # INFINITE - Never stop trying
        self.fast_reconnect_window = 60.0  # If disconnected recently, try fast reconnect
        self.last_successful_connection = None

        # REMOVED: Circuit breaker - We want infinite reconnection, not giving up
        # Health quality thresholds (for UI indicators, NOT for disconnection)
        self.health_excellent_threshold = 1  # 0-1 missed heartbeats = Excellent
        self.health_good_threshold = 5      # 2-5 missed heartbeats = Good
        self.health_degraded_threshold = 15  # 6-15 missed heartbeats = Degraded
        self.health_poor_threshold = 50     # 16-49 missed heartbeats = Poor
        # 50+ missed heartbeats = No Response (but still retrying forever!)

        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue: List[Dict] = []
        self.max_queue_size = 1000

        # Tasks
        self.connection_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.http_polling_task: Optional[asyncio.Task] = None
        self.keepalive_task: Optional[asyncio.Task] = None  # NEW: WebSocket keepalive

        # Connection keepalive settings - TCP-level keepalive via WebSocket
        self.keepalive_interval = 30.0  # Send WebSocket ping every 30 seconds (match Railway)
        self.keepalive_enabled = True
        self.websocket_ping_interval = None  # DISABLE native WebSocket ping during DCC operations (use custom keepalive instead)
        self.websocket_ping_timeout = None   # DISABLE native ping timeout - use infinite retry instead

        # Load persisted state
        self._load_state()

    def _load_state(self):
        """Load connection state from disk."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'rb') as f:
                    saved_state = pickle.load(f)
                    self.health.total_reconnections = saved_state.get('total_reconnections', 0)
                    self.current_delay_index = min(saved_state.get('delay_index', 0), len(self.reconnect_delays) - 1)
                    logger.info(f"📁 Loaded connection state: {saved_state}")
        except Exception as e:
            logger.warning(f"Failed to load connection state: {e}")

    def _save_state(self):
        """Save connection state to disk."""
        try:
            state_data = {
                'total_reconnections': self.health.total_reconnections,
                'delay_index': self.current_delay_index,
                'last_save': datetime.now().isoformat()
            }
            with open(self.state_file, 'wb') as f:
                pickle.dump(state_data, f)
        except Exception as e:
            logger.warning(f"Failed to save connection state: {e}")

    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a message handler for specific message types."""
        self.message_handlers[message_type] = handler

    async def start(self):
        """Start the connection manager."""
        logger.info("🚀 Starting Enhanced Connection Manager v2.0")

        # Start all monitoring tasks
        self.connection_task = asyncio.create_task(self._connection_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        if self.keepalive_enabled:
            self.keepalive_task = asyncio.create_task(self._keepalive_loop())

        logger.info("✅ Connection Manager started successfully")

    async def stop(self):
        """Stop the connection manager and cleanup."""
        logger.info("🛑 Stopping Connection Manager")

        # Cancel all tasks
        for task in [self.connection_task, self.heartbeat_task, self.health_monitor_task, self.http_polling_task, self.keepalive_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        # Close connections
        if self.websocket:
            await self.websocket.close()
        if self.http_session:
            await self.http_session.close()

        # Save state
        self._save_state()
        logger.info("✅ Connection Manager stopped")

    async def _connection_loop(self):
        """Main connection management loop - INFINITE RETRY, NEVER GIVE UP."""
        while True:
            try:
                if self.state in [ConnectionState.DISCONNECTED, ConnectionState.RECONNECTING]:
                    await self._attempt_connection()
                elif self.state == ConnectionState.CONNECTED:
                    # Connection is active, just wait
                    await asyncio.sleep(5)
                # REMOVED: Circuit breaker handling - we never give up

                await asyncio.sleep(1)  # Prevent tight loop

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Connection loop error: {e}")
                # ALWAYS retry, even on errors
                self.state = ConnectionState.RECONNECTING
                await asyncio.sleep(5)

    async def _attempt_connection(self):
        """Attempt to establish connection with INFINITE retry and exponential backoff."""
        # REMOVED: Circuit breaker check - we never give up!

        self.state = ConnectionState.CONNECTING

        # Fast reconnect for recent disconnections (likely network blips)
        if (self.last_successful_connection and
            datetime.now() - self.last_successful_connection < timedelta(seconds=self.fast_reconnect_window) and
            self.health.consecutive_failures <= 2):
            delay = 0.5  # Very fast reconnect for recent disconnections
            logger.info(f"🚀 Fast reconnect attempt (recent disconnection, delay: {delay}s)")
        else:
            delay = self.reconnect_delays[self.current_delay_index]
            logger.info(f"🔄 Attempting connection (attempt {self.health.consecutive_failures + 1}, delay: {delay}s, will retry forever)")

        # Wait before attempting (with jitter to avoid thundering herd)
        import random
        jitter = random.uniform(0.1, 0.5)
        await asyncio.sleep(delay + jitter)

        try:
            # Try WebSocket first
            if await self._connect_websocket():
                self._on_connection_success()
                return

            # Fallback to HTTP polling
            if await self._connect_http_polling():
                self._on_connection_success()
                return

            # Both failed - but we'll keep trying!
            self._on_connection_failure()

        except Exception as e:
            logger.error(f"❌ Connection attempt failed: {e}")
            self._on_connection_failure()

        # Don't wait again - the loop already has delays

    async def _connect_websocket(self) -> bool:
        """Attempt WebSocket connection with TCP-level keepalive."""
        try:
            logger.info(f"[LOCAL AGENT DEBUG] 🔌 Attempting WebSocket connection to: {self.railway_ws_url}")

            # Add connection timeout and TCP-level keepalive
            websocket = await asyncio.wait_for(
                websockets.connect(
                    self.railway_ws_url,
                    ping_interval=self.websocket_ping_interval,  # Send TCP ping every 20s
                    ping_timeout=self.websocket_ping_timeout,     # NEVER timeout on pong
                    close_timeout=None,                           # NEVER timeout on close
                    max_size=10 * 1024 * 1024  # 10MB max message size for large operations
                ),
                timeout=15.0  # Initial connection timeout (increased from 10s)
            )
            logger.info("[LOCAL AGENT DEBUG] WebSocket connection established, sending registration...")

            # Send registration
            registration_msg = {
                "type": "agent_registration",
                "agent_id": self.agent_id,
                "enhanced_features": True,
                "connection_version": "2.0",
                "heartbeat_supported": True,
                "dcc_applications": self.dcc_applications,
                "system_info": self.system_info,
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"[LOCAL AGENT DEBUG] Sending registration with {len(self.dcc_applications)} DCC applications")

            await websocket.send(json.dumps(registration_msg))
            logger.info("[LOCAL AGENT DEBUG] Registration sent, waiting for confirmation...")

            # Wait for confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            logger.info(f"[LOCAL AGENT DEBUG] Received response: {response_data.get('type')}")

            if response_data.get("type") == "registration_confirmed":
                self.websocket = websocket
                self.connection_type = ConnectionType.WEBSOCKET
                logger.info("✅ [LOCAL AGENT DEBUG] WebSocket connection established and confirmed")

                # Start message listening
                asyncio.create_task(self._websocket_listener())
                logger.info("[LOCAL AGENT DEBUG] WebSocket listener started")
                return True
            else:
                logger.warning(f"[LOCAL AGENT DEBUG] Unexpected response type: {response_data.get('type')}")
                await websocket.close()
                return False

        except Exception as e:
            logger.warning(f"[LOCAL AGENT DEBUG] WebSocket connection failed: {e}")
            import traceback
            logger.warning(f"[LOCAL AGENT DEBUG] Traceback: {traceback.format_exc()}")
            return False

    async def _connect_http_polling(self) -> bool:
        """Attempt HTTP polling connection."""
        try:
            logger.info("🔄 Falling back to HTTP polling")

            # Create HTTP session
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )

            # Test connection with registration
            registration_data = {
                "agent_id": self.agent_id,
                "enhanced_features": True,
                "connection_version": "2.0",
                "connection_type": "http_polling",
                "dcc_applications": self.dcc_applications,
                "system_info": self.system_info
            }

            async with self.http_session.post(
                f"{self.railway_url}/api/agents/register",
                json=registration_data
            ) as response:
                if response.status == 200:
                    self.connection_type = ConnectionType.HTTP_POLLING
                    logger.info("✅ HTTP polling connection established")

                    # Start polling task
                    self.http_polling_task = asyncio.create_task(self._http_polling_loop())
                    return True

        except Exception as e:
            logger.warning(f"HTTP polling connection failed: {e}")
            if self.http_session:
                await self.http_session.close()
                self.http_session = None

        return False

    async def _websocket_listener(self):
        """Listen for WebSocket messages."""
        try:
            logger.info("[LOCAL AGENT DEBUG] WebSocket listener starting...")
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.info(f"[LOCAL AGENT DEBUG] Received message type: {data.get('type')}")
                    await self._handle_message(data)
                except Exception as e:
                    logger.error(f"[LOCAL AGENT DEBUG] Error handling WebSocket message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.warning("[LOCAL AGENT DEBUG] 🔌 WebSocket connection closed")
            self.state = ConnectionState.RECONNECTING
        except Exception as e:
            logger.error(f"[LOCAL AGENT DEBUG] WebSocket listener error: {e}")
            import traceback
            logger.error(f"[LOCAL AGENT DEBUG] Traceback: {traceback.format_exc()}")
            self.state = ConnectionState.RECONNECTING

    async def _http_polling_loop(self):
        """HTTP polling loop for message retrieval."""
        while self.connection_type == ConnectionType.HTTP_POLLING:
            try:
                # Poll for messages
                async with self.http_session.get(
                    f"{self.railway_url}/api/agents/{self.agent_id}/messages"
                ) as response:
                    if response.status == 200:
                        messages = await response.json()
                        for message in messages:
                            await self._handle_message(message)
                    elif response.status == 404:
                        # Agent not found, need to re-register
                        self.state = ConnectionState.RECONNECTING
                        break

                await asyncio.sleep(2)  # Poll every 2 seconds

            except Exception as e:
                logger.error(f"HTTP polling error: {e}")
                self.state = ConnectionState.RECONNECTING
                break

    async def _handle_message(self, data: Dict):
        """Handle incoming message."""
        message_type = data.get("type")

        # Handle heartbeat
        if message_type == "heartbeat":
            await self._handle_heartbeat(data)
            return

        # Route to registered handlers
        if message_type in self.message_handlers:
            try:
                await self.message_handlers[message_type](data)
            except Exception as e:
                logger.error(f"Message handler error for {message_type}: {e}")
        else:
            logger.debug(f"No handler for message type: {message_type}")

    async def _handle_heartbeat(self, data: Dict):
        """Handle heartbeat message."""
        self.last_heartbeat_received = datetime.now()
        heartbeat_id = data.get("heartbeat_id")
        logger.info(f"[LOCAL AGENT DEBUG] Received heartbeat {heartbeat_id}, preparing response...")

        # Calculate latency if timestamp provided
        if "timestamp" in data:
            try:
                sent_time = datetime.fromisoformat(data["timestamp"])
                latency = (self.last_heartbeat_received - sent_time).total_seconds() * 1000
                self.health.add_latency_sample(latency)
                logger.info(f"[LOCAL AGENT DEBUG] Heartbeat latency: {latency:.2f}ms")
            except:
                pass

        # Send response
        response = {
            "type": "heartbeat_response",
            "agent_id": self.agent_id,
            "heartbeat_id": heartbeat_id,
            "timestamp": self.last_heartbeat_received.isoformat(),
            "connection_quality": self.health.calculate_quality(),
            "connection_type": self.connection_type.value
        }

        await self._send_message(response)
        logger.info(f"[LOCAL AGENT DEBUG] 📡 Heartbeat response sent for {heartbeat_id} (quality: {self.health.connection_quality:.2f})")

    async def _heartbeat_loop(self):
        """Send periodic heartbeats."""
        while True:
            try:
                if self.state == ConnectionState.CONNECTED:
                    await self._send_heartbeat()

                # Adaptive heartbeat interval based on connection quality
                interval = self.heartbeat_interval
                if self.health.connection_quality < 0.5:
                    interval = 15  # More frequent heartbeats for poor connections

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def _send_heartbeat(self):
        """
        Send heartbeat to Railway backend.

        REMOVED: Proactive agent_heartbeat messages (Railway doesn't recognize this type)
        Railway initiates heartbeats, agent only responds via _handle_heartbeat()
        This function is kept for backward compatibility but does nothing.
        """
        # Railway controls heartbeat timing - we only respond to their pings
        # Response is handled in _handle_heartbeat() with correct "heartbeat_response" type
        pass

    async def _health_monitor_loop(self):
        """Monitor connection health - ONLY FOR QUALITY METRICS, NEVER DISCONNECT."""
        while True:
            try:
                # Calculate connection health quality (for UI display only)
                quality = self.health.calculate_quality()
                missed_heartbeats = self.health.consecutive_failures

                # Determine health status based on thresholds
                if missed_heartbeats <= self.health_excellent_threshold:
                    health_status = "excellent"
                elif missed_heartbeats <= self.health_good_threshold:
                    health_status = "good"
                elif missed_heartbeats <= self.health_degraded_threshold:
                    health_status = "degraded"
                elif missed_heartbeats <= self.health_poor_threshold:
                    health_status = "poor"
                else:
                    health_status = "no_response"

                # Log health changes (but never disconnect!)
                if health_status in ["degraded", "poor"]:
                    logger.warning(f"📊 Connection health: {health_status} (quality: {quality:.2f}, missed: {missed_heartbeats})")
                elif health_status == "no_response":
                    logger.error(f"📊 Connection health: NO RESPONSE (missed: {missed_heartbeats}) - BUT STILL RETRYING FOREVER")
                else:
                    logger.debug(f"📊 Connection health: {health_status} (quality: {quality:.2f})")

                # CRITICAL: We never set state to RECONNECTING based on health
                # Only WebSocket connection errors should trigger reconnection

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)

    def _on_connection_success(self):
        """Handle successful connection (FIXED: Track success time for alpha tester issue)."""
        self.state = ConnectionState.CONNECTED
        self.health.consecutive_failures = 0
        self.current_delay_index = 0  # Reset backoff
        self.last_successful_connection = datetime.now()  # Track for fast reconnect logic
        self.health.total_reconnections += 1
        self._save_state()

        logger.info(f"✅ Connection established (type: {self.connection_type.value}, quality: {self.health.calculate_quality():.2f})")

        # Process queued messages
        asyncio.create_task(self._process_message_queue())

    def _on_connection_failure(self):
        """Handle connection failure - INFINITE RETRY with exponential backoff."""
        self.health.consecutive_failures += 1
        # Increase delay index but cap at maximum delay (don't go beyond array bounds)
        self.current_delay_index = min(self.current_delay_index + 1, len(self.reconnect_delays) - 1)

        logger.warning(f"❌ Connection failed (failures: {self.health.consecutive_failures}, next delay: {self.reconnect_delays[self.current_delay_index]}s) - Will retry forever")

    # REMOVED: _open_circuit_breaker() - We never give up!
    # REMOVED: _handle_circuit_breaker() - We never give up!

    async def _send_message(self, message: Dict) -> bool:
        """Send message via active connection."""
        try:
            if self.connection_type == ConnectionType.WEBSOCKET and self.websocket:
                await self.websocket.send(json.dumps(message))
                return True
            elif self.connection_type == ConnectionType.HTTP_POLLING and self.http_session:
                async with self.http_session.post(
                    f"{self.railway_url}/api/agents/{self.agent_id}/messages",
                    json=message
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Failed to send message: {e}")

        # Queue message for retry
        if len(self.message_queue) < self.max_queue_size:
            self.message_queue.append(message)

        return False

    async def _process_message_queue(self):
        """Process queued messages after reconnection."""
        if not self.message_queue:
            return

        logger.info(f"📤 Processing {len(self.message_queue)} queued messages")

        failed_messages = []
        for message in self.message_queue:
            success = await self._send_message(message)
            if not success:
                failed_messages.append(message)

        self.message_queue = failed_messages
        logger.info(f"✅ Processed queued messages ({len(failed_messages)} failed)")

    async def send_operation_response(self, operation_id: str, status: str, data: Dict):
        """Send operation response to Railway backend."""
        response = {
            "type": "dcc_operation_response",
            "operation_id": operation_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            **data
        }

        success = await self._send_message(response)
        if not success:
            logger.warning(f"Failed to send operation response for {operation_id}")

            # Queue completion messages for retry after reconnection
            if status in ["completed", "failed"]:
                logger.info(f"📦 Queueing {status} response for retry after reconnection")
                # Message will be automatically retried via message_queue

    async def send_operation_with_heartbeat(self, operation_id: str, operation_func, *args, **kwargs):
        """Execute DCC operation with heartbeat support for long operations."""
        heartbeat_task = None

        try:
            # Start heartbeat for long operation
            heartbeat_task = asyncio.create_task(self._dcc_operation_heartbeat(operation_id))

            # Send initial progress
            await self.send_operation_progress(operation_id, 0.0, "DCC operation starting...")

            # Execute the operation
            result = await operation_func(*args, **kwargs)

            # Send final progress
            await self.send_operation_progress(operation_id, 1.0, "DCC operation completed")

            return result

        except Exception as e:
            await self.send_operation_progress(operation_id, -1, f"DCC operation failed: {str(e)}")
            raise
        finally:
            # Stop heartbeat
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

    async def _dcc_operation_heartbeat(self, operation_id: str):
        """Send heartbeat messages during long DCC operations."""
        interval = 15  # Send heartbeat every 15 seconds during DCC operations

        while True:
            try:
                await asyncio.sleep(interval)

                # Send specialized DCC operation heartbeat
                heartbeat_msg = {
                    "type": "dcc_operation_heartbeat",
                    "operation_id": operation_id,
                    "agent_id": self.agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "status": "executing"
                }

                await self._send_message(heartbeat_msg)
                logger.debug(f"💓 DCC operation heartbeat sent for {operation_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"DCC heartbeat failed for {operation_id}: {e}")

    async def _keepalive_loop(self):
        """Send WebSocket ping/pong to prevent connection timeout (FIXED: Alpha tester issue)."""
        while True:
            try:
                if self.state == ConnectionState.CONNECTED and self.websocket:
                    # Send WebSocket ping
                    try:
                        pong_waiter = await self.websocket.ping()
                        await asyncio.wait_for(pong_waiter, timeout=10.0)
                        logger.debug("🏓 WebSocket keepalive ping/pong successful")

                        # Update health with successful keepalive
                        self.health.record_successful_packet()

                    except asyncio.TimeoutError:
                        logger.warning("🏓 WebSocket ping timeout - connection may be unstable")
                        self.health.record_failed_packet()
                    except Exception as e:
                        logger.warning(f"🏓 WebSocket keepalive failed: {e}")
                        self.health.record_failed_packet()

                # Wait for next keepalive interval
                await asyncio.sleep(self.keepalive_interval)

            except asyncio.CancelledError:
                logger.debug("🏓 WebSocket keepalive loop stopped")
                break
            except Exception as e:
                logger.error(f"🏓 Keepalive loop error: {e}")
                await asyncio.sleep(self.keepalive_interval)

    async def send_operation_progress(self, operation_id: str, progress: float, message: str):
        """Send progress update for DCC operation."""
        progress_msg = {
            "type": "dcc_operation_progress",
            "operation_id": operation_id,
            "agent_id": self.agent_id,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        await self._send_message(progress_msg)

    def get_connection_status(self) -> Dict:
        """Get current connection status with health quality metrics."""
        missed_heartbeats = self.health.consecutive_failures

        # Determine health status
        if missed_heartbeats <= self.health_excellent_threshold:
            health_status = "excellent"
        elif missed_heartbeats <= self.health_good_threshold:
            health_status = "good"
        elif missed_heartbeats <= self.health_degraded_threshold:
            health_status = "degraded"
        elif missed_heartbeats <= self.health_poor_threshold:
            health_status = "poor"
        else:
            health_status = "no_response"

        return {
            "state": self.state.value,
            "connection_type": self.connection_type.value,
            "quality": self.health.calculate_quality(),
            "health_status": health_status,  # NEW: Human-readable health status
            "missed_heartbeats": missed_heartbeats,
            "consecutive_failures": self.health.consecutive_failures,
            "total_reconnections": self.health.total_reconnections,
            "last_heartbeat": self.last_heartbeat_received.isoformat() if self.last_heartbeat_received else None,
            "queued_messages": len(self.message_queue),
            "will_retry_forever": True  # NEW: Indicate infinite retry capability
        }