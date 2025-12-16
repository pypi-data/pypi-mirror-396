"""External API for network management functionality."""

import logging
from typing import List
from .network_fsm import NetworkFSM
from .models import NetworkInfo, NetworkState, NetworkRole
from .platform import scan_networks
import asyncio

logger = logging.getLogger(__name__)

# Create global FSM instance that manages all network operations
logger.info("Creating network FSM instance...")
network_manager = NetworkFSM()
_initialized = False

async def initialize_network_manager():
    """Initialize the network manager - should be called during app startup."""
    global _initialized
    if not _initialized:
        logger.info("Starting network state machine")
        await network_manager.start()
        logger.info("Transitioning network state machine to IDLE state")
        logger.info(f"Current FSM state before transition: {network_manager.context.current_state}")
        result = await network_manager.transition_to(NetworkState.IDLE)
        logger.info(f"Transition result: {result}")
        logger.info(f"Current FSM state after transition: {network_manager.context.current_state}")
        _initialized = True
        logger.info("Network state machine initialized")

async def shutdown_network_manager():
    """Shutdown the network manager - should be called during app shutdown."""
    global _initialized
    if _initialized:
        logger.info("Shutting down network manager")
        await network_manager.stop()
        _initialized = False
        logger.info("Network manager shut down")

async def connect_to_wifi(ssid: str, password: str) -> bool:
    """
    Request to connect to a specific WiFi network.
    
    Args:
        ssid: Network SSID
        password: Network password
        
    Returns:
        bool: True if request was accepted
    """
    # If we're in CONNECTED state, treat this as a test request
    if network_manager.context.current_state == NetworkState.CONNECTED:
        return await network_manager.request_network_test(ssid, password)
    
    # Otherwise, update external network credentials and restart from IDLE
    external_network = next(
        (net for net in network_manager.context.networks if net.role == NetworkRole.EXTERNAL),
        None
    )
    if external_network:
        external_network.ssid = ssid
        external_network.password = password
        external_network.is_failed = False
        await network_manager.transition_to(NetworkState.IDLE)
        return True
    return False

async def scan_available_networks() -> List[NetworkInfo]:
    """
    Scan for available WiFi networks.
    
    Returns:
        List[NetworkInfo]: List of discovered networks
    """
    return await scan_networks() 