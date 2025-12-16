"""
Network State Machine - Class-based architecture with preserved logic.

This refactors the existing wifi_state_machine.py to use class-based states
while maintaining all the existing logic and behavior.
"""

from enum import Enum
import logging
import asyncio
from typing import Optional, List, Union
from pydantic import BaseModel

from globe_server import config
from .models import (
    NetworkInfo,
    ConnectionInfo,
    ConnectionType,
    NetworkRole,
    NetworkState,
    WiFiNetwork
)
from .platform import (
    get_current_connection_info,
    enable_ap_mode,
    disable_ap_mode,
    connect_to_network,
    disconnect_from_network
)
from globe_server.hardware.esp32_client import esp32_client, discover_esp32_mdns
from .mdns_manager import mdns_manager
from globe_server.db.orm import NetworkConfig
from globe_server.db.database import get_singleton, update
from globe_server.db.broadcast_queue import broadcast_message

logger = logging.getLogger(__name__)


class NetworkContext:
    """Shared context for all network states."""
    
    def __init__(self):
        # State tracking
        self.current_state: NetworkState = NetworkState.DISCONNECTING
        self.last_state: Optional[NetworkState] = None
        self.error_message: Optional[str] = None
        self.current_ip: Optional[str] = None
        
        # ESP32 state
        self.esp32_connected: bool = False
        
        # Test request flag
        self.test_requested: bool = False
           
        # Network configurations (populated in FSM.start())
        self.networks: List[WiFiNetwork] = []
        
        # Network attempt tracking (like original)
        self.current_network_index: int = 0
        self.current_attempt: int = 0
        
        # Monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None


class NetworkStateBase:
    """Base class for all network states."""
    
    def __init__(self, context: NetworkContext, fsm: 'NetworkFSM'):
        self.context = context
        self.fsm = fsm
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def enter(self) -> Union[bool, str, None]:
        """
        Enter the state and perform its work.
        
        Returns:
            - str: Name of next state to transition to
            - True: Stay in this state
            - False: Transition to FAILED state
            - None: State handles its own transitions
        """
        raise NotImplementedError
    
    async def exit(self) -> bool:
        """Exit the state and clean up resources."""
        return True


class IdleState(NetworkStateBase):
    """IDLE state - Main decision hub for network connections"""
    
    async def enter(self) -> None:
        """Handle the IDLE state - exact logic from original"""
        self.logger.info("=== ENTERING IDLE STATE ===")
        self.logger.info(f"Current network index: {self.context.current_network_index}")
        self.logger.info(f"Current attempt: {self.context.current_attempt}")
        self.logger.info(f"Total networks configured: {len(self.context.networks)}")
        for i, net in enumerate(self.context.networks):
            self.logger.info(f"  Network {i}: role={net.role.value}, ssid={net.ssid}, has_password={bool(net.password)}, is_failed={net.is_failed}")
        
        # Check if we're connected to anything
        conn_info = await get_current_connection_info()
        if conn_info.is_connected:
            # self.logger.info(f"Already connected to network: {conn_info.ssid}")
            
            # # Normalize SSID (Windows adds " 2", " 3" etc for multiple connections)
            # import re
            # normalized_ssid = re.sub(r'\s+\d+$', '', conn_info.ssid) if conn_info.ssid else None
            # self.logger.info(f"Normalised SSID: {normalized_ssid.ssid}")
            # # Check if we're connected to one of our target networks
            # current_network = self.context.networks[self.context.current_network_index]
            # if normalized_ssid == current_network.ssid:
            #     self.logger.info(f"Already connected to target network {current_network.ssid} (OS reports as: {conn_info.ssid}), transitioning to DISCOVERING_ESP32")
            #     await self.fsm.transition_to(NetworkState.DISCOVERING_ESP32)
            #     return
            
            # Connected to wrong network - disconnect first
            self.logger.warning(f"Connected to unexpected network: {conn_info.ssid}, disconnecting")
            await self.fsm.transition_to(NetworkState.DISCOVERING_ESP32)
            return
                
        # Try networks in sequence
        while self.context.current_network_index < len(self.context.networks):
            current_network = self.context.networks[self.context.current_network_index]
            
            # Skip if no credentials
            if not (current_network.ssid and current_network.password):
                self.logger.info(f"No credentials for {current_network.role.value} network")
            # Skip if already failed
            elif current_network.is_failed:
                self.logger.info(f"{current_network.role.value} network marked as failed, skipping")
            # Check attempt limit
            elif self.context.current_attempt >= config.MAX_CONNECTION_ATTEMPTS:
                self.logger.info(f"Max attempts reached for {current_network.role.value} network")
                current_network.is_failed = True
            # Try connection
            else:
                self.logger.info(f"Attempting {current_network.role.value} connection "
                              f"(attempt {self.context.current_attempt + 1}/{config.MAX_CONNECTION_ATTEMPTS})")
                self.context.current_attempt += 1
                await self.fsm.transition_to(NetworkState.CONNECTING)
                return
            
            # Move to next network
            self.context.current_network_index += 1
            self.context.current_attempt = 0
        
        # If we've tried all networks and none worked, go to failed state
        self.logger.error("All network options exhausted")
        self.context.error_message = "Failed to connect to any available network"
        await self.fsm.transition_to(NetworkState.FAILED)


