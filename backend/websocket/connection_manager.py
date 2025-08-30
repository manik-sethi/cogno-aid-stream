import asyncio
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time communication with frontend."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_data: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.client_data[websocket] = {
            'connected_at': asyncio.get_event_loop().time(),
            'last_ping': asyncio.get_event_loop().time()
        }
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "data": {
                "message": "Connected to BCI Confusion Monitor",
                "timestamp": asyncio.get_event_loop().time()
            }
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.client_data:
            del self.client_data[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self._handle_connection_error(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        disconnected_clients = []
        message_json = json.dumps(message)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.append(connection)
        
        # Clean up disconnected clients
        for client in disconnected_clients:
            await self._handle_connection_error(client)
    
    async def broadcast_confusion_update(self, confusion_level: float, timestamp: float, additional_data: Dict = None):
        """Broadcast confusion level update to all clients."""
        message = {
            "type": "confusion_update",
            "data": {
                "level": confusion_level,
                "timestamp": timestamp,
                **(additional_data or {})
            }
        }
        await self.broadcast(message)
    
    async def broadcast_bci_status(self, connected: bool, device_info: Dict = None):
        """Broadcast BCI device status to all clients."""
        message = {
            "type": "bci_status",
            "data": {
                "connected": connected,
                "device_info": device_info or {},
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        await self.broadcast(message)
    
    async def broadcast_help_suggestion(self, suggestions: List[str], confusion_level: float, context: Dict = None):
        """Broadcast help suggestions when confusion threshold is exceeded."""
        message = {
            "type": "help_suggestion",
            "data": {
                "suggestions": suggestions,
                "confusion_level": confusion_level,
                "context": context or {},
                "timestamp": asyncio.get_event_loop().time()
            }
        }
        await self.broadcast(message)
    
    async def broadcast_brain_activity(self, eeg_data: Dict):
        """Broadcast brain activity visualization data."""
        # Prepare simplified data for frontend visualization
        activity_data = {
            "type": "brain_activity",
            "data": {
                "channels": {},
                "timestamp": eeg_data.get('timestamp', asyncio.get_event_loop().time()),
                "quality": eeg_data.get('quality', {})
            }
        }
        
        # Send only key channels to reduce bandwidth
        key_channels = ['AF3', 'AF4', 'F3', 'F4', 'F7', 'F8']
        eeg_channels = eeg_data.get('eeg', {})
        
        for channel in key_channels:
            if channel in eeg_channels:
                activity_data["data"]["channels"][channel] = eeg_channels[channel]
        
        await self.broadcast(activity_data)
    
    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            payload = data.get('data', {})
            
            if message_type == 'ping':
                await self._handle_ping(websocket, payload)
            elif message_type == 'set_threshold':
                await self._handle_threshold_update(websocket, payload)
            elif message_type == 'request_status':
                await self._handle_status_request(websocket)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from client")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def _handle_ping(self, websocket: WebSocket, payload: Dict):
        """Handle ping messages for connection health."""
        if websocket in self.client_data:
            self.client_data[websocket]['last_ping'] = asyncio.get_event_loop().time()
        
        await self.send_personal_message({
            "type": "pong",
            "data": {
                "timestamp": asyncio.get_event_loop().time(),
                "client_timestamp": payload.get('timestamp')
            }
        }, websocket)
    
    async def _handle_threshold_update(self, websocket: WebSocket, payload: Dict):
        """Handle confusion threshold update requests."""
        threshold = payload.get('threshold', 0.7)
        
        # Validate threshold
        threshold = max(0.0, min(1.0, threshold))
        
        # Broadcast threshold update to all clients
        await self.broadcast({
            "type": "threshold_updated",
            "data": {
                "threshold": threshold,
                "updated_by": "client",
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def _handle_status_request(self, websocket: WebSocket):
        """Handle status information requests."""
        status = {
            "type": "status_response",
            "data": {
                "connected_clients": len(self.active_connections),
                "server_time": asyncio.get_event_loop().time(),
                "connection_info": self.client_data.get(websocket, {})
            }
        }
        await self.send_personal_message(status, websocket)
    
    async def _handle_connection_error(self, websocket: WebSocket):
        """Handle connection errors and cleanup."""
        try:
            await websocket.close()
        except:
            pass
        finally:
            self.disconnect(websocket)
    
    async def cleanup_stale_connections(self):
        """Periodically clean up stale connections."""
        current_time = asyncio.get_event_loop().time()
        stale_threshold = 300  # 5 minutes
        
        stale_connections = []
        
        for websocket, data in self.client_data.items():
            if current_time - data.get('last_ping', 0) > stale_threshold:
                stale_connections.append(websocket)
        
        for websocket in stale_connections:
            logger.info("Cleaning up stale connection")
            await self._handle_connection_error(websocket)
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about current connections."""
        current_time = asyncio.get_event_loop().time()
        
        stats = {
            "total_connections": len(self.active_connections),
            "connections": []
        }
        
        for websocket, data in self.client_data.items():
            connection_info = {
                "connected_duration": current_time - data.get('connected_at', current_time),
                "last_ping_ago": current_time - data.get('last_ping', current_time),
                "is_active": websocket in self.active_connections
            }
            stats["connections"].append(connection_info)
        
        return stats