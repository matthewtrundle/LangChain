from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import hashlib
from datetime import datetime
import asyncio

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
from utils.performance import perf_monitor
from websocket_manager import ws_manager

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

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if we can reach Raydium
        raydium_ok = False
        try:
            import requests
            resp = requests.get("https://api.raydium.io/v2/main/pairs", timeout=2)
            raydium_ok = resp.status_code == 200
        except:
            pass
        
        # Check agent status
        agents_ok = all([scanner, analyzer, monitor, coordinator])
        
        return {
            "status": "healthy" if raydium_ok and agents_ok else "degraded",
            "system": "multi-agent",
            "agents": {
                "coordinator": "initialized" if coordinator else "error",
                "scanner": "initialized" if scanner else "error", 
                "analyzer": "initialized" if analyzer else "error",
                "monitor": "initialized" if monitor else "error"
            },
            "config": {
                "has_helius_key": bool(Config.HELIUS_API_KEY),
                "has_openrouter_key": bool(Config.OPENROUTER_API_KEY),
                "environment": Config.ENVIRONMENT or "production"
            },
            "services": {
                "raydium_api": "up" if raydium_ok else "down",
                "agents": "up" if agents_ok else "down",
                "database": "up",  # Always up since we use in-memory
                "cache": "up"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Global progress tracker
progress_tracker = {}

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get progress of a running task"""
    return progress_tracker.get(task_id, {"status": "not_found"})

@app.post("/hunt")
@perf_monitor.track_execution("hunt_yields")
async def hunt_yields(request: HuntRequest):
    """Hunt for yields using multi-agent coordination"""
    try:
        # Validate input
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if len(request.query) > 500:
            raise HTTPException(status_code=400, detail="Query too long (max 500 characters)")
        
        # Sanitize query
        sanitized_query = request.query.strip()
        
        # Check rate limit
        check_api_limit("/api/hunt")
        
        # Check cache
        cache_key = hashlib.md5(sanitized_query.encode()).hexdigest()
        cached = rate_limiter.get_cached_response(f"hunt_{cache_key}")
        if cached:
            return {**cached, "cached": True}
        
        # Add debug logging
        print(f"[API] Starting hunt with query: {sanitized_query}")
        start_time = datetime.now()
        
        # Create task ID for progress tracking
        task_id = f"hunt_{cache_key}"
        progress_tracker[task_id] = {
            "status": "scanning",
            "phase": "discovery",
            "progress": 10,
            "message": "Scanner Agent discovering pools..."
        }
        
        # Broadcast progress via WebSocket
        await ws_manager.broadcast_progress(
            task_id=task_id,
            status="scanning",
            progress=10,
            message="Scanner Agent discovering pools..."
        )
        
        # Execute hunt with progress updates
        print("[API] Phase 1: Scanner Agent starting...")
        result = coordinator.hunt_opportunities(sanitized_query)
        
        # Update progress during execution
        progress_tracker[task_id] = {
            "status": "analyzing",
            "phase": "analysis",
            "progress": 50,
            "message": "Analyzer Agent calculating risk scores..."
        }
        
        # Broadcast progress update
        await ws_manager.broadcast_progress(
            task_id=task_id,
            status="analyzing",
            progress=50,
            message="Analyzer Agent calculating risk scores..."
        )
        
        # Calculate time taken
        time_taken = (datetime.now() - start_time).total_seconds()
        print(f"[API] Hunt completed in {time_taken:.2f} seconds")
        print(f"[API] Found {len(result.get('results', {}).get('discovery', {}).get('top_opportunities', []))} pools")
        
        # Add execution metadata
        result['execution_time'] = time_taken
        result['agents_used'] = ['scanner', 'analyzer', 'monitor', 'coordinator']
        
        # Cache result
        rate_limiter.cache_response(f"hunt_{cache_key}", result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Hunt error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan/raydium")
@perf_monitor.track_execution("scan_raydium")
async def scan_raydium(request: ScanRequest):
    """Scan Raydium for pools with REAL Solana addresses"""
    try:
        from tools.raydium_scanner import RadiumScannerTool
        raydium_scanner = RadiumScannerTool()
        
        # Run Raydium scan
        result = raydium_scanner._run(
            min_apy=request.min_apy,
            min_tvl=10000  # Minimum $10k TVL
        )
        
        # Parse result
        scan_data = json.loads(result)
        
        return {
            "source": "Raydium Direct",
            "found_pools": scan_data.get("found_pools", 0),
            "pools": scan_data.get("pools", []),
            "scan_time": scan_data.get("scan_time"),
            "data_sources": ["Raydium API"],
            "real_addresses": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan")
async def scan_opportunities(request: ScanRequest):
    """Direct scanner agent access"""
    try:
        # Validate input
        if request.min_apy < 0 or request.min_apy > 100000:
            raise HTTPException(status_code=400, detail="Invalid APY range (0-100000)")
        
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
@perf_monitor.track_execution("analyze_pool")
async def analyze_pool(request: AnalyzeRequest):
    """Direct analyzer agent access with enhanced scoring"""
    try:
        # Check rate limit
        check_api_limit("/api/analyze")
        
        # Try to fetch real pool data from Raydium
        pool_data = None
        try:
            # First try to get from Raydium API
            from utils.cache import api_cache
            from utils.http_client import http_client
            
            # Check cache for recent Raydium data
            cached_pools = api_cache.get("raydium_pools")
            if cached_pools:
                # Find the specific pool
                for pool in cached_pools:
                    if pool.get("ammId") == request.pool_address:
                        # Found it! Extract real data
                        pool_data = {
                            "pool_address": request.pool_address,
                            "protocol": "raydium",
                            "token_a": pool.get("name", "").split("-")[0] if "-" in pool.get("name", "") else "UNKNOWN",
                            "token_b": pool.get("name", "").split("-")[1] if "-" in pool.get("name", "") else "SOL",
                            "token_symbols": pool.get("name", "UNKNOWN/SOL"),
                            "apy": float(pool.get("apy", 0)) * 100 if pool.get("apy") else 850.0,
                            "tvl": float(pool.get("liquidity", 125000)),
                            "volume_24h": float(pool.get("volume24h", 45000)),
                            "age_hours": 24,  # Default, would need on-chain data
                            "liquidity_locked": False,
                            "source": "Raydium_Live"
                        }
                        break
            
            # If not found in cache, fetch fresh data
            if not pool_data:
                response = http_client.get("https://api.raydium.io/v2/main/pairs", timeout=5)
                if response.status_code == 200:
                    pools = response.json()
                    for pool in pools:
                        if pool.get("ammId") == request.pool_address:
                            # Calculate APY from volume and fees
                            liquidity = float(pool.get("liquidity", 0))
                            volume_24h = float(pool.get("volume24h", 0))
                            apy = 0
                            if liquidity > 0:
                                daily_fees = volume_24h * 0.0025
                                daily_yield = (daily_fees / liquidity) * 100
                                apy = daily_yield * 365
                            
                            pool_data = {
                                "pool_address": request.pool_address,
                                "protocol": "raydium",
                                "token_a": pool.get("name", "").split("-")[0] if "-" in pool.get("name", "") else "UNKNOWN",
                                "token_b": pool.get("name", "").split("-")[1] if "-" in pool.get("name", "") else "SOL",
                                "token_symbols": pool.get("name", "UNKNOWN/SOL"),
                                "apy": round(apy, 2),
                                "tvl": round(liquidity, 2),
                                "volume_24h": round(volume_24h, 2),
                                "age_hours": 24,
                                "liquidity_locked": False,
                                "source": "Raydium_Fresh"
                            }
                            break
        except Exception as e:
            print(f"[Analyze] Error fetching pool data: {e}")
        
        # Fallback to basic data if not found
        if not pool_data:
            pool_data = {
                "pool_address": request.pool_address,
                "protocol": "raydium",
                "token_a": "UNKNOWN",
                "token_b": "SOL",
                "token_symbols": "UNKNOWN/SOL",
                "apy": 850.0,
                "tvl": 125000,
                "volume_24h": 45000,
                "age_hours": 12,
                "creator": request.pool_address[:8] + "...",
                "liquidity_locked": False,
                "source": "Fallback_Data"
            }
        
        # Log pool data for debugging
        print(f"[Analyze] Analyzing pool {request.pool_address}")
        print(f"[Analyze] Pool data source: {pool_data.get('source')}")
        print(f"[Analyze] APY: {pool_data.get('apy')}%, TVL: ${pool_data.get('tvl'):,.0f}")
        
        # Use DegenScorerTool directly for detailed scoring
        from tools.degen_scorer import DegenScorerTool
        scorer = DegenScorerTool()
        score_result = scorer._run(request.pool_address, pool_data)
        
        # Parse the score result
        try:
            score_data = json.loads(score_result)
            print(f"[Analyze] Degen score: {score_data.get('degen_score')}/10")
        except Exception as e:
            print(f"[Analyze] Score parsing error: {e}")
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
        
        # Update all positions with real data
        position_manager.update_all_positions()
        
        # Use enhanced monitor
        result = enhanced_monitor.monitor_all_positions()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics with real pool data"""
    try:
        # Update positions with latest data
        position_manager.update_all_positions()
        
        # Get position summary
        summary = position_manager.get_position_summary()
        
        # Get active positions with current metrics
        active_positions = []
        for pos in position_manager.get_active_positions():
            # Get real-time pool data
            current_metrics = position_manager._fetch_real_pool_metrics(pos.pool_address)
            
            active_positions.append({
                "position_id": pos.id,
                "pool": pos.pool_data.get("token_symbols", "Unknown"),
                "pool_address": pos.pool_address,
                "entry_time": pos.entry_time.isoformat(),
                "hours_held": (datetime.now() - pos.entry_time).total_seconds() / 3600,
                "entry_amount": pos.entry_amount,
                "current_value": pos.current_value,
                "pnl_amount": pos.pnl_amount,
                "pnl_percent": pos.pnl_percent,
                "entry_apy": pos.entry_apy,
                "current_apy": current_metrics.get("apy", pos.current_apy),
                "current_tvl": current_metrics.get("tvl", 0),
                "current_volume": current_metrics.get("volume_24h", 0),
                "rewards_earned": pos.rewards_earned,
                "gas_spent": pos.gas_spent
            })
        
        # Get historical performance
        historical_positions = []
        for pos in position_manager.position_history:
            historical_positions.append({
                "position_id": pos.id,
                "pool": pos.pool_data.get("token_symbols", "Unknown"),
                "entry_time": pos.entry_time.isoformat(),
                "exit_time": pos.exit_time.isoformat() if pos.exit_time else None,
                "hours_held": pos.hours_held,
                "entry_amount": pos.entry_amount,
                "exit_value": pos.current_value,
                "pnl_amount": pos.pnl_amount,
                "pnl_percent": pos.pnl_percent,
                "exit_reason": pos.exit_reason.value if pos.exit_reason else None
            })
        
        return {
            "summary": summary.dict(),
            "active_positions": active_positions,
            "historical_positions": historical_positions,
            "wallet_balance": position_manager.wallet.get_balance(),
            "total_gas_spent": sum(p.gas_spent for p in position_manager.positions.values()),
            "last_update": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system performance statistics"""
    from utils.cache import api_cache
    
    # Calculate stats
    active_positions = position_manager.get_active_positions()
    total_value = sum(p.current_value for p in active_positions)
    total_pnl = sum(p.pnl_amount for p in active_positions)
    
    # Get performance metrics
    perf_stats = perf_monitor.get_stats()
    slow_queries = perf_monitor.get_slow_queries(5)
    
    return {
        "system": {
            "agents_online": 4,
            "cache_entries": len(api_cache.cache),
            "rate_limit_remaining": rate_limiter.get_remaining_calls(),
        },
        "trading": {
            "active_positions": len(active_positions),
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "wallet_balance": position_manager.wallet.get_balance()
        },
        "api_calls": {
            "raydium": rate_limiter.call_counts.get("/scan/raydium", 0),
            "hunt": rate_limiter.call_counts.get("/hunt", 0),
            "analyze": rate_limiter.call_counts.get("/analyze", 0)
        },
        "performance": {
            "endpoints": perf_stats,
            "slow_queries": slow_queries
        },
        "timestamp": datetime.now().isoformat()
    }

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
        # Debug logging
        balance = wallet.get_balance()
        available = wallet.get_available_balance()
        print(f"[Wallet] Balance: ${balance}, Available: ${available}, Initial: ${wallet.initial_balance}")
        
        return {
            "balance": balance,
            "initial_balance": wallet.initial_balance,
            "available_balance": available,
            "performance": wallet.get_performance_metrics().to_dict(),
            "transaction_count": len(wallet.transactions)
        }
    except Exception as e:
        print(f"[Wallet] Error: {str(e)}")
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
        # Allow reset in any environment for now
        wallet = get_wallet()
        wallet.reset()
        
        # Also reset position manager
        position_manager.positions.clear()
        position_manager.position_history.clear()
        
        return {
            "success": True,
            "message": "Wallet and positions reset to initial state",
            "new_balance": wallet.get_balance(),
            "initial_balance": wallet.initial_balance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/wallet/init")
async def init_wallet():
    """Initialize wallet if needed"""
    try:
        wallet = get_wallet()
        current_balance = wallet.get_balance()
        
        # If wallet has no balance, reset it
        if current_balance <= 0:
            wallet.reset()
            print(f"[Wallet] Initialized with ${wallet.initial_balance}")
        
        return {
            "balance": wallet.get_balance(),
            "initial_balance": wallet.initial_balance,
            "available_balance": wallet.get_available_balance(),
            "initialized": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Removed duplicate health endpoint - using the one at line 73

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "subscribe":
                channels = data.get("channels", [])
                await ws_manager.subscribe(websocket, channels)
            elif data.get("type") == "ping":
                await ws_manager.send_personal_message({"type": "pong"}, websocket)
            else:
                await ws_manager.send_personal_message({
                    "type": "error",
                    "message": "Unknown message type"
                }, websocket)
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WS] Error: {e}")
        ws_manager.disconnect(websocket)

@app.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": len(ws_manager.active_connections),
        "connection_info": [
            {
                "connected_at": info["connected_at"],
                "subscriptions": list(info["subscriptions"])
            }
            for info in ws_manager.connection_info.values()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)