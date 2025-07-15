import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Core API keys
    HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Optional API keys for enhanced features
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")  # Free tier available
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")  # For Twitter API v2
    SERP_API_KEY = os.getenv("SERP_API_KEY")  # For Google search results
    
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Helius endpoints
    HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    HELIUS_WEBHOOK_URL = f"https://api.helius.xyz/v0/webhooks?api-key={HELIUS_API_KEY}"
    
    # Free API endpoints
    DEFI_LLAMA_API = "https://yields.llama.fi"
    JUPITER_PRICE_API = "https://price.jup.ag/v4"
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    # Degen score thresholds
    MIN_APY_THRESHOLD = 100  # 100%
    HIGH_APY_THRESHOLD = 1000  # 1000%
    
    # Pool age thresholds (in hours)
    NEW_POOL_MAX_AGE = 24
    DEGEN_POOL_MAX_AGE = 72