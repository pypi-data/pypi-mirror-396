from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any, Optional, Set, Union
from .playback_context import PlaybackContext
from .playback_state import PlaybackState
import asyncio
import threading
import time
from enum import Enum

class PlaybackStateBase(ABC):
    def __init__(self, context: PlaybackContext):
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def enter(self) -> bool:
        """Actions when entering this state"""
        pass
        
    @abstractmethod
    async def exit(self) -> bool:
        """Actions when exiting this state"""
        pass

class IdleState(PlaybackStateBase):
    async def enter(self) -> Union[bool, str]:
        """Reset playlist and handle startup autoplay"""
        try:
            self.logger.info("Entering IDLE state")
            
            # Reset playlist to ensure clean slate for next playback
            self.logger.info("Resetting playlist to unplayed state")
            if not self.context.reset_playlist():
                self.logger.warning("Failed to reset playlist")
            
            # IDLE is passive - just wait for user action
            # TODO: Add autostart setting check here if needed
            self.logger.info("Staying in IDLE - waiting for user action")
            return True
            
        except Exception as e:
            self.logger.error(f"Error entering IDLE state: {e}")
            return False
        
    async def exit(self) -> bool:
        """Clean up any idle state resources"""
        try:
            self.logger.info("Exiting IDLE state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting IDLE state: {e}")
            return False

class StartingState(PlaybackStateBase):
    async def enter(self) -> Union[bool, str]:
        """Prepare for playback by loading next item"""
        try:
            self.logger.info("Entering STARTING state")
            
            # Get the next playlist item
            next_item = self.context.get_next_playlist_item()
            if not next_item:
                self.logger.info("No items to play")
                return 'IDLE'  # No items to play, go back to IDLE
                
            self.logger.info(f"Found next item: {next_item.id}")
            
            # Use our high-level play_item method to handle all the details
            success, media_item = await self.context.play_item(next_item.id)
            
            if not success or not media_item:
                self.logger.error("Failed to play item")
                return False
                
            # Ready to transition to PLAYING
            return 'PLAYING'
        except Exception as e:
            self.logger.error(f"Error entering STARTING state: {e}")
            return False
        
    async def exit(self) -> bool:
        """Clean up any preparation resources"""
        try:
            self.logger.info("Exiting STARTING state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting STARTING state: {e}")
            return False

class ResumingState(PlaybackStateBase):
    async def enter(self) -> Union[bool, str]:
        """Resume the paused item"""
        try:
            self.logger.info("Entering RESUMING state")
            
            # Resume the currently paused item
            if not self.context.resume_playback():
                self.logger.error("Failed to resume playback")
                return False
            
            # Transition to PLAYING
            self.logger.info("Resume successful, transitioning to PLAYING")
            return 'PLAYING'
            
        except Exception as e:
            self.logger.error(f"Error entering RESUMING state: {e}")
            return False
    
    async def exit(self) -> bool:
        """Clean up any resuming resources"""
        try:
            self.logger.info("Exiting RESUMING state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting RESUMING state: {e}")
            return False

class PlayingState(PlaybackStateBase):
    def __init__(self, context: PlaybackContext):
        super().__init__(context)
        self.playback_task: Optional[asyncio.Task] = None
        self.stop_event = asyncio.Event()

    async def enter(self) -> bool:
        """Start playing the current media item"""
        try:
            self.logger.info("Entering PLAYING state")
            
            # Reset stop event
            self.stop_event.clear()
            
            # Determine if we need to start new playback or resume
            if not self.context.current_playlist_item:
                self.logger.error("No current playlist item to play")
                return False
                
            # Start the playback monitoring task
            self.playback_task = asyncio.create_task(self._monitor_playback())
            
            return True
        except Exception as e:
            self.logger.error(f"Error entering PLAYING state: {e}")
            return False
            
    async def exit(self) -> bool:
        """Clean up playback resources"""
        try:
            self.logger.info("Exiting PLAYING state")
            
            # Get the next state we're transitioning to from the state machine
            next_state = self.context.state_machine._next_state.value.upper() if self.context.state_machine._next_state else None
            self.logger.info(f"Next state during PLAYING exit: {next_state}")
            self.logger.info(f"Raw next state: {self.context.state_machine._next_state}")
            
            # Signal the monitoring task to stop
            self.stop_event.set()
            
            # Cancel the playback monitoring task if it exists
            if self.playback_task and not self.playback_task.done():
                self.playback_task.cancel()
                try:
                    await self.playback_task
                except asyncio.CancelledError:
                    pass
                    
            self.logger.info(f"Next state: {next_state} - Media handling will be done by PlaybackContext")
                
            return True
        except Exception as e:
            self.logger.error(f"Error exiting PLAYING state: {e}")
            return False
        
    async def _monitor_playback(self):
        """Monitor for stop signal and handle natural completion"""
        try:
            # Wait for stop signal (either user-initiated or natural completion)
            while not self.stop_event.is_set():
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
            
            # Stop signal received - determine what to do next
            self.logger.info("Stop signal received - checking what's next")
            
            # Check if there's a next item to play
            next_item = self.context.get_next_playlist_item()
            
            if next_item:
                # More items to play - go directly to STARTING
                self.logger.info(f"Found next item {next_item.id} - transitioning to STARTING")
                await self.context.fsm.transition_to('STARTING')
                return
            
            # No more items - check loop setting
            self.logger.info("No more unplayed items - checking loop setting")
            loop_enabled = self.context.get_loop_setting()
            
            if loop_enabled:
                # Loop is on - reset playlist and start again
                self.logger.info("Loop enabled - resetting playlist")
                if self.context.reset_playlist():
                    self.logger.info("Playlist reset - transitioning to STARTING")
                    await self.context.fsm.transition_to('STARTING')
                    return
                else:
                    self.logger.error("Failed to reset playlist")
            
            # No more items and loop off (or reset failed) - go to STOPPING then IDLE
            self.logger.info("Playlist complete - transitioning to STOPPING")
            await self.context.fsm.transition_to('STOPPING')
            
        except asyncio.CancelledError:
            self.logger.info("Playback monitoring task cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitor task: {e}")

