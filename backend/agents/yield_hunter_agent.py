from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import SystemMessage
from typing import List, Dict, Any
import json

from tools.pool_scanner import PoolScannerTool
from tools.degen_scorer import DegenScorerTool
from config import Config

class YieldHunterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize tools
        self.tools = [
            PoolScannerTool(),
            DegenScorerTool()
        ]
        
        # Create memory
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create the agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def _create_agent(self):
        """Create the ReAct agent with custom prompt"""
        
        prompt = PromptTemplate.from_template("""
You are SolDegen, an elite Solana yield farming assistant. You help users find high-APY opportunities while managing risk.

Your personality:
- Sharp, direct, and knowledgeable about DeFi
- Use degen terminology but explain risks clearly
- Always calculate real returns (APY minus gas, IL risk, etc.)
- Warn about rugs but don't be overly cautious
- Use emojis strategically: 🔥 for hot opportunities, ⚠️ for warnings, 📈 for analysis

Available tools:
{tools}

Your decision-making process:
1. When asked to find opportunities, use pool_scanner with user's criteria
2. For each interesting pool, use degen_scorer to assess risk
3. Present findings with clear risk/reward analysis
4. Always explain your reasoning

Remember: You're helping degens make informed decisions, not preventing them from aping.

Previous conversation:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
""")
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def hunt_yields(self, query: str) -> str:
        """Main method to hunt for yields based on user query"""
        try:
            response = self.agent_executor.invoke({"input": query})
            return response["output"]
        except Exception as e:
            return f"Error hunting yields: {str(e)}"
    
    def scan_for_opportunities(self, min_apy: float = 500, max_age_hours: int = 24) -> Dict:
        """Direct method to scan for opportunities"""
        try:
            # Use pool scanner tool directly
            scanner = PoolScannerTool()
            results = scanner._run(min_apy, max_age_hours)
            
            # Parse results and score each pool
            pool_data = json.loads(results)
            scored_pools = []
            
            scorer = DegenScorerTool()
            
            for pool in pool_data.get("pools", []):
                score_result = scorer._run(pool["pool_address"], pool)
                score_data = json.loads(score_result)
                
                # Combine pool data with score
                pool_with_score = {
                    **pool,
                    "degen_score": score_data["degen_score"],
                    "risk_level": score_data["risk_level"],
                    "recommendation": score_data["recommendation"]
                }
                scored_pools.append(pool_with_score)
            
            return {
                "found_pools": len(scored_pools),
                "pools": scored_pools,
                "scan_time": pool_data.get("scan_time")
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_pool(self, pool_address: str) -> Dict:
        """Analyze a specific pool"""
        try:
            # In production, we'd fetch pool data from Helius
            # For now, return mock analysis
            mock_pool_data = {
                "pool_address": pool_address,
                "protocol": "raydium",
                "token_a": "UNKNOWN",
                "token_b": "UNKNOWN",
                "estimated_apy": 0,
                "tvl": 0,
                "volume_24h": 0,
                "age_hours": 0,
                "creator": "unknown",
                "liquidity_locked": False
            }
            
            scorer = DegenScorerTool()
            score_result = scorer._run(pool_address, mock_pool_data)
            
            return json.loads(score_result)
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_recommendations(self, risk_tolerance: str = "medium") -> str:
        """Get personalized recommendations based on risk tolerance"""
        risk_queries = {
            "low": "Find me safe yield opportunities above 50% APY with low risk",
            "medium": "Find me balanced yield opportunities above 200% APY with moderate risk",
            "high": "Find me high-yield opportunities above 500% APY, I can handle the risk",
            "extreme": "Find me the most degen opportunities above 1000% APY, I'm ready to ape"
        }
        
        query = risk_queries.get(risk_tolerance.lower(), risk_queries["medium"])
        return self.hunt_yields(query)