class DisconnectingState(NetworkStateBase):
    """DISCONNECTING state - Gracefully disconnect from current network"""
    
    async def enter(self) -> None:
        self.logger.info("Initiating network disconnect")
        
        try:
            conn_info = await get_current_connection_info()
            
            if conn_info.is_connected:
                self.logger.info(f"Disconnecting from: {conn_info.ssid}")
                
                # Stop mDNS (ignore errors)
                try:
                    await mdns_manager.stop()
                except Exception as e:
                    self.logger.error(f"Failed to stop mDNS: {e}")
                
                # Disconnect from network
                if not await disconnect_from_network():
                    self.logger.error("Failed to disconnect from network")
                    self.context.error_message = "Failed to disconnect from network"
                    await self.fsm.transition_to(NetworkState.FAILED)
                    return
            else:
                self.logger.info("Already disconnected")
            
            # Reset connection state
            self.context.current_ip = None
            self.context.esp32_connected = False
            
            await self.fsm.transition_to(NetworkState.IDLE)
                
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
            self.context.error_message = str(e)
            await self.fsm.transition_to(NetworkState.FAILED)


class ConnectingState(NetworkStateBase):
    """CONNECTING state - Establish network connection"""
    
    async def enter(self) -> None:
        current_network = self.context.networks[self.context.current_network_index]
        
        try:
            # Handle AP mode differently
            if current_network.role == NetworkRole.AP:
                self.logger.info("Enabling AP mode")
                success = await enable_ap_mode()
            else:
                # Regular network connection
                self.logger.info(f"Connecting to network: {current_network.ssid}")
                success = await connect_to_network(current_network.ssid, current_network.password)
            
            if success:
                self.logger.info("Connection successful")
                await self.fsm.transition_to(NetworkState.DISCOVERING_ESP32)
                
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            self.context.error_message = str(e)
            # Only mark as failed if we've exceeded max attempts
            if self.context.current_attempt >= config.MAX_CONNECTION_ATTEMPTS:
                current_network.is_failed = True
            await self.fsm.transition_to(NetworkState.IDLE)  # Back to IDLE to try next option or retry


