from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import hashlib

from agents.coordinator_agent import CoordinatorAgent
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.monitor_agent import MonitorAgent
from config import Config
from middleware.rate_limiter import rate_limiter, check_api_limit

app = FastAPI(title="Solana Degen Hunter Multi-Agent API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "https://*.up.railway.app",  # Railway deployments
        "https://*.railway.app",  # Railway deployments
        "*"  # Allow all origins for now (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the multi-agent system
coordinator = CoordinatorAgent()
scanner = ScannerAgent()
analyzer = AnalyzerAgent()
monitor = MonitorAgent()

# Request models
class HuntRequest(BaseModel):
    query: str

class ScanRequest(BaseModel):
    min_apy: float = 500
    max_age_hours: int = 24

class AnalyzeRequest(BaseModel):
    pool_address: str

class RecommendationRequest(BaseModel):
    risk_tolerance: str = "medium"

class AddPositionRequest(BaseModel):
    pool_address: str
    pool_data: Dict[str, Any]
    user_position: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Solana Degen Hunter Multi-Agent API", "status": "online", "agents": 4}

@app.post("/hunt")
async def hunt_yields(request: HuntRequest):
    """Hunt for yields using multi-agent coordination"""
    try:
        # Check rate limit
        check_api_limit("/api/hunt")
        
        # Check cache
        cache_key = hashlib.md5(request.query.encode()).hexdigest()
        cached = rate_limiter.get_cached_response(f"hunt_{cache_key}")
        if cached:
            return {**cached, "cached": True}
        
        # Execute hunt
        result = coordinator.hunt_opportunities(request.query)
        
        # Cache result
        rate_limiter.cache_response(f"hunt_{cache_key}", result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan")
async def scan_opportunities(request: ScanRequest):
    """Direct scanner agent access"""
    try:
        # Check rate limit
        check_api_limit("/api/scan")
        
        # Check cache
        cache_key = f"scan_{request.min_apy}_{request.max_age_hours}"
        cached = rate_limiter.get_cached_response(cache_key)
        if cached:
            return {**cached, "cached": True}
        
        # Execute scan
        result = scanner.scan_new_opportunities(
            min_apy=request.min_apy,
            max_age_hours=request.max_age_hours
        )
        
        # Cache result
        rate_limiter.cache_response(cache_key, result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_pool(request: AnalyzeRequest):
    """Direct analyzer agent access"""
    try:
        # Check rate limit
        check_api_limit("/api/analyze")
        
        # For direct analysis, we need pool data
        mock_pool_data = {
            "pool_address": request.pool_address,
            "protocol": "unknown",
            "token_a": "UNKNOWN",
            "token_b": "UNKNOWN",
            "estimated_apy": 0,
            "tvl": 0,
            "volume_24h": 0,
            "age_hours": 0,
            "creator": "unknown",
            "liquidity_locked": False
        }
        
        result = analyzer.analyze_pool(mock_pool_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor/add")
async def add_position(request: AddPositionRequest):
    """Add position to monitoring"""
    try:
        result = monitor.add_position(
            request.pool_address,
            request.pool_data,
            request.user_position
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitor/check")
async def check_positions():
    """Check all monitored positions"""
    try:
        # Check rate limit
        check_api_limit("/api/monitor/check")
        
        result = monitor.check_positions()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/status")
async def system_status():
    """Get multi-agent system status"""
    try:
        result = coordinator.get_system_status()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/rate-limits")
async def get_rate_limit_status():
    """Get current rate limit usage"""
    return {
        "usage": rate_limiter.get_usage_stats(),
        "limits": {
            "openrouter_per_minute": Config.OPENROUTER_RATE_LIMIT,
            "helius_per_minute": Config.HELIUS_RATE_LIMIT,
            "coingecko_per_minute": Config.COINGECKO_RATE_LIMIT,
            "max_pools_per_scan": Config.MAX_POOLS_PER_SCAN
        },
        "caching_enabled": Config.ENABLE_CACHING,
        "cache_ttl_seconds": Config.CACHE_TTL
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "multi-agent",
        "agents": {
            "coordinator": "initialized",
            "scanner": "initialized", 
            "analyzer": "initialized",
            "monitor": "initialized"
        },
        "config": {
            "has_helius_key": bool(Config.HELIUS_API_KEY),
            "has_openrouter_key": bool(Config.OPENROUTER_API_KEY),
            "environment": Config.ENVIRONMENT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)