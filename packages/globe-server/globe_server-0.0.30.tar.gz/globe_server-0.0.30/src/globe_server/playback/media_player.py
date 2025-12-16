import logging
import json
from typing import Dict, Any, Optional
from .media_services import VLCService, EarthVizService, MediaWindowManager
from globe_server.db.schemas import PlanetOptions
from globe_server.db.orm import Media
from globe_server import config

class MediaPlayer:
    """Handles media playback using appropriate players based on media type."""
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create shared media window (manages Qt window with stacked layout)
        self.media_window = MediaWindowManager()
        
        # Create media service managers (no longer manage their own windows)
        self.vlc_service = VLCService()  # Widget ID will be set after window starts
        self.earth_viz_service = EarthVizService()
        
        self.logger.info("MediaPlayer initialized with shared window architecture")
        
    async def initialize_services(self):
        """Initialize all media services."""
        self.logger.info("Initializing media services...")
        
        # Start the shared media window (contains both VLC and earth-viz widgets)
        if not self.media_window.start():
            self.logger.error("Failed to start media window")
            return False
        
        # Get the VLC widget ID (cached from Qt thread, safe to access)
        vlc_widget_id = self.media_window.vlc_widget_id
        if vlc_widget_id is None:
            self.logger.error("Failed to get VLC widget ID from media window")
            return False
        
        self.logger.info(f"Got VLC widget ID (from cache): {vlc_widget_id}")
        
        # Initialize VLC with the widget ID for embedding
        self.vlc_service.widget_id = vlc_widget_id
        if not self.vlc_service.start():
            self.logger.error("Failed to initialize VLC service")
            return False
        self.logger.info("VLC service initialized successfully")
        
        # Initialize Earth-viz service (just marks it as running)
        if not self.earth_viz_service.start():
            self.logger.error("Failed to initialize Earth-viz service")
            return False
        
        # Don't switch to earth-viz yet - let it happen naturally on first play
        # The window starts with VLC view by default (black screen)
        
        self.logger.info("All media services initialized successfully")
        return True

    async def play(self, media_id: int) -> bool:
        """Play a media item."""
        try:
            # Get media info from database
            from globe_server.db.database import get_by_id
            media_info = get_by_id(Media, media_id)
            if not media_info:
                logging.error(f"Media item {media_id} not found")
                return False

            filepath = media_info.filepath
            mediatype = media_info.type
            
            # Play based on media type
            if mediatype in ["image", "video"]:
                return self._play_vlc_media(filepath, mediatype)
            
            elif mediatype in ["planet", "weather"]:
                # Parse options for earth-viz (already validated in DB)
                opts = None
                if media_info.planet_options:
                    try:
                        import json
                        opts_dict = json.loads(media_info.planet_options)
                        opts = PlanetOptions(**opts_dict)
                    except Exception as e:
                        logging.error(f"Failed to parse planet_options: {e}")
                        return False
                
                return await self._play_earth_viz(mediatype, opts)
            
            else:
                logging.error(f"Unsupported media type: {mediatype}")
                return False

        except Exception as e:
            logging.error(f"Error in play(): {e}")
            return False

    def _play_vlc_media(self, filepath: str, mediatype: str) -> bool:
        """Play video or image using VLC service."""
        try:
            # Switch to VLC view in the stacked window
            self.logger.info("Switching to VLC view")
            self.media_window.switch_to_vlc()
            
            # Use VLC service to play the media
            if self.vlc_service.play_media(filepath):
                self.logger.info(f"Started VLC {mediatype} playback")
                return True
            else:
                self.logger.error(f"Failed to start VLC {mediatype} playback")
                return False
            
        except Exception as e:
            self.logger.error(f"Error playing {mediatype} with VLC: {e}")
            return False

    async def _play_earth_viz(self, mode: str, opts: Optional[PlanetOptions]) -> bool:
        """Play earth-viz visualization (planet or weather)."""
        try:
            self.logger.info(f"Starting earth-viz {mode} visualization with options: {opts}")
            
            # Switch to earth-viz view in the stacked window
            self.logger.info("Switching to earth-viz view")
            self.media_window.switch_to_earth_viz()
            
            # Configure based on mode
            if mode == "planet":
                success = await self.earth_viz_service.configure_for_planet(opts)
            elif mode == "weather":
                success = await self.earth_viz_service.configure_for_weather(opts)
            else:
                self.logger.error(f"Unknown earth-viz mode: {mode}")
                return False
            
            if success:
                self.logger.info(f"Successfully configured earth-viz for {mode} mode")
                return True
            else:
                self.logger.error(f"Failed to configure earth-viz for {mode} mode")
                return False
            
        except Exception as e:
            self.logger.error(f"Error starting earth-viz visualization: {e}")
            return False

    def stop(self):
        """Stop playback and clean up resources."""
        logging.info("Stopping playback...")
        
        # Stop VLC playback using the service
        self.vlc_service.stop()
        
    def pause(self):
        """Pause the current playback."""
        self.logger.info("Attempting to pause playback")
        # Use the VLC service to pause playback
        return self.vlc_service.pause()

    def resume(self):
        """Resume the current playback."""
        self.logger.info("Attempting to resume playback")
        # Use the VLC service to resume playback
        return self.vlc_service.resume()
        
    def cleanup(self):
        """Clean up all media services and resources."""
        self.logger.info("Cleaning up media services...")
        
        # Cleanup services
        if hasattr(self, 'vlc_service'):
            self.vlc_service.cleanup()
            
        if hasattr(self, 'earth_viz_service'):
            self.earth_viz_service.cleanup()
        
        # Cleanup shared media window
        if hasattr(self, 'media_window'):
            self.media_window.cleanup()