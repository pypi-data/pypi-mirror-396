"""External API for playback management functionality."""

import logging
from .playback_fsm import PlaybackFSM
from .playback_context import PlaybackContext

logger = logging.getLogger(__name__)

# Create global FSM instance (FSM owns context)
logger.info("Creating playback FSM instance...")
context = PlaybackContext()
playback_fsm = PlaybackFSM(context)
_initialized = False

async def initialize_playback():
    """Initialize the playback manager - should be called during app startup."""
    global _initialized
    if not _initialized:
        logger.info("Initializing media services...")
        await context.media_player.initialize_services()
        
        logger.info("Starting playback FSM")
        await playback_fsm.start()
        _initialized = True
        logger.info("Playback FSM initialized")

async def shutdown_playback():
    """Shutdown the playback manager - should be called during app shutdown."""
    global _initialized
    if _initialized:
        logger.info("Shutting down playback manager")
        await playback_fsm.stop()
        _initialized = False
        logger.info("Playback manager shut down")

# High-level playback control functions for API
async def play() -> bool:
    """Start or resume playback."""
    from .playback_state import PlaybackState
    current_state = context.state_machine.get_state()
    
    if current_state == PlaybackState.PAUSED:
        return await playback_fsm.transition_to('RESUMING')
    else:
        return await playback_fsm.transition_to('STARTING')

async def stop() -> bool:
    """Stop playback."""
    return await playback_fsm.transition_to('STOPPING')

async def pause() -> bool:
    """Pause playback."""
    return await playback_fsm.transition_to('PAUSING')

def get_current_state() -> str:
    """Get current playback state."""
    return context.state_machine.get_state().value
