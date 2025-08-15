"""
Helius WebSocket Integration for Real-Time Pool Updates
Based on GPT-4o Builder recommendations
"""
import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional, Callable, Set
from datetime import datetime, timedelta
from collections import defaultdict
import backoff
from enum import Enum

logger = logging.getLogger(__name__)

class SubscriptionType(Enum):
    ACCOUNT = "accountSubscribe"
    PROGRAM = "programSubscribe"
    LOGS = "logsSubscribe"
    SIGNATURE = "signatureSubscribe"

class HeliusWebSocketClient:
    def __init__(self, api_key: str, max_reconnect_attempts: int = 5):
        self.api_key = api_key
        self.ws_url = f"wss://atlas-mainnet.helius-rpc.com/?api-key={api_key}"
        self.max_reconnect_attempts = max_reconnect_attempts
        self.subscriptions: Dict[str, Dict] = {}
        self.subscription_id = 0
        self.websocket = None
        self.running = False
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.connection_task = None
        self.heartbeat_task = None
        self.metrics = {
            "messages_received": 0,
            "connection_failures": 0,
            "last_message_time": None,
            "connected_since": None
        }
        
    async def connect(self):
        """Establish WebSocket connection with Helius"""
        try:
            logger.info("Connecting to Helius WebSocket...")
            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            self.running = True
            self.metrics["connected_since"] = datetime.now()
            logger.info("Successfully connected to Helius WebSocket")
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
            
            # Resubscribe to all previous subscriptions
            await self._resubscribe_all()
            
        except Exception as e:
            logger.error(f"Failed to connect to Helius WebSocket: {e}")
            self.metrics["connection_failures"] += 1
            raise
    
    async def disconnect(self):
        """Gracefully disconnect from WebSocket"""
        self.running = False
        
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        logger.info("Disconnected from Helius WebSocket")
    
    @backoff.on_exception(
        backoff.expo,
        websockets.exceptions.WebSocketException,
        max_tries=5,
        max_time=300
    )
    async def _reconnect(self):
        """Reconnect with exponential backoff"""
        logger.info("Attempting to reconnect...")
        await self.disconnect()
        await self.connect()
    
    async def _heartbeat(self):
        """Send periodic ping to keep connection alive"""
        while self.running:
            try:
                if self.websocket and not self.websocket.closed:
                    pong_waiter = await self.websocket.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                await asyncio.sleep(30)
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                if self.running:
                    await self._reconnect()
    
    async def subscribe_to_program(self, program_id: str, handler: Callable):
        """Subscribe to all transactions for a specific program"""
        sub_id = self._get_next_subscription_id()
        
        request = {
            "jsonrpc": "2.0",
            "id": sub_id,
            "method": "programSubscribe",
            "params": [
                program_id,
                {
                    "encoding": "jsonParsed",
                    "commitment": "confirmed",
                    "filters": []
                }
            ]
        }
        
        await self._send_subscription(sub_id, request, program_id, handler)
        return sub_id
    
    async def subscribe_to_account(self, account: str, handler: Callable):
        """Subscribe to account changes"""
        sub_id = self._get_next_subscription_id()
        
        request = {
            "jsonrpc": "2.0",
            "id": sub_id,
            "method": "accountSubscribe",
            "params": [
                account,
                {
                    "encoding": "jsonParsed",
                    "commitment": "confirmed"
                }
            ]
        }
        
        await self._send_subscription(sub_id, request, account, handler)
        return sub_id
    
    async def subscribe_to_logs(self, mentions: List[str], handler: Callable):
        """Subscribe to logs mentioning specific addresses"""
        sub_id = self._get_next_subscription_id()
        
        request = {
            "jsonrpc": "2.0",
            "id": sub_id,
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": mentions
                },
                {
                    "commitment": "confirmed"
                }
            ]
        }
        
        await self._send_subscription(sub_id, request, f"logs_{mentions[0]}", handler)
        return sub_id
    
    async def unsubscribe(self, subscription_id: int):
        """Unsubscribe from a specific subscription"""
        if subscription_id not in self.subscriptions:
            logger.warning(f"Subscription {subscription_id} not found")
            return
            
        sub_info = self.subscriptions[subscription_id]
        
        request = {
            "jsonrpc": "2.0",
            "id": subscription_id + 1000,  # Different ID for unsubscribe
            "method": f"{sub_info['type']}Unsubscribe",
            "params": [sub_info['subscription_id']]
        }
        
        if self.websocket and not self.websocket.closed:
            await self.websocket.send(json.dumps(request))
            del self.subscriptions[subscription_id]
            logger.info(f"Unsubscribed from {subscription_id}")
    
    async def _send_subscription(self, sub_id: int, request: Dict, key: str, handler: Callable):
        """Send subscription request and register handler"""
        if not self.websocket or self.websocket.closed:
            await self.connect()
            
        await self.websocket.send(json.dumps(request))
        
        # Store subscription info for reconnection
        self.subscriptions[sub_id] = {
            "request": request,
            "key": key,
            "handler": handler,
            "type": request["method"].replace("Subscribe", ""),
            "subscription_id": None  # Will be set when confirmed
        }
        
        # Register handler
        self.message_handlers[key].append(handler)
        
        logger.info(f"Sent subscription request {sub_id} for {key}")
    
    async def _resubscribe_all(self):
        """Resubscribe to all subscriptions after reconnection"""
        for sub_id, info in self.subscriptions.items():
            try:
                await self.websocket.send(json.dumps(info['request']))
                logger.info(f"Resubscribed to {info['key']}")
            except Exception as e:
                logger.error(f"Failed to resubscribe to {info['key']}: {e}")
    
    def _get_next_subscription_id(self) -> int:
        """Get next subscription ID"""
        self.subscription_id += 1
        return self.subscription_id
    
    async def listen(self):
        """Main loop to listen for WebSocket messages"""
        while self.running:
            try:
                if not self.websocket or self.websocket.closed:
                    await self._reconnect()
                    
                message = await self.websocket.recv()
                await self._handle_message(message)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                if self.running:
                    await self._reconnect()
                    
            except Exception as e:
                logger.error(f"Error in WebSocket listener: {e}")
                if self.running:
                    await asyncio.sleep(1)
    
    async def _handle_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            self.metrics["messages_received"] += 1
            self.metrics["last_message_time"] = datetime.now()
            
            # Handle subscription confirmation
            if "id" in data and "result" in data:
                sub_id = data["id"]
                if sub_id in self.subscriptions:
                    self.subscriptions[sub_id]["subscription_id"] = data["result"]
                    logger.info(f"Subscription {sub_id} confirmed with ID {data['result']}")
                return
            
            # Handle notification
            if "method" in data and data["method"].endswith("Notification"):
                await self._handle_notification(data)
                
        except json.JSONDecodeError:
            logger.error(f"Failed to decode message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _handle_notification(self, data: Dict):
        """Handle subscription notification"""
        params = data.get("params", {})
        subscription_id = params.get("subscription")
        
        # Find subscription info
        sub_info = None
        for sid, info in self.subscriptions.items():
            if info.get("subscription_id") == subscription_id:
                sub_info = info
                break
                
        if not sub_info:
            logger.warning(f"Received notification for unknown subscription {subscription_id}")
            return
            
        # Call registered handlers
        result = params.get("result")
        if result and sub_info["key"] in self.message_handlers:
            for handler in self.message_handlers[sub_info["key"]]:
                try:
                    await handler(result)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
    
    def get_metrics(self) -> Dict:
        """Get connection metrics"""
        return {
            **self.metrics,
            "active_subscriptions": len(self.subscriptions),
            "is_connected": self.websocket is not None and not self.websocket.closed
        }


class PoolUpdateHandler:
    """Handler for processing pool updates from WebSocket"""
    
    def __init__(self, update_callback: Callable):
        self.update_callback = update_callback
        self.seen_signatures: Set[str] = set()
        self.pool_cache: Dict[str, Dict] = {}
        
    async def handle_program_update(self, data: Dict):
        """Process program update notification"""
        try:
            signature = data.get("signature")
            
            # Skip if already processed
            if signature in self.seen_signatures:
                return
                
            self.seen_signatures.add(signature)
            
            # Extract pool data from transaction
            pool_data = await self._extract_pool_data(data)
            if pool_data:
                await self.update_callback(pool_data)
                
        except Exception as e:
            logger.error(f"Error handling program update: {e}")
    
    async def _extract_pool_data(self, transaction_data: Dict) -> Optional[Dict]:
        """Extract pool information from transaction data"""
        # This would parse the transaction to extract pool creation/update info
        # Implementation depends on specific program structure
        
        # For now, return a basic structure
        return {
            "type": "pool_update",
            "timestamp": datetime.now().isoformat(),
            "signature": transaction_data.get("signature"),
            "program": transaction_data.get("accountId"),
            "data": transaction_data
        }