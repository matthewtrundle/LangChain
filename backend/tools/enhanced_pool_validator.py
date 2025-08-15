"""
Enhanced Pool Validator
Filters out obvious rugs and scam pools with sophisticated checks
"""

from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta

class EnhancedPoolValidator:
    def __init__(self):
        self.MIN_TVL_FOR_SAFETY = 10000  # $10k minimum TVL
        self.MIN_VOLUME_RATIO = 0.1  # Volume should be at least 10% of TVL daily
        self.MAX_VOLUME_RATIO = 10.0  # Volume shouldn't be more than 10x TVL (wash trading)
        self.MAX_REASONABLE_APY = 5000  # 5000% APY is suspicious
        self.MIN_REASONABLE_APY = 10    # Less than 10% APY not worth the risk
        
        # Known scam tokens/patterns
        self.SCAM_PATTERNS = [
            "PUMP", "MOON", "SAFE", "ELON", "DOGE", "INU", "SHIB",
            "100X", "1000X", "GEM", "ROCKET", "LAMBO"
        ]
        
        # Trusted tokens
        self.TRUSTED_TOKENS = [
            "SOL", "USDC", "USDT", "ETH", "BTC", "mSOL", "stSOL",
            "RAY", "ORCA", "JUP", "BONK", "WIF", "PYTH", "JTO"
        ]
    
    def validate_pool(self, pool: Dict) -> Optional[Dict]:
        """
        Validate a single pool and return it if valid, None if it's a rug
        """
        try:
            # Extract key metrics
            tvl = float(pool.get("tvl", 0))
            volume_24h = float(pool.get("volume_24h", 0))
            apy = float(pool.get("apy", 0))
            token_symbols = pool.get("token_symbols", "").upper()
            
            # 1. TVL Check - Must have reasonable liquidity
            if tvl < self.MIN_TVL_FOR_SAFETY:
                print(f"[Validator] Rejected {token_symbols}: TVL too low (${tvl:,.0f})")
                return None
            
            # 2. Volume Ratio Check - Detect wash trading or dead pools
            if tvl > 0:
                volume_ratio = volume_24h / tvl
                if volume_ratio < self.MIN_VOLUME_RATIO:
                    print(f"[Validator] Rejected {token_symbols}: Volume too low relative to TVL ({volume_ratio:.2f})")
                    return None
                if volume_ratio > self.MAX_VOLUME_RATIO:
                    print(f"[Validator] Rejected {token_symbols}: Suspicious volume/TVL ratio ({volume_ratio:.2f})")
                    return None
            
            # 3. APY Sanity Check
            if apy > self.MAX_REASONABLE_APY:
                print(f"[Validator] Rejected {token_symbols}: APY unreasonably high ({apy:.0f}%)")
                return None
            if apy < self.MIN_REASONABLE_APY:
                print(f"[Validator] Rejected {token_symbols}: APY too low ({apy:.0f}%)")
                return None
            
            # 4. Token Name Check - Filter obvious scams
            tokens = token_symbols.split("-") if "-" in token_symbols else [token_symbols]
            for token in tokens:
                # Check for scam patterns
                for scam_pattern in self.SCAM_PATTERNS:
                    if scam_pattern in token.upper():
                        print(f"[Validator] Rejected {token_symbols}: Contains scam pattern '{scam_pattern}'")
                        return None
            
            # 5. Check for at least one trusted token
            has_trusted_token = False
            for token in tokens:
                if token in self.TRUSTED_TOKENS:
                    has_trusted_token = True
                    break
            
            if not has_trusted_token:
                print(f"[Validator] Rejected {token_symbols}: No trusted tokens in pair")
                return None
            
            # 6. Calculate sustainability score
            sustainability_score = self._calculate_sustainability_score(pool)
            pool["sustainability_score"] = sustainability_score
            
            # 7. Calculate risk score
            risk_score = self._calculate_risk_score(pool)
            pool["risk_score"] = risk_score
            
            # 8. Add quality metrics
            pool["quality_metrics"] = {
                "tvl_score": min(tvl / 100000, 10),  # Score out of 10
                "volume_ratio_score": min(volume_ratio * 10, 10),
                "apy_reasonability": 10 - min(apy / 1000, 10),
                "has_trusted_token": has_trusted_token,
                "passes_all_checks": True
            }
            
            print(f"[Validator] Approved {token_symbols}: APY {apy:.0f}%, TVL ${tvl:,.0f}, Risk {risk_score}/10")
            return pool
            
        except Exception as e:
            print(f"[Validator] Error validating pool: {e}")
            return None
    
    def _calculate_sustainability_score(self, pool: Dict) -> float:
        """Calculate how sustainable the APY is"""
        apy = float(pool.get("apy", 0))
        tvl = float(pool.get("tvl", 0))
        volume_24h = float(pool.get("volume_24h", 0))
        
        score = 10.0
        
        # Penalize extreme APYs
        if apy > 1000:
            score -= (apy - 1000) / 1000  # Lose 1 point per 1000% over 1000%
        
        # Reward good TVL
        if tvl > 100000:
            score = min(score + 2, 10)
        elif tvl > 50000:
            score = min(score + 1, 10)
        
        # Reward healthy volume
        if tvl > 0:
            volume_ratio = volume_24h / tvl
            if 0.5 < volume_ratio < 3:
                score = min(score + 1, 10)
        
        return max(0, min(score, 10))
    
    def _calculate_risk_score(self, pool: Dict) -> float:
        """Calculate overall risk score (0-10, 10 being highest risk)"""
        apy = float(pool.get("apy", 0))
        tvl = float(pool.get("tvl", 0))
        
        risk = 0
        
        # APY risk
        if apy > 2000:
            risk += 4
        elif apy > 1000:
            risk += 2
        elif apy > 500:
            risk += 1
        
        # TVL risk
        if tvl < 25000:
            risk += 3
        elif tvl < 50000:
            risk += 2
        elif tvl < 100000:
            risk += 1
        
        # Token risk
        token_symbols = pool.get("token_symbols", "").upper()
        tokens = token_symbols.split("-") if "-" in token_symbols else [token_symbols]
        
        trusted_count = sum(1 for token in tokens if token in self.TRUSTED_TOKENS)
        if trusted_count == 0:
            risk += 3
        elif trusted_count == 1:
            risk += 1
        
        return min(risk, 10)
    
    def batch_validate(self, pools: List[Dict]) -> List[Dict]:
        """Validate multiple pools and return only valid ones"""
        validated_pools = []
        
        for pool in pools:
            validated_pool = self.validate_pool(pool)
            if validated_pool:
                validated_pools.append(validated_pool)
        
        # Sort by quality (lower risk, higher sustainability)
        validated_pools.sort(
            key=lambda p: (
                -p.get("sustainability_score", 0),  # Higher sustainability first
                p.get("risk_score", 10),            # Lower risk first
                -p.get("apy", 0)                    # Higher APY as tiebreaker
            )
        )
        
        return validated_pools

# Global instance
enhanced_validator = EnhancedPoolValidator()