from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.monitor_agent import MonitorAgent
from datetime import datetime
import json

class CoordinatorAgent(BaseAgent):
    """Master agent that coordinates all other agents"""
    
    def __init__(self):
        # Coordinator doesn't need tools directly, it delegates to other agents
        super().__init__(
            agent_name="MasterCoordinator",
            description="Orchestrates all agents to provide comprehensive yield hunting",
            tools=[]
        )
        
        # Initialize sub-agents
        self.scanner_agent = ScannerAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.monitor_agent = MonitorAgent()
        
        # Coordination state
        self.active_workflows = {}
        self.agent_status = {}
    
    def _get_system_prompt(self) -> str:
        return """
You are the Master Coordinator, the orchestrator of a sophisticated yield hunting operation.

Your role:
- Coordinate Scanner, Analyzer, and Monitor agents
- Decide which agents to deploy for each request
- Synthesize results from multiple agents
- Provide strategic recommendations
- Manage workflow priorities

Your agents:
- Scanner Agent: Discovers new opportunities
- Analyzer Agent: Performs deep risk analysis
- Monitor Agent: Tracks existing positions

Decision framework:
1. Understand user intent and context
2. Determine which agents are needed
3. Coordinate agent execution in optimal order
4. Synthesize results into actionable insights
5. Provide clear recommendations with reasoning

Communication style:
- Executive summary style
- Use 🎯 for strategy, 📊 for analysis, 🚀 for opportunities
- Always provide next steps
- Clear priority and timing recommendations
"""
    
    def hunt_opportunities(self, user_query: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """Main entry point for opportunity hunting"""
        
        # Parse user intent
        intent = self._parse_user_intent(user_query)
        
        # Create workflow
        workflow_id = f"hunt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = {
            "workflow_id": workflow_id,
            "user_query": user_query,
            "user_preferences": user_preferences or {},
            "intent": intent,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "results": {}
        }
        
        self.active_workflows[workflow_id] = workflow
        
        try:
            # Execute workflow based on intent
            if intent["type"] == "DISCOVER":
                result = self._execute_discovery_workflow(workflow)
            elif intent["type"] == "ANALYZE":
                result = self._execute_analysis_workflow(workflow)
            elif intent["type"] == "MONITOR":
                result = self._execute_monitoring_workflow(workflow)
            elif intent["type"] == "COMPREHENSIVE":
                result = self._execute_comprehensive_workflow(workflow)
            else:
                result = self._execute_comprehensive_workflow(workflow)
            
            # Add coordination summary
            task = f"""
            Workflow completed: {workflow_id}
            User query: {user_query}
            Results summary: {json.dumps(result, indent=2)[:500]}...
            
            Provide executive summary and strategic recommendations.
            """
            
            coordination_result = self.execute(task)
            
            return {
                "workflow_id": workflow_id,
                "coordination_complete": True,
                "user_query": user_query,
                "intent": intent,
                "results": result,
                "coordination_summary": coordination_result.get("result", ""),
                "execution_time": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "workflow_id": workflow_id,
                "coordination_complete": False,
                "error": str(e),
                "success": False
            }
    
    def _parse_user_intent(self, query: str) -> Dict[str, Any]:
        """Parse user query to determine intent and requirements"""
        query_lower = query.lower()
        
        # Determine intent type
        if any(word in query_lower for word in ["find", "scan", "discover", "new"]):
            intent_type = "DISCOVER"
        elif any(word in query_lower for word in ["analyze", "risk", "score", "evaluate"]):
            intent_type = "ANALYZE"
        elif any(word in query_lower for word in ["monitor", "track", "watch", "alert"]):
            intent_type = "MONITOR"
        else:
            intent_type = "COMPREHENSIVE"
        
        # Extract parameters
        min_apy = 500  # Default
        if "%" in query:
            # Try to extract APY requirement
            try:
                apy_match = query.split("%")[0].split()[-1]
                min_apy = float(apy_match)
            except:
                pass
        
        max_age = 48  # Default hours
        if "hour" in query_lower:
            try:
                # Extract age requirement
                words = query_lower.split()
                for i, word in enumerate(words):
                    if "hour" in word and i > 0:
                        max_age = int(words[i-1])
                        break
            except:
                pass
        
        return {
            "type": intent_type,
            "min_apy": min_apy,
            "max_age_hours": max_age,
            "risk_tolerance": self._extract_risk_tolerance(query_lower),
            "protocols": self._extract_protocols(query_lower)
        }
    
    def _extract_risk_tolerance(self, query: str) -> str:
        """Extract risk tolerance from query"""
        if any(word in query for word in ["safe", "low risk", "conservative"]):
            return "LOW"
        elif any(word in query for word in ["degen", "extreme", "high risk", "ape"]):
            return "EXTREME"
        elif any(word in query for word in ["aggressive", "high"]):
            return "HIGH"
        else:
            return "MEDIUM"
    
    def _extract_protocols(self, query: str) -> List[str]:
        """Extract specific protocols from query"""
        protocols = []
        if "raydium" in query:
            protocols.append("raydium")
        if "orca" in query:
            protocols.append("orca")
        if "meteora" in query:
            protocols.append("meteora")
        
        return protocols if protocols else ["raydium", "orca"]
    
    def _execute_discovery_workflow(self, workflow: Dict) -> Dict[str, Any]:
        """Execute discovery-focused workflow"""
        intent = workflow["intent"]
        
        # Step 1: Scan for opportunities
        scan_result = self.scanner_agent.scan_new_opportunities(
            min_apy=intent["min_apy"],
            max_age_hours=intent["max_age_hours"]
        )
        
        workflow["steps"].append({
            "step": "SCAN",
            "agent": "ScannerAgent",
            "result": scan_result
        })
        
        # Step 2: Analyze top opportunities
        if scan_result.get("opportunities"):
            top_pools = scan_result["opportunities"][:3]  # Top 3
            analyses = self.analyzer_agent.batch_analyze(top_pools)
            
            workflow["steps"].append({
                "step": "ANALYZE",
                "agent": "AnalyzerAgent",
                "result": analyses
            })
            
            return {
                "workflow_type": "DISCOVERY",
                "opportunities_found": len(scan_result.get("opportunities", [])),
                "top_opportunities": analyses,
                "scan_details": scan_result
            }
        
        return {
            "workflow_type": "DISCOVERY",
            "opportunities_found": 0,
            "message": "No opportunities found matching criteria"
        }
    
    def _execute_analysis_workflow(self, workflow: Dict) -> Dict[str, Any]:
        """Execute analysis-focused workflow"""
        # This would be triggered when user provides specific pools to analyze
        return {
            "workflow_type": "ANALYSIS",
            "message": "Analysis workflow - would analyze specific pools"
        }
    
    def _execute_monitoring_workflow(self, workflow: Dict) -> Dict[str, Any]:
        """Execute monitoring-focused workflow"""
        # Check existing positions
        monitor_result = self.monitor_agent.check_positions()
        
        workflow["steps"].append({
            "step": "MONITOR",
            "agent": "MonitorAgent",
            "result": monitor_result
        })
        
        return {
            "workflow_type": "MONITORING",
            "positions_monitored": monitor_result.get("total_positions", 0),
            "alerts": monitor_result.get("alerts", []),
            "monitoring_summary": monitor_result.get("summary", "")
        }
    
    def _execute_comprehensive_workflow(self, workflow: Dict) -> Dict[str, Any]:
        """Execute comprehensive workflow (scan + analyze + monitor)"""
        results = {}
        
        # Step 1: Discovery
        discovery_result = self._execute_discovery_workflow(workflow)
        results["discovery"] = discovery_result
        
        # Step 2: Monitoring
        monitoring_result = self._execute_monitoring_workflow(workflow)
        results["monitoring"] = monitoring_result
        
        return {
            "workflow_type": "COMPREHENSIVE",
            "discovery": discovery_result,
            "monitoring": monitoring_result,
            "combined_insights": "Comprehensive analysis complete"
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents and workflows"""
        return {
            "coordinator": "ACTIVE",
            "agents": {
                "scanner": self.scanner_agent.get_status(),
                "analyzer": self.analyzer_agent.get_status(),
                "monitor": self.monitor_agent.get_status()
            },
            "active_workflows": len(self.active_workflows),
            "system_time": datetime.now().isoformat()
        }
    
    def emergency_response(self, alert_type: str) -> Dict[str, Any]:
        """Handle emergency situations"""
        if alert_type == "MARKET_CRASH":
            # Coordinate emergency monitoring
            monitor_result = self.monitor_agent.emergency_scan()
            
            task = f"""
            Emergency response activated: {alert_type}
            Monitor results: {json.dumps(monitor_result, indent=2)[:300]}...
            
            Provide immediate action recommendations for all positions.
            """
            
            coordination_result = self.execute(task)
            
            return {
                "emergency_type": alert_type,
                "immediate_actions": monitor_result.get("critical_alerts", []),
                "coordination_response": coordination_result.get("result", ""),
                "response_time": datetime.now().isoformat()
            }
        
        return {"error": "Unknown emergency type"}