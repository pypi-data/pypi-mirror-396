"""
Main application module for Globe Server.

This module initializes the FastAPI application, connects to the database,
and sets up the various API routers.
"""

import os
import sys
import time
import shutil
import platform
import logging
import traceback
import asyncio
import requests

from fastapi import FastAPI, HTTPException, Request
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from globe_server.api import media, playlist, settings, status, motor, update, playback, websocket, version
from globe_server.api.network import router as network_router
from globe_server.network_manager.mdns_manager import mdns_manager
from globe_server.db import orm
from globe_server.db import events  # Import event system
from globe_server import config
from globe_server.network_manager.network_service import shutdown_network_manager, initialize_network_manager
from globe_server.db.broadcast_queue import stop_broadcast_worker,start_broadcast_worker
from earth_viz_backend.services.cloud_scheduler import scheduler
from globe_server.playback.playback_service import shutdown_playback, initialize_playback
from globe_server.hardware.server_hardware import server_hardware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Globe Server API",
    description="API for controlling the Globe Server",
    version="0.1.0",
)


def main():
    """Entry point function for running the server."""
    import uvicorn
    # Start the server with development settings (matching the existing __main__ block)
    uvicorn.run("globe_server.main:app", host="0.0.0.0", port=8000, reload=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(media.router, prefix="/api")
app.include_router(playlist.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(motor.router, prefix="/api")
app.include_router(update.router, prefix="/api")
app.include_router(playback.router, prefix="/api")
app.include_router(network_router, prefix="/api")
app.include_router(version.router, prefix="/api")

# Include Earth-viz routers
try:
    from earth_viz_backend.earth_viz_api import create_earth_viz_router
    from earth_viz_backend.earth_control import create_earth_control_router
    import earth_viz_backend
    
    # Create and mount routers (at root level - they have their own prefixes)
    earth_viz_router = create_earth_viz_router()
    earth_control_router = create_earth_control_router()
    
    app.include_router(earth_viz_router)
    app.include_router(earth_control_router)
    
    # Mount earth-viz static files
    earth_viz_pkg_dir = os.path.dirname(earth_viz_backend.__file__)
    earth_viz_static = os.path.join(earth_viz_pkg_dir, "static")
    app.mount("/earth-viz-app", StaticFiles(directory=earth_viz_static, html=True), name="earth-viz-static")
    logger.info(f"Earth-viz mounted at /earth-viz-app from: {earth_viz_static}")
    
    logger.info("Earth-viz routers mounted successfully")
except ImportError as e:
    logger.warning(f"Earth-viz backend not available: {e}")

# Include WebSocket routers
app.include_router(websocket.router)

# ============================================================================
# FRONTEND SERVING - Toggle between DEV and PRODUCTION modes
# ============================================================================

# --- DEV MODE: Separate frontend server (Vite dev server on port 5173) ---
# Uncomment this block for development with hot reload
'''
@app.get("/")
async def read_root():
    return {"message": "Globe Server API is running"}
'''
# --- PRODUCTION MODE: Serve static frontend from backend ---
# Uncomment this block for production (comment out DEV MODE above)

from fastapi.responses import HTMLResponse

static_dir = os.path.join(os.path.dirname(__file__), "static")

# Serve index.html at root
@app.get("/")
async def read_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r") as f:
        return HTMLResponse(content=f.read())

# Mount static assets LAST (after all routes)
app.mount("/globe-assets", StaticFiles(directory=static_dir), name="globe-assets")

logger.info(f"Frontend static files mounted from: {static_dir}")

# ============================================================================

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = str(exc)
    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR
    
    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_detail = exc.detail
    
    error_id = int(time.time())
    error_info = {
        "error_id": error_id,
        "error": error_detail,
        "path": request.url.path,
    }
    
    # Log the error
    logger.error(f"Error {error_id} at {request.url.path}: {error_detail}")
    logger.error(traceback.format_exc())
    
    # Insert into errors table
    from globe_server.db.database import log_error
    log_error(request.url.path, error_detail, traceback.format_exc())
    
    return JSONResponse(
        status_code=status_code,
        content=error_info,
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Globe Server...")

    # Initialize database using SQLAlchemy ORM
    logger.info("Initializing database...")
    
    # Ensure database directory exists
    from pathlib import Path
    db_path = Path(config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    orm.Base.metadata.create_all(orm.engine)
    
    # Initialize singleton records
    from globe_server.db.database import get_all, create
    if not get_all(orm.Settings):
        logger.info("Creating initial settings record")
        settings = orm.Settings()
        create(settings)
    
    if not get_all(orm.NetworkConfig):
        logger.info("Creating initial network config record")
        network_config = orm.NetworkConfig()
        create(network_config)

    # Initialize event listeners
    logger.info("Initializing database event listeners...")
    events.init_events()
    
    # Start broadcast worker for thread-safe WebSocket broadcasting
    logger.info("Starting broadcast worker...")

    await start_broadcast_worker()
    
    # Initialize playback manager
    logger.info("Initializing playback manager...")
    await initialize_playback()
    
    # Initialize network manager
    logger.info("Initializing network manager...")
    await initialize_network_manager()

    # Start Earth-viz scheduler
    try:
        asyncio.create_task(scheduler.start())
        logger.info("Earth-viz scheduler started")
    except ImportError:
        logger.warning("Earth-viz scheduler not available")
    
    # Start server status polling
    logger.info("Starting server status polling...")
    await server_hardware.start()
    
    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    # Stop playback manager
    try:

        await shutdown_playback()
    except Exception as e:
        logger.error(f"Failed to stop playback manager: {e}")
    
    # Stop network manager (which handles mDNS internally)
    try:
        await shutdown_network_manager()
    except Exception as e:
        logger.error(f"Failed to stop network manager: {e}")
    
    # Stop broadcast worker
    try: 
        await stop_broadcast_worker()
        logger.info("Stopped broadcast worker")
    except Exception as e:
        logger.error(f"Failed to stop broadcast worker: {e}")
    
    # Stop Earth-viz scheduler
    try: 
        await scheduler.stop()
        logger.info("Stopped Earth-viz scheduler")
    except ImportError:
        pass
    
    # Stop server status polling
    try:
        await server_hardware.stop()
    except Exception as e:
        logger.error(f"Failed to stop server status polling: {e}")
    
    # Close database session
    orm.Session.remove()
    
    logger.info("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("globe_server.main:app", host="0.0.0.0", port=8000, reload=True)
