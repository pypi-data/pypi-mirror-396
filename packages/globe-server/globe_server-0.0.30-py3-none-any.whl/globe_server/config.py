# app/config.py
import os
import sys
import socket
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# Globe Server data directory - always use home directory
globe_data_dir = Path.home() / ".globe-server"

# Load .env from data directory
env_file = globe_data_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)

# OS-Independent Settings

# ESP32 Device Communication API Key (loaded from environment)
ESP32_API_KEY = os.getenv("ESP32_API_KEY")
ESP32_HOSTNAME = os.getenv("ESP32_HOSTNAME")
UART_BAUD_RATE = 9600
MOTOR_RPM = 1000  # Default motor speed in RPM

# WiFi Access Point Settings (loaded from environment)
# AP_SSID is dynamically generated from Pi hostname
AP_SSID = f"{socket.gethostname()}-AP"
AP_PASSWORD = os.getenv("AP_PASSWORD")
AP_IP = os.getenv("AP_IP")

# Current Network Configuration (loaded from environment)
NETWORK_SSID = os.getenv("NETWORK_SSID")  # Current/last known working network SSID
NETWORK_PASSWORD = os.getenv("NETWORK_PASSWORD")  # Current/last known working network password

# Network Connection Timeouts (in seconds)
NETWORK_TEST_TIMEOUT = 30  # Timeout for testing network connection
NETWORK_SWITCH_TIMEOUT = 30  # Timeout for switching networks
NETWORK_CONFIRM_TIMEOUT = 10  # Timeout for confirming communication on new network
NETWORK_RETRY_DELAY = 2  # Delay between retries

# Network connection configuration
MAX_CONNECTION_ATTEMPTS = 3  # Maximum number of attempts to connect to any network

# Directory Configuration - hardcoded relative paths from data directory
GLOBE_DATA_DIR = str(globe_data_dir)
GLOBE_MEDIA_DIRECTORY = str(globe_data_dir / "media")
UPDATE_DIRECTORY = str(globe_data_dir / "updates")

LOG_PATH = str(globe_data_dir / "logs")
DATABASE_PATH = str(globe_data_dir / "globe.db")

# Ensure data directory exists
globe_data_dir.mkdir(parents=True, exist_ok=True)

# Earth Viz related stuff
STATIC_IMAGES_DIR = globe_data_dir / "static-images"
# Output directories (for generated images)
TEMP_BASE_DIR = Path(tempfile.gettempdir()) / "earth_viz"
OUTPUT_DIR = TEMP_BASE_DIR / "images"
TEMP_DIR = TEMP_BASE_DIR / "tmp"

# Ensure temp directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)



# Media Player Configuration
# Window management strategy: "persistent" or "on_demand"
# - persistent: Keep windows alive, switch visibility (faster switching, more memory)
# - on_demand: Kill and restart windows as needed (slower switching, less memory)
MEDIA_WINDOW_STRATEGY = os.getenv("MEDIA_WINDOW_STRATEGY", "persistent")

# Earth Viz Configuration
# Hardware Configuration - OS-specific defaults
if os.name == "nt":  # Windows
    UART_DEVICE = os.getenv("UART_DEVICE", "COM1")
elif sys.platform.startswith("linux"):  # Linux (including Raspberry Pi)
    UART_DEVICE = os.getenv("UART_DEVICE", "/dev/ttyS0")
else:
    UART_DEVICE = os.getenv("UART_DEVICE", "/dev/ttyS0")
    print("Warning: Unknown operating system. Using default configuration.")

