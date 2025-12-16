"""
API endpoints for system status information.

This module provides REST endpoints for monitoring server,
hardware, and network status, using SQLAlchemy ORM for data access.
"""

from fastapi import APIRouter
import logging

from globe_server.hardware.esp32_client import esp32_client
from globe_server.hardware.server_hardware import server_hardware
from globe_server.network_manager.network_service import network_manager
from globe_server.network_manager.platform import get_current_connection_info

logger = logging.getLogger(__name__)

# Create router for REST endpoints
router = APIRouter(prefix="/status", tags=["status"])


# --- REST API Endpoints ---

@router.get("/server")
async def get_server_status():
    """Get the server's status from cached data."""
    # Return cached status from server hardware manager
    if server_hardware.status:
        return server_hardware.status
    else:
        return {"message": "No server status available yet"}


@router.get("/esp32")
async def get_esp32_status():
    """Get ESP32/hardware status from cached data."""
    # Return cached status from ESP32 client
    if esp32_client.status:
        return esp32_client.status
    else:
        return {"message": "No ESP32 status available yet"}


@router.get("/network")
async def get_network_status():
    """Get network status from FSM context."""
    # Get current connection info from OS
    conn_info = await get_current_connection_info()
    
    return {
        "status": network_manager.context.current_state.value,
        "current_ssid": conn_info.ssid or "",
        "ip_address": conn_info.ip_address or "",
        "esp32_connected": network_manager.context.esp32_connected,
        "error": network_manager.context.error_message or ""
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for the ESP32 to verify server connectivity."""
    return {"status": "success"}
