from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from tools.helius_client import HeliusClient
from datetime import datetime, timedelta
from models.position import Position, PositionStatus, ExitReason
import json

class EnhancedMonitorAgent(BaseAgent):
    """Enhanced monitor agent that works with the position manager"""
    
    def __init__(self):
        tools = []  # Will add monitoring tools later
        super().__init__(
            agent_name="EnhancedPositionMonitor",
            description="Monitors positions 24/7 and triggers exits when needed",
            tools=tools
        )
        self.helius_client = HeliusClient()
        self.monitored_positions = {}
        self.check_interval = 60  # Check every 60 seconds
        self.last_check = datetime.now()
    
    def _get_system_prompt(self) -> str:
        return """
You are the Enhanced Monitor Agent, a vigilant guardian of active DeFi positions.

Your role:
- Monitor positions in real-time for risk signals
- Track APY changes and sustainability
- Detect rug pull indicators early
- Trigger automatic exits when needed
- Provide detailed monitoring reports

Alert triggers:
- Stop loss: Position down 10%
- Take profit: Position up 50%
- APY drop: More than 50% decrease
- Low liquidity: TVL < $10k
- Rug indicators: Liquidity removal, creator dumps

Monitoring frequency:
- Critical positions: Every 30 seconds
- Normal positions: Every 60 seconds
- Low risk positions: Every 5 minutes

Communication style:
- 🚨 CRITICAL: Immediate action required
- ⚠️ WARNING: Close monitoring needed
- 📊 UPDATE: Status report
- ✅ SAFE: Position healthy
"""
    
    def monitor_position(self, position: Position) -> Dict[str, Any]:
        """Monitor a single position and check for exit conditions"""
        from services.position_manager import position_manager
        
        try:
            # Get current pool metrics (simulated for now)
            current_metrics = self._fetch_current_metrics(position.pool_address)
            
            # Update position with current data
            updated_position = position_manager.update_position(position.id, current_metrics)
            
            # Build monitoring report
            report = {
                "position_id": position.id,
                "pool": position.pool_data.get("token_symbols", "Unknown"),
                "status": updated_position.status.value,
                "entry_value": updated_position.entry_amount,
                "current_value": updated_position.current_value,
                "pnl_amount": updated_position.pnl_amount,
                "pnl_percent": updated_position.pnl_percent,
                "current_apy": updated_position.current_apy,
                "apy_change": updated_position.current_apy - updated_position.entry_apy,
                "time_in_position": str(datetime.now() - updated_position.entry_time),
                "alerts": [],
                "risk_level": "NORMAL"
            }
            
            # Check for alerts
            if updated_position.pnl_percent < -5:
                report["alerts"].append({
                    "type": "LOSS_WARNING",
                    "message": f"⚠️ Position down {abs(updated_position.pnl_percent):.1f}%",
                    "severity": "WARNING"
                })
                report["risk_level"] = "HIGH"
            
            if updated_position.pnl_percent < -8:
                report["alerts"].append({
                    "type": "NEAR_STOP_LOSS",
                    "message": f"🚨 Approaching stop loss: {updated_position.pnl_percent:.1f}%",
                    "severity": "CRITICAL"
                })
                report["risk_level"] = "CRITICAL"
            
            if abs(report["apy_change"]) > updated_position.entry_apy * 0.3:
                report["alerts"].append({
                    "type": "APY_CHANGE",
                    "message": f"📊 APY changed significantly: {report['apy_change']:.1f}%",
                    "severity": "WARNING"
                })
            
            # Check if position was auto-exited
            if updated_position.status == PositionStatus.EXITED:
                report["alerts"].append({
                    "type": "AUTO_EXIT",
                    "message": f"✅ Position auto-exited: {updated_position.exit_reason.value}",
                    "severity": "INFO"
                })
            
            return report
            
        except Exception as e:
            return {
                "position_id": position.id,
                "error": str(e),
                "status": "ERROR"
            }
    
    def _fetch_current_metrics(self, pool_address: str) -> Dict[str, Any]:
        """Fetch current metrics for a pool (simulated for now)"""
        import random
        
        # In production, this would fetch real data from Helius/DeFiLlama
        # For now, simulate some changes
        base_metrics = {
            "apy": 500 + random.uniform(-100, 100),
            "tvl": 100000 + random.uniform(-20000, 20000),
            "volume_24h": 50000 + random.uniform(-10000, 10000),
            "price": 1.0 + random.uniform(-0.1, 0.1),
            "rug_risk": random.random() < 0.02  # 2% chance
        }
        
        return base_metrics
    
    def monitor_all_positions(self) -> Dict[str, Any]:
        """Monitor all active positions"""
        from services.position_manager import position_manager
        
        active_positions = position_manager.get_active_positions()
        monitoring_reports = []
        critical_alerts = []
        
        for position in active_positions:
            report = self.monitor_position(position)
            monitoring_reports.append(report)
            
            # Collect critical alerts
            for alert in report.get("alerts", []):
                if alert["severity"] == "CRITICAL":
                    critical_alerts.append({
                        "position_id": position.id,
                        "pool": position.pool_data.get("token_symbols"),
                        "alert": alert
                    })
        
        # Get position summary
        summary = position_manager.get_position_summary()
        
        return {
            "agent": "EnhancedMonitorAgent",
            "timestamp": datetime.now().isoformat(),
            "positions_monitored": len(active_positions),
            "critical_alerts": len(critical_alerts),
            "alerts": critical_alerts,
            "monitoring_reports": monitoring_reports,
            "portfolio_summary": {
                "total_value": summary.current_value,
                "total_pnl": summary.total_pnl,
                "total_pnl_percent": summary.total_pnl_percent,
                "average_apy": summary.average_apy
            },
            "next_check": (datetime.now() + timedelta(seconds=self.check_interval)).isoformat()
        }
    
    def get_position_report(self, position_id: str) -> Dict[str, Any]:
        """Get detailed report for a specific position"""
        from services.position_manager import position_manager
        
        positions = position_manager.positions
        position = positions.get(position_id)
        
        if not position:
            # Check history
            for p in position_manager.position_history:
                if p.id == position_id:
                    position = p
                    break
        
        if not position:
            return {"error": "Position not found"}
        
        # Generate detailed analysis
        task = f"""
        Analyze this position in detail:
        
        Pool: {position.pool_data.get('token_symbols')}
        Entry: ${position.entry_amount} at {position.entry_apy}% APY
        Current: ${position.current_value} at {position.current_apy}% APY
        P&L: ${position.pnl_amount} ({position.pnl_percent:.1f}%)
        Time: {datetime.now() - position.entry_time}
        Status: {position.status.value}
        
        Provide:
        1. Performance analysis
        2. Risk assessment
        3. Exit recommendation
        4. Optimization suggestions
        """
        
        result = self.execute(task)
        
        return {
            "agent": "EnhancedMonitorAgent",
            "position": position.dict(),
            "analysis": result.get("result", ""),
            "recommendations": self._generate_recommendations(position)
        }
    
    def _generate_recommendations(self, position: Position) -> List[str]:
        """Generate recommendations for a position"""
        recommendations = []
        
        if position.pnl_percent > 30:
            recommendations.append("🎯 Consider taking partial profits (50%)")
        
        if position.pnl_percent < -5:
            recommendations.append("⚠️ Monitor closely - approaching stop loss")
        
        if position.current_apy < position.entry_apy * 0.5:
            recommendations.append("📉 APY has degraded significantly - consider exit")
        
        hours_in_position = (datetime.now() - position.entry_time).total_seconds() / 3600
        if hours_in_position > 72 and position.pnl_percent < 5:
            recommendations.append("⏰ Position stagnant - consider redeploying capital")
        
        return recommendations
    
    def configure_alerts(self, config: Dict) -> Dict[str, Any]:
        """Configure monitoring alerts"""
        self.check_interval = config.get("check_interval", 60)
        
        return {
            "agent": "EnhancedMonitorAgent",
            "config_updated": True,
            "check_interval": self.check_interval,
            "message": "Monitoring configuration updated"
        }