from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from typing import List, Optional
from globe_server.network_manager.network_service import network_manager as state_machine, connect_to_wifi, scan_available_networks
from globe_server.network_manager.models import NetworkInfo as NetworkInfoModel
from globe_server.network_manager.platform import get_current_connection_info
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/network", tags=["network"])

class WiFiConfig(BaseModel):
    ssid: str
    password: str

# Use our model directly
class WiFiNetwork(BaseModel):
    ssid: str
    signal_strength: int
    security: str
    
    @classmethod
    def from_model(cls, model: NetworkInfoModel) -> 'WiFiNetwork':
        return cls(
            ssid=model.ssid,
            signal_strength=model.signal_strength,
            security=model.security
        )

class WiFiStatus(BaseModel):
    status: str  # FSM state (idle, connecting, connected, etc.)
    current_ssid: str | None  # From OS
    ip_address: str | None  # From OS
    esp32_connected: bool  # From FSM
    error: str | None = None  # From FSM


@router.post("/wifi")
async def configure_wifi(wifi_config: WiFiConfig):
    """Initiate WiFi connection (async operation)."""
    success = await connect_to_wifi(wifi_config.ssid, wifi_config.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to initiate WiFi connection"
        )
    
    return {"message": f"Connection to {wifi_config.ssid} initiated"}


@router.get("/wifi/status", response_model=WiFiStatus)
async def get_wifi_status():
    """Get current WiFi connection status."""
    # Query OS for real-time connection info
    conn_info = await get_current_connection_info()
    
    return WiFiStatus(
        status=state_machine.context.current_state.value,
        current_ssid=conn_info.ssid,
        ip_address=conn_info.ip_address,
        esp32_connected=state_machine.context.esp32_connected,
        error=state_machine.context.error_message
    )

@router.get("/wifi/scan", response_model=dict)
async def scan_networks():
    """Scan for available WiFi networks."""
    network_models = await scan_available_networks()
    networks = [WiFiNetwork.from_model(model) for model in network_models]
    return {"networks": networks}


