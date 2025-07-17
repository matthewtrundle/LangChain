from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool
from ..config import Config

class BaseAgent(ABC):
    """Base class for all specialized agents"""
    
    def __init__(self, agent_name: str, description: str, tools: List[BaseTool]):
        self.agent_name = agent_name
        self.description = description
        self.tools = tools
        
        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=Config.OPENROUTER_MODEL,
            temperature=0.1,
            api_key=Config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/matthewtrundle/LangChain",
                "X-Title": "Solana Degen Hunter"
            }
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def _create_agent(self):
        """Create the ReAct agent with specialized prompt"""
        prompt = PromptTemplate.from_template(f"""
{self._get_system_prompt()}

Available tools:
{{tools}}

Your decision-making process:
1. Understand the task clearly
2. Choose the most appropriate tool(s)
3. Analyze the results
4. Provide clear, actionable insights
5. Communicate with other agents when needed

Previous conversation:
{{chat_history}}

Task: {{input}}
Thought: {{agent_scratchpad}}
""")
        
        return create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def execute(self, task: str) -> Dict[str, Any]:
        """Execute a task and return structured results"""
        try:
            response = self.agent_executor.invoke({"input": task})
            return {
                "agent": self.agent_name,
                "success": True,
                "result": response["output"],
                "task": task
            }
        except Exception as e:
            return {
                "agent": self.agent_name,
                "success": False,
                "error": str(e),
                "task": task
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            "agent_name": self.agent_name,
            "description": self.description,
            "tools": [tool.name for tool in self.tools],
            "memory_length": len(self.memory.chat_memory.messages) if self.memory.chat_memory else 0
        }