class StoppingState(PlaybackStateBase):
    async def enter(self) -> Union[bool, str]:
        """Ensure all resources are cleaned up"""
        try:
            self.logger.info("Entering STOPPING state")
            
            # Use the high-level stop_playback method to handle all cleanup
            if not self.context.stop_playback():
                self.logger.warning("Failed to stop playback")
                # Continue anyway - we still want to transition to IDLE
                            
            self.logger.info("Cleanup complete, transitioning to IDLE")
            return 'IDLE' # IDLE will decide if we play next item or stay idle
            
        except Exception as e:
            self.logger.error(f"Error entering STOPPING state: {e}")
            return False
        
    async def exit(self) -> bool:
        """Final cleanup before transitioning to IDLE"""
        try:
            self.logger.info("Exiting STOPPING state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting STOPPING state: {e}")
            return False

class ErrorState(PlaybackStateBase):
    async def enter(self) -> bool:
        """Handle error state entry"""
        try:
            self.logger.error("Entering ERROR state")
            
            # Clear current items
            self.context.current_playlist_item = None
            self.context.current_media_item = None
            
            # Reset playback tracker
            self.context.playback_tracker.reset()
            
            # Log the error state
            self.logger.error("Playback system in error state")
            
            return True
        except Exception as e:
            self.logger.error(f"Error entering ERROR state: {e}")
            return False
        
    async def exit(self) -> bool:
        """Clean up error state"""
        try:
            self.logger.info("Exiting ERROR state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting ERROR state: {e}")
            return False

class PausingState(PlaybackStateBase):
    """State for pausing playback"""
    
    async def enter(self) -> Union[bool, str]:
        """Enter the pausing state"""
        self.logger.info("Entering PAUSING state")

        try:
            if not self.context.pause_playback():
                self.logger.error("Failed to pause playback")
                return False
                
            self.logger.info("Successfully paused playback")
                        
        except Exception as e:
            self.logger.error(f"Error updating playlist item status: {e}")
            return False
        
        # Return PAUSED state to transition
        return 'PAUSED'
        
    async def exit(self) -> bool:
        """Clean up any pausing state resources"""
        try:
            self.logger.info("Exiting PAUSING state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting PAUSING state: {e}")
            return False

class PausedState(PlaybackStateBase):
    """State for when playback is paused"""
    
    def __init__(self, context: PlaybackContext):
        super().__init__(context)
        self.stop_event = asyncio.Event()
    
    async def enter(self) -> Union[bool, str]:
        """Enter the paused state"""
        self.logger.info("Entering PAUSED state")
        
        # Start monitoring for resume/stop signals
        asyncio.create_task(self._monitor_pause())
        
        return True
        
    async def exit(self) -> bool:
        """Clean up any paused state resources"""
        try:
            self.logger.info("Exiting PAUSED state")
            return True
        except Exception as e:
            self.logger.error(f"Error exiting PAUSED state: {e}")
            return False
    
    async def _monitor_pause(self):
        """Monitor for resume or stop signals"""
        try:
            while not self.stop_event.is_set():
                # Wait for either resume or stop signal
                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue
                    
            # If we get here, we received a stop signal
            self.logger.info("Stop signal received while paused, transitioning to STOPPING")
            await self.context.fsm.transition_to('STOPPING')
            
        except asyncio.CancelledError:
            self.logger.info("Pause monitoring cancelled")
        except Exception as e:
            self.logger.error(f"Error monitoring pause state: {e}")
    
    def resume(self):
        """Resume playback"""
        self.logger.info("Resume requested, transitioning to RESUMING")
        asyncio.create_task(self.context.fsm.transition_to('RESUMING'))
    
    def stop(self):
        """Stop playback"""
        self.logger.info("Stop requested, transitioning to STOPPING")
        asyncio.create_task(self.context.fsm.transition_to('STOPPING'))

