"""
WebSocket Connection Manager
Handles real-time connections and broadcasting updates
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            self.connection_count += 1
            logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
        
        if disconnected:
            logger.info(f"Removed {len(disconnected)} disconnected connections")
    
    async def broadcast_trade_event(self, event_type: str, data: dict):
        """Broadcast trading-specific events"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": data.get("timestamp", ""),
            "event_id": f"{event_type}_{self.connection_count}"
        }
        
        await self.broadcast(message)
        logger.info(f"Broadcasted {event_type} to {len(self.active_connections)} clients")
    
    async def broadcast_status_update(self, status_data: dict):
        """Broadcast bot status updates"""
        message = {
            "type": "status_update",
            "data": status_data,
            "timestamp": status_data.get("timestamp", "")
        }
        
        await self.broadcast(message)
    
    async def broadcast_pnl_update(self, pnl_data: dict):
        """Broadcast P&L updates"""
        message = {
            "type": "pnl_update",
            "data": pnl_data,
            "timestamp": pnl_data.get("timestamp", "")
        }
        
        await self.broadcast(message)
    
    def get_connection_info(self):
        """Get current connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "total_connections": self.connection_count,
            "connections_healthy": all(
                conn.client_state.name == "CONNECTED" 
                for conn in self.active_connections
            )
        }
