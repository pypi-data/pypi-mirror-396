"""ESP32 HTTP client for all communications with the ESP32."""

import logging
import aiohttp
import socket
import psutil
import time
from typing import Optional, Dict, Any, Union
from globe_server import config
from globe_server.db.broadcast_queue import broadcast_message
from globe_server.models.status import ESP32Status

logger = logging.getLogger(__name__)

class ESP32Error(Exception):
    """Base exception for ESP32-related errors"""
    pass

class ESP32ConnectionError(ESP32Error):
    """Raised when there are connection issues with the ESP32"""
    pass


def discover_esp32_mdns(timeout: int = 30, hostname: Optional[str] = None) -> Optional[str]:
    """
    Discover ESP32 using hostname resolution.
    
    Args:
        timeout: Time in seconds to wait for discovery
        hostname: The hostname to resolve (e.g. "globe-71183C")
                 If not provided, discovery will fail
    
    Returns:
        str: IP address if found, None otherwise
    """
    if not hostname:
        logger.warning("No hostname provided for ESP32 discovery")
        return None
        
    # Ensure hostname has .local suffix
    if not hostname.endswith('.local'):
        hostname = f"{hostname}.local"
        
    try:
        logger.info(f"Starting ESP32 discovery for hostname: {hostname}")
        logger.info(f"Using timeout of {timeout} seconds")
        
        # Log current network status
        try:
            network_info = psutil.net_if_addrs()
            logger.info("Current network interfaces:")
            for interface, addrs in network_info.items():
                logger.info(f"Interface {interface}:")
                for addr in addrs:
                    logger.info(f"  {addr.family} - {addr.address}")
        except Exception as e:
            logger.warning(f"Could not get network interface info: {e}")
        
        logger.info(f"Attempting to resolve hostname: {hostname}")
        addrinfo = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addrinfo:
            if family in (socket.AF_INET, socket.AF_INET6):
                ip = sockaddr[0]
                logger.info(f"Resolved {hostname} to {ip}")
                return ip
            
    except Exception as e:
        logger.error(f"Failed to resolve hostname {hostname}: {e}")
        return None
    
    logger.warning(f"Could not resolve hostname: {hostname}")
    return None


