from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class SimpleCache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(seconds=30)  # 30 second cache
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 30):
        """Set value in cache with TTL"""
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=ttl_seconds)
        }
    
    def clear_expired(self):
        """Remove all expired entries"""
        now = datetime.now()
        expired_keys = [k for k, v in self.cache.items() if now >= v['expires']]
        for key in expired_keys:
            del self.cache[key]

# Global cache instance
api_cache = SimpleCache()