# app/api/version.py

from fastapi import APIRouter
from pydantic import BaseModel
import importlib.metadata
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/version", tags=["version"])


class VersionInfo(BaseModel):
    globe_server: str
    earth_viz: str | None


@router.get("/", response_model=VersionInfo)
async def get_version():
    """Get version information for globe-server and earth-viz."""
    
    # Get globe-server version
    try:
        globe_version = importlib.metadata.version("globe-server-backend")
    except importlib.metadata.PackageNotFoundError:
        logger.warning("globe-server-backend package metadata not found")
        globe_version = "unknown"
    
    # Get earth-viz version
    try:
        earth_viz_version = importlib.metadata.version("earth-viz")
    except importlib.metadata.PackageNotFoundError:
        logger.warning("earth-viz package not found")
        earth_viz_version = None
    
    return VersionInfo(
        globe_server=globe_version,
        earth_viz=earth_viz_version
    )
