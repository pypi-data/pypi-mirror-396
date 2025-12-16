# app/api/update.py

import os
import zipfile
import shutil
import logging
import datetime
import subprocess
import sys
import random
import signal
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from globe_server.utils.files import save_uploaded_file, delete_file, extract_zip_file, calculate_sha256, check_disk_space
from globe_server import config
from globe_server.hardware.esp32_client import esp32_client  # Import esp32_client directly
import aiofiles

router = APIRouter(prefix="/update", tags=["update"])

# Configure logging (consider moving this to a central place)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store the process ID for graceful shutdown
server_pid = os.getpid()

@router.post("/fpga")
async def upload_fpga_firmware(file: UploadFile = File(...)):
    """Uploads and flashes the FPGA firmware."""
    try:
        # 1. Configuration
        upload_directory = os.path.join(config.UPDATE_DIRECTORY, "FPGA")
        file_path = await save_uploaded_file(file, upload_directory)

        # 2. Validation
        if not file.filename.endswith(".bin"):
            delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .bin files are allowed."
            )

        # 3. Construct the command
        # Use the tools directly from the package
        package_dir = os.path.dirname(os.path.dirname(__file__))  # globe_server package dir
        tools_dir = os.path.join(package_dir, "tools")
        proxy_bitstream = os.path.join(tools_dir, "bscan_spi_xc6slx9.bit")
        logger.info(f"Using proxy bitstream: {proxy_bitstream}")
        command = [
            "sudo",
            "openocd",
            "-f", "/usr/local/share/openocd/scripts/interface/raspberrypi-native.cfg",
            "-f", "/usr/local/share/openocd/scripts/cpld/xilinx-xc6s.cfg",
            "-f", "/usr/local/share/openocd/scripts/cpld/jtagspi.cfg",
            "-c", f"init; jtagspi_init xc6s.pld {proxy_bitstream}; jtagspi_program {file_path} 0; virtex2 refresh xc6s.pld; shutdown"
        ]

        # 4. Execute the xc3sprog.py script
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 5. Check the return code
        if process.returncode != 0:
            logger.error(f"xc3sprog.py script failed with return code: {process.returncode}, Stdout: {stdout.decode()}, Stderr: {stderr.decode()}")
            delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"xc3sprog.py script failed: {stderr.decode()}"
            )

        logger.info("FPGA firmware upload and update started successfully")
        return {"message": "FPGA firmware upload and update started successfully", "status": "in_progress"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error during FPGA firmware upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload FPGA firmware: {str(e)}"
        )


@router.post("/esp32")
async def upload_esp32_firmware(file: UploadFile = File(...)):
    """Uploads and flashes the ESP32 firmware."""
    try:
        # 1. Configuration
        upload_directory = os.path.join(config.UPDATE_DIRECTORY, "ESP32")
        file_path = await save_uploaded_file(file, upload_directory)

        # 2. Validation
        if not file.filename.endswith(".bin"):
            delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .bin files are allowed."
            )

        # 3. Construct the command using esp32_client.ip directly
        if not esp32_client.ip:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ESP32 is not connected"
            )

        # Import and use espota directly (it's a Python module in our package)
        import sys
        import importlib.util
        import asyncio
        
        # Import the espota module from our tools directory
        package_dir = os.path.dirname(os.path.dirname(__file__))  # globe_server package dir
        tools_dir = os.path.join(package_dir, "tools")
        espota_path = os.path.join(tools_dir, "espota.py")
        
        logger.info(f"Importing espota from: {espota_path}")
        
        # Dynamic import of the espota module
        spec = importlib.util.spec_from_file_location("espota", espota_path)
        espota = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(espota)
        
        # Set up the arguments we would pass to espota.py
        args = [
            "-i", esp32_client.ip,            # ESP32 IP
            "-a", config.ESP32_API_KEY,       # Auth key
            "-f", file_path,                  # Firmware file
            "-t", "20",                      # Longer timeout
            "--progress"                      # Show progress
        ]
        
        # Run the espota module in a separate thread to prevent blocking
        loop = asyncio.get_event_loop()
        
        # This runs the serve function directly with our parameters
        def run_espota():
            try:
                logger.info(f"Starting ESP32 firmware update to {esp32_client.ip}")
                result = espota.main(args)
                logger.info(f"ESP32 firmware update completed with status: {result}")
                return result
            except Exception as e:
                logger.exception(f"Error during ESP32 update: {str(e)}")
                return 1
                
        # Run in thread pool and get result
        result = await loop.run_in_executor(None, run_espota)
        
        # Check the result
        if result != 0:
            delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ESP32 firmware update failed. Check logs for details."
            )

        logger.info("ESP32 firmware upload and update started successfully")
        return {"message": "ESP32 firmware upload and update started successfully", "status": "in_progress"}

    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.exception("An unexpected error occurred during the ESP32 update process.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/restart")
async def restart_server():
    """Restart server using the startup script (which handles updates)."""
    try:
        logger.info("=== Server Restart Process Started ===")
        
        # Determine the correct startup script path
        if os.name == 'nt':  # Windows
            script_path = "globe-server-startup.ps1"
            command = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path]
        else:  # Linux/Unix
            script_path = "globe-server-startup.sh"
            command = ["bash", script_path]
        
        logger.info(f"Launching startup script: {script_path}")
        
        # Start the startup script (which will kill this process and restart)
        subprocess.Popen(command, cwd=os.getcwd())
        
        logger.info("Startup script launched - server will restart shortly")
        return {
            "message": "Server restart initiated", 
            "status": "restarting",
            "note": "Server will check for updates and restart automatically"
        }
        
    except Exception as e:
        logger.error(f"Error during restart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restart failed: {str(e)}"
        )


@router.post("/server")
async def upload_server_update(file: UploadFile = File(...)):
    """Download server update package (.whl file) for offline installation."""
    try:
        # Configuration - use update directory from config
        update_directory = config.UPDATE_DIRECTORY
        
        # Create update directory if it doesn't exist
        os.makedirs(update_directory, exist_ok=True)
        logger.info(f"Update directory: {update_directory}")
        
        # Validation - only accept .whl files
        if not file.filename.endswith(".whl"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only .whl files are allowed."
            )
        
        # Check disk space (estimate 100MB required for .whl file)
        if not await check_disk_space(update_directory, 100):
            raise HTTPException(
                status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                detail="Insufficient disk space for update file."
            )
        
        # Save the uploaded .whl file
        file_path = await save_uploaded_file(file, update_directory)
        logger.info(f"Saved update file to: {file_path}")
        
        # Calculate file hash for verification
        file_hash = await calculate_sha256(file_path)
        file_size = os.path.getsize(file_path)
        
        return {
            "message": "Update file downloaded successfully",
            "status": "ready",
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "sha256": file_hash,
            "next_step": "Restart server to apply update"
        }
            
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        logger.exception("An unexpected error occurred during the update download.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )