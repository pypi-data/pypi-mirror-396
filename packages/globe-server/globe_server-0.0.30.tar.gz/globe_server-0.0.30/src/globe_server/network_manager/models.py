"""Common data models for network functionality."""

from enum import Enum
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel


# Platform/Connection Types
class ConnectionType(Enum):
    """Types of network connections (platform-level)"""
    WIFI = "wifi"
    AP = "ap"
    NONE = "none"
    UNKNOWN = "unknown"
    ETHERNET = "ethernet"


# FSM Network Roles
class NetworkRole(Enum):
    """Role/priority of networks in FSM connection sequence"""
    TEST = "test"        # Temporary test network
    EXTERNAL = "external"  # Main external network (user's WiFi)
    AP = "ap"            # Access point fallback


# FSM States
class NetworkState(Enum):
    """Network FSM states"""
    IDLE = "idle"                          # Decision hub for network selection
    DISCONNECTING = "disconnecting"        # Gracefully disconnecting from current network
    CONNECTING = "connecting"              # Establishing network connection
    DISCOVERING_ESP32 = "discovering_esp32"  # Looking for ESP32 via mDNS
    CONNECTED = "connected"                # Stable connection established
    FAILED = "failed"                      # Terminal error state


# Data Models
@dataclass
class ConnectionInfo:
    """Structured data for current network connection (from OS)"""
    type: ConnectionType
    ssid: Optional[str]
    ip_address: Optional[str]
    interface_name: Optional[str]
    is_connected: bool


class NetworkInfo(BaseModel):
    """Model for WiFi network scan results"""
    ssid: str
    signal_strength: int
    security: str


class WiFiNetwork(BaseModel):
    """Model for a configured WiFi network in FSM"""
    role: NetworkRole
    ssid: Optional[str] = None
    password: Optional[str] = None
    is_failed: bool = False
