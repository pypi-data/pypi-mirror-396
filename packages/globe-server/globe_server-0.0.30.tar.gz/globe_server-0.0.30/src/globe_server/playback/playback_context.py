import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as SQLAlchemySession
from ..db.database import get_by_id, create, update, get_all, bulk_update
from ..db.orm import PlaylistItem, Media, Settings
from .playback_tracker import PlaybackTracker
from .media_player import MediaPlayer
from .playback_state import PlaybackStateMachine
from globe_server.db.database import get_singleton, get_first_by_status

class PlaybackContext:
    """Manages the state and resources for a playback session."""
    
    def __init__(self):
        # Initialize state machine
        self.state_machine = PlaybackStateMachine()
        
        # Initialize state handling
        self.playback_tracker = PlaybackTracker()
        
        # Register event handlers
        self.playback_tracker.on('time_update', self._handle_time_update)
        self.playback_tracker.on('playback_complete', self._handle_playback_complete)
        
        # Current item tracking
        self.current_playlist_item = None
        self.current_media_item = None
        
        # Initialize media player
        self.media_player = MediaPlayer()
    
    # High-level playback control methods
    
    async def play_item(self, item_id):
        """Play a specific playlist item (new or unplayed items only).
        
        For resuming paused items, use resume_playback() instead.
        
        Args:
            item_id: ID of the playlist item to play
            
        Returns:
            tuple: (success, media_info) - success is boolean, media_info contains media details if successful
        """
        try:
            logging.info(f"Starting playback of item {item_id}")
            
            # 1. Get the playlist item details
            playlist_item = get_by_id(PlaylistItem, item_id)
            if not playlist_item:
                logging.error(f"Cannot play item {item_id}: not found")
                return False, None
            
            # 2. Get the associated media item
            media_item = get_by_id(Media, playlist_item.media_id)
            if not media_item:
                logging.error(f"Cannot play item {item_id}: associated media {playlist_item.media_id} not found")
                return False, None
            
            # 3. Start actual media playback FIRST (fail fast if it won't work)
            logging.info(f"Starting media playback for item {item_id}")
            if not await self.media_player.play(media_item.id):
                logging.error(f"Failed to start media playback for item {item_id}")
                return False, None
            
            # 5. ONLY NOW update state (media is actually playing)
            if not self.update_playlist_item_status(item_id, 'playing'):
                logging.error(f"Failed to mark item {item_id} as playing")
                # Media is playing but DB update failed - stop media and fail
                self.media_player.stop()
                return False, None
            
            # 6. Set as current item in context
            self.current_playlist_item = playlist_item
            self.current_media_item = media_item
            
            # 7. Start the playback tracker from beginning
            duration = media_item.display_duration
            self.playback_tracker.start_tracking(item_id, duration)
            
            logging.info(f"Successfully started playback of item {item_id}")
            return True, media_item
            
        except Exception as e:
            logging.error(f"Error playing item {item_id}: {e}")
            return False, None
            
    def pause_playback(self):
        """Pause the currently playing item.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_playlist_item:
                logging.error("Cannot pause: no item currently playing")
                return False
            
            item_id = self.current_playlist_item.id
            logging.info(f"Pausing playback of item {item_id}")
            
            # 1. Pause the media player first
            self.media_player.pause()
            
            # 2. Pause the playback tracker and get elapsed time
            self.playback_tracker.pause()
            elapsed_time = self.playback_tracker.get_elapsed_time()
            
            # 3. Update database status to paused
            if not self.update_playlist_item_status(item_id, 'paused'):
                logging.error(f"Failed to mark item {item_id} as paused")
                return False
                
            # 4. Update elapsed time
            if not self.update_elapsed_time(item_id, elapsed_time):
                logging.warning(f"Failed to update elapsed time for item {item_id}")
            
            logging.info(f"Successfully paused item {item_id} at {elapsed_time}s")
            return True
            
        except Exception as e:
            logging.error(f"Error pausing playback: {e}")
            return False
            
    def resume_playback(self):
        """Resume the currently paused item.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_playlist_item:
                logging.error("Cannot resume: no item currently paused")
                return False
            
            item_id = self.current_playlist_item.id
            logging.info(f"Resuming playback of item {item_id}")
            
            # 1. Resume the media player first
            if not self.media_player.resume():
                logging.error(f"Failed to resume media playback for item {item_id}")
                return False
                
            # 2. Update database status to 'playing'
            if not self.update_playlist_item_status(item_id, 'playing'):
                logging.error(f"Failed to mark item {item_id} as playing")
                self.media_player.pause()  # Pause it back
                return False
            
            # 3. Resume the playback tracker
            self.playback_tracker.resume()
                    
            logging.info(f"Successfully resumed item {item_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error resuming playback: {e}")
            return False
            
    def stop_playback(self):
        """Stop the currently playing/paused item and mark as played.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.current_playlist_item:
                logging.warning("Stop called but no item currently playing")
                return True  # Not an error, just nothing to stop
            
            item_id = self.current_playlist_item.id
            logging.info(f"Stopping playback of item {item_id}")
            
            # 1. Stop the media player first
            self.media_player.stop()
            
            # 2. Get current elapsed time from tracker
            elapsed_time = self.playback_tracker.get_elapsed_time()
            
            # 3. Mark as played in the database
            if not self.update_playlist_item_status(item_id, 'played'):
                logging.error(f"Failed to mark item {item_id} as played")
            
            logging.info(f"Marked item {item_id} as played with final time {elapsed_time}s")
            
            # 4. Reset tracking and clear context
            self.playback_tracker.reset()
            self.current_playlist_item = None
            self.current_media_item = None
            
            logging.info(f"Successfully stopped playback of item {item_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error stopping playback of item {item_id}: {e}")
            return False

    def get_next_playlist_item(self):
        """Get the next playlist item to play.
        
        Priority: paused items first (max one), then unplayed items by position.
        """
        try:    
            # Check for paused item first (there should only be one max)
            paused_item = get_first_by_status('paused')
            if paused_item:
                return paused_item
            
            # Otherwise get first unplayed item
            return get_first_by_status('unplayed')
            
        except Exception as e:
            logging.error(f"Error getting next playlist item: {e}")
            return None

    def update_playlist_item_status(self, item_id, status):
        """Update a playlist item's status.
        
        Args:
            item_id: ID of the playlist item to update
            status: New status ('playing', 'paused', 'played', 'unplayed')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the playlist item
            item = get_by_id(PlaylistItem, item_id)
            if not item:
                logging.error(f"Playlist item {item_id} not found")
                return False
                
            # Update status
            item.status = status
            
            # Handle special case for 'played' status
            if status == 'played':
                # For 'played' status, set elapsed_time to display_duration
                media = get_by_id(Media, item.media_id)
                if media:
                    item.elapsed_time = media.display_duration
                else:
                    logging.error(f"Media for playlist item {item_id} not found")
                    return False
            
            # Use CRUD function to update
            update(item)
            logging.info(f"Updated item {item_id} status to '{status}'")
            return True
            
        except Exception as e:
            logging.error(f"Error updating item {item_id} status to '{status}': {e}")
            return False
            

    def update_elapsed_time(self, item_id, elapsed_time):
        """Update the elapsed time for a playlist item using ORM.
        
        Args:
            item_id: ID of the playlist item to update
            elapsed_time: New elapsed time value in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the playlist item
            item = get_by_id(PlaylistItem, item_id)
            if not item:
                logging.error(f"Playlist item {item_id} not found")
                return False
            
            # Update elapsed time
            item.elapsed_time = elapsed_time
            update(item)
            
            logging.debug(f"Updated item {item_id} elapsed time to {elapsed_time}s")
            return True
            
        except Exception as e:
            logging.error(f"Error updating elapsed time for item {item_id}: {e}")
            return False

    def reset_playlist(self):
        """Reset all playlist items to unplayed status."""
        try:
            items = get_all(PlaylistItem)
            
            if not items:
                logging.info("No playlist items to reset")
                return False
            
            logging.info(f"Resetting {len(items)} playlist items")
            
            # Update all items in memory
            for item in items:
                item.status = 'unplayed'
                item.elapsed_time = 0
            
            # Save all changes in a single transaction
            bulk_update(items)
            
            logging.info("Playlist reset complete")
            return True
            
        except Exception as e:
            logging.error(f"Error resetting playlist: {e}")
            return False

    def get_loop_setting(self):
        """Get the loop setting from database using ORM."""
        try:

            settings = get_singleton(Settings)
            
            # Convert to boolean - in the database it's stored as an integer (0/1)
            loop_setting = bool(settings.loop) if settings else False
            
            logging.info(f"Retrieved loop setting from database: {loop_setting} (raw value: {settings.loop if settings else None})")
            return loop_setting
            
        except Exception as e:
            logging.error(f"Error getting loop setting: {e}")
            return False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
            
    def cleanup(self):
        """Clean up all resources."""
        logging.info("Cleaning up playback context resources...")
        
        # Clean up the media player if it exists
        if self.media_player:
            self.media_player.cleanup()
            self.media_player = None
        
        # Reset playback tracker
        if hasattr(self, 'playback_tracker'):
            self.playback_tracker.reset()
        
        # Reset state
        self.current_playlist_item = None
        self.current_media_item = None
        
    # Event handlers for tracker
    
    def _handle_time_update(self, data):
        """Just update the DB when time update events come in"""
        self.update_elapsed_time(data['playlist_item_id'], data['elapsed_time'])
        
    def _handle_playback_complete(self, data):
        """Handle the playback complete event"""
        try:
            # Mark the completed item as played
            if self.current_playlist_item:
                item_id = self.current_playlist_item.id
                logging.info(f"Marking completed item {item_id} as played")
                self.update_playlist_item_status(item_id, 'played')
            
            # Signal FSM that playback is complete
            self.fsm.current_state.stop_event.set()
        except Exception as e:
            logging.error(f"Error handling playback complete: {e}")