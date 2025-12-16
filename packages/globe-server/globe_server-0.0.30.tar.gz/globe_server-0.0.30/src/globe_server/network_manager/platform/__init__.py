"""Platform-specific network manager factory."""

import platform
from typing import List, Optional, Tuple
import logging
from .base_network import BaseNetworkManager
from globe_server.network_manager.models import NetworkInfo, ConnectionInfo

logger = logging.getLogger(__name__)

# Import platform-specific implementations
def get_network_manager() -> BaseNetworkManager:
    """Factory function to get the appropriate network manager based on platform"""
    if platform.system() == 'Windows':
        from .windows_network import WindowsNetworkManager
        return WindowsNetworkManager()
    else:
        from .linux_network import LinuxNetworkManager
        return LinuxNetworkManager()

# Create a singleton instance
_network_manager = None

def get_manager_instance() -> BaseNetworkManager:
    """Get or create the singleton network manager instance"""
    global _network_manager
    if _network_manager is None:
        _network_manager = get_network_manager()
    return _network_manager

# Proxy functions to the network manager instance for backward compatibility
async def connect_to_network(ssid: str, password: str) -> bool:
    return await get_manager_instance().connect_to_network(ssid, password)

async def disconnect_from_network() -> bool:
    return await get_manager_instance().disconnect_from_network()

async def scan_networks() -> List[NetworkInfo]:
    return await get_manager_instance().scan_networks()

async def get_current_connection_info() -> ConnectionInfo:
    return await get_manager_instance().get_current_connection_info()

async def enable_ap_mode() -> bool:
    return await get_manager_instance().enable_ap_mode()

async def disable_ap_mode() -> bool:
    return await get_manager_instance().disable_ap_mode()

async def is_ap_mode_active() -> bool:
    return await get_manager_instance().is_ap_mode_active()