class DiscoveringESP32State(NetworkStateBase):
    """DISCOVERING_ESP32 state - Look for ESP32 using mDNS and confirm connection"""
    
    async def enter(self) -> None:
        current_network = self.context.networks[self.context.current_network_index]
        
        try:
            # Discover ESP32
            self.logger.info(f"=== ESP32 DISCOVERY START ===")
            self.logger.info(f"Looking for ESP32 with hostname: {config.ESP32_HOSTNAME}")
            self.logger.info(f"ESP32_API_KEY configured: {bool(config.ESP32_API_KEY)}")
            
            esp32_ip = discover_esp32_mdns(hostname=config.ESP32_HOSTNAME)
            
            if not esp32_ip:
                self.logger.error(f"ESP32 discovery returned None - hostname {config.ESP32_HOSTNAME} could not be resolved")
                raise ConnectionError("Failed to discover ESP32")
            
            self.logger.info(f"✓ ESP32 discovered at {esp32_ip}")
            
            # Connect to ESP32
            self.logger.info(f"Attempting to connect to ESP32 at {esp32_ip}")
            esp32_client.ip = esp32_ip
            await esp32_client.get_wifi_status()
            self.logger.info(f"✓ ESP32 connection successful")
            
            # Update state
            self.context.esp32_connected = True
            
            # Handle test network promotion
            if current_network.role == NetworkRole.TEST:
                self.logger.info(f"Promoting test network to external network")
                await self._promote_test_network(current_network)
            
            self.logger.info(f"=== ESP32 DISCOVERY COMPLETE ===")
            await self.fsm.transition_to(NetworkState.CONNECTED)
                
        except Exception as e:
            self.logger.error(f"=== ESP32 DISCOVERY FAILED ===")
            self.logger.error(f"Error: {e}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            current_network.is_failed = True
            await self.fsm.transition_to(NetworkState.IDLE)
    
    async def _promote_test_network(self, test_network):
        """Promote test network to external network"""
        await esp32_client.confirm_network_connection()
        
        # Update external network
        self.context.networks[1].ssid = test_network.ssid
        self.context.networks[1].password = test_network.password
        self.context.networks[1].is_failed = False
        
        # Save to DB
        self.logger.info(f"Saving external network to DB: {test_network.ssid}")
        db_config = get_singleton(NetworkConfig)
        db_config.external_ssid = test_network.ssid
        db_config.external_password = test_network.password
        update(db_config)
        
        # Clear test network
        test_network.ssid = None
        test_network.password = None
        self.context.test_requested = False


class ConnectedState(NetworkStateBase):
    """CONNECTED state - Monitor connection and handle test requests"""
    
    async def enter(self) -> None:
        try:
            # Restart mDNS (critical - ESP32 needs this to find us)
            await mdns_manager.handle_network_change()
            
            # Start monitoring loop
            self.context.monitoring_task = asyncio.create_task(self._monitor_connection())
            await self.context.monitoring_task
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"Connected state failed: {e}")
            self.context.error_message = str(e)
            await self.fsm.transition_to(NetworkState.FAILED)
    
    async def _monitor_connection(self):
        """Monitor connection health"""
        try:
            while True:
                # Handle test request
                if self.context.test_requested:
                    await self._send_test_to_esp32()
                    await self.fsm.transition_to(NetworkState.DISCONNECTING)
                    return
                
                # Check network still connected
                conn_info = await get_current_connection_info()
                if not conn_info.is_connected:
                    self.logger.error("Lost network connection")
                    await self.fsm.transition_to(NetworkState.IDLE)
                    return
                
                # Check ESP32 still reachable
                try:
                    await esp32_client.get_status()
                    self.context.esp32_connected = True
                except Exception:
                    self.logger.error("Lost ESP32 connection")
                    self.context.esp32_connected = False
                    await self.fsm.transition_to(NetworkState.IDLE)
                    return
                
                await asyncio.sleep(5)
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
            await self.fsm.transition_to(NetworkState.FAILED)
    
    async def _send_test_to_esp32(self):
        """Send test network credentials to ESP32"""
        test_network = self.context.networks[0]
        if test_network.ssid and test_network.password:
            try:
                await esp32_client.test_network_connection(
                    test_network.ssid, test_network.password
                )
            except Exception as e:
                self.logger.error(f"Failed to send test to ESP32: {e}")
    
    async def exit(self) -> bool:
        """Stop monitoring when leaving state"""
        if self.context.monitoring_task:
            self.context.monitoring_task.cancel()
            try:
                await self.context.monitoring_task
            except asyncio.CancelledError:
                pass
            self.context.monitoring_task = None
        return True

class FailedState(NetworkStateBase):
    """FAILED state - Terminal error state"""
    
    async def enter(self) -> None:
        """Handle failed state - exact logic from original"""
        self.logger.error(f"System in FAILED state: {self.context.error_message}")
        # Nothing to do in failed state - wait for external reset


