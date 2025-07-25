from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from datetime import datetime, timedelta
import json
from tools.helius_client import HeliusClient, PROGRAM_IDS

class PoolScannerInput(BaseModel):
    min_apy: float = Field(description="Minimum APY threshold to scan for")
    max_age_hours: int = Field(description="Maximum pool age in hours", default=24)
    protocols: List[str] = Field(description="List of protocols to scan", default=["raydium", "orca"])

class PoolScannerTool(BaseTool):
    name = "pool_scanner"
    description = "Scans for new liquidity pools on Solana with high APY potential"
    args_schema = PoolScannerInput
    helius_client: Any = Field(default=None, exclude=True)
    
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
        """Deprecated - Use RadiumScannerTool instead"""
        raise NotImplementedError(
            "Mock pool scanner has been removed. Use RadiumScannerTool or RealPoolScannerTool for real data."
        )
    
    def _scan_orca(self, min_apy: float, max_age_hours: int) -> List[Dict]:
        """Deprecated - Use real scanners instead"""
        raise NotImplementedError(
            "Mock pool scanner has been removed. Use RadiumScannerTool or RealPoolScannerTool for real data."
        )
    
    async def _arun(self, min_apy: float, max_age_hours: int = 24, protocols: List[str] = ["raydium", "orca"]) -> str:
        """Async version of the tool"""
        return self._run(min_apy, max_age_hours, protocols)