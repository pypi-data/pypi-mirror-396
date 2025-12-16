from enum import Enum
import logging
import threading
from typing import Callable, List, Dict, Set

class PlaybackState(Enum):
    """Enumeration of possible playback states"""
    IDLE = 'IDLE'
    STARTING = 'STARTING'
    RESUMING = 'RESUMING'
    PLAYING = 'PLAYING'
    STOPPING = 'STOPPING'
    ERROR = 'ERROR'
    PAUSING = 'PAUSING'
    PAUSED = 'PAUSED'

class PlaybackStateMachine:
    """Manages the state of the playback system"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._state = PlaybackState.IDLE
        self._next_state = None  # Track the state we're transitioning to
        self._lock = threading.Lock()
        self._state_change_callbacks: List[Callable[[PlaybackState, PlaybackState], None]] = []
        self._is_transitioning = False
        
        # Define valid state transitions
        self._valid_transitions: Dict[PlaybackState, List[PlaybackState]] = {
            PlaybackState.IDLE: [PlaybackState.STARTING],
            PlaybackState.STARTING: [PlaybackState.PLAYING, PlaybackState.ERROR],
            PlaybackState.RESUMING: [PlaybackState.PLAYING, PlaybackState.ERROR],
            PlaybackState.PLAYING: [PlaybackState.STARTING, PlaybackState.PAUSING, PlaybackState.STOPPING, PlaybackState.ERROR],
            PlaybackState.STOPPING: [PlaybackState.IDLE, PlaybackState.ERROR],
            PlaybackState.ERROR: [PlaybackState.IDLE],
            PlaybackState.PAUSING: [PlaybackState.PAUSED],
            PlaybackState.PAUSED: [PlaybackState.RESUMING, PlaybackState.STOPPING]
        }

    def _validate_transition(self, new_state: PlaybackState) -> bool:
        """Validate if the transition from current state to new state is allowed."""
        valid_next_states = self._valid_transitions.get(self._state, [])
        return new_state in valid_next_states

    def transition_to(self, new_state: PlaybackState) -> bool:
        """
        Attempt to transition to a new state.
        Returns True if transition was successful, False otherwise.
        """
        with self._lock:
            # If we're already transitioning, don't allow another transition
            if self._is_transitioning:
                logging.warning(f"State transition already in progress, ignoring transition to {new_state}")
                return False

            # If we're already in the target state, don't transition
            if self._state == new_state:
                logging.debug(f"Already in state {new_state}, skipping transition")
                return True

            if not self._validate_transition(new_state):
                logging.error(f"Invalid state transition: {self._state} -> {new_state}")
                return False
                
            try:
                self._is_transitioning = True
                old_state = self._state
                
                # Notify callbacks of state change
                for callback in self._state_change_callbacks:
                    try:
                        callback(old_state, new_state)
                    except Exception as e:
                        logging.error(f"Error in state change callback: {e}")
                
                self._state = new_state  # Update current state after callbacks
                logging.info(f"Playback state changed: {old_state} -> {new_state}")
                return True
            finally:
                self._is_transitioning = False
                self._next_state = None  # Clear next state after transition

    def get_state(self) -> PlaybackState:
        """Get the current state."""
        with self._lock:
            return self._state

    def add_state_change_callback(self, callback: Callable[[PlaybackState, PlaybackState], None]) -> None:
        """Add a callback to be notified of state changes."""
        self._state_change_callbacks.append(callback)

    def is_valid_transition(self, new_state: PlaybackState) -> bool:
        """Check if a transition to the new state would be valid without performing it."""
        with self._lock:
            return self._validate_transition(new_state)

    def get_valid_transitions(self) -> Set[PlaybackState]:
        """Get the set of valid next states from the current state."""
        with self._lock:
            return set(self._valid_transitions.get(self._state, [])) 