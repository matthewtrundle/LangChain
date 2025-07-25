from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import hashlib
from datetime import datetime

from agents.coordinator_agent import CoordinatorAgent
from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.monitor_agent import MonitorAgent
from agents.enhanced_monitor_agent import EnhancedMonitorAgent
from config import Config
from middleware.rate_limiter import rate_limiter, check_api_limit
from services.position_manager import position_manager
from models.position import Position, PositionStatus
from services.wallet_service import get_wallet, TransactionType

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
enhanced_monitor = EnhancedMonitorAgent()

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
    amount: float = 100.0  # Default $100

class ExitPositionRequest(BaseModel):
    position_id: str
    reason: str = "manual"

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
        
        # Transform to expected format
        scan_response = {
            "source": "Scanner Agent",
            "found_pools": result.get("pools_found", 0),
            "pools": result.get("opportunities", []),
            "scan_time": datetime.now().isoformat(),
            "data_sources": ["Helius RPC", "Jupiter", "DeFi Llama"]
        }
        
        # Cache result
        rate_limiter.cache_response(cache_key, scan_response)
        
        return scan_response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_pool(request: AnalyzeRequest):
    """Direct analyzer agent access with enhanced scoring"""
    try:
        # Check rate limit
        check_api_limit("/api/analyze")
        
        # Try to find pool data from recent scans (in production, would query blockchain)
        # For now, create realistic mock data based on pool address
        pool_data = {
            "pool_address": request.pool_address,
            "protocol": "raydium",  # Most common on Solana
            "token_a": "UNKNOWN",
            "token_b": "SOL",
            "token_symbols": "UNKNOWN/SOL",
            "apy": 850.0,  # Realistic high APY
            "estimated_apy": 850.0,
            "tvl": 125000,  # $125k TVL
            "volume_24h": 45000,  # $45k volume
            "age_hours": 12,  # 12 hours old
            "creator": request.pool_address[:8] + "...",
            "liquidity_locked": False,
            "source": "Analyzer Mock Data"
        }
        
        # Use DegenScorerTool directly for detailed scoring
        from tools.degen_scorer import DegenScorerTool
        scorer = DegenScorerTool()
        score_result = scorer._run(request.pool_address, pool_data)
        
        # Parse the score result
        try:
            score_data = json.loads(score_result)
        except:
            score_data = {"error": "Failed to calculate score"}
        
        # Run the analyzer agent for narrative analysis
        analysis_result = analyzer.analyze_pool(pool_data)
        
        # Combine results
        return {
            "success": True,
            "agent": "AnalyzerAgent",
            "result": f"""
🔍 POOL ANALYSIS COMPLETE

{score_data.get('analysis_summary', 'No summary available')}

📊 DEGEN SCORE: {score_data.get('degen_score', 'N/A')}/10
🎯 RISK LEVEL: {score_data.get('risk_level', 'UNKNOWN')}

💡 SCORE BREAKDOWN:
- Liquidity Score: {score_data.get('score_breakdown', {}).get('liquidity_score', 0):.1f}/10
- Volume Score: {score_data.get('score_breakdown', {}).get('volume_score', 0):.1f}/10
- Age Score: {score_data.get('score_breakdown', {}).get('age_score', 0):.1f}/10
- APY Sustainability: {score_data.get('score_breakdown', {}).get('apy_sustainability', 0):.1f}/10

🚨 RED FLAGS:
{chr(10).join(score_data.get('red_flags', ['None detected']))}

📌 RECOMMENDATION:
{score_data.get('recommendation', 'Unable to generate recommendation')}

💭 AGENT ANALYSIS:
{analysis_result.get('analysis_result', 'No additional analysis available')}
""",
            "pool_data": pool_data,
            "score_data": score_data,
            "analysis_data": analysis_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/position/enter")
async def enter_position(request: AddPositionRequest):
    """Enter a new position"""
    try:
        # Use enhanced monitor to add position
        result = enhanced_monitor.monitored_positions
        
        # Enter position through position manager
        position = position_manager.enter_position(request.pool_data, request.amount)
        
        # Start monitoring
        enhanced_monitor.monitored_positions[position.id] = {
            "position": position,
            "last_check": datetime.now(),
            "alerts": []
        }
        
        return {
            "success": True,
            "position": position.dict(),
            "message": f"Entered ${request.amount} position in {request.pool_data.get('token_symbols', 'Unknown')}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/position/exit")
async def exit_position(request: ExitPositionRequest):
    """Exit a position"""
    try:
        from models.position import ExitReason
        
        # Parse exit reason
        exit_reason = ExitReason.MANUAL
        for reason in ExitReason:
            if reason.value == request.reason:
                exit_reason = reason
                break
        
        # Exit position
        position = position_manager.exit_position(request.position_id, exit_reason)
        
        return {
            "success": True,
            "position": position.dict(),
            "final_pnl": position.pnl_amount,
            "final_pnl_percent": position.pnl_percent,
            "message": f"Exited position with {position.pnl_percent:.1f}% P&L"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/positions")
async def get_positions():
    """Get all positions"""
    try:
        active = position_manager.get_active_positions()
        summary = position_manager.get_position_summary()
        
        return {
            "active_positions": [p.dict() for p in active],
            "position_history": [p.dict() for p in position_manager.position_history],
            "summary": summary.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/position/{position_id}")
async def get_position(position_id: str):
    """Get specific position details"""
    try:
        report = enhanced_monitor.get_position_report(position_id)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitor/check")
async def check_positions():
    """Check all monitored positions"""
    try:
        # Check rate limit
        check_api_limit("/api/monitor/check")
        
        # Use enhanced monitor
        result = enhanced_monitor.monitor_all_positions()
        
        # Also run position updates
        position_manager.simulate_position_updates()
        
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

@app.get("/wallet")
async def get_wallet_info():
    """Get wallet balance and performance metrics"""
    try:
        wallet = get_wallet()
        return {
            "balance": wallet.get_balance(),
            "initial_balance": wallet.initial_balance,
            "available_balance": wallet.get_available_balance(),
            "performance": wallet.get_performance_metrics().to_dict(),
            "transaction_count": len(wallet.transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet/transactions")
async def get_wallet_transactions(
    limit: int = 50,
    offset: int = 0,
    position_id: Optional[str] = None
):
    """Get wallet transaction history"""
    try:
        wallet = get_wallet()
        transactions = wallet.get_transactions(limit, offset, position_id)
        return {
            "transactions": [t.to_dict() for t in transactions],
            "total": len(wallet.transactions),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallet/performance")
async def get_wallet_performance():
    """Get detailed wallet performance metrics"""
    try:
        wallet = get_wallet()
        metrics = wallet.get_performance_metrics()
        
        # Add additional context
        return {
            "metrics": metrics.to_dict(),
            "current_balance": wallet.get_balance(),
            "initial_balance": wallet.initial_balance,
            "all_time_high": max(wallet.balance, wallet.initial_balance),  # Simple ATH
            "position_count": {
                "active": len(position_manager.get_active_positions()),
                "total": len(position_manager.positions) + len(position_manager.position_history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wallet/reset")
async def reset_wallet():
    """Reset wallet to initial state (dev only)"""
    try:
        if Config.ENVIRONMENT != "development":
            raise HTTPException(status_code=403, detail="Wallet reset only allowed in development")
        
        wallet = get_wallet()
        wallet.reset()
        
        # Also reset position manager
        position_manager.positions.clear()
        position_manager.position_history.clear()
        
        return {
            "success": True,
            "message": "Wallet and positions reset to initial state",
            "new_balance": wallet.get_balance()
        }
    except HTTPException:
        raise
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
            "has_openrouter_key": bool(Config.OPENROUTER_API_KEY),
            "environment": Config.ENVIRONMENT
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)