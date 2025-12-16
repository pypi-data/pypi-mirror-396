"""
Setup script for Globe Server.

This script handles first-time setup including:
- Creating .env configuration file
- Setting up earth-viz static images
- Initializing the database
"""

import os
import sys
import argparse
import secrets
from pathlib import Path
from typing import Optional


def prompt_for_config() -> dict:
    """Interactively prompt user for configuration values."""
    print("\n=== Globe Server Setup ===\n")
    print("Please provide the following configuration values.")
    print("Press Enter to use default values where available.\n")
    
    config = {}
    
    # ESP32 Configuration
    print("--- ESP32 Device Configuration ---")
    while True:
        config['ESP32_API_KEY'] = input("ESP32 API Key (required): ").strip()
        if config['ESP32_API_KEY']:
            break
        print("ESP32 API Key is required. Please enter a value.")
    
    while True:
        config['ESP32_HOSTNAME'] = input("ESP32 Hostname (e.g., globe-71183C, required): ").strip()
        if config['ESP32_HOSTNAME']:
            break
        print("ESP32 Hostname is required. Please enter a value.")
    
    # WiFi Access Point Configuration
    print("\n--- WiFi Access Point Configuration ---")
    while True:
        config['AP_PASSWORD'] = input("Access Point Password (required): ").strip()
        if config['AP_PASSWORD']:
            break
        print("Access Point Password is required. Please enter a value.")
    
    config['AP_IP'] = input("Access Point IP [192.168.0.1]: ").strip() or "192.168.0.1"
    
    # Network Configuration
    print("\n--- Network Configuration ---")
    config['NETWORK_SSID'] = input("Default Network SSID (optional): ").strip()
    config['NETWORK_PASSWORD'] = input("Default Network Password (optional): ").strip()
    
    return config





def write_env_file(config: dict, output_path: Path):
    """Write configuration to .env file."""
    env_content = """# ESP32 Device Communication API Key
ESP32_API_KEY={ESP32_API_KEY}

# ESP32 Device Hostname
ESP32_HOSTNAME={ESP32_HOSTNAME}

# WiFi Access Point Settings (fallback when no network available)
AP_PASSWORD={AP_PASSWORD}
AP_IP={AP_IP}

# Current Network Configuration (last known working network)
NETWORK_SSID={NETWORK_SSID}
NETWORK_PASSWORD={NETWORK_PASSWORD}
""".format(**config)
    
    output_path.write_text(env_content)
    print(f"\n✓ Configuration written to: {output_path}")


def setup_earth_viz():
    """Setup earth-viz by calling its setup script."""
    print("\n--- Setting up Earth-Viz ---")
    try:
        # Try to import and call earth-viz setup
        from earth_viz_backend.setup import setup as earth_viz_setup
        
        print("Running earth-viz setup (will use GLOBE_DATA_DIR env var)...")
        earth_viz_setup()
        print("✓ Earth-Viz setup complete")
    except ImportError:
        print("⚠ Warning: earth-viz-backend not installed, skipping earth-viz setup")
    except Exception as e:
        print(f"⚠ Warning: Earth-Viz setup failed: {e}")





def setup(env_file: Optional[str] = None):
    """Main setup function."""
    # Globe Server data directory - always use home directory
    data_dir = Path.home() / ".globe-server"
    
    # Set env var so earth-viz uses the same location
    os.environ['GLOBE_DATA_DIR'] = str(data_dir)
    
    print(f"\nGlobe Server data directory: {data_dir}")
    
    # Create data directory structure
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "media" / "Images").mkdir(parents=True, exist_ok=True)
    (data_dir / "media" / "Videos").mkdir(parents=True, exist_ok=True)
    (data_dir / "updates" / "FPGA").mkdir(parents=True, exist_ok=True)
    (data_dir / "updates" / "ESP32").mkdir(parents=True, exist_ok=True)
    (data_dir / "updates" / "server").mkdir(parents=True, exist_ok=True)
    (data_dir / "logs").mkdir(exist_ok=True)
    (data_dir / "static-images").mkdir(exist_ok=True)
    print(f"✓ Created directory structure")
    
    # Get configuration
    env_path = data_dir / ".env"
    if env_file:
        print(f"\nCopying configuration from: {env_file}")
        import shutil
        shutil.copy2(env_file, env_path)
        print(f"✓ Configuration copied to: {env_path}")
    else:
        config = prompt_for_config()
        write_env_file(config, env_path)
    
    # Setup earth-viz (will use GLOBE_DATA_DIR from environment)
    setup_earth_viz()
    
    print("\n" + "="*50)
    print("✓ Globe Server setup complete!")
    print("="*50)
    print(f"\nData directory: {data_dir}")
    print(f"Configuration file: {env_path}")
    print(f"\nTo start the server, run: globe-server")
    print(f"(Database will be initialized automatically on first run)")
    print()


def main():
    """Entry point for globe-server-setup command."""
    parser = argparse.ArgumentParser(
        description="Setup Globe Server for first-time use"
    )
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to existing .env file to use (skips interactive prompts)'
    )
    
    args = parser.parse_args()
    
    try:
        setup(env_file=args.env_file)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
