"""
Earth-Viz Service Manager.

This module handles Earth-Viz initialization, monitoring, and control using PyQt WebEngine.
"""

import logging
from typing import Optional

from globe_server.db.schemas import PlanetOptions, PlanetName, WeatherOverlay, AirLevel
from earth_viz_backend.earth_control import (
    set_projection, 
    set_planet_mode, 
    set_air_mode, 
    hideUI,
    enable_full_screen,
    disable_full_screen,
    await_earth_connection
)
class EarthVizService:
    """Manages Earth Visualization service using PyQt WebEngine."""
    
    def __init__(self):
        # Note: Window management is now handled by MediaWindowManager
        # This service only handles earth-viz API configuration
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_running = False
    
    def is_running(self) -> bool:
        """Check if earth-viz service is running and healthy."""
        return self._is_running
    
    def start(self) -> bool:
        """Mark earth-viz service as started (window is managed externally)."""
        self._is_running = True
        self.logger.info("Earth-viz service marked as running")
        return True
    
    def ensure_running(self) -> bool:
        """Ensure earth-viz service is running."""
        if not self.is_running():
            return self.start()
        return True
    
    async def configure_for_planet(self, planet_opts: Optional[PlanetOptions] = None) -> bool:
        """Configure earth-viz for planet visualization."""
        try:
            # Ensure service is running
            if not self.ensure_running():
                self.logger.error("Failed to ensure earth-viz service is running")
                return False
            
            self.logger.info("Waiting for earth-viz client to connect...")
            if not await await_earth_connection(timeout=15.0):
                self.logger.error("Earth-viz client did not connect within 15 seconds")
                return False
            
            self.logger.info("Earth-viz client connected, configuring...")
                
            # Use default options if none are provided
            opts = planet_opts or PlanetOptions(planet_name=PlanetName.EARTH)
            
            # Configure earth-viz
            await hideUI()
            await set_projection('equirectangular')
            await enable_full_screen()
            await set_planet_mode(opts.planet_name.value)
            
            self.logger.info(f"Successfully configured earth-viz for planet mode: {opts.planet_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring earth-viz for planet visualization: {e}")
            return False
    
    async def configure_for_weather(self, weather_opts: Optional[PlanetOptions] = None) -> bool:
        """Configure earth-viz for weather visualization."""
        try:
            # Ensure service is running
            if not self.ensure_running():
                self.logger.error("Failed to ensure earth-viz service is running")
                return False
            
            self.logger.info("Waiting for earth-viz client to connect...")
            if not await await_earth_connection(timeout=15.0):
                self.logger.error("Earth-viz client did not connect within 15 seconds")
                return False
            
            self.logger.info("Earth-viz client connected, configuring...")
            
            # Use safe defaults if options are missing
            level = weather_opts.level.value if weather_opts and weather_opts.level else AirLevel.SURFACE.value
            overlay = weather_opts.overlay.value if weather_opts and weather_opts.overlay else WeatherOverlay.WIND.value
            
            # Configure earth-viz
            await hideUI()
            await set_projection('equirectangular')
            await enable_full_screen()
            await set_air_mode(level, 'wind', overlay)
            
            self.logger.info(f"Successfully configured earth-viz for weather mode: level={level}, overlay={overlay}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring earth-viz for weather visualization: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up earth-viz resources."""
        self._is_running = False
        self.logger.info("Earth-viz service stopped")