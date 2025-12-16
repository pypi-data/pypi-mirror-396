"""Base interface for network operations."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from globe_server.network_manager.models import NetworkInfo, ConnectionInfo

class NetworkError(Exception):
    """Base exception for network-related errors"""
    pass

class BaseNetworkManager(ABC):
    """Base interface for network operations"""
    
    @abstractmethod
    async def run_command(self, cmd: list[str]) -> Tuple[str, str]:
        """Run a system command and return stdout and stderr"""
        pass
    
    @abstractmethod
    async def connect_to_network(self, ssid: str, password: str) -> bool:
        """Connect to a WiFi network"""
        pass
        
    @abstractmethod
    async def disconnect_from_network(self) -> bool:
        """Disconnect from current network"""
        pass
        
    @abstractmethod
    async def scan_networks(self) -> List[NetworkInfo]:
        """Scan for available networks"""
        pass
        
    @abstractmethod
    async def get_current_connection_info(self) -> ConnectionInfo:
        """Get current connection information"""
        pass
        
    @abstractmethod
    async def enable_ap_mode(self) -> bool:
        """Enable Access Point mode"""
        pass
        
    @abstractmethod
    async def disable_ap_mode(self) -> bool:
        """Disable Access Point mode"""
        pass
        
    @abstractmethod
    async def is_ap_mode_active(self) -> bool:
        """Check if AP mode is active"""
        pass
