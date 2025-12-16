from fastapi import APIRouter
from .status import router as status_router
from .media import router as media_router
from .motor import router as motor_router
from .playlist import router as playlist_router
from .playback import router as playback_router
from .update import router as update_router
from .settings import router as settings_router
from .version import router as version_router


api_router = APIRouter()

api_router.include_router(status_router)
api_router.include_router(media_router)
api_router.include_router(motor_router)
api_router.include_router(playlist_router)
api_router.include_router(playback_router)
api_router.include_router(update_router)
api_router.include_router(settings_router)
api_router.include_router(version_router)

