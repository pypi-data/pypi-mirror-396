# app/api/settings.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from globe_server.db.orm import Settings
from globe_server.db.schemas import SettingsRead, SettingsUpdate
from globe_server.db.database import get_singleton, update, get_all
from globe_server.utils import uart  # Import the uart module
from globe_server import config
import logging

router = APIRouter(prefix="/settings", tags=["settings"])
@router.get("/", response_model=SettingsRead)
async def get_settings():
    # Get singleton settings record
    settings = get_singleton(Settings)
    if not settings:
        # This shouldn't happen because init_db creates settings
        # But just in case, we'll return an error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Settings record not found in database")
    
    return settings

@router.put("/", response_model=SettingsRead)
async def update_settings(settings_update: SettingsUpdate):
    try:
        # Get existing settings
        db_settings = get_singleton(Settings)
        if not db_settings:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                              detail="Settings record not found in database")
        
        # Update with new values
        update_data = settings_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Only update non-None values
                setattr(db_settings, key, value)
        
        # Send brightness values to FPGA via UART
        red_brightness = getattr(settings_update, 'red_brightness', None)
        if red_brightness is not None:
            red_hex = uart.convert_brightness_to_hex(red_brightness)
            red_command = uart.create_uart_message("red", red_hex)
            uart.send_uart_command(red_command)
            
        green_brightness = getattr(settings_update, 'green_brightness', None)
        if green_brightness is not None:
            green_hex = uart.convert_brightness_to_hex(green_brightness)
            green_command = uart.create_uart_message("green", green_hex)
            uart.send_uart_command(green_command)
            
        blue_brightness = getattr(settings_update, 'blue_brightness', None)
        if blue_brightness is not None:
            blue_hex = uart.convert_brightness_to_hex(blue_brightness)
            blue_command = uart.create_uart_message("blue", blue_hex)
            uart.send_uart_command(blue_command)

        # Save changes using CRUD function
        db_settings = update(db_settings)
        
        return db_settings
    except Exception as e:
        logging.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=str(e))