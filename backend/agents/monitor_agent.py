from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from tools.helius_client import HeliusClient
from datetime import datetime, timedelta
import json
import requests

class MonitorAgent(BaseAgent):
    """Specialized agent for monitoring existing positions and market changes"""
    
    def __init__(self):
        tools = []  # Will add monitoring tools later
        super().__init__(
            agent_name="PositionMonitor",
            description="Monitors existing positions and alerts on significant changes",
            tools=tools
        )
        self.helius_client = HeliusClient()
        self.tracked_positions = {}  # In production, this would be a database
    
    def _get_system_prompt(self) -> str:
        return """
You are the Monitor Agent, a vigilant guardian of DeFi positions and market conditions.

Your role:
- Track existing yield farming positions
- Monitor APY changes and sustainability
- Alert on significant market movements
- Detect potential rug pulls or exit signals
- Provide exit timing recommendations

Your monitoring focus:
- APY degradation patterns
- Liquidity pool health
- Volume and trading activity changes
- Creator wallet movements
- Token price correlations

Alert triggers:
- APY drops > 25% in 1 hour
- TVL drops > 50% in 24 hours
- Unusual creator wallet activity
- Liquidity unlock events
- Volume spikes indicating exits

Communication style:
- Urgent and actionable
- Use 🚨 for critical alerts, ⚠️ for warnings, 📊 for status updates
- Always include time-sensitive recommendations
- Clear priority levels: CRITICAL/HIGH/MEDIUM/LOW
"""
    
    def add_position(self, pool_address: str, pool_data: Dict, user_position: Dict) -> Dict[str, Any]:
        """Add a new position to monitoring"""
        position_id = f"{pool_address}_{user_position.get('user_id', 'anonymous')}"
        
        position_record = {
            "position_id": position_id,
            "pool_address": pool_address,
            "pool_data": pool_data,
            "user_position": user_position,
            "entry_time": datetime.now().isoformat(),
            "entry_apy": pool_data.get("estimated_apy", 0),
            "alerts": [],
            "status": "ACTIVE"
        }
        
        self.tracked_positions[position_id] = position_record
        
        task = f"""
        New position added for monitoring:
        Pool: {pool_data.get('token_a')}/{pool_data.get('token_b')}
        Entry APY: {pool_data.get('estimated_apy')}%
        Position Size: ${user_position.get('amount', 0):,}
        
        Set up monitoring alerts and establish baseline metrics.
        """
        
        result = self.execute(task)
        
        return {
            "agent": "MonitorAgent",
            "action": "position_added",
            "position_id": position_id,
            "monitoring_active": True,
            "result": result.get("result", ""),
            "success": result.get("success", False)
        }
    
    def check_positions(self) -> Dict[str, Any]:
        """Check all monitored positions for alerts"""
        alerts = []
        position_updates = []
        
        for position_id, position in self.tracked_positions.items():
            # Simulate position checking (in production, would query live data)
            current_status = self._check_position_status(position)
            
            if current_status["alerts"]:
                alerts.extend(current_status["alerts"])
            
            position_updates.append(current_status)
        
        task = f"""
        Position monitoring scan complete:
        - Tracked positions: {len(self.tracked_positions)}
        - Alerts generated: {len(alerts)}
        - Critical alerts: {len([a for a in alerts if a.get('priority') == 'CRITICAL'])}
        
        Provide summary of monitoring status and recommended actions.
        """
        
        result = self.execute(task)
        
        return {
            "agent": "MonitorAgent",
            "scan_complete": True,
            "total_positions": len(self.tracked_positions),
            "alerts": alerts,
            "position_updates": position_updates,
            "summary": result.get("result", ""),
            "scan_time": datetime.now().isoformat()
        }
    
    def _check_position_status(self, position: Dict) -> Dict[str, Any]:
        """Check individual position status"""
        position_id = position["position_id"]
        pool_data = position["pool_data"]
        entry_apy = position["entry_apy"]
        pool_address = pool_data.get("pool_address", "")
        
        # Fetch current pool data from Raydium API
        current_pool_data = self._fetch_current_pool_data(pool_address)
        
        # Use real data or fallback to entry data if fetch fails
        current_apy = current_pool_data.get("apy", entry_apy)
        current_tvl = current_pool_data.get("tvl", pool_data.get("tvl", 0))
        
        alerts = []
        
        # Check APY degradation
        apy_change = ((current_apy - entry_apy) / entry_apy) * 100
        if apy_change < -25:
            alerts.append({
                "type": "APY_DEGRADATION",
                "priority": "HIGH",
                "message": f"🚨 APY dropped {abs(apy_change):.1f}% from entry",
                "recommendation": "Consider exit if trend continues"
            })
        
        # Check TVL changes
        tvl_change = ((current_tvl - pool_data.get("tvl", 0)) / pool_data.get("tvl", 1)) * 100
        if tvl_change < -50:
            alerts.append({
                "type": "LIQUIDITY_DRAIN",
                "priority": "CRITICAL",
                "message": f"🚨 TVL dropped {abs(tvl_change):.1f}% - potential rug!",
                "recommendation": "EXIT IMMEDIATELY"
            })
        
        return {
            "position_id": position_id,
            "current_apy": current_apy,
            "apy_change": apy_change,
            "current_tvl": current_tvl,
            "tvl_change": tvl_change,
            "alerts": alerts,
            "status": "CRITICAL" if any(a["priority"] == "CRITICAL" for a in alerts) else "ACTIVE"
        }
    
    def get_position_history(self, position_id: str) -> Dict[str, Any]:
        """Get historical data for a position"""
        if position_id not in self.tracked_positions:
            return {"error": "Position not found"}
        
        position = self.tracked_positions[position_id]
        
        task = f"""
        Generate historical analysis for position:
        Position ID: {position_id}
        Pool: {position['pool_data'].get('token_a')}/{position['pool_data'].get('token_b')}
        Entry Time: {position['entry_time']}
        Entry APY: {position['entry_apy']}%
        
        Provide performance summary and trend analysis.
        """
        
        result = self.execute(task)
        
        return {
            "agent": "MonitorAgent",
            "position_id": position_id,
            "history_available": True,
            "analysis": result.get("result", ""),
            "success": result.get("success", False)
        }
    
    def set_alert_preferences(self, user_id: str, preferences: Dict) -> Dict[str, Any]:
        """Set user-specific alert preferences"""
        task = f"""
        Update alert preferences for user {user_id}:
        {json.dumps(preferences, indent=2)}
        
        Configure monitoring system to match user preferences.
        """
        
        result = self.execute(task)
        
        return {
            "agent": "MonitorAgent",
            "action": "preferences_updated",
            "user_id": user_id,
            "preferences": preferences,
            "result": result.get("result", ""),
            "success": result.get("success", False)
        }
    
    def emergency_scan(self) -> Dict[str, Any]:
        """Emergency scan for critical issues across all positions"""
        task = "Perform emergency scan across all monitored positions for critical risks"
        result = self.execute(task)
        
        critical_alerts = []
        
        # Check all positions for critical issues
        for position_id, position in self.tracked_positions.items():
            status = self._check_position_status(position)
            critical_alerts.extend([
                alert for alert in status["alerts"] 
                if alert.get("priority") == "CRITICAL"
            ])
        
        return {
            "agent": "MonitorAgent",
            "scan_type": "EMERGENCY",
            "critical_alerts": critical_alerts,
            "positions_scanned": len(self.tracked_positions),
            "immediate_action_required": len(critical_alerts) > 0,
            "analysis": result.get("result", ""),
            "scan_time": datetime.now().isoformat()
        }
    
    def _fetch_current_pool_data(self, pool_address: str) -> Dict[str, Any]:
        """Fetch current pool data from Raydium API"""
        try:
            # If it's a DeFiLlama UUID, we can't fetch real data
            if "-" in pool_address and len(pool_address) == 36:
                print(f"[MonitorAgent] Skipping UUID pool address: {pool_address}")
                return {}
            
            # Fetch from Raydium API
            response = requests.get("https://api.raydium.io/v2/main/pairs", timeout=5)
            if response.status_code == 200:
                pools = response.json()
                
                # Find the specific pool
                for pool in pools:
                    if pool.get("ammId") == pool_address:
                        # Calculate current APY from volume and liquidity
                        liquidity = float(pool.get("liquidity", 0))
                        volume_24h = float(pool.get("volume24h", 0))
                        
                        if liquidity > 0:
                            daily_fees = volume_24h * 0.0025  # 0.25% fee
                            daily_yield = (daily_fees / liquidity) * 100
                            current_apy = daily_yield * 365
                        else:
                            current_apy = 0
                        
                        return {
                            "apy": current_apy,
                            "tvl": liquidity,
                            "volume_24h": volume_24h,
                            "price": float(pool.get("price", 0)),
                            "last_update": datetime.now().isoformat()
                        }
            
            print(f"[MonitorAgent] Pool {pool_address} not found in Raydium data")
            return {}
            
        except Exception as e:
            print(f"[MonitorAgent] Error fetching pool data: {str(e)}")
            return {}