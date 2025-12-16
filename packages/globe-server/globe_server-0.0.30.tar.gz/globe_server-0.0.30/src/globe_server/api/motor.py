# app/api/motor.py

from fastapi import APIRouter, HTTPException, status
from globe_server import config
from globe_server.hardware.esp32_client import esp32_client, ESP32Error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/motor", tags=["motor"])

@router.post("/start")
async def start_motor():
    try:
        await esp32_client.set_motor_speed(config.MOTOR_RPM)
        return {"message": "Motor started successfully"}
    except ESP32Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

@router.post("/stop")
async def stop_motor():
    try:
        await esp32_client.set_motor_speed(0)
        return {"message": "Motor stopped successfully"}
    except ESP32Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

@router.get("/status")
async def get_motor_status():
    """Get the current motor status."""
    try:
        return await esp32_client.get_status()
    except ESP32Error as e:
        logger.error(f"Error getting motor status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )