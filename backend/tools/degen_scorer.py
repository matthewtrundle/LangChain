from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
import json
from tools.helius_client import HeliusClient

class DegenScorerInput(BaseModel):
    pool_address: str = Field(description="Pool address to analyze")
    pool_data: Dict = Field(description="Pool data from scanner")

class DegenScorerTool(BaseTool):
    name = "degen_scorer"
    description = "Calculates a degen score (0-10) for a pool based on risk factors"
    args_schema = DegenScorerInput
    helius_client: Any = Field(default=None, exclude=True)
    
    def __init__(self):
        super().__init__()
        self.helius_client = HeliusClient()
    
    def _run(self, pool_address: str, pool_data: Dict = None) -> str:
        """Calculate degen score for a pool"""
        try:
            # If no pool data provided, create basic data
            if not pool_data:
                pool_data = {
                    "pool_address": pool_address,
                    "tvl": 50000,  # Mock $50k TVL
                    "volume_24h": 25000,
                    "apy": 500,
                    "age_hours": 24,
                    "liquidity_locked": False
                }
            
            # Calculate all scoring components
            score_components = {
                "liquidity_score": self._score_liquidity(pool_data),
                "age_score": self._score_age(pool_data),
                "volume_score": self._score_volume(pool_data),
                "creator_score": self._score_creator(pool_data),
                "token_score": self._score_tokens(pool_data),
                "apy_sustainability": self._score_apy_sustainability(pool_data)
            }
            
            # Calculate weighted average
            weights = {
                "liquidity_score": 0.20,
                "age_score": 0.10,
                "volume_score": 0.20,
                "creator_score": 0.20,
                "token_score": 0.15,
                "apy_sustainability": 0.15
            }
            
            total_score = sum(
                score_components[component] * weights[component]
                for component in score_components
            )
            
            risk_level = self._get_risk_level(total_score)
            red_flags = self._check_red_flags(pool_data, score_components)
            
            return json.dumps({
                "pool_address": pool_address,
                "degen_score": round(total_score, 1),
                "risk_level": risk_level,
                "score_breakdown": score_components,
                "red_flags": red_flags,
                "recommendation": self._get_recommendation(total_score, pool_data, red_flags),
                "analysis_summary": self._get_analysis_summary(pool_data, score_components)
            }, indent=2)
            
        except Exception as e:
            return f"Error calculating degen score: {str(e)}"
    
    def _score_liquidity(self, pool_data: Dict) -> float:
        """Score based on liquidity factors (0-10)"""
        tvl = pool_data.get("tvl", 0)
        locked = pool_data.get("liquidity_locked", False)
        
        # Base score from TVL
        if tvl > 10000000:  # > $10M
            tvl_score = 9.0
        elif tvl > 1000000:  # > $1M
            tvl_score = 7.0
        elif tvl > 100000:  # > $100K
            tvl_score = 5.0
        elif tvl > 10000:  # > $10K
            tvl_score = 3.0
        else:
            tvl_score = 1.0
        
        # Bonus for locked liquidity
        lock_bonus = 2.0 if locked else 0.0
        
        return min(10.0, tvl_score + lock_bonus)
    
    def _score_age(self, pool_data: Dict) -> float:
        """Score based on pool age (0-10)"""
        age_hours = pool_data.get("age_hours", 0)
        
        # Newer pools are riskier but potentially more rewarding
        if age_hours < 1:
            return 10.0  # Brand new - highest risk/reward
        elif age_hours < 6:
            return 8.5
        elif age_hours < 24:
            return 7.0
        elif age_hours < 72:
            return 5.0
        else:
            return 3.0  # Older pools are safer but lower potential
    
    def _score_volume(self, pool_data: Dict) -> float:
        """Score based on trading volume (0-10)"""
        volume_24h = pool_data.get("volume_24h", 0)
        tvl = pool_data.get("tvl", 1)
        
        # Volume to TVL ratio
        if tvl > 0:
            volume_ratio = volume_24h / tvl
            
            if volume_ratio > 0.5:  # High activity
                return 9.0
            elif volume_ratio > 0.1:
                return 7.0
            elif volume_ratio > 0.01:
                return 5.0
            else:
                return 2.0
        
        return 1.0
    
    def _score_creator(self, pool_data: Dict) -> float:
        """Score based on pool creator analysis (0-10)"""
        creator = pool_data.get("creator", "")
        
        # In production, we'd analyze creator's history
        # For now, return a mock score
        known_good_creators = ["4xZ7...9qWx"]  # Mock whitelist
        known_bad_creators = ["8xZ7...1qWx"]   # Mock blacklist
        
        if creator in known_good_creators:
            return 8.0
        elif creator in known_bad_creators:
            return 2.0
        else:
            return 5.0  # Unknown creator
    
    def _score_tokens(self, pool_data: Dict) -> float:
        """Score based on token analysis (0-10)"""
        token_a = pool_data.get("token_a", "")
        token_b = pool_data.get("token_b", "")
        
        # Stable pairs are safer
        stables = ["USDC", "USDT", "SOL"]
        
        stable_count = sum(1 for token in [token_a, token_b] if token in stables)
        
        if stable_count == 2:
            return 4.0  # Very safe but low yield potential
        elif stable_count == 1:
            return 7.0  # Good balance
        else:
            return 9.0  # High risk, high reward
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 8.0:
            return "EXTREME"
        elif score >= 6.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _score_apy_sustainability(self, pool_data: Dict) -> float:
        """Score APY sustainability (0-10)"""
        apy = pool_data.get("apy", pool_data.get("estimated_apy", 0))
        volume_24h = pool_data.get("volume_24h", 0)
        tvl = pool_data.get("tvl", 1)
        
        # Very high APY is often unsustainable
        if apy > 5000:  # > 5000%
            apy_score = 9.0  # Extremely risky
        elif apy > 2000:  # > 2000%
            apy_score = 7.5
        elif apy > 1000:  # > 1000%
            apy_score = 6.0
        elif apy > 500:   # > 500%
            apy_score = 4.5
        else:
            apy_score = 3.0
        
        # Check if volume supports the APY
        if tvl > 0:
            daily_yield = (apy / 365) * tvl / 100
            if volume_24h > daily_yield * 2:  # Volume can support yield
                apy_score = max(1.0, apy_score - 2.0)
        
        return apy_score
    
    def _check_red_flags(self, pool_data: Dict, scores: Dict) -> List[str]:
        """Check for red flags in the pool"""
        red_flags = []
        
        # Check TVL
        if pool_data.get("tvl", 0) < 10000:
            red_flags.append("⚠️ Very low TVL (< $10k)")
        
        # Check liquidity lock
        if not pool_data.get("liquidity_locked", False) and pool_data.get("apy", 0) > 1000:
            red_flags.append("🚨 No liquidity lock with extreme APY")
        
        # Check volume
        if pool_data.get("volume_24h", 0) < 1000:
            red_flags.append("⚠️ Extremely low volume")
        
        # Check age
        if pool_data.get("age_hours", 24) < 6:
            red_flags.append("🆕 Very new pool (< 6 hours)")
        
        # Check APY sustainability
        if scores.get("apy_sustainability", 0) > 7:
            red_flags.append("💀 Unsustainable APY")
        
        return red_flags
    
    def _get_analysis_summary(self, pool_data: Dict, scores: Dict) -> str:
        """Generate detailed analysis summary"""
        apy = pool_data.get("apy", pool_data.get("estimated_apy", 0))
        tvl = pool_data.get("tvl", 0)
        volume = pool_data.get("volume_24h", 0)
        
        summary = f"Pool Analysis:\n"
        summary += f"- APY: {apy:.1f}% {'(Sustainable)' if scores['apy_sustainability'] < 5 else '(Unsustainable)'}\n"
        summary += f"- TVL: ${tvl:,.0f} {'(Healthy)' if tvl > 100000 else '(Low)'}\n"
        summary += f"- 24h Volume: ${volume:,.0f}\n"
        summary += f"- Liquidity: {'Locked ✅' if pool_data.get('liquidity_locked') else 'Not Locked ❌'}\n"
        summary += f"- Age: {pool_data.get('age_hours', 0):.1f} hours\n"
        
        return summary

    def _get_recommendation(self, score: float, pool_data: Dict, red_flags: List[str]) -> str:
        """Generate recommendation based on score and red flags"""
        apy = pool_data.get("apy", pool_data.get("estimated_apy", 0))
        
        if len(red_flags) >= 3:
            return f"🚫 AVOID: Too many red flags ({len(red_flags)}). This pool is extremely risky."
        elif score >= 8.0:
            return f"🔥 DEGEN PLAY: {apy:.1f}% APY but EXTREME risk. Max 1% of portfolio."
        elif score >= 6.0:
            return f"⚠️ HIGH RISK: {apy:.1f}% APY. Consider small position (2-5% of portfolio)."
        elif score >= 4.0:
            return f"📈 MODERATE: {apy:.1f}% APY with balanced risk. Up to 10% of portfolio."
        else:
            return f"🛡️ CONSERVATIVE: {apy:.1f}% APY with low risk. Safe for larger positions."
    
    async def _arun(self, pool_address: str, pool_data: Dict) -> str:
        """Async version of the tool"""
        return self._run(pool_address, pool_data)