class PlaybackFSM:
    def __init__(self, context: PlaybackContext):
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)
        self._lock = threading.Lock()
        self.next_state: Optional[str] = None
        self._requested_state: Optional[str] = None
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Set this FSM as the context's FSM
        self.context.fsm = self
        
        # Initialize states
        self.states: Dict[str, PlaybackStateBase] = {
            'IDLE': IdleState(context),
            'STARTING': StartingState(context),
            'RESUMING': ResumingState(context),
            'PLAYING': PlayingState(context),
            'STOPPING': StoppingState(context),
            'ERROR': ErrorState(context),
            'PAUSING': PausingState(context),
            'PAUSED': PausedState(context)
        }
        
        # State will be initialized when start() is called
        self._started = False

    async def start(self):
        """Start the playback FSM and initialize the first state."""
        if self._started:
            return
        
        self._started = True
        # Start the transition request monitor
        self._monitor_task = asyncio.create_task(self._monitor_transition_requests())
        # Initialize the first state
        await self.current_state.enter()
    
    async def stop(self):
        """Stop the playback FSM and clean up resources."""
        if not self._started:
            return
        
        self.logger.info("Stopping playback FSM")
        
        # Cancel monitor task
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
        
        # Clean up context resources
        self.context.cleanup()
        
        self._started = False
        self.logger.info("Playback FSM stopped")

    @property
    def current_state(self) -> PlaybackStateBase:
        """Get the current state from the state machine"""
        return self.states[self.context.state_machine.get_state().value.upper()]

    def get_next_state(self) -> Optional[str]:
        """Get the next state to transition to"""
        return self.next_state

    def set_next_state(self, state: str):
        """Set the next state to transition to"""
        self.next_state = state
    
    def request_transition(self, new_state: str) -> None:
        """Request a state transition from sync context (e.g., thread-safe)"""
        self._requested_state = new_state
        self.logger.info(f"Transition to {new_state} requested")
    
    async def _monitor_transition_requests(self):
        """Monitor for transition requests from sync contexts"""
        while True:
            try:
                if self._requested_state:
                    state = self._requested_state
                    self._requested_state = None
                    self.logger.info(f"Processing requested transition to {state}")
                    await self.transition_to(state)
                await asyncio.sleep(0.1)  # Check every 100ms
            except asyncio.CancelledError:
                self.logger.info("Transition monitor cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in transition monitor: {e}")

    async def transition_to(self, new_state: str, is_recursive: bool = False) -> bool:
        """Transition to a new state"""
        try:
            # Only acquire lock if this is not a recursive call
            if not is_recursive:
                self._lock.acquire()
            
            try:
                # Get current state from state machine
                current_state = self.context.state_machine.get_state().value.upper()
                
                # Set the next state in the state machine before exiting
                self.context.state_machine._next_state = PlaybackState(new_state)
                
                # Exit current state
                self.logger.info(f"Exiting {current_state} state")
                if not await self.current_state.exit():
                    self.logger.error(f"Failed to exit {current_state} state")
                    return False
                
                # Update state machine
                if not self.context.state_machine.transition_to(PlaybackState(new_state)):
                    self.logger.error(f"Failed to transition state machine to {new_state}")
                    return False
                
                # Enter new state
                self.logger.info(f"Entering {new_state} state")
                result = await self.current_state.enter()
                
                if isinstance(result, str):
                    # State wants to transition to another state immediately
                    self.logger.info(f"State {new_state} requested immediate transition to {result}")
                    return await self.transition_to(result, is_recursive=True)
                elif result:
                    # State transition successful
                    self.set_next_state(None)
                    # Broadcasting is now handled automatically by SQLAlchemy events
                else:
                    # State transition failed
                    self.logger.error(f"Failed to enter {new_state} state")
                    return False
                
            
                return True
                
            finally:
                # Only release lock if this is not a recursive call
                if not is_recursive:
                    self._lock.release()
                    
        except Exception as e:
            self.logger.error(f"Error during state transition: {e}")
            return False




    def get_current_state(self) -> str:
        """Get the name of the current state"""
        return self.context.state_machine.get_state().value.upper() 