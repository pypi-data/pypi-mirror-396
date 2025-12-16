"""
VLC Service Manager.

This module handles VLC initialization, monitoring, and control.
"""

import logging
import os
import platform
import time
import vlc
from typing import Optional, Any

class VLCService:
    """Manages VLC media player service."""
    
    def __init__(self, widget_id: Optional[int] = None):
        self.vlc_instance: Optional[Any] = None
        self.vlc_player: Optional[Any] = None
        self.widget_id = widget_id
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def is_running(self) -> bool:
        """Check if VLC service is running and healthy."""
        return (self.vlc_instance is not None and 
                self.vlc_player is not None)
    
    def start(self) -> bool:
        """Start the VLC service."""
        try:
            # Find VLC installation on Windows
            if platform.system().lower() == 'windows':
                possible_paths = [
                    os.path.join("C:\\Program Files\\VideoLAN\\VLC"),
                    os.path.join("C:\\Program Files (x86)\\VideoLAN\\VLC"),
                    os.getenv("VLC_PATH", "")
                ]
                
                vlc_path = None
                for path in possible_paths:
                    if path and os.path.exists(path):
                        vlc_path = path
                        break
                
                if vlc_path:
                    os.environ["PATH"] = vlc_path + os.pathsep + os.environ["PATH"]
                    self.logger.info(f"Using VLC from: {vlc_path}")
            
            # Create VLC instance and player
            self.vlc_instance = vlc.Instance('--no-audio')
            self.vlc_player = self.vlc_instance.media_player_new()
            
            # Embed VLC in Qt widget if widget_id is provided
            if self.widget_id is not None:
                system = platform.system().lower()
                if system == 'windows':
                    self.vlc_player.set_hwnd(self.widget_id)
                    self.logger.info(f"VLC embedded in Qt widget (Windows hwnd: {self.widget_id})")
                elif system == 'linux':
                    self.vlc_player.set_xwindow(self.widget_id)
                    self.logger.info(f"VLC embedded in Qt widget (Linux xwindow: {self.widget_id})")
                elif system == 'darwin':
                    self.vlc_player.set_nsobject(self.widget_id)
                    self.logger.info(f"VLC embedded in Qt widget (macOS nsobject: {self.widget_id})")
            else:
                # Fallback to fullscreen mode if no widget provided
                self.vlc_player.set_fullscreen(True)
                self.logger.info("VLC running in standalone fullscreen mode")
            
            self.logger.info("VLC service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VLC service: {e}")
            return False
    
    def ensure_running(self) -> bool:
        """Ensure VLC service is running, restart if crashed."""
        if not self.is_running():
            self.logger.warning("VLC service not running, attempting to restart...")
            return self.start()
        return True
    
    def play_media(self, filepath: str, duration: Optional[int] = None) -> bool:
        """Play media file using VLC."""
        try:
            # Ensure service is running
            if not self.ensure_running():
                self.logger.error("Failed to ensure VLC service is running")
                return False
                
            # Set up media with optional duration (useful for images)
            if duration:
                media = self.vlc_instance.media_new(filepath, f':duration={duration}')
            else:
                media = self.vlc_instance.media_new(filepath)
                
            self.vlc_player.set_media(media)
            
            # Start playback
            self.vlc_player.play()
            self.logger.info(f"Started VLC playback of {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error playing media with VLC: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop playback."""
        try:
            if self.vlc_player:
                self.vlc_player.stop()
                self.logger.info("Stopped VLC playback")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error stopping VLC playback: {e}")
            return False
    
    def pause(self) -> bool:
        """Pause the current playback."""
        try:
            if not self.vlc_player:
                self.logger.info("No VLC player found")
                return False
                
            # Get current state before pause
            current_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state before pause: {current_state}")
            
            # Try the pause sequence
            self.vlc_player.set_pause(1)
            
            # Give VLC a moment to process the state change
            time.sleep(0.1)
            
            # Verify state after pause
            new_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state after pause: {new_state}")
            
            if new_state == vlc.State.Playing:
                self.logger.error("Failed to pause VLC playback")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error pausing VLC: {e}")
            return False
    
    def resume(self) -> bool:
        """Resume the current playback."""
        try:
            if not self.vlc_player:
                self.logger.info("No VLC player found")
                return False
                
            # Get current state before resume
            current_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state before resume: {current_state}")
            
            # Try the resume sequence
            self.vlc_player.set_pause(0)
            
            # Give VLC a moment to process the state change
            time.sleep(0.1)
            
            # Verify state after resume
            new_state = self.vlc_player.get_state()
            self.logger.info(f"VLC state after resume: {new_state}")
            
            if new_state == vlc.State.Paused:
                self.logger.error("Failed to resume VLC playback")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error resuming VLC: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up VLC resources."""
        if self.vlc_player:
            self.vlc_player.stop()
            self.vlc_player.release()
            self.vlc_player = None
            
        if self.vlc_instance:
            self.vlc_instance.release()
            self.vlc_instance = None
            
        self.logger.info("VLC resources cleaned up")
