"""WebSocket connection manager for real-time updates"""
from typing import Dict, Set, List
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_info: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_info[websocket] = {
            "connected_at": datetime.now().isoformat(),
            "subscriptions": set()
        }
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "Connected to Solana Degen Hunter real-time updates",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)
        if websocket in self.connection_info:
            del self.connection_info[websocket]
            
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"[WS] Error sending message: {e}")
            self.disconnect(websocket)
            
    async def broadcast(self, message: dict, channel: str = "general"):
        """Broadcast message to all connected clients"""
        # Add metadata
        message["channel"] = channel
        message["timestamp"] = datetime.now().isoformat()
        
        # Send to all active connections
        disconnected = []
        for connection in self.active_connections:
            try:
                # Check if client is subscribed to this channel
                subs = self.connection_info.get(connection, {}).get("subscriptions", set())
                if channel == "general" or channel in subs:
                    await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Broadcast error: {e}")
                disconnected.append(connection)
                
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
            
    async def broadcast_progress(self, task_id: str, status: str, progress: int, message: str):
        """Broadcast task progress update"""
        await self.broadcast({
            "type": "progress",
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "message": message
        }, channel="progress")
        
    async def broadcast_position_update(self, position_data: dict):
        """Broadcast position update"""
        await self.broadcast({
            "type": "position_update",
            "data": position_data
        }, channel="positions")
        
    async def broadcast_opportunity(self, pool_data: dict):
        """Broadcast new opportunity discovery"""
        await self.broadcast({
            "type": "new_opportunity",
            "data": pool_data
        }, channel="opportunities")
        
    async def subscribe(self, websocket: WebSocket, channels: List[str]):
        """Subscribe connection to specific channels"""
        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].update(channels)
            await self.send_personal_message({
                "type": "subscription",
                "status": "subscribed",
                "channels": channels
            }, websocket)

# Global WebSocket manager
ws_manager = ConnectionManager()