class ESP32Client:
    """Client for communicating with the ESP32 via HTTP."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}
        self._ip: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self.status: Optional[Dict[str, Any]] = None
    
    @property
    def ip(self) -> Optional[str]:
        """Get the current ESP32 IP address."""
        return self._ip
    
    @ip.setter
    def ip(self, value: Optional[str]) -> None:
        """Set the ESP32 IP address."""
        self._ip = value
    
    def _get_url(self, endpoint: str) -> str:
        """Build the full URL for an endpoint."""
        if not self._ip:
            raise ESP32ConnectionError("ESP32 IP address not set")
        return f"http://{self._ip}/esp32/{endpoint}"

    async def _ensure_session(self):
        """Ensure we have an active session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the ESP32.
        
        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint
            **kwargs: Additional arguments for the request
            
        Returns:
            Dict containing the response data
            
        Raises:
            ESP32ConnectionError: If there are connection issues
            ESP32Error: If the request fails for other reasons
        """
        await self._ensure_session()
        try:
            # Add headers if not provided
            if 'headers' not in kwargs:
                kwargs['headers'] = self.headers
                
            # Add timeout if not provided
            if 'timeout' not in kwargs:
                kwargs['timeout'] = aiohttp.ClientTimeout(total=5)
                
            async with self._session.request(method, self._get_url(endpoint), **kwargs) as response:
                response.raise_for_status()
                json_response = await response.json()
                
                # Validate response authenticity using API key in headers only
                response_api_key = response.headers.get('X-API-Key')
                if response_api_key != self.api_key:
                    raise ESP32Error("Invalid or missing API key in response headersh")
                
                # Handle ESP32's response format which wraps data in level/data structure
                if isinstance(json_response, dict) and "level" in json_response and "data" in json_response:
                    if json_response["level"] == "error":
                        raise ESP32Error(str(json_response["data"].get("error", "Unknown error")))
                    return json_response["data"]
                return json_response
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Failed to connect to ESP32: {e}")
            raise ESP32ConnectionError(f"Failed to connect to ESP32: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"Request to ESP32 failed: {e}")
            raise ESP32Error(f"Request to ESP32 failed: {e}")

    # Status endpoints
    async def get_status(self) -> Dict[str, Any]:
        """Get the ESP32's system status and broadcast it."""
        try:
            response = await self._make_request("GET", "status")
            
            # Validate response with Pydantic
            status_model = ESP32Status(
                motor_rpm=response.get("motor_rpm", 0.0),
                motor_current=response.get("motor_current", 0.0),
                driver_temperature=response.get("driver_temperature", 0.0),
                driver_status=response.get("driver_status", "unknown"),
                imu_status=response.get("imu_status", False),
                state=response.get("status", "Unknown"),
                error_code=None
            )
            
            # Store and broadcast as dict
            self.status = status_model.model_dump()
            await broadcast_message("hardware_status", self.status)
            
            return self.status
            
        except ESP32Error as e:
            logger.error(f"Error getting ESP32 status: {e}")
            status_model = ESP32Status(
                motor_rpm=0.0,
                motor_current=0.0,
                driver_temperature=0.0,
                driver_status="error",
                imu_status=False,
                state="Error",
                error_code=str(e)
            )
            self.status = status_model.model_dump()
            await broadcast_message("hardware_status", self.status)
            return self.status
        
    async def get_wifi_status(self) -> Dict[str, Any]:
        """Get the ESP32's WiFi status."""
        response = await self._make_request("GET", "wifi_status")
        return response["data"]

    async def get_rpm(self) -> float:
        """Get the current motor RPM."""
        response = await self._make_request("GET", "rpm")
        try:
            return float(response["data"]["motor_rpm"])
        except KeyError as e:
            logger.error(f"Failed to get motor_rpm from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    async def get_imu_status(self) -> bool:
        """Get the IMU status."""
        response = await self._make_request("GET", "imu_status")
        try:
            # Convert any non-zero value to True, zero to False
            return bool(response["data"]["imu_status"])
        except KeyError as e:
            logger.error(f"Failed to get imu_status from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    async def get_temperature(self) -> float:
        """Get the A4964 temperature."""
        response = await self._make_request("GET", "A4964_temperature")
        try:
            return float(response["data"]["A4964_temperature"])
        except KeyError as e:
            logger.error(f"Failed to get A4964_temperature from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    async def get_current(self) -> float:
        """Get the A4964 current."""
        response = await self._make_request("GET", "A4964_current")
        try:
            return float(response["data"]["A4964_current"])
        except KeyError as e:
            logger.error(f"Failed to get A4964_current from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    async def get_a4964_status(self) -> str:
        """Get the A4964 status."""
        response = await self._make_request("GET", "A4964_status")
        try:
            # Convert the status code to a string representation
            status_code = response["data"]["A4964_status"]
            return str(status_code)  # Simple string conversion for now
        except KeyError as e:
            logger.error(f"Failed to get A4964_status from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    async def get_firmware_version(self) -> str:
        """Get the firmware version."""
        response = await self._make_request("GET", "firmware_version")
        try:
            return response["data"]["firmware_version"]
        except KeyError as e:
            logger.error(f"Failed to get firmware_version from response: {response}")
            raise ESP32Error(f"Missing expected key in response: {e}")

    # Control endpoints
    async def set_motor_speed(self, rpm: Union[int, float, str]) -> None:
        """Set the motor speed.
        
        Args:
            rpm: Speed in RPM (0 to stop)
        """
        await self._make_request("POST", "motor", json={"value": str(rpm)})

    async def set_api_key(self, api_key: str) -> None:
        """Set the API key on the ESP32."""
        await self._make_request("POST", "set_api_key", json={"value": api_key})

    # Network test endpoints
    async def test_network_connection(self, ssid: str, password: str) -> bool:
        """Request the ESP32 to test a network connection."""
        try:
            await self._make_request(
                "POST",
                "test_network_connection",
                json={"ssid": ssid, "password": password}
            )
            return True
        except ESP32Error:
            return False

    async def confirm_network_connection(self) -> bool:
        """Request the ESP32 to confirm the current network connection."""
        try:
            await self._make_request("GET", "confirm_network_connection")
            return True
        except ESP32Error:
            return False

    async def close(self):
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

# Create a global instance
esp32_client = ESP32Client(config.ESP32_API_KEY) 