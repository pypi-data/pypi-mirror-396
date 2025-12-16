from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging
import asyncio
from globe_server.playback import playback_service
import time
import vlc
import subprocess
from globe_server import config
import os
import json
from typing import List, Optional, Dict, Any

# Create router for REST endpoints
router = APIRouter(prefix="/playback", tags=["playback"])

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# =====================================================================
# API ENDPOINTS
# =====================================================================

@router.post("/play")
async def play_playlist():
    """Start playing the playlist or resume if paused."""
    try:
        if await playback_service.play():
            return JSONResponse({"status": "success", "message": "Playback started/resumed"})
        else:
            return JSONResponse({"status": "error", "message": "Failed to start playback"})
    except Exception as e:
        logging.error(f"Error starting playback: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@router.post("/stop")
async def stop_playback():
    """Stop the current playback."""
    try:
        if await playback_service.stop():
            return JSONResponse({"status": "success", "message": "Playback stopped"})
        else:
            return JSONResponse({"status": "error", "message": "Failed to stop playback"})
    except Exception as e:
        logging.error(f"Error stopping playback: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

@router.post("/pause")
async def pause_item():
    """Pauses the currently playing media item."""
    try:
        if await playback_service.pause():
            return JSONResponse({"status": "success", "message": "Playback paused"})
        else:
            return JSONResponse({"status": "error", "message": "Failed to pause playback"})
    except Exception as e:
        logging.error(f"Error pausing playback: {e}")
        return JSONResponse({"status": "error", "message": str(e)})

