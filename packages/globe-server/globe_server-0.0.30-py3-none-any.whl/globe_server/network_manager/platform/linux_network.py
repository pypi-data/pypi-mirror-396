"""Linux-specific network operations."""

import logging
import asyncio
import json
from typing import List, Tuple, Optional

from .base_network import BaseNetworkManager, NetworkError
from globe_server.network_manager.models import NetworkInfo, ConnectionInfo, ConnectionType
from globe_server import config

logger = logging.getLogger(__name__)

class LinuxNetworkManager(BaseNetworkManager):
    """Linux-specific network operations"""
    
    async def run_command(self, cmd: list[str]) -> Tuple[str, str]:
        """Run a command using Linux-specific command execution"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return_code = process.returncode
            stdout = stdout.decode().strip()
            stderr = stderr.decode().strip()
            
            logger.info(f"Process completed with return code: {return_code}")
            return stdout, stderr
        except Exception as e:
            logger.error(f"Error running command {' '.join(cmd)}: {str(e)}", exc_info=True)
            raise NetworkError(f"Command execution failed: {str(e)}")
    
    async def get_current_connection_info(self) -> ConnectionInfo:
        try:
            if await self.is_ap_mode_active():
                return ConnectionInfo(
                    type=ConnectionType.AP,
                    ssid=config.AP_SSID,
                    ip_address=config.AP_IP,
                    interface_name="ap0",
                    is_connected=True
                )
            
            stdout, _ = await self.run_command([
                'nmcli',
                '-t',
                '-f', 'DEVICE,STATE,CONNECTION,IP4.ADDRESS',
                'device', 'show'
            ])
            
            for line in stdout.splitlines():
                if 'wifi' in line:
                    parts = line.split(':')
                    if len(parts) >= 4 and 'connected' in parts[1].lower():
                        return ConnectionInfo(
                            type=ConnectionType.WIFI,
                            ssid=parts[2],
                            ip_address=parts[3].split('/')[0] if '/' in parts[3] else parts[3],
                            interface_name=parts[0],
                            is_connected=True
                        )
            
            return ConnectionInfo(
                type=ConnectionType.NONE,
                ssid=None,
                ip_address=None,
                interface_name=None,
                is_connected=False
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
            stdout, _ = await self.run_command(['iwconfig'])
            return 'Mode:Master' in stdout
        except Exception as e:
            logger.error(f"Error checking AP mode: {e}")
            return False

    async def enable_ap_mode(self) -> bool:
        try:
            await self.run_command(['sudo', 'systemctl', 'stop', 'NetworkManager'])
            await self.run_command(['sudo', 'hostapd', '-B', '/etc/hostapd/hostapd.conf'])
            await self.run_command(['sudo', 'systemctl', 'start', 'dnsmasq'])
            return True
        except Exception as e:
            logger.error(f"Error enabling AP mode: {e}")
            return False

    async def disable_ap_mode(self) -> bool:
        try:
            await self.run_command(['sudo', 'killall', 'hostapd'])
            await self.run_command(['sudo', 'systemctl', 'stop', 'dnsmasq'])
            await self.run_command(['sudo', 'systemctl', 'restart', 'NetworkManager'])
            return True
        except Exception as e:
            logger.error(f"Error disabling AP mode: {e}")
            return False

    async def connect_to_network(self, ssid: str, password: str) -> bool:
        try:
            stdout, stderr = await self.run_command([
                'nmcli', 'device', 'wifi',
                'connect', ssid,
                'password', password
            ])
            if stderr:
                logger.error(f"Error connecting with nmcli: {stderr}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error connecting to network: {e}", exc_info=True)
            return False

    async def disconnect_from_network(self) -> bool:
        try:
            conn_info = await self.get_current_connection_info()
            
            if not conn_info.is_connected:
                logger.info("No active connection to disconnect from")
                return True
                
            if conn_info.type == ConnectionType.AP:
                return await self.disable_ap_mode()
                
            if conn_info.interface_name:
                stdout, stderr = await self.run_command([
                    'nmcli', 'device', 'disconnect', conn_info.interface_name
                ])
                
                if stderr:
                    logger.error(f"Error disconnecting from network: {stderr}")
                    return False
                    
                return True
            else:
                logger.error("No interface name found for current connection")
                return False
        except Exception as e:
            logger.error(f"Error disconnecting from network: {e}", exc_info=True)
            return False

    async def scan_networks(self) -> List[NetworkInfo]:
        try:
            stdout, _ = await self.run_command([
                'nmcli',
                '-t',
                '-f', 'SSID,SIGNAL,SECURITY',
                'device', 'wifi', 'list'
            ])
            
            networks = []
            for line in stdout.splitlines():
                if not line.strip():
                    continue
                    
                parts = line.split(':')
                if len(parts) >= 3:
                    try:
                        networks.append(NetworkInfo(
                            ssid=parts[0],
                            signal_strength=int(parts[1]),
                            security=parts[2] if parts[2] else 'none'
                        ))
                    except ValueError:
                        continue
            
            return sorted(networks, key=lambda x: x.signal_strength, reverse=True)
            
        except Exception as e:
            logger.error(f"Error scanning networks: {str(e)}")
            return []
