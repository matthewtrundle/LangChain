from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from datetime import datetime, timedelta
import json
from .helius_client import HeliusClient, PROGRAM_IDS

class PoolScannerInput(BaseModel):
    min_apy: float = Field(description="Minimum APY threshold to scan for")
    max_age_hours: int = Field(description="Maximum pool age in hours", default=24)
    protocols: List[str] = Field(description="List of protocols to scan", default=["raydium", "orca"])

class PoolScannerTool(BaseTool):
    name = "pool_scanner"
    description = "Scans for new liquidity pools on Solana with high APY potential"
    args_schema = PoolScannerInput
    
    def __init__(self):
        super().__init__()
        self.helius_client = HeliusClient()
    
    def _run(self, min_apy: float, max_age_hours: int = 24, protocols: List[str] = ["raydium", "orca"]) -> str:
        """Scan for new pools with high APY potential"""
        try:
            results = []
            
            # Scan each protocol
            for protocol in protocols:
                pools = self._scan_protocol(protocol, min_apy, max_age_hours)
                results.extend(pools)
            
            # Sort by APY descending
            results.sort(key=lambda x: x.get('estimated_apy', 0), reverse=True)
            
            return json.dumps({
                "found_pools": len(results),
                "pools": results[:10],  # Top 10 results
                "scan_time": datetime.now().isoformat()
            }, indent=2)
            
        except Exception as e:
            return f"Error scanning pools: {str(e)}"
    
    def _scan_protocol(self, protocol: str, min_apy: float, max_age_hours: int) -> List[Dict]:
        """Scan a specific protocol for new pools"""
        protocol_pools = []
        
        if protocol.lower() == "raydium":
            protocol_pools = self._scan_raydium(min_apy, max_age_hours)
        elif protocol.lower() == "orca":
            protocol_pools = self._scan_orca(min_apy, max_age_hours)
        
        return protocol_pools
    
    def _scan_raydium(self, min_apy: float, max_age_hours: int) -> List[Dict]:
        """Scan Raydium for new pools"""
        pools = []
        
        try:
            # Get recent transactions from Raydium program
            program_id = PROGRAM_IDS["RAYDIUM_AMM"]
            
            # This is a simplified version - in production we'd parse actual transactions
            # For now, return mock data that demonstrates the concept
            mock_pools = [
                {
                    "pool_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                    "protocol": "raydium",
                    "token_a": "BONK",
                    "token_b": "USDC",
                    "estimated_apy": 1247.5,
                    "tvl": 890000,
                    "volume_24h": 125000,
                    "age_hours": 18,
                    "creator": "4xZ7...9qWx",
                    "liquidity_locked": True
                },
                {
                    "pool_address": "9yKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                    "protocol": "raydium",
                    "token_a": "PEPE",
                    "token_b": "SOL",
                    "estimated_apy": 2847.2,
                    "tvl": 340000,
                    "volume_24h": 89000,
                    "age_hours": 6,
                    "creator": "8xZ7...1qWx",
                    "liquidity_locked": False
                }
            ]
            
            # Filter by criteria
            for pool in mock_pools:
                if (pool["estimated_apy"] >= min_apy and 
                    pool["age_hours"] <= max_age_hours):
                    pools.append(pool)
            
        except Exception as e:
            print(f"Error scanning Raydium: {e}")
        
        return pools
    
    def _scan_orca(self, min_apy: float, max_age_hours: int) -> List[Dict]:
        """Scan Orca for new pools"""
        pools = []
        
        try:
            # Mock Orca data
            mock_pools = [
                {
                    "pool_address": "5xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                    "protocol": "orca",
                    "token_a": "SAMO",
                    "token_b": "USDC",
                    "estimated_apy": 567.8,
                    "tvl": 1200000,
                    "volume_24h": 95000,
                    "age_hours": 12,
                    "creator": "3xZ7...5qWx",
                    "liquidity_locked": True
                }
            ]
            
            # Filter by criteria
            for pool in mock_pools:
                if (pool["estimated_apy"] >= min_apy and 
                    pool["age_hours"] <= max_age_hours):
                    pools.append(pool)
            
        except Exception as e:
            print(f"Error scanning Orca: {e}")
        
        return pools
    
    async def _arun(self, min_apy: float, max_age_hours: int = 24, protocols: List[str] = ["raydium", "orca"]) -> str:
        """Async version of the tool"""
        return self._run(min_apy, max_age_hours, protocols)