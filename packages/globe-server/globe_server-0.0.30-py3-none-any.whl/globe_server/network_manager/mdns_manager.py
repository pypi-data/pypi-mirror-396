"""mDNS service manager for advertising the Globe server."""

import logging
import asyncio
import json
from typing import Optional
from zeroconf import Zeroconf, ServiceInfo, IPVersion
from zeroconf.asyncio import AsyncZeroconf
import socket
from globe_server import config
from .platform import get_current_connection_info
from .models import ConnectionType

logger = logging.getLogger(__name__)

class MDNSManager:
    """Manages mDNS service advertising for the Globe server."""
    
    def __init__(self):
        self.aiozc: Optional[AsyncZeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self._port: Optional[int] = None
        
    async def start(self, port: int = 8000):
        """Start mDNS service advertising.
        
        Args:
            port: Port number the backend is running on (default: 8000)
        """
        self._port = port
        await self._register_service()
            
    async def _register_service(self):
        """Register the mDNS service with current network details."""
        try:
            # Stop any existing service first
            await self.stop()
            
            # Get current connection info from network manager
            conn_info = await get_current_connection_info()
            if not conn_info.is_connected or not conn_info.ip_address:
                logger.warning("No active network connection, cannot register mDNS service")
                return
                
            # Initialize AsyncZeroconf with both IPv4 and IPv6 support
            self.aiozc = AsyncZeroconf(ip_version=IPVersion.All)
            
            # Get ESP32 identifier from hostname
            esp_id = config.ESP32_HOSTNAME.split('-')[-1] if config.ESP32_HOSTNAME else 'unknown'
            
            # Create hostname for the server
            hostname = f"globe-server-{esp_id}"
            
            # Create service info with unique name based on ESP32 identifier
            service_type = "_globe._tcp.local."
            service_name = hostname
            
            # Create properties dict with byte keys and values
            # Include direct URLs that users can copy-paste
            frontend_url = f"http://{hostname}.local:{self._port}"
            api_url = f"http://{hostname}.local:{self._port}/api"
            ws_url = f"ws://{hostname}.local:{self._port}/ws"
            
            properties = {
                b'version': b'1.0',
                b'type': b'globe-server',
                b'hostname': hostname.encode('utf-8'),
                b'esp_id': esp_id.encode('utf-8'),
                b'network_type': conn_info.type.value.encode('utf-8'),
                b'ip_address': conn_info.ip_address.encode('utf-8'),
                b'port': str(self._port).encode('utf-8'),
                b'frontend_url': frontend_url.encode('utf-8'),
                b'api_url': api_url.encode('utf-8'),
                b'ws_url': ws_url.encode('utf-8')
            }
            
            # Create service info that includes both the service and hostname records
            self.service_info = ServiceInfo(
                service_type,
                f"{service_name}.{service_type}",
                addresses=[socket.inet_aton(conn_info.ip_address)],
                port=self._port,  # Use the backend port for direct connections
                properties=properties,
                server=f"{hostname}.local."  # This is key for hostname resolution
            )
            
            # Register service
            await self.aiozc.async_register_service(self.service_info)
            logger.info(f"mDNS service registered: {service_name} at {conn_info.ip_address}:{self._port}")
            logger.info("Available URLs:")
            logger.info(f"  Frontend: {frontend_url}")
            logger.info(f"  API: {api_url}")
            logger.info(f"  WebSocket: {ws_url}")
            
        except Exception as e:
            logger.error(f"Failed to register mDNS service: {e}")
            if self.aiozc:
                await self.aiozc.async_close()
                self.aiozc = None
            raise
    
    async def stop(self):
        """Stop mDNS service advertising."""
        if self.aiozc:
            try:
                if self.service_info:
                    await self.aiozc.async_unregister_service(self.service_info)
                await self.aiozc.async_close()
                logger.info("mDNS service stopped")
            except Exception as e:
                logger.error(f"Error stopping mDNS service: {e}")
            finally:
                self.aiozc = None
                self.service_info = None
                
    async def handle_network_change(self):
        """Handle network change by re-registering the service."""
        if self._port is not None:  # Only restart if we were previously started
            logger.info("Network changed, re-registering mDNS service")
            await self._register_service()

# Create a global instance
mdns_manager = MDNSManager() 