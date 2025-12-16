from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ServerStatus(BaseModel):
    """Server status including process and resource information."""
    uptime: float = Field(..., description="Server uptime in seconds")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    database_connected: bool = Field(..., description="Whether database connection is active")
    error: Optional[str] = Field(None, description="Error message if any")

class ESP32Status(BaseModel):
    """Status of the motor PCB hardware"""
    motor_rpm: float = Field(..., description="Current motor RPM")
    motor_current: float = Field(..., description="Current draw in Amps")
    driver_temperature: float = Field(..., description="Temperature in Celsius")
    driver_status: str = Field(..., description="A4964 driver status")
    imu_status: bool = Field(..., description="imu status message")
    state : str = Field(..., description="Current state of the ESP32")
    error_code: Optional[str] = Field(None, description="Error code if any")

class NetworkStatus(BaseModel):
    """Network connectivity status"""
    esp32_connected: bool = Field(..., description="Whether ESP32 is responding to network requests")
    esp32_ip: Optional[str] = Field(None, description="ESP32's IP address")
    wifi_network: Optional[str] = Field(None, description="Currently connected WiFi network")
    wifi_signal: Optional[int] = Field(None, description="WiFi signal strength in dBm")
    ap_mode: bool = Field(..., description="Whether in Access Point mode")
    server_ip: Optional[str] = Field(None, description="Server's IP address") 

