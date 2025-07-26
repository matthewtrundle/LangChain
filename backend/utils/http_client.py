"""HTTP client with connection pooling and retry logic"""
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import Optional, Dict, Any

class HTTPClient:
    """Singleton HTTP client with connection pooling"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HTTPClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "User-Agent": "Solana-Degen-Hunter/1.0",
            "Accept": "application/json"
        })
        
        self._initialized = True
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """GET request with automatic retries"""
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """POST request"""
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session"""
        self.session.close()

# Global HTTP client instance
http_client = HTTPClient()