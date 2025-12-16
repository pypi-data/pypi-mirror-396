"""Playback tracker for monitoring media playback progress."""

import logging
import time
import threading
from typing import Optional, Dict, Any

from .event_emitter import EventEmitter


class PlaybackTracker(EventEmitter):
    """Event-driven playback tracker.
    
    Events emitted:
    - time_update: {playlist_item_id, elapsed_time, remaining_time}
    - playback_complete: {playlist_item_id}
    - playback_paused: {playlist_item_id, elapsed_time}
    - playback_resumed: {playlist_item_id, elapsed_time}
    - playback_reset: {}
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = None
        self.total_time_played = 0.0
        self.duration = 0
        self.playlist_item_id = None
        self.is_paused = False
        self.update_interval = 0.1  # 100ms
        self.timer = None
        self.logger.info("PlaybackTracker initialized")

    def start_tracking(self, playlist_item_id: int, duration: int):
        """Start tracking playback time for an item."""
        self.logger.info(f"Starting to track item {playlist_item_id} with duration {duration}s")
        self.playlist_item_id = playlist_item_id
        self.duration = duration
        self.total_time_played = 0.0
        self.start_time = time.time()
        self.is_paused = False
        
        # Cancel any existing timer
        self._cancel_timer()
        
        # Start the timer
        self._schedule_next_update()

    def pause(self):
        """Pause the playback tracking."""
        if not self.is_paused and self.playlist_item_id is not None:
            self.logger.info(f"Pausing playback tracking for item {self.playlist_item_id}")
            self.is_paused = True
            
            # Add the time played since last start/resume to our total
            if self.start_time is not None:
                self.total_time_played += (time.time() - self.start_time)
                self.start_time = None
            
            # Cancel the timer
            self._cancel_timer()
            
            # Emit pause event
            elapsed_time = self.get_elapsed_time()
            self.logger.info(f"Paused with total time played: {elapsed_time}s")
            self.emit('playback_paused', {
                'playlist_item_id': self.playlist_item_id,
                'elapsed_time': elapsed_time
            })

    def resume(self):
        """Resume the playback tracking."""
        if self.is_paused and self.playlist_item_id is not None:
            self.logger.info(f"Resuming playback tracking for item {self.playlist_item_id}")
            self.is_paused = False
            self.start_time = time.time()
            
            # Restart timer
            self._schedule_next_update()
            
            # Emit resume event
            elapsed_time = self.get_elapsed_time()
            self.logger.info(f"Resumed with total time played: {elapsed_time}s")
            self.emit('playback_resumed', {
                'playlist_item_id': self.playlist_item_id,
                'elapsed_time': elapsed_time
            })

    def get_elapsed_time(self) -> float:
        """Get the elapsed playback time in seconds."""
        if self.start_time is None:
            return self.total_time_played
            
        if self.is_paused:
            return self.total_time_played
        else:
            return self.total_time_played + (time.time() - self.start_time)
    
    def get_remaining_time(self) -> float:
        """Get the remaining playback time in seconds."""
        elapsed = self.get_elapsed_time()
        remaining = max(0.0, self.duration - elapsed)
        return remaining

    def is_complete(self) -> bool:
        """Check if playback is complete."""
        elapsed = self.get_elapsed_time()
        return elapsed >= self.duration

    def reset(self):
        """Reset the playback tracker."""
        self.logger.info("Resetting playback tracker")
        
        # Cancel any pending timer
        self._cancel_timer()
        
        # Reset state
        self.start_time = None
        self.total_time_played = 0.0
        self.duration = 0
        self.is_paused = False
        old_id = self.playlist_item_id
        self.playlist_item_id = None
        
        # Emit reset event
        self.emit('playback_reset', {'previous_item_id': old_id})
        self.logger.info("Playback tracker reset")
    
    def _cancel_timer(self):
        """Cancel any pending timer."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
    
    def _schedule_next_update(self):
        """Schedule the next time update."""
        if not self.is_paused and self.playlist_item_id is not None:
            self.timer = threading.Timer(self.update_interval, self._emit_update)
            self.timer.daemon = True
            self.timer.start()
    
    def _emit_update(self):
        """Emit a time update event."""
        try:
            # Calculate current times
            elapsed = self.get_elapsed_time()
            remaining = self.get_remaining_time()
            
            # Emit time update event
            self.emit('time_update', {
                'playlist_item_id': self.playlist_item_id,
                'elapsed_time': elapsed,
                'remaining_time': remaining
            })
            
            # Check if complete
            if elapsed >= self.duration:
                self.logger.info(f"Playback complete for item {self.playlist_item_id}")
                self.emit('playback_complete', {'playlist_item_id': self.playlist_item_id})
                return  # Don't schedule next update
                
            # Schedule next update
            self._schedule_next_update()
        except Exception as e:
            self.logger.error(f"Error in _emit_update: {e}")
            # Try to reschedule anyway
            self._schedule_next_update()