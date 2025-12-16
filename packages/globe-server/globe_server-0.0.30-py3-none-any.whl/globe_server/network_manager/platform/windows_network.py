"""Windows-specific network operations."""

import logging
import asyncio
import subprocess
import json
import os
import tempfile
from typing import List, Tuple, Optional
from xml.sax.saxutils import escape
import time

from .base_network import BaseNetworkManager, NetworkError
from globe_server.network_manager.models import NetworkInfo, ConnectionInfo, ConnectionType

logger = logging.getLogger(__name__)

class WindowsNetworkManager(BaseNetworkManager):
    """Windows-specific network operations"""
    
    async def run_command(self, cmd: list[str]) -> Tuple[str, str]:
        """Run a command using Windows-specific command execution"""
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            def _run_sync():
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                return process.stdout, process.stderr, process.returncode
            
            stdout, stderr, return_code = await asyncio.to_thread(_run_sync)
            logger.debug(f"Command completed with return code: {return_code}")
            return stdout, stderr
        except RuntimeError as e:
            if "Executor shutdown" in str(e):
                logger.warning("Executor shutdown during command execution (likely hot reload)")
                raise NetworkError("Service shutting down")
            raise
        except Exception as e:
            logger.error(f"Error running command {' '.join(cmd)}: {str(e)}", exc_info=True)
            raise NetworkError(f"Command execution failed: {str(e)}")
    
    async def get_current_connection_info(self) -> ConnectionInfo:
        try:
            cmd = """
            $profile = Get-NetConnectionProfile;
            if ($profile) {
                $interface = Get-NetAdapter -InterfaceIndex $profile.InterfaceIndex;
                $ip = Get-NetIPAddress -InterfaceIndex $profile.InterfaceIndex -AddressFamily IPv4;
                @{
                    'SSID' = $profile.Name;
                    'InterfaceName' = $interface.Name;
                    'IP' = $ip.IPAddress;
                    'State' = $interface.Status;
                } | ConvertTo-Json
            }
            """
            stdout, _ = await self.run_command(['powershell', '-Command', cmd])
            
            if not stdout.strip():
                return ConnectionInfo(
                    type=ConnectionType.NONE,
                    ssid=None,
                    ip_address=None,
                    interface_name=None,
                    is_connected=False
                )
            
            info = json.loads(stdout)
            return ConnectionInfo(
                type=ConnectionType.WIFI,
                ssid=info.get('SSID'),
                ip_address=info.get('IP'),
                interface_name=info.get('InterfaceName'),
                is_connected=info.get('State') == 'Up'
            )
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return ConnectionInfo(
                type=ConnectionType.NONE,
                ssid=None,
                ip_address=None,
                interface_name=None,
                is_connected=False
            )

    async def is_ap_mode_active(self) -> bool:
        try:
            stdout, _ = await self.run_command([
                'powershell',
                'Get-NetAdapter | Where-Object { $_.Name -like "*Mobile Hotspot*" -and $_.Status -eq "Up" }'
            ])
            return bool(stdout.strip())
        except Exception as e:
            logger.error(f"Error checking AP mode: {e}")
            return False

    async def enable_ap_mode(self) -> bool:
        try:
            await self.run_command([
                'powershell',
                '$connectionProfile = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile();',
                '$tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($connectionProfile);',
                '$tetheringManager.StartTetheringAsync()'
            ])
            return True
        except Exception as e:
            logger.error(f"Error enabling AP mode: {e}")
            return False

    async def disable_ap_mode(self) -> bool:
        try:
            await self.run_command([
                'powershell',
                '$connectionProfile = [Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile();',
                '$tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager]::CreateFromConnectionProfile($connectionProfile);',
                '$tetheringManager.StopTetheringAsync()'
            ])
            return True
        except Exception as e:
            logger.error(f"Error disabling AP mode: {e}")
            return False

    async def connect_to_network(self, ssid: str, password: str) -> bool:
        try:
            logger.info(f"=== Starting connection process for network: {ssid} ===")
            logger.info("Step 1: Creating WiFi profile")
            profile_path = await self._create_wifi_profile(ssid, password)
            logger.info(f"Profile created at: {profile_path}")
            
            try:
                # Check if WiFi is enabled
                logger.info("Step 2: Checking WiFi interface status")
                stdout, stderr = await self.run_command(['netsh', 'wlan', 'show', 'interfaces'])
                logger.info(f"Interface check output: {stdout}")
                
                if "There is 1 interface on the system" not in stdout:
                    logger.error("No WiFi interfaces found")
                    return False
                logger.info("WiFi interface check passed")
                
                # Delete existing profile if it exists
                logger.info("Step 3: Checking for existing profile")
                stdout, stderr = await self.run_command(['netsh', 'wlan', 'show', 'profiles'])
                if ssid in stdout:
                    logger.info(f"Found existing profile for {ssid}, deleting it")
                    await self.run_command(['netsh', 'wlan', 'delete', 'profile', 'name=' + ssid])
                    logger.info("Waiting 1 second after profile deletion")
                    await asyncio.sleep(1)
                else:
                    logger.info("No existing profile found")
                
                # Add and connect using the profile
                logger.info("Step 4: Adding new WiFi profile")
                stdout, stderr = await self.run_command(['netsh', 'wlan', 'add', 'profile', 'filename=' + profile_path, 'interface=WiFi'])
                logger.info(f"Add profile stdout: {stdout}")
                logger.info(f"Add profile stderr: {stderr}")
                if stderr or "error" in stdout.lower() or "failed" in stdout.lower():
                    logger.error(f"Error adding profile - stdout: {stdout}, stderr: {stderr}")
                    return False
                logger.info("Profile added successfully")
                logger.info("Waiting 1 second after profile addition")
                await asyncio.sleep(1)
                
                logger.info("Step 5: Initiating connection")
                stdout, stderr = await self.run_command(['netsh', 'wlan', 'connect', 'name=' + ssid, 'ssid=' + ssid, 'interface=WiFi'])
                if stderr:
                    logger.error(f"Error connecting to network: {stderr}")
                    return False
                logger.info(f"Connection command output: {stdout}")
                
                logger.info("Step 6: Waiting for connection to establish")
                await asyncio.sleep(6)
                
                logger.info("Step 7: Verifying connection")
                stdout, stderr = await self.run_command([
                    'powershell',
                    '(Get-NetConnectionProfile).Name'
                ])
                logger.info(f"Connection verification output: {stdout}")
                
                success = ssid in stdout
                logger.info(f"=== Connection process {'successful' if success else 'failed'} ===")
                return success
                
            finally:
                try:
                    logger.info("Cleaning up: Deleting temporary profile file")
                    os.unlink(profile_path)
                    logger.info("Profile file deleted successfully")
                except Exception as e:
                    logger.warning(f"Failed to delete temporary profile file: {e}")
                    
        except Exception as e:
            logger.error(f"Error connecting to network: {e}", exc_info=True)
            return False

    async def _create_wifi_profile(self, ssid: str, password: str) -> str:
        """Create Windows WiFi profile XML and return the temp file path"""
        escaped_ssid = escape(ssid)
        escaped_password = escape(password)
        profile_content = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{escaped_ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{escaped_ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{escaped_password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(profile_content)
            return temp_file.name

    async def disconnect_from_network(self) -> bool:
        try:
            stdout, stderr = await self.run_command(['netsh', 'wlan', 'disconnect'])
            if stderr:
                logger.error(f"Error disconnecting from network: {stderr}")
                return False
            await asyncio.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from network: {e}", exc_info=True)
            return False

    async def scan_networks(self) -> List[NetworkInfo]:
        try:
            stdout, _ = await self.run_command(['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'])
            
            networks = []
            current_network = None
            
            for line in stdout.splitlines():
                line = line.strip()
                
                if line.startswith('SSID'):
                    if current_network:
                        networks.append(current_network)
                    current_network = NetworkInfo(
                        ssid='',
                        signal_strength=0,
                        security='unknown'
                    )
                    ssid_parts = line.split(' : ')
                    if len(ssid_parts) > 1:
                        current_network.ssid = ssid_parts[1].strip()
                
                elif current_network:
                    if 'Authentication' in line:
                        security = line.split(' : ')[1].strip()
                        current_network.security = security
                    elif 'Signal' in line:
                        try:
                            signal = int(line.split(' : ')[1].strip().rstrip('%'))
                            current_network.signal_strength = signal
                        except ValueError:
                            current_network.signal_strength = 0
            
            if current_network:
                networks.append(current_network)
            
            unique_networks = {network.ssid: network for network in networks if network.ssid}.values()
            return sorted(unique_networks, key=lambda x: x.signal_strength, reverse=True)
            
        except Exception as e:
            logger.error(f"Error scanning networks: {str(e)}")
            return []
