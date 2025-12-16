"""
Pydantic schemas for API validation.

This module defines Pydantic models for API request/response validation,
which work with the SQLAlchemy ORM models through from_orm conversion.
"""

from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, Dict, Any, List, Union
import json
from datetime import datetime
from enum import Enum

# --- Visualization Options (Can't be auto-generated) ---

class PlanetName(str, Enum):
    EARTH = 'earth'
    EARTH_CLOUDS = 'earth-clouds'
    EARTH_LIVE = 'earth-live'
    MERCURY = 'mercury'
    VENUS = 'venus'
    MOON = 'moon'
    MARS = 'mars'
    JUPITER = 'jupiter'
    SATURN = 'saturn'
    SUN = 'sun'

class AirLevel(str, Enum):
    SURFACE = 'surface'
    HPA_850 = '850hPa'
    HPA_700 = '700hPa'
    HPA_500 = '500hPa'
    HPA_250 = '250hPa'
    HPA_70 = '70hPa'
    HPA_10 = '10hPa'

class WeatherOverlay(str, Enum):
    OFF = 'off'
    WIND = 'wind'
    TEMP = 'temp'
    RELATIVE_HUMIDITY = 'relative_humidity'
    MEAN_SEA_LEVEL_PRESSURE = 'mean_sea_level_pressure'
    TOTAL_PRECIPITABLE_WATER = 'total_precipitable_water'
    TOTAL_CLOUD_WATER = 'total_cloud_water'

class PlanetOptions(BaseModel):
    """Planet visualization options."""
    planet_name: Optional[PlanetName] = None
    level: Optional[AirLevel] = None
    overlay: Optional[WeatherOverlay] = None
    
    model_config = ConfigDict(
        json_schema_extra={"example": {"planet_name": "earth-live"}}
    )

# --- Media Schemas ---

class MediaBase(BaseModel):
    """Base schema for media items."""
    type: str
    name: str
    display_duration: int
    filepath: Optional[str] = None
    planet_options: Optional[Union[PlanetOptions, Dict[str, Any]]] = None
    
    @validator("planet_options", pre=True)
    def parse_planet_options(cls, value):
        if value is None:
            return None
            
        # If the value is a string (JSON), parse it into a dict first
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in planet_options")
                
        return value

class MediaCreate(MediaBase):
    """Schema for creating new media items."""
    pass

class MediaUpdate(MediaBase):
    """Schema for updating existing media items."""
    type: Optional[str] = None
    name: Optional[str] = None
    display_duration: Optional[int] = None
    filepath: Optional[str] = None
    planet_options: Optional[Union[PlanetOptions, Dict[str, Any]]] = None

class MediaRead(MediaBase):
    """Schema for reading media items."""
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- PlaylistItem Schemas ---

class PlaylistItemBase(BaseModel):
    """Base schema for playlist items."""
    media_id: int
    position: int
    status: str
    elapsed_time: float = 0.0

class PlaylistItemCreate(PlaylistItemBase):
    """Schema for creating new playlist items."""
    pass

class PlaylistItemUpdate(BaseModel):
    """Schema for updating existing playlist items."""
    media_id: Optional[int] = None
    position: Optional[int] = None
    status: Optional[str] = None
    elapsed_time: Optional[float] = None

class PlaylistItemRead(PlaylistItemBase):
    """Schema for reading playlist items.
    
    Note: Does not include nested media object to avoid lazy-loading issues.
    Frontend should join media data using media_id from the /api/media endpoint.
    """
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Settings Schemas ---

class SettingsBase(BaseModel):
    """Base schema for settings."""
    autoplay: int = 1
    autostart: int = 1
    loop: int = 1
    red_brightness: int = 255
    green_brightness: int = 255
    blue_brightness: int = 255

class SettingsUpdate(BaseModel):
    """Schema for updating settings."""
    autoplay: Optional[int] = None
    autostart: Optional[int] = None
    loop: Optional[int] = None
    red_brightness: Optional[int] = None
    green_brightness: Optional[int] = None
    blue_brightness: Optional[int] = None

class SettingsRead(SettingsBase):
    """Schema for reading settings."""
    id: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Network Config Schemas ---

class NetworkConfigBase(BaseModel):
    """Schema for persistent network configuration."""
    external_ssid: Optional[str] = None
    external_password: Optional[str] = None

class NetworkConfigCreate(NetworkConfigBase):
    """Schema for creating network config."""
    pass

class NetworkConfigUpdate(NetworkConfigBase):
    """Schema for updating network config."""
    pass

class NetworkConfigRead(NetworkConfigBase):
    """Schema for reading network config."""
    id: int = 1
    updated_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Error Schemas ---

class ErrorLogBase(BaseModel):
    """Schema for error logs."""
    endpoint: Optional[str] = None
    message: Optional[str] = None
    stacktrace: Optional[str] = None

class ErrorLogCreate(ErrorLogBase):
    """Schema for creating error logs."""
    pass

class ErrorLogRead(ErrorLogBase):
    """Schema for reading error logs."""
    id: int
    timestamp: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
