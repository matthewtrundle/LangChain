"""
Real-time Pool Scanner using Helius WebSocket
Implements Executive AI and DeFi Strategist recommendations
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import aiohttp
from collections import deque

from tools.helius_websocket import HeliusWebSocketClient, PoolUpdateHandler
from tools.helius_client import HeliusClient, PROGRAM_IDS
from config import Config

logger = logging.getLogger(__name__)

class RealtimePoolScannerInput(BaseModel):
    min_apy: float = Field(description="Minimum APY threshold to track", default=100)
    max_pools: int = Field(description="Maximum number of pools to track", default=100)
    protocols: List[str] = Field(
        description="Protocols to monitor", 
        default=["raydium", "orca", "meteora"]
    )

class PoolMetrics:
    """Track pool metrics with DeFi Strategist formulas"""
    
    def __init__(self, pool_address: str):
        self.pool_address = pool_address
        self.creation_time = datetime.now()
        self.updates = deque(maxlen=100)  # Keep last 100 updates
        self.tvl_history = deque(maxlen=24)  # 24 hour history
        self.volume_history = deque(maxlen=24)
        self.apy_history = deque(maxlen=24)
        
    def add_update(self, data: Dict):
        """Add new update and calculate metrics"""
        self.updates.append({
            "timestamp": datetime.now(),
            "data": data
        })
        
        # Update histories
        if "tvl" in data:
            self.tvl_history.append((datetime.now(), data["tvl"]))
        if "volume_24h" in data:
            self.volume_history.append((datetime.now(), data["volume_24h"]))
        if "apy" in data:
            self.apy_history.append((datetime.now(), data["apy"]))
    
    def calculate_apy_with_fees(self, fee_rate: float, volume_24h: float, tvl: float) -> float:
        """Calculate APY including trading fees (DeFi Strategist formula)"""
        if tvl <= 0:
            return 0
            
        daily_fees = volume_24h * fee_rate
        daily_yield = (daily_fees / tvl) * 100
        apy = ((1 + daily_yield / 100) ** 365 - 1) * 100
        
        return apy
    
    def calculate_impermanent_loss(self, price_ratio_change: float) -> float:
        """Calculate IL based on price ratio change (DeFi Strategist formula)"""
        import math
        
        if price_ratio_change <= 0:
            return 0
            
        # IL = 1 - (2 * sqrt(price_ratio)) / (1 + price_ratio)
        sqrt_ratio = math.sqrt(price_ratio_change)
        il = 1 - (2 * sqrt_ratio) / (1 + price_ratio_change)
        
        return il * 100  # Return as percentage
    
    def calculate_sustainability_score(self) -> float:
        """Calculate sustainability score based on multiple factors"""
        if not self.apy_history or not self.tvl_history:
            return 0
            
        latest_apy = self.apy_history[-1][1] if self.apy_history else 0
        latest_tvl = self.tvl_history[-1][1] if self.tvl_history else 0
        
        # Factors for sustainability
        score = 10.0
        
        # APY too high is unsustainable
        if latest_apy > 5000:
            score -= 5
        elif latest_apy > 2000:
            score -= 3
        elif latest_apy > 1000:
            score -= 1
            
        # Low TVL is risky
        if latest_tvl < 10000:
            score -= 4
        elif latest_tvl < 100000:
            score -= 2
        elif latest_tvl < 1000000:
            score -= 1
            
        # Age factor
        age_days = (datetime.now() - self.creation_time).days
        if age_days < 1:
            score -= 2
        elif age_days < 7:
            score -= 1
            
        # Volatility in APY
        if len(self.apy_history) > 3:
            apy_values = [h[1] for h in self.apy_history[-5:]]
            apy_std = self._calculate_std(apy_values)
            if apy_std > 1000:
                score -= 2
                
        return max(0, score)
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_metrics_summary(self) -> Dict:
        """Get comprehensive metrics summary"""
        latest_update = self.updates[-1] if self.updates else {}
        latest_data = latest_update.get("data", {})
        
        return {
            "pool_address": self.pool_address,
            "age_hours": (datetime.now() - self.creation_time).total_seconds() / 3600,
            "update_count": len(self.updates),
            "current_tvl": self.tvl_history[-1][1] if self.tvl_history else 0,
            "current_apy": self.apy_history[-1][1] if self.apy_history else 0,
            "sustainability_score": self.calculate_sustainability_score(),
            "last_update": latest_update.get("timestamp", "").isoformat() if latest_update else None
        }

class RealtimePoolScannerTool(BaseTool):
    """Real-time pool scanner using WebSocket for instant updates"""
    
    name = "realtime_pool_scanner"
    description = "Monitors pools in real-time using WebSocket connections"
    args_schema = RealtimePoolScannerInput
    
    def __init__(self):
        super().__init__()
        self.helius_client = HeliusClient()
        self.ws_client = None
        self.pool_metrics: Dict[str, PoolMetrics] = {}
        self.active_subscriptions: Set[str] = set()
        self.running = False
        self._session = None
        
    async def start(self):
        """Start the real-time scanner"""
        if self.running:
            logger.warning("Scanner already running")
            return
            
        logger.info("Starting realtime pool scanner...")
        
        # Initialize WebSocket client
        self.ws_client = HeliusWebSocketClient(Config.HELIUS_API_KEY)
        await self.ws_client.connect()
        
        # Create aiohttp session for API calls
        self._session = aiohttp.ClientSession()
        
        # Subscribe to DeFi programs
        await self._subscribe_to_programs()
        
        # Start WebSocket listener
        self.running = True
        asyncio.create_task(self.ws_client.listen())
        
        # Start metrics updater
        asyncio.create_task(self._update_metrics_loop())
        
        logger.info("Realtime pool scanner started successfully")
    
    async def stop(self):
        """Stop the scanner"""
        self.running = False
        
        if self.ws_client:
            await self.ws_client.disconnect()
            
        if self._session:
            await self._session.close()
            
        logger.info("Realtime pool scanner stopped")
    
    async def _subscribe_to_programs(self):
        """Subscribe to all DeFi program updates"""
        handler = PoolUpdateHandler(self._handle_pool_update)
        
        for protocol, program_id in PROGRAM_IDS.items():
            try:
                sub_id = await self.ws_client.subscribe_to_program(
                    program_id, 
                    handler.handle_program_update
                )
                self.active_subscriptions.add(f"{protocol}:{sub_id}")
                logger.info(f"Subscribed to {protocol} program: {program_id}")
            except Exception as e:
                logger.error(f"Failed to subscribe to {protocol}: {e}")
    
    async def _handle_pool_update(self, pool_data: Dict):
        """Handle incoming pool update"""
        try:
            pool_address = pool_data.get("pool_address") or pool_data.get("address")
            
            if not pool_address:
                return
                
            # Create or update pool metrics
            if pool_address not in self.pool_metrics:
                self.pool_metrics[pool_address] = PoolMetrics(pool_address)
                logger.info(f"New pool discovered: {pool_address}")
                
            metrics = self.pool_metrics[pool_address]
            metrics.add_update(pool_data)
            
            # Check if pool meets criteria
            if await self._evaluate_pool(pool_address):
                logger.info(f"High-yield pool alert: {pool_address}")
                
        except Exception as e:
            logger.error(f"Error handling pool update: {e}")
    
    async def _evaluate_pool(self, pool_address: str) -> bool:
        """Evaluate if pool meets criteria"""
        metrics = self.pool_metrics.get(pool_address)
        if not metrics:
            return False
            
        summary = metrics.get_metrics_summary()
        
        # Apply criteria
        if summary["current_apy"] >= 100 and summary["sustainability_score"] >= 5:
            return True
            
        return False
    
    async def _update_metrics_loop(self):
        """Periodically update pool metrics from APIs"""
        while self.running:
            try:
                # Update metrics for tracked pools
                for pool_address in list(self.pool_metrics.keys()):
                    await self._update_pool_metrics(pool_address)
                    
                # Clean up old pools
                await self._cleanup_old_pools()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error in metrics update loop: {e}")
                await asyncio.sleep(10)
    
    async def _update_pool_metrics(self, pool_address: str):
        """Update pool metrics from various sources"""
        try:
            # Get TVL and volume from DeFiLlama
            defi_data = await self._get_defi_llama_data(pool_address)
            
            # Get price data from Jupiter
            price_data = await self._get_jupiter_prices(pool_address)
            
            # Combine data
            update_data = {
                **defi_data,
                **price_data,
                "timestamp": datetime.now().isoformat()
            }
            
            if pool_address in self.pool_metrics:
                self.pool_metrics[pool_address].add_update(update_data)
                
        except Exception as e:
            logger.error(f"Error updating metrics for {pool_address}: {e}")
    
    async def _get_defi_llama_data(self, pool_address: str) -> Dict:
        """Get pool data from DeFiLlama"""
        try:
            async with self._session.get(
                "https://yields.llama.fi/pools",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Find matching pool
                    for pool in data.get("data", []):
                        if pool.get("pool", "").lower() == pool_address.lower():
                            return {
                                "tvl": pool.get("tvlUsd", 0),
                                "apy": pool.get("apy", 0),
                                "volume_24h": pool.get("volumeUsd1d", 0)
                            }
        except Exception as e:
            logger.error(f"DeFiLlama API error: {e}")
            
        return {}
    
    async def _get_jupiter_prices(self, pool_address: str) -> Dict:
        """Get token prices from Jupiter"""
        # Implementation would fetch actual prices
        # For now return empty dict
        return {}
    
    async def _cleanup_old_pools(self):
        """Remove pools that haven't been updated recently"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        to_remove = []
        for pool_address, metrics in self.pool_metrics.items():
            if metrics.updates:
                last_update = metrics.updates[-1]["timestamp"]
                if last_update < cutoff_time:
                    to_remove.append(pool_address)
                    
        for pool_address in to_remove:
            del self.pool_metrics[pool_address]
            logger.info(f"Removed stale pool: {pool_address}")
    
    def _run(self, min_apy: float = 100, max_pools: int = 100, 
             protocols: List[str] = ["raydium", "orca", "meteora"]) -> str:
        """Get current high-yield pools from real-time data"""
        
        # Filter and sort pools
        eligible_pools = []
        
        for pool_address, metrics in self.pool_metrics.items():
            summary = metrics.get_metrics_summary()
            
            if summary["current_apy"] >= min_apy:
                eligible_pools.append(summary)
                
        # Sort by APY descending
        eligible_pools.sort(key=lambda x: x["current_apy"], reverse=True)
        
        # Limit to max_pools
        top_pools = eligible_pools[:max_pools]
        
        return json.dumps({
            "source": "REALTIME_WEBSOCKET",
            "found_pools": len(eligible_pools),
            "monitoring_pools": len(self.pool_metrics),
            "active_subscriptions": len(self.active_subscriptions),
            "pools": top_pools,
            "scan_time": datetime.now().isoformat(),
            "websocket_metrics": self.ws_client.get_metrics() if self.ws_client else {}
        }, indent=2)
    
    async def _arun(self, min_apy: float = 100, max_pools: int = 100,
                    protocols: List[str] = ["raydium", "orca", "meteora"]) -> str:
        """Async version"""
        return self._run(min_apy, max_pools, protocols)