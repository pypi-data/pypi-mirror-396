"""
WebSocket endpoints for real-time status updates.

This module provides WebSocket connections for broadcasting server,
hardware, network, and playlist status updates to connected clients.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status as http_status
from typing import Set, Dict, Any
import logging

from globe_server.db.schemas import PlaylistItemRead
from globe_server.utils.eventbus import event_bus
from globe_server.hardware.server_hardware import server_hardware
from globe_server.hardware.esp32_client import esp32_client
from globe_server.network_manager.network_service import network_manager
from globe_server.network_manager.platform import get_current_connection_info

logger = logging.getLogger(__name__)

# Create router for WebSocket endpoints (no prefix)
router = APIRouter(tags=["websocket"])

# Track active WebSocket connections
status_connections: Set[WebSocket] = set()


async def validate_websocket(websocket: WebSocket) -> bool:
    """Accept WebSocket connection without API key validation."""
    logger.debug("[WS VALIDATE] Accepting WebSocket connection")
    return True


async def broadcast_status(connections: Set[WebSocket], status_data: Dict[str, Any]):
    """Broadcast status update to all connected clients."""
    disconnected = set()
    for connection in connections:
        try:
            await connection.send_json(status_data)
        except Exception:
            disconnected.add(connection)
    
    # Remove disconnected clients
    connections.difference_update(disconnected)


# Event handlers for database changes
async def handle_server_status_event(data: Dict[str, Any]):
    """Handle server status updates and broadcast to all connected clients."""
    if not status_connections:
        return  # No clients connected, nothing to do
        
    # Data is already formatted from server_hardware manager
    await broadcast_status(status_connections, {"type": "server", "data": data})


async def handle_hardware_status_event(data: Dict[str, Any]):
    """Handle hardware status updates and broadcast to all connected clients."""
    if not status_connections:
        return  # No clients connected, nothing to do
        
    # Data is already formatted from esp32_client manager
    await broadcast_status(status_connections, {"type": "hardware", "data": data})


async def handle_network_status_event(data: Dict[str, Any]):
    """Handle network status updates and broadcast to all connected clients."""
    if not status_connections:
        return  # No clients connected, nothing to do
    
    # Data is already formatted from network_fsm manager
    await broadcast_status(status_connections, {"type": "network", "data": data})


async def handle_playlist_event(data: Dict[str, Any]):
    """Handle playlist item change events by broadcasting full playlist."""
    if not status_connections:
        return  # No clients connected, nothing to do
    
    try:
        # Get all playlist items ordered by position using CRUD helper
        from globe_server.db.database import get_all_ordered_by_position
        playlist_items = get_all_ordered_by_position()
        
        # Serialize using Pydantic models for consistent format
        serialized_items = [PlaylistItemRead.model_validate(item).model_dump() for item in playlist_items]
        
        # Send to all clients - consistent with other event handlers
        await broadcast_status(status_connections, {
            "type": "playlist",
            "items": serialized_items
        })
    except Exception as e:
        logger.error(f"Error sending playlist update: {e}")


@router.websocket("/status")
async def status_websocket(websocket: WebSocket):
    """Unified WebSocket endpoint for all status updates (server, hardware, network, playlist)."""
    logger.debug(f"[WS STATUS] WebSocket connection attempt")
    
    try:
        if not await validate_websocket(websocket):
            logger.debug("[WS STATUS] WebSocket validation failed")
            return
            
        logger.debug("[WS STATUS] Accepting WebSocket connection")
        await websocket.accept()
        
        # Subscribe to status events
        event_bus.subscribe("server_status", handle_server_status_event)
        event_bus.subscribe("hardware_status", handle_hardware_status_event)
        event_bus.subscribe("network_status", handle_network_status_event)
        event_bus.subscribe("playlist_item", handle_playlist_event)
        
        status_connections.add(websocket)
        logger.debug("[WS STATUS] WebSocket connection accepted")
        
        # Send initial status data from cached managers
        if server_hardware.status:
            await broadcast_status(
                status_connections, 
                {"type": "server", "data": server_hardware.status}
            )
            
        if esp32_client.status:
            await broadcast_status(
                status_connections, 
                {"type": "hardware", "data": esp32_client.status}
            )
            
        # Get current network status
        conn_info = await get_current_connection_info()
        network_status = {
            "status": network_manager.context.current_state.value,
            "current_ssid": conn_info.ssid or "",
            "ip_address": conn_info.ip_address or "",
            "esp32_connected": network_manager.context.esp32_connected,
            "error": network_manager.context.error_message or ""
        }
        await broadcast_status(
            status_connections, 
            {"type": "network", "data": network_status}
        )
            
        # Send initial playlist data
        await handle_playlist_event({})
        
        # Now wait for messages or disconnects
        try:
            while True:
                # Keep connection alive and handle any incoming messages
                data = await websocket.receive_text()
                logger.debug(f"[WS STATUS] Received message: {data}")
        except WebSocketDisconnect:
            logger.debug("[WS STATUS] WebSocket disconnected normally")
            status_connections.remove(websocket)
    except Exception as e:
        logger.error(f"[WS STATUS] WebSocket error: {e}")
        if websocket in status_connections:
            status_connections.remove(websocket)
        if websocket.client_state.CONNECTED:
            await websocket.close(code=http_status.WS_1011_INTERNAL_ERROR, reason=str(e))
    finally:
        # Always unsubscribe to prevent memory leaks
        event_bus.unsubscribe("server_status", handle_server_status_event)
        event_bus.unsubscribe("hardware_status", handle_hardware_status_event)
        event_bus.unsubscribe("network_status", handle_network_status_event)
        event_bus.unsubscribe("playlist_item", handle_playlist_event)