class NetworkFSM:
    """Network Finite State Machine - class-based with preserved logic"""
    
    def __init__(self):
        self.context = NetworkContext()
        self.current_state_handler: Optional[NetworkStateBase] = None
        self.state_task: Optional[asyncio.Task] = None
        self._is_transitioning = False
        
        # Validate required configuration
        if not hasattr(config, 'ESP32_HOSTNAME') or not config.ESP32_HOSTNAME:
            raise ValueError("ESP32_HOSTNAME must be configured in config file to initialize NetworkFSM")
        
        # Define valid state transitions
        self._valid_transitions = {
            NetworkState.IDLE: [NetworkState.DISCONNECTING, NetworkState.CONNECTING, NetworkState.DISCOVERING_ESP32, NetworkState.FAILED],
            NetworkState.DISCONNECTING: [NetworkState.IDLE, NetworkState.FAILED],
            NetworkState.CONNECTING: [NetworkState.DISCOVERING_ESP32, NetworkState.IDLE, NetworkState.FAILED],
            NetworkState.DISCOVERING_ESP32: [NetworkState.CONNECTED, NetworkState.IDLE, NetworkState.FAILED],
            NetworkState.CONNECTED: [NetworkState.DISCONNECTING, NetworkState.IDLE, NetworkState.FAILED],
            NetworkState.FAILED: []  # Terminal state - no transitions allowed
        }
        
        # Initialize state handlers
        self.states = {
            NetworkState.IDLE: IdleState(self.context, self),
            NetworkState.DISCONNECTING: DisconnectingState(self.context, self),
            NetworkState.CONNECTING: ConnectingState(self.context, self),
            NetworkState.DISCOVERING_ESP32: DiscoveringESP32State(self.context, self),
            NetworkState.CONNECTED: ConnectedState(self.context, self),
            NetworkState.FAILED: FailedState(self.context, self)
        }
        
        logger.info("Network FSM initialized")
    
    async def start(self):
        """Start the FSM in IDLE state"""
        logger.info("Starting Network FSM")

                # Load external network credentials: DB → .env fallback
        db_config = get_singleton(NetworkConfig)
        if db_config and db_config.external_ssid:
            external_ssid = db_config.external_ssid
            external_password = db_config.external_password
            logger.info(f"Loaded external network from DB: {external_ssid}")
        else:
            external_ssid = config.NETWORK_SSID if hasattr(config, 'NETWORK_SSID') else None
            external_password = config.NETWORK_PASSWORD if hasattr(config, 'NETWORK_PASSWORD') else None
            logger.info(f"Using external network from .env: {external_ssid}")

        # Network configurations (array like original)
        self.context.networks: List[WiFiNetwork] = [
            WiFiNetwork(role=NetworkRole.TEST),
            WiFiNetwork(
                role=NetworkRole.EXTERNAL,
                ssid=external_ssid,
                password=external_password,
            ),
            WiFiNetwork(
                role=NetworkRole.AP,
                ssid=config.AP_SSID if hasattr(config, 'AP_SSID') else None,
                password=config.AP_PASSWORD if hasattr(config, 'AP_PASSWORD') else None,
            )
        ]    
        await self.transition_to(NetworkState.IDLE)
    
    def _validate_transition(self, new_state: NetworkState) -> bool:
        """Validate if the transition from current state to new state is allowed."""
        valid_next_states = self._valid_transitions.get(self.context.current_state, [])
        return new_state in valid_next_states
    
    async def transition_to(self, new_state: NetworkState) -> bool:
        """Transition to a new state with validation"""
        try:
            # If we're already transitioning, don't allow another transition
            if self._is_transitioning:
                logger.warning(f"State transition already in progress, ignoring transition to {new_state}")
                return False
            
            # If we're already in the target state, don't transition
            if self.context.current_state == new_state:
                logger.debug(f"Already in state {new_state}, skipping transition")
                return True
            
            # Validate transition
            if not self._validate_transition(new_state):
                logger.error(f"Invalid state transition: {self.context.current_state.value} -> {new_state.value}")
                logger.error(f"Valid transitions from {self.context.current_state.value}: {[s.value for s in self._valid_transitions.get(self.context.current_state, [])]}")
                return False
            
            # Get state handler
            new_state_handler = self.states.get(new_state)
            if not new_state_handler:
                logger.error(f"Unknown state: {new_state}")
                return False
            
            self._is_transitioning = True
            
            logger.info(f"=== State Transition === \nFrom: {self.context.current_state.value} \nTo: {new_state.value}")
            
            # Exit current state
            if self.current_state_handler:
                await self.current_state_handler.exit()
            
            # Update context
            self.context.last_state = self.context.current_state
            self.context.current_state = new_state
            self.current_state_handler = new_state_handler
            
            # Cancel existing state task
            if self.state_task and not self.state_task.done():
                self.state_task.cancel()
                try:
                    await self.state_task
                except asyncio.CancelledError:
                    pass
            
            # Broadcast status update before allowing nested transitions
            await self._broadcast_status()
            
            # Clear transitioning flag before entering state (allows nested transitions)
            self._is_transitioning = False
            
            # Enter new state (may trigger nested transitions)
            self.state_task = asyncio.create_task(new_state_handler.enter())
            
            return True
            
        except Exception as e:
            logger.error(f"Error during state transition: {e}")
            self.context.error_message = str(e)
            self.context.current_state = NetworkState.FAILED
            self._is_transitioning = False
            return False
    
    async def request_network_test(self, ssid: str, password: str) -> bool:
        """Request a test of new network credentials (original logic)"""
        # Only accept test requests when in CONNECTED state
        if self.context.current_state != NetworkState.CONNECTED:
            logger.warning("Cannot test new network - system not in CONNECTED state")
            return False
            
        # Don't accept new test if one is pending
        if self.context.test_requested:
            logger.warning("Cannot test new network - previous test still pending")
            return False
            
        logger.info(f"Queueing network test request for SSID: {ssid}")

        # Update test network with new credentials
        self.context.networks[0].ssid = ssid
        self.context.networks[0].password = password
        self.context.networks[0].is_failed = False
        
        self.context.test_requested = True
        
        # Reset network index and attempt counter for the test
        self.context.current_network_index = 0
        self.context.current_attempt = 0
        
        return True
    
    def get_state(self) -> NetworkState:
        """Get current state"""
        return self.context.current_state
    
    def is_valid_transition(self, new_state: NetworkState) -> bool:
        """Check if a transition to the new state would be valid without performing it."""
        return self._validate_transition(new_state)
    
    def get_valid_transitions(self) -> List[NetworkState]:
        """Get the list of valid next states from the current state."""
        return self._valid_transitions.get(self.context.current_state, [])

    async def stop(self):
        """Stop the FSM and clean up all resources"""
        logger.info("Stopping Network FSM")
        
        # Stop mDNS (FSM owns this)
        try:
            await mdns_manager.stop()
            logger.info("Stopped mDNS service")
        except Exception as e:
            logger.error(f"Failed to stop mDNS: {e}")
        
        # Cancel monitoring task if running
        if self.context.monitoring_task:
            self.context.monitoring_task.cancel()
            try:
                await self.context.monitoring_task
            except asyncio.CancelledError:
                pass
            self.context.monitoring_task = None
        
        # Cancel state task if running
        if self.state_task:
            self.state_task.cancel()
            try:
                await self.state_task
            except asyncio.CancelledError:
                pass
            self.state_task = None
        
        logger.info("Network FSM stopped")
    
    async def _broadcast_status(self):
        """Broadcast current network status via WebSocket"""
        # Get current connection info from OS
        conn_info = await get_current_connection_info()
        
        status = {
            "status": self.context.current_state.value,
            "current_ssid": conn_info.ssid or "",
            "ip_address": conn_info.ip_address or "",
            "esp32_connected": self.context.esp32_connected,
            "error": self.context.error_message or ""
        }
        
        await broadcast_message("network_status", status)
