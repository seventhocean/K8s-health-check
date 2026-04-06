"""WebSocket for real-time metrics"""

import asyncio
import json
from typing import Set, Optional
from fastapi import WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
import logging

from app.services.metrics_service import metrics_service
from app.config import settings
from app.services.auth_service import decode_token

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, data: dict) -> None:
        """Send data to all connected clients"""
        if not self.active_connections:
            return

        message = json.dumps(data)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def metrics_updater():
    """Background task to periodically collect and broadcast metrics"""
    while True:
        try:
            await asyncio.sleep(settings.COLLECTOR_INTERVAL)
            logger.debug("Running scheduled metrics collection")

            # Collect metrics
            data = await metrics_service.collect_all()

            # Broadcast to all clients
            await manager.broadcast({
                "type": "metrics_update",
                "data": data,
            })
        except Exception as e:
            logger.error(f"Metrics updater error: {e}")


async def websocket_metrics(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
) -> None:
    """WebSocket endpoint for real-time metrics with authentication"""
    # Validate token
    if not token:
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Authentication required. Please provide a valid token."
        }))
        await websocket.close()
        return

    try:
        # Decode and validate token
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            raise ValueError("Invalid token")

        username = payload.get("sub")
        logger.info(f"WebSocket authenticated: {username}")
    except (JWTError, ValueError) as e:
        await websocket.accept()
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Invalid token: {str(e)}"
        }))
        await websocket.close()
        return

    # Accept connection after successful authentication
    await manager.connect(websocket)
    try:
        # Send initial data
        initial_data = await metrics_service.get_cluster_summary()
        if initial_data:
            await websocket.send_text(json.dumps({
                "type": "initial_data",
                "data": initial_data,
            }))

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong or commands)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Handle client commands if needed
                try:
                    msg = json.loads(data)
                    if msg.get("action") == "refresh":
                        await metrics_service.collect_all()
                except json.JSONDecodeError:
                    pass
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                continue
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
