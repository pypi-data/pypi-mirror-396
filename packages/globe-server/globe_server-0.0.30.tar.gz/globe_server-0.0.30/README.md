# Globe Software

Complete interactive globe visualization system with hardware control, media playback, and web interface.

## Overview

Globe Software is a complete system for controlling and visualizing content on a physical rotating globe display. This package includes both the FastAPI backend server and the React web interface as static files.

WARNING: This package is designed to be used on the Globe platform hardware - use on other systems may result in unexpected behaviour like forced network disconnects.

## Features

- **Web Interface**: React-based UI for controlling the globe (served as static files)
- **FastAPI Backend**: High-performance async web server with REST API
- **Globe Visualization**: Real-time 3D globe rendering with earth-viz
- **Media Management**: Upload and manage video/image content with playlist support
- **Hardware Control**: Interface with ESP32 (motor) and FPGA (display) hardware
- **Network Management**: WiFi configuration, network switching, and access point mode
- **Automatic Updates**: Online (PyPI) and offline (.whl) update support
- **Real-time Communication**: WebSocket support for live status updates

## Installation

### Quick Install
```bash
pip install globe-server-backend
```

### Initial Setup
After installation, run the setup wizard to configure the system:
```bash
globe-server-setup
```

This will:
- Create the `~/.globe-server/` directory structure
- Download required static images for visualization
- Prompt for configuration (ESP32 API key, WiFi credentials, etc.)

### Production Deployment (Raspberry Pi)

For production deployment on Raspberry Pi, see the [installation guide](https://github.com/edcatley/Globe-Software/blob/main/INSTALL.md) which covers:
- Creating the installation directory and virtual environment
- Installing as a systemd service
- Automatic startup and update management

## Usage

### Starting the Server
```bash
# Start the server
globe-server
```

The server will start on `http://localhost:8000` and serve:
- Web interface at `http://localhost:8000/`
- API documentation at `http://localhost:8000/docs`
- Alternative API docs at `http://localhost:8000/redoc`

### Accessing the Web Interface

Once the server is running, open your browser to:
- `http://localhost:8000` (local access)
- `http://<raspberry-pi-ip>:8000` (remote access)

The web interface provides:
- Media upload and playlist management
- Globe visualization controls
- Motor speed and rotation control
- Network and WiFi configuration
- System settings and firmware updates

### Command Line Options
```bash
# Start with default settings
globe-server

# Or use uvicorn directly for custom configuration
uvicorn globe_server.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

The server stores configuration and data in `~/.globe-server/`:

- `.env` - Environment variables (API keys, WiFi credentials)
- `globe.db` - SQLite database
- `media/` - Uploaded media files
- `updates/` - Software update packages (.whl files)
- `logs/` - Application logs

Key configuration settings (from `globe_server.config`):
- `GLOBE_DATA_DIR`: `~/.globe-server` (base directory)
- `GLOBE_MEDIA_DIRECTORY`: Media storage location
- `UPDATE_DIRECTORY`: Software update packages
- `MOTOR_RPM`: Default motor rotation speed
- `ESP32_API_KEY`: Authentication for ESP32 communication

## System Architecture

```
┌─────────────────┐
│  Web Interface  │ (React - served as static files)
│  Port 8000      │
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  FastAPI Server │ (Python)
│  Port 8000      │
└────┬───────┬────┘
     │       │
     │       └──────────┐
┌────▼────┐      ┌──────▼──────┐
│  ESP32  │      │    FPGA     │
│ (Motor) │      │ (Display)   │
└─────────┘      └─────────────┘
```

## API Endpoints

The REST API provides programmatic access to all features:

- `/` - Web interface (static files)
- `/media/*` - Media file management and playback
- `/playlist/*` - Playlist operations
- `/motor/*` - Motor control (ESP32)
- `/status/*` - Server status and WebSocket updates
- `/settings/*` - Server configuration
- `/update/*` - Software and firmware updates (server, ESP32, FPGA)
- `/network/*` - Network and WiFi management
- `/earth-viz/*` - Globe visualization rendering

Full interactive API documentation available at `/docs` when server is running.

## Software Updates

Globe Software supports both online and offline updates:

### Online Updates (PyPI)
When connected to the internet, the system automatically checks for updates on startup (when using the systemd service).

### Offline Updates
For systems without internet access:
1. Download the update bundle (`.whl` files for the package and all dependencies)
2. Copy all `.whl` files to `~/.globe-server/updates/`
3. Restart the server

The startup script will automatically install from local files if PyPI is unavailable.

## Development

### From Source
```bash
git clone https://github.com/edcatley/Globe-Software.git
cd Globe-Software/backend
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/
```

## Links

- **GitHub Repository**: https://github.com/edcatley/Globe-Software
- **Issue Tracker**: https://github.com/edcatley/Globe-Software/issues
- **Installation Guide**: https://github.com/edcatley/Globe-Software/blob/main/INSTALL.md

## Requirements

### Software
- Python 3.8 or higher
- VLC media player (for video/image playback)

### Hardware (Optional)
- Raspberry Pi (tested on Bookworm)
- ESP32 microcontroller (for motor control)
- FPGA (for display control)

The system can run without hardware for development and testing.

### Python Dependencies
All Python dependencies are automatically installed:
- FastAPI & Uvicorn (web server)
- SQLite (database)
- VLC Python bindings (media playback)
- PyQt5 & PyQtWebEngine (visualization windows)
- earth-viz (globe rendering)
- pyserial (UART communication)
- zeroconf (network discovery)

See the [pyproject.toml](https://github.com/edcatley/Globe-Software/blob/main/backend/pyproject.toml) for the complete dependency list.

## Author

Edward Catley (edward.catley@catleytech.com)

## License

MIT License - see [LICENSE](https://github.com/edcatley/Globe-Software/blob/main/backend/LICENSE) for details
