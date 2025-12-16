# app/utils/files.py

import os
import zipfile
import logging
from fastapi import UploadFile
import aiofiles
from globe_server import config
import shutil

# Configure logging (consider moving this to a central place)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def save_uploaded_file(file: UploadFile, destination_directory: str) -> str:
    """Saves an uploaded file to the specified directory.

    Args:
        file: The UploadFile object from FastAPI.
        destination_directory: The directory to save the file to.

    Returns:
        The full path to the saved file.

    Raises:
        Exception: If the file cannot be saved.
    """
    # Validate the directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory, exist_ok=True)

    file_path = os.path.join(destination_directory, file.filename)

    try:
        # Open the destination file
        async with aiofiles.open(file_path, "wb") as out_file:
            # Read and write in chunks of 1MB
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := await file.read(chunk_size):
                await out_file.write(chunk)
        
        logger.info(f"Successfully saved file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save file {file.filename} to {destination_directory}: {e}")
        raise Exception(f"Failed to save file: {e}")


def delete_file(file_path: str) -> None:
    """Deletes a file.

    Args:
        file_path: The path to the file to delete.

    Raises:
        Exception: If the file cannot be deleted.
    """
    try:
        os.remove(file_path)
        logger.info(f"Successfully deleted file: {file_path}")
    except FileNotFoundError:
        logger.warning(f"File not found, cannot delete: {file_path}")
        pass  # File already deleted or doesn't exist
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        raise Exception(f"Failed to delete file: {e}")


def extract_zip_file(zip_path: str, extract_path: str) -> None:
    """Extracts a ZIP file to the specified path.

    Args:
        zip_path: Path to the ZIP file.
        extract_path: Path to extract the ZIP contents to.

    Raises:
        Exception: If the ZIP file cannot be extracted.
    """
    try:
        logger.info(f"Opening ZIP file: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            logger.info(f"ZIP file opened successfully. Number of files: {len(zip_ref.namelist())}")
            logger.info("Contents of ZIP file:")
            for name in zip_ref.namelist():
                logger.info(f"  - {name}")
            
            logger.info(f"Extracting to: {extract_path}")
            zip_ref.extractall(extract_path)
            
            # Check if the first level is a single directory
            extracted_items = os.listdir(extract_path)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_path, extracted_items[0])):
                logger.info(f"ZIP contains a root directory: {extracted_items[0]}")
                root_dir = os.path.join(extract_path, extracted_items[0])
                
                # Move contents up one level
                for item in os.listdir(root_dir):
                    s = os.path.join(root_dir, item)
                    d = os.path.join(extract_path, item)
                    logger.info(f"Moving {s} to {d}")
                    shutil.move(s, d)
                
                # Remove the now-empty root directory
                os.rmdir(root_dir)
                logger.info("Removed root directory after moving contents")
            
            # Log extracted files
            logger.info("Extracted files:")
            for root, dirs, file_list in os.walk(extract_path):
                logger.info(f"Directory: {root}")
                logger.info(f"Subdirectories: {dirs}")
                logger.info(f"Files: {file_list}")
                
        logger.info(f"Successfully extracted ZIP file to: {extract_path}")
    except Exception as e:
        logger.error(f"Failed to extract ZIP file {zip_path}: {e}")
        raise Exception(f"Failed to extract ZIP file: {e}")


def list_media_files(type: str) -> list:
    """List available media files in the specified media directory.
    
    Args:
        type (str): Type of media files to list ('video' or 'image')
        
    Returns:
        list: List of dictionaries containing file information
    """
    try:
        # Get the appropriate directory based on type
        base_dir = os.path.join(config.GLOBE_MEDIA_DIRECTORY, "Videos" if type == "video" else "Images")
        logging.info(f"Looking for files in directory: {base_dir}")
        
        if not os.path.exists(base_dir):
            logging.warning(f"Directory does not exist: {base_dir}")
            return []

        # List all files in the directory
        files = []
        for filename in os.listdir(base_dir):
            filepath = os.path.join(base_dir, filename)
            if os.path.isfile(filepath):
                # Get file info
                stats = os.stat(filepath)
                file_info = {
                    "name": filename,
                    "path": filepath,
                    "size": stats.st_size,
                }
                logging.info(f"Found file: {file_info}")
                files.append(file_info)

        return sorted(files, key=lambda x: x["name"])
    except Exception as e:
        logging.error(f"Error listing media files: {str(e)}", exc_info=True)
        raise


async def calculate_sha256(file_path: str) -> str:
    """Calculates the SHA256 hash of a file.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        The hex digest of the SHA256 hash
    """
    import hashlib  # Import here to avoid adding to top if not already present
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):  # Read in chunks for large files
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


async def check_disk_space(directory: str, required_space_mb: int) -> bool:
    """Checks if there's enough disk space in the given directory.
    
    Args:
        directory: The directory to check disk space for
        required_space_mb: The minimum required space in megabytes
        
    Returns:
        True if there's enough space, False otherwise
    """
    try:
        total, used, free = shutil.disk_usage(directory)
        available_space_mb = free / (1024 * 1024)  # Convert bytes to MB
        return available_space_mb >= required_space_mb
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return False