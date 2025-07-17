import time
from typing import Dict, Optional
from fastapi import HTTPException
from collections import defaultdict, deque
from datetime import datetime, timedelta
from ..config import Config

class RateLimiter:
    """Simple in-memory rate limiter to prevent API abuse and save credits"""
    
    def __init__(self):
        # Track API calls per endpoint
        self.call_history: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Define rate limits (calls per minute)
        self.rate_limits = {
            "/api/scan": Config.MAX_POOLS_PER_SCAN,  # Limit scans to save OpenRouter credits
            "/api/hunt": 5,  # Coordinator agent uses more API calls
            "/api/analyze": Config.OPENROUTER_RATE_LIMIT,  # Direct limit on analysis
            "/api/monitor/check": 30,  # Allow more frequent monitoring
            "openrouter": Config.OPENROUTER_RATE_LIMIT,  # Global OpenRouter limit
            "helius": Config.HELIUS_RATE_LIMIT,  # Helius has generous limits
            "coingecko": Config.COINGECKO_RATE_LIMIT  # Free tier limit
        }
        
        # Cache for API responses (5 minute TTL)
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = Config.CACHE_TTL if Config.ENABLE_CACHING else 0
    
    def check_rate_limit(self, key: str, limit: Optional[int] = None) -> bool:
        """Check if request is within rate limit"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean old entries
        while self.call_history[key] and self.call_history[key][0] < one_minute_ago:
            self.call_history[key].popleft()
        
        # Get appropriate limit
        if limit is None:
            limit = self.rate_limits.get(key, 60)  # Default to 60 calls/min
        
        # Check if under limit
        if len(self.call_history[key]) >= limit:
            return False
        
        # Record this call
        self.call_history[key].append(now)
        return True
    
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        if not Config.ENABLE_CACHING:
            return None
            
        cached = self.cache.get(cache_key)
        if cached and time.time() - cached['timestamp'] < self.cache_ttl:
            return cached['data']
        
        # Remove expired cache
        if cached:
            del self.cache[cache_key]
        
        return None
    
    def cache_response(self, cache_key: str, data: Dict):
        """Cache a response with timestamp"""
        if Config.ENABLE_CACHING:
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        stats = {}
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        for key, history in self.call_history.items():
            # Clean old entries
            while history and history[0] < one_minute_ago:
                history.popleft()
            
            limit = self.rate_limits.get(key, 60)
            stats[key] = {
                'calls_last_minute': len(history),
                'limit_per_minute': limit,
                'usage_percentage': round((len(history) / limit) * 100, 2)
            }
        
        return stats

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_api_limit(endpoint: str):
    """Decorator to check rate limits before API calls"""
    if not rate_limiter.check_rate_limit(endpoint):
        wait_time = 60  # Wait 1 minute
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {endpoint}. Try again in {wait_time} seconds. "
                   f"(Limit: {rate_limiter.rate_limits.get(endpoint, 60)} calls/min)"
        )