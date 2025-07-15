from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

from agents.coordinator_agent import CoordinatorAgent
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.monitor_agent import MonitorAgent
from config import Config

app = FastAPI(title="Solana Degen Hunter Multi-Agent API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
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
        result = coordinator.hunt_opportunities(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan")
async def scan_opportunities(request: ScanRequest):
    """Direct scanner agent access"""
    try:
        result = scanner.scan_new_opportunities(
            min_apy=request.min_apy,
            max_age_hours=request.max_age_hours
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_pool(request: AnalyzeRequest):
    """Direct analyzer agent access"""
    try:
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
        result = monitor.check_positions()
        return result
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
            "has_openai_key": bool(Config.OPENAI_API_KEY),
            "environment": Config.ENVIRONMENT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)