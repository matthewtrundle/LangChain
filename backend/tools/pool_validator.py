import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json

class PoolValidator:
    """Validates pool activity and liquidity status"""
    
    def __init__(self):
        self.minimum_liquidity_usd = 1000  # Minimum $1k liquidity to be considered active
        self.minimum_volume_24h = 100  # Minimum $100 daily volume
        self.known_deprecated_pools = set()  # Cache of known bad pools
        
    def validate_pool(self, pool_data: Dict) -> Dict[str, any]:
        """
        Validates if a pool is actually tradeable and has real liquidity
        Returns validation result with status and reasons
        """
        validation_result = {
            "is_valid": True,
            "is_tradeable": True,
            "warnings": [],
            "errors": [],
            "status": "ACTIVE"
        }
        
        # Check liquidity
        tvl = pool_data.get("tvl", 0)
        if tvl < self.minimum_liquidity_usd:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Liquidity too low: ${tvl:,.2f} < ${self.minimum_liquidity_usd}")
            validation_result["status"] = "LOW_LIQUIDITY"
        
        # Check volume
        volume_24h = pool_data.get("volume_24h", 0)
        if volume_24h < self.minimum_volume_24h:
            validation_result["warnings"].append(f"Low 24h volume: ${volume_24h:,.2f}")
            if volume_24h == 0:
                validation_result["is_tradeable"] = False
                validation_result["errors"].append("No trading volume - pool may be inactive")
                validation_result["status"] = "INACTIVE"
        
        # Check for suspicious patterns
        apy = pool_data.get("apy", 0)
        if apy > 10000:  # 10,000% APY
            validation_result["warnings"].append(f"Suspiciously high APY: {apy:,.1f}%")
        
        # Volume to TVL ratio check
        if tvl > 0:
            volume_tvl_ratio = volume_24h / tvl
            if volume_tvl_ratio > 10:  # Volume is 10x TVL
                validation_result["warnings"].append(f"High volume/TVL ratio: {volume_tvl_ratio:.2f}x - possible wash trading")
            elif volume_tvl_ratio < 0.01:  # Volume is less than 1% of TVL
                validation_result["warnings"].append(f"Very low volume/TVL ratio: {volume_tvl_ratio:.4f}x - low activity")
        
        # Check pool age if available
        age_hours = pool_data.get("age_hours", 24)
        if age_hours < 1:
            validation_result["warnings"].append("Brand new pool - less than 1 hour old")
        
        # Additional Raydium-specific checks
        if pool_data.get("protocol") == "raydium":
            self._validate_raydium_pool(pool_data, validation_result)
        
        return validation_result
    
    def _validate_raydium_pool(self, pool_data: Dict, validation_result: Dict):
        """Raydium-specific validation"""
        pool_address = pool_data.get("pool_address", "")
        
        # Check if pool is in deprecated list
        if pool_address in self.known_deprecated_pools:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Pool is deprecated or migrated")
            validation_result["status"] = "DEPRECATED"
            return
        
        # Check for Raydium v3/v4 migration patterns
        # Old pools often have specific patterns in their addresses
        if self._is_likely_old_pool(pool_data):
            validation_result["warnings"].append("Pool may be from older Raydium version")
    
    def _is_likely_old_pool(self, pool_data: Dict) -> bool:
        """Heuristic to detect likely old/migrated pools"""
        # If volume is 0 but TVL exists, likely old
        if pool_data.get("volume_24h", 0) == 0 and pool_data.get("tvl", 0) > 0:
            return True
        
        # If APY is exactly 0 with some TVL, likely inactive
        if pool_data.get("apy", 0) == 0 and pool_data.get("tvl", 0) > 10000:
            return True
        
        return False
    
    def batch_validate(self, pools: List[Dict]) -> List[Dict]:
        """Validate multiple pools and filter out invalid ones"""
        validated_pools = []
        
        for pool in pools:
            validation = self.validate_pool(pool)
            pool["validation"] = validation
            
            # Only include pools that are valid and tradeable
            if validation["is_valid"] and validation["is_tradeable"]:
                validated_pools.append(pool)
            else:
                print(f"[PoolValidator] Filtered out {pool.get('token_symbols', 'unknown')} - Status: {validation['status']}")
        
        return validated_pools
    
    def check_pool_on_chain(self, pool_address: str, helius_client) -> Dict:
        """
        Advanced: Check pool status directly on-chain
        This would use Helius to get account info
        """
        try:
            # This would make an actual RPC call to check the pool account
            # For now, returning a placeholder
            return {
                "exists": True,
                "has_liquidity": True,
                "last_update": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "exists": False,
                "error": str(e)
            }