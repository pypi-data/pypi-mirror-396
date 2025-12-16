"""
Server hardware monitoring and status management.

This module polls system metrics (CPU, memory, disk) and broadcasts them via WebSocket.
"""

import logging
import asyncio
import psutil
import time
from typing import Optional, Dict, Any

from globe_server.db.broadcast_queue import broadcast_message

logger = logging.getLogger(__name__)


class ServerHardwareManager:
    """Manages server hardware monitoring and status broadcasting."""
    
    def __init__(self):
        self.status: Optional[Dict[str, Any]] = None
        self._polling_task: Optional[asyncio.Task] = None
        self._start_time = time.time()
    
    async def _poll_status(self):
        """Poll server status every second and broadcast it."""
        logger.info("Server status polling task started")
        
        while True:
            try:
                # Get system metrics
                cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                disk = psutil.disk_usage('/')
                disk_usage = disk.percent
                uptime = time.time() - self._start_time
                database_connected = True
                
                # Build and store status dict
                self.status = {
                    "uptime": uptime,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "disk_usage": disk_usage,
                    "database_connected": database_connected,
                    "error": None
                }
                
                # Broadcast to frontend
                await broadcast_message("server_status", self.status)
                
            except Exception as e:
                logger.error(f"Error polling server status: {e}")
                self.status = {
                    "uptime": 0.0,
                    "cpu_usage": 0.0,
                    "memory_usage": 0.0,
                    "disk_usage": 0.0,
                    "database_connected": False,
                    "error": str(e)
                }
                await broadcast_message("server_status", self.status)
            
            await asyncio.sleep(1.0)
    
    async def start(self):
        """Start the server status polling task."""
        if self._polling_task is None:
            self._polling_task = asyncio.create_task(self._poll_status())
            logger.info("Started server status polling")
        else:
            logger.warning("Server status polling already running")
    
    async def stop(self):
        """Stop the server status polling task."""
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            self._polling_task = None
            logger.info("Stopped server status polling")


# Global instance
server_hardware = ServerHardwareManager()
