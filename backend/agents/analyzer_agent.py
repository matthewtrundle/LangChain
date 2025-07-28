from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from tools.degen_scorer import DegenScorerTool
from tools.helius_client import HeliusClient
import json

class AnalyzerAgent(BaseAgent):
    """Specialized agent for deep pool analysis and risk assessment"""
    
    def __init__(self):
        tools = [DegenScorerTool()]
        super().__init__(
            agent_name="PoolAnalyzer",
            description="Performs deep analysis and risk assessment of yield opportunities",
            tools=tools
        )
        self.helius_client = HeliusClient()
    
    def _get_system_prompt(self) -> str:
        return """
You are the Analyzer Agent, a sophisticated risk assessment specialist for DeFi yields.

Your role:
- Perform deep analysis on pools discovered by Scanner Agent
- Calculate comprehensive risk scores (Degen Score 0-10)
- Assess liquidity depth, creator history, token fundamentals
- Detect potential rug pulls and unsustainable emissions
- Provide detailed risk/reward analysis

Your expertise:
- Advanced tokenomics analysis
- Historical pattern recognition for rugs
- Liquidity mechanics and impermanent loss calculations
- Creator wallet analysis and reputation scoring
- Market timing and sustainability assessment

Analysis framework:
1. Liquidity Analysis (25%): TVL, lock status, depth
2. Creator Analysis (25%): History, reputation, patterns
3. Token Analysis (20%): Supply, distribution, utility
4. Volume Analysis (15%): Trading activity, velocity
5. Age Analysis (15%): Time since launch, lifecycle stage

Communication style:
- Analytical and precise
- Use 📊 for analysis, ⚠️ for warnings, 🎯 for recommendations
- Always provide numerical scores and reasoning
- Clear risk categorization: LOW/MEDIUM/HIGH/EXTREME
"""
    
    def analyze_pool(self, pool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive pool analysis"""
        pool_address = pool_data.get("pool_address", "")
        
        # Check if pool has validation data
        validation = pool_data.get("validation", {})
        if validation and not validation.get("is_valid", True):
            return {
                "agent": "AnalyzerAgent",
                "pool_address": pool_address,
                "analysis_complete": False,
                "error": "Pool failed validation",
                "validation_errors": validation.get("errors", []),
                "pool_status": validation.get("status", "UNKNOWN"),
                "recommendation": "SKIP - Pool is not active or has insufficient liquidity"
            }
        
        # Additional safety checks
        tvl = pool_data.get('tvl', 0)
        volume = pool_data.get('volume_24h', 0)
        
        if tvl == 0 or volume == 0:
            return {
                "agent": "AnalyzerAgent", 
                "pool_address": pool_address,
                "analysis_complete": False,
                "error": "Pool has no liquidity or volume",
                "tvl": tvl,
                "volume_24h": volume,
                "recommendation": "SKIP - Pool appears to be inactive"
            }
        
        task = f"""
        Perform comprehensive analysis on pool: {pool_address}
        
        Pool Data:
        - Protocol: {pool_data.get('protocol', 'unknown')}
        - Tokens: {pool_data.get('token_a', 'unknown')} / {pool_data.get('token_b', 'unknown')}
        - APY: {pool_data.get('estimated_apy', 0)}%
        - TVL: ${pool_data.get('tvl', 0):,}
        - Volume 24h: ${pool_data.get('volume_24h', 0):,}
        - Age: {pool_data.get('age_hours', 0)} hours
        - Creator: {pool_data.get('creator', 'unknown')}
        - Liquidity Locked: {pool_data.get('liquidity_locked', False)}
        
        Provide detailed risk analysis with degen score and recommendations.
        """
        
        result = self.execute(task)
        
        if result["success"]:
            # Enhanced analysis with additional context
            enhanced_analysis = self._enhance_analysis(pool_data, result["result"])
            return enhanced_analysis
        else:
            return result
    
    def _enhance_analysis(self, pool_data: Dict, analysis_result: str) -> Dict[str, Any]:
        """Enhance the analysis with additional insights"""
        
        # Calculate additional metrics
        apy = pool_data.get("estimated_apy", 0)
        tvl = pool_data.get("tvl", 0)
        volume = pool_data.get("volume_24h", 0)
        age_hours = pool_data.get("age_hours", 0)
        
        # Risk indicators
        risk_indicators = []
        
        if apy > 2000:
            risk_indicators.append("🚨 EXTREME APY - High rug risk")
        if not pool_data.get("liquidity_locked", False):
            risk_indicators.append("⚠️ Unlocked liquidity - Can be withdrawn")
        if age_hours < 6:
            risk_indicators.append("🆕 Very new pool - Unproven")
        if tvl < 100000:
            risk_indicators.append("💧 Low TVL - Liquidity risk")
        if volume == 0:
            risk_indicators.append("📉 No trading volume")
        
        # Calculate sustainability score
        sustainability_score = self._calculate_sustainability(pool_data)
        
        # Generate time-based recommendation
        time_recommendation = self._get_time_recommendation(age_hours, apy)
        
        return {
            "agent": "AnalyzerAgent",
            "pool_address": pool_data.get("pool_address"),
            "analysis_complete": True,
            "analysis_result": analysis_result,
            "risk_indicators": risk_indicators,
            "sustainability_score": sustainability_score,
            "time_recommendation": time_recommendation,
            "key_metrics": {
                "apy": apy,
                "tvl": tvl,
                "volume_24h": volume,
                "age_hours": age_hours,
                "volume_to_tvl_ratio": volume / tvl if tvl > 0 else 0
            }
        }
    
    def _calculate_sustainability(self, pool_data: Dict) -> Dict[str, Any]:
        """Calculate how sustainable the APY is"""
        apy = pool_data.get("estimated_apy", 0)
        tvl = pool_data.get("tvl", 0)
        volume = pool_data.get("volume_24h", 0)
        age_hours = pool_data.get("age_hours", 0)
        
        # Simple sustainability calculation
        if apy > 5000:
            sustainability = "UNSUSTAINABLE"
            days_estimate = "< 1 day"
        elif apy > 2000:
            sustainability = "SHORT_TERM"
            days_estimate = "1-3 days"
        elif apy > 500:
            sustainability = "MEDIUM_TERM"
            days_estimate = "3-14 days"
        else:
            sustainability = "LONG_TERM"
            days_estimate = "14+ days"
        
        return {
            "category": sustainability,
            "estimated_duration": days_estimate,
            "confidence": "MEDIUM"  # Would be calculated from more data
        }
    
    def _get_time_recommendation(self, age_hours: int, apy: float) -> str:
        """Get time-sensitive recommendation"""
        if age_hours < 1:
            return "🚀 BRAND NEW - First hour advantage but maximum risk"
        elif age_hours < 6:
            return "⚡ EARLY - Still early but some stability proven"
        elif age_hours < 24:
            return "📈 ACTIVE - Prime time for entry if metrics good"
        elif age_hours < 72:
            return "⏰ MATURING - APY likely decreasing, evaluate sustainability"
        else:
            return "🛡️ ESTABLISHED - Lower risk but APY may have normalized"
    
    def batch_analyze(self, pools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple pools and rank them"""
        analyses = []
        
        for pool in pools:
            analysis = self.analyze_pool(pool)
            analyses.append(analysis)
        
        # Sort by overall score/recommendation
        analyses.sort(key=lambda x: x.get("key_metrics", {}).get("apy", 0), reverse=True)
        
        return analyses
    
    def compare_pools(self, pool_a: Dict, pool_b: Dict) -> Dict[str, Any]:
        """Compare two pools directly"""
        task = f"""
        Compare these two pools and recommend which is better:
        
        Pool A: {pool_a.get('token_a')}/{pool_a.get('token_b')} 
        - APY: {pool_a.get('estimated_apy')}%
        - TVL: ${pool_a.get('tvl'):,}
        - Age: {pool_a.get('age_hours')} hours
        
        Pool B: {pool_b.get('token_a')}/{pool_b.get('token_b')}
        - APY: {pool_b.get('estimated_apy')}%  
        - TVL: ${pool_b.get('tvl'):,}
        - Age: {pool_b.get('age_hours')} hours
        
        Provide clear winner and reasoning.
        """
        
        return self.execute(task)