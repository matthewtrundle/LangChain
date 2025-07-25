from typing import Dict, List, Any
from agents.base_agent import BaseAgent
from tools.pool_scanner import PoolScannerTool
from tools.real_pool_scanner import RealPoolScannerTool
from tools.web_search_tool import WebSearchTool
from tools.helius_client import HeliusClient
import json

class ScannerAgent(BaseAgent):
    """Specialized agent for discovering new yield opportunities"""
    
    def __init__(self):
        tools = [
            PoolScannerTool(),           # Mock data for testing
            RealPoolScannerTool(),       # Real DeFiLlama + Helius data
            WebSearchTool()              # Web search for alpha
        ]
        super().__init__(
            agent_name="PoolScanner",
            description="Discovers new high-yield pools using real data from DeFiLlama, Helius, and web sources",
            tools=tools
        )
        self.helius_client = HeliusClient()
    
    def _get_system_prompt(self) -> str:
        return """
You are the Scanner Agent, an elite pool discovery specialist for Solana DeFi.

Your role:
- Use REAL DATA from DeFiLlama, Helius, and web sources
- Scan for pools with high APY potential (>500%)
- Focus on pools less than 48 hours old
- Cross-reference multiple data sources for accuracy
- Search web for alpha plays and new opportunities

Your tools:
- real_pool_scanner: Gets live data from DeFiLlama + Helius
- web_search: Finds alpha plays from crypto news and Twitter
- pool_scanner: Fallback mock data for testing

Your expertise:
- Real-time data analysis and cross-referencing
- Distinguishing between sustainable and unsustainable yields
- Identifying early opportunities before they go viral
- Risk awareness for obvious scams and rugs

Communication style:
- Always mention data sources for credibility
- Use 🔍 for discoveries, ⚡ for urgent opportunities, 📊 for real data
- Provide key metrics: APY, TVL, age, protocol, data source
- Flag when data is real vs estimated
"""
    
    def scan_new_opportunities(self, min_apy: float = 500, max_age_hours: int = 48) -> Dict[str, Any]:
        """Primary method to scan for new opportunities"""
        # Directly use the real pool scanner tool for now
        try:
            from tools.real_pool_scanner import RealPoolScannerTool
            scanner_tool = RealPoolScannerTool()
            
            # Execute the scan
            scan_params = {
                "min_apy": min_apy,
                "max_age_hours": max_age_hours
            }
            
            tool_result = scanner_tool.run(json.dumps(scan_params))
            
            # Parse the tool result
            if isinstance(tool_result, str):
                # Try to extract JSON from the result
                try:
                    import re
                    json_match = re.search(r'\{.*\}', tool_result, re.DOTALL)
                    if json_match:
                        result_data = json.loads(json_match.group())
                        pools_data = result_data.get("pools", [])
                    else:
                        pools_data = []
                except:
                    pools_data = []
            else:
                pools_data = []
            
            return {
                "agent": "ScannerAgent",
                "scan_complete": True,
                "pools_found": len(pools_data),
                "opportunities": pools_data,
                "scan_criteria": {
                    "min_apy": min_apy,
                    "max_age_hours": max_age_hours
                }
            }
        except Exception as e:
            print(f"Scanner error: {str(e)}")
            # Fallback to agent execution
            task = f"Use the real_pool_scanner tool to scan for pools with minimum {min_apy}% APY"
            result = self.execute(task)
            
            if result["success"]:
                pools_data = self._extract_pools_from_response(result["result"])
                return {
                    "agent": "ScannerAgent",
                    "scan_complete": True,
                    "pools_found": len(pools_data),
                    "opportunities": pools_data,
                    "scan_criteria": {
                        "min_apy": min_apy,
                        "max_age_hours": max_age_hours
                    }
                }
            else:
                return result
    
    def _extract_pools_from_response(self, response: str) -> List[Dict]:
        """Extract structured pool data from agent response"""
        # Try to parse JSON from the agent's response
        try:
            import re
            # Look for JSON data in the response
            json_matches = re.findall(r'\{[^{}]*\}', response)
            pools = []
            
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if "pool_address" in data or "protocol" in data:
                        # Ensure required fields
                        pool = {
                            "pool_address": data.get("pool_address", "unknown"),
                            "protocol": data.get("protocol", "unknown"),
                            "token_symbols": data.get("token_symbols", data.get("symbol", "UNKNOWN")),
                            "apy": data.get("apy", data.get("estimated_apy", 0)),
                            "tvl": data.get("tvl", data.get("tvlUsd", 0)),
                            "volume_24h": data.get("volume_24h", data.get("volumeUsd1d", 0)),
                            "source": data.get("source", "Scanner Agent"),
                            "real_data": data.get("real_data", True)
                        }
                        pools.append(pool)
                except:
                    continue
            
            if pools:
                return pools
        except Exception as e:
            print(f"Error parsing response: {e}")
        
        # If no pools found in response, return empty list
        return []
    
    def focus_scan(self, protocol: str, token_symbol: str) -> Dict[str, Any]:
        """Focus scan on specific protocol or token"""
        task = f"Focus scan on {protocol} protocol for {token_symbol} pairs with high yield potential"
        return self.execute(task)
    
    def monitor_pool_creation(self) -> Dict[str, Any]:
        """Monitor for new pool creation events"""
        task = "Monitor recent pool creation events across all protocols"
        return self.execute(task)