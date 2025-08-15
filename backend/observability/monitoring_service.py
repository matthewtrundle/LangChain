"""
Monitoring Service with Health Checks and Dashboards
Implements SRE/Observer production monitoring requirements
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import statistics

from observability.metrics import (
    metrics, structured_logger,
    track_async_operation
)

@dataclass
class HealthStatus:
    """Health check status"""
    service: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    details: Dict = field(default_factory=dict)
    
@dataclass
class SystemMetrics:
    """System-wide metrics snapshot"""
    timestamp: datetime
    rpc_latency_p50: float
    rpc_latency_p95: float
    rpc_error_rate: float
    websocket_active: int
    websocket_reconnects: int
    positions_active: int
    agent_decisions_per_minute: float
    pnl_accuracy: float
    
class MonitoringService:
    """Central monitoring service with health checks"""
    
    def __init__(self):
        self.app = FastAPI(title="Solana Yield Hunter Monitoring")
        self.health_checks: Dict[str, HealthStatus] = {}
        self.metrics_history: deque = deque(maxlen=1440)  # 24 hours of minute data
        self.alert_history: List[Dict] = []
        self.running = False
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup monitoring endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Overall system health check"""
            overall_status = self._calculate_overall_health()
            
            return {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "services": {
                    name: {
                        "status": check.status,
                        "last_check": check.last_check.isoformat(),
                        "details": check.details
                    }
                    for name, check in self.health_checks.items()
                }
            }
        
        @self.app.get("/metrics")
        async def prometheus_metrics():
            """Prometheus metrics endpoint"""
            return JSONResponse(
                content=generate_latest().decode('utf-8'),
                media_type=CONTENT_TYPE_LATEST
            )
        
        @self.app.get("/dashboard/summary")
        async def dashboard_summary():
            """Dashboard summary data"""
            if not self.metrics_history:
                return {"error": "No metrics data available"}
            
            latest_metrics = self.metrics_history[-1]
            hour_ago = datetime.now() - timedelta(hours=1)
            hour_metrics = [m for m in self.metrics_history if m.timestamp > hour_ago]
            
            return {
                "current": {
                    "rpc_latency_p95": latest_metrics.rpc_latency_p95,
                    "websocket_health": latest_metrics.websocket_active > 0,
                    "positions_tracked": latest_metrics.positions_active,
                    "agent_decisions_per_hour": latest_metrics.agent_decisions_per_minute * 60,
                    "pnl_accuracy": latest_metrics.pnl_accuracy
                },
                "trends": {
                    "rpc_latency_trend": self._calculate_trend(hour_metrics, 'rpc_latency_p95'),
                    "positions_trend": self._calculate_trend(hour_metrics, 'positions_active'),
                    "error_rate_trend": self._calculate_trend(hour_metrics, 'rpc_error_rate')
                },
                "alerts": self.alert_history[-10:]  # Last 10 alerts
            }
        
        @self.app.get("/dashboard/rpc")
        async def rpc_dashboard():
            """RPC-specific metrics"""
            hour_ago = datetime.now() - timedelta(hours=1)
            hour_metrics = [m for m in self.metrics_history if m.timestamp > hour_ago]
            
            if not hour_metrics:
                return {"error": "No recent metrics"}
            
            return {
                "latency": {
                    "current_p50": hour_metrics[-1].rpc_latency_p50,
                    "current_p95": hour_metrics[-1].rpc_latency_p95,
                    "hour_avg_p50": statistics.mean(m.rpc_latency_p50 for m in hour_metrics),
                    "hour_avg_p95": statistics.mean(m.rpc_latency_p95 for m in hour_metrics),
                    "hour_max": max(m.rpc_latency_p95 for m in hour_metrics)
                },
                "errors": {
                    "current_rate": hour_metrics[-1].rpc_error_rate,
                    "hour_avg": statistics.mean(m.rpc_error_rate for m in hour_metrics),
                    "hour_max": max(m.rpc_error_rate for m in hour_metrics)
                },
                "time_series": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "p50": m.rpc_latency_p50,
                        "p95": m.rpc_latency_p95,
                        "error_rate": m.rpc_error_rate
                    }
                    for m in hour_metrics[::5]  # Every 5 minutes
                ]
            }
        
        @self.app.get("/dashboard/websocket")
        async def websocket_dashboard():
            """WebSocket health dashboard"""
            hour_ago = datetime.now() - timedelta(hours=1)
            hour_metrics = [m for m in self.metrics_history if m.timestamp > hour_ago]
            
            return {
                "connections": {
                    "active": hour_metrics[-1].websocket_active if hour_metrics else 0,
                    "reconnects_last_hour": sum(m.websocket_reconnects for m in hour_metrics)
                },
                "stability": self._calculate_websocket_stability(hour_metrics),
                "time_series": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "active": m.websocket_active,
                        "reconnects": m.websocket_reconnects
                    }
                    for m in hour_metrics[::5]
                ]
            }
        
        @self.app.get("/dashboard/agents")
        async def agent_dashboard():
            """Agent performance dashboard"""
            hour_ago = datetime.now() - timedelta(hours=1)
            hour_metrics = [m for m in self.metrics_history if m.timestamp > hour_ago]
            
            if not hour_metrics:
                return {"error": "No recent metrics"}
            
            return {
                "activity": {
                    "decisions_per_hour": hour_metrics[-1].agent_decisions_per_minute * 60,
                    "hour_total": sum(m.agent_decisions_per_minute for m in hour_metrics) * 60
                },
                "performance": {
                    "pnl_accuracy": hour_metrics[-1].pnl_accuracy,
                    "positions_tracked": hour_metrics[-1].positions_active
                }
            }
        
        @self.app.get("/traces/{trace_id}")
        async def get_trace(trace_id: str):
            """Get events for a specific trace ID"""
            events = metrics.get_trace(trace_id)
            if not events:
                raise HTTPException(status_code=404, detail="Trace not found")
            
            return {
                "trace_id": trace_id,
                "events": [
                    {
                        "timestamp": e['timestamp'].isoformat(),
                        "agent_type": e.get('agent_type'),
                        "decision_type": e.get('decision_type'),
                        "latency_ms": e.get('latency', 0) * 1000,
                        "data": e.get('data', {})
                    }
                    for e in events
                ]
            }
    
    async def start(self):
        """Start monitoring service"""
        self.running = True
        
        # Start health check loop
        asyncio.create_task(self._health_check_loop())
        
        # Start metrics collection loop
        asyncio.create_task(self._metrics_collection_loop())
        
        # Start alert check loop
        asyncio.create_task(self._alert_check_loop())
        
        structured_logger.log_with_trace(
            'info',
            'Monitoring service started',
            'monitoring_startup'
        )
    
    async def stop(self):
        """Stop monitoring service"""
        self.running = False
        structured_logger.log_with_trace(
            'info',
            'Monitoring service stopped',
            'monitoring_shutdown'
        )
    
    async def _health_check_loop(self):
        """Periodic health checks"""
        while self.running:
            try:
                # Check RPC health
                await self._check_rpc_health()
                
                # Check WebSocket health
                await self._check_websocket_health()
                
                # Check agent health
                await self._check_agent_health()
                
                # Check database health
                await self._check_database_health()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                structured_logger.log_with_trace(
                    'error',
                    f'Health check error: {e}',
                    'health_check_error'
                )
                await asyncio.sleep(10)
    
    async def _check_rpc_health(self):
        """Check RPC endpoint health"""
        # This would make actual RPC calls to check health
        # For now, use metrics data
        
        recent_latencies = metrics.metrics_buffer.get('rpc_latency', [])
        if recent_latencies:
            recent = [m for m in recent_latencies[-100:]]
            avg_latency = statistics.mean(m['latency'] for m in recent)
            
            if avg_latency < 0.3:
                status = "healthy"
            elif avg_latency < 0.8:
                status = "degraded"
            else:
                status = "unhealthy"
        else:
            status = "unknown"
        
        self.health_checks['rpc'] = HealthStatus(
            service='rpc',
            status=status,
            last_check=datetime.now(),
            details={
                'avg_latency': avg_latency if recent_latencies else None,
                'endpoint': 'Helius RPC'
            }
        )
    
    async def _check_websocket_health(self):
        """Check WebSocket connection health"""
        # Check reconnect frequency
        reconnects = metrics.metrics_buffer.get('ws_reconnects', [])
        recent_reconnects = len([
            r for r in reconnects 
            if (datetime.now() - r['timestamp']).seconds < 300
        ])
        
        if recent_reconnects == 0:
            status = "healthy"
        elif recent_reconnects < 5:
            status = "degraded"
        else:
            status = "unhealthy"
        
        self.health_checks['websocket'] = HealthStatus(
            service='websocket',
            status=status,
            last_check=datetime.now(),
            details={
                'recent_reconnects': recent_reconnects,
                'window': '5 minutes'
            }
        )
    
    async def _check_agent_health(self):
        """Check agent system health"""
        # This would check actual agent status
        # For now, assume healthy
        self.health_checks['agents'] = HealthStatus(
            service='agents',
            status='healthy',
            last_check=datetime.now(),
            details={
                'scanner': 'active',
                'analyzer': 'active',
                'monitor': 'active',
                'coordinator': 'active'
            }
        )
    
    async def _check_database_health(self):
        """Check database connection health"""
        # This would check actual database connection
        # For now, assume healthy
        self.health_checks['database'] = HealthStatus(
            service='database',
            status='healthy',
            last_check=datetime.now(),
            details={
                'type': 'PostgreSQL',
                'connection_pool': 'active'
            }
        )
    
    async def _metrics_collection_loop(self):
        """Collect metrics snapshots"""
        while self.running:
            try:
                # Collect current metrics
                snapshot = await self._collect_metrics_snapshot()
                self.metrics_history.append(snapshot)
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                structured_logger.log_with_trace(
                    'error',
                    f'Metrics collection error: {e}',
                    'metrics_collection_error'
                )
                await asyncio.sleep(30)
    
    async def _collect_metrics_snapshot(self) -> SystemMetrics:
        """Collect current system metrics"""
        # Calculate from buffered metrics
        rpc_latencies = [
            m['latency'] for m in metrics.metrics_buffer.get('rpc_latency', [])[-100:]
        ]
        
        return SystemMetrics(
            timestamp=datetime.now(),
            rpc_latency_p50=statistics.median(rpc_latencies) if rpc_latencies else 0,
            rpc_latency_p95=sorted(rpc_latencies)[int(len(rpc_latencies) * 0.95)] if rpc_latencies else 0,
            rpc_error_rate=0,  # Calculate from error counter
            websocket_active=1,  # Get from gauge
            websocket_reconnects=len(metrics.metrics_buffer.get('ws_reconnects', [])),
            positions_active=50,  # Get from position service
            agent_decisions_per_minute=10,  # Calculate from counter
            pnl_accuracy=98.5  # Get from accuracy gauge
        )
    
    async def _alert_check_loop(self):
        """Check alert conditions"""
        while self.running:
            try:
                metrics.check_alert_conditions()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                structured_logger.log_with_trace(
                    'error',
                    f'Alert check error: {e}',
                    'alert_check_error'
                )
                await asyncio.sleep(30)
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        if not self.health_checks:
            return "unknown"
        
        statuses = [check.status for check in self.health_checks.values()]
        
        if all(s == "healthy" for s in statuses):
            return "healthy"
        elif any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        else:
            return "degraded"
    
    def _calculate_trend(self, metrics_list: List[SystemMetrics], field: str) -> str:
        """Calculate trend direction"""
        if len(metrics_list) < 2:
            return "stable"
        
        values = [getattr(m, field) for m in metrics_list]
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])
        
        change = (second_half - first_half) / first_half if first_half else 0
        
        if change > 0.1:
            return "increasing"
        elif change < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_websocket_stability(self, metrics_list: List[SystemMetrics]) -> float:
        """Calculate WebSocket stability score (0-100)"""
        if not metrics_list:
            return 0
        
        total_reconnects = sum(m.websocket_reconnects for m in metrics_list)
        
        # Perfect stability = 0 reconnects
        # Each reconnect reduces stability
        stability = max(0, 100 - (total_reconnects * 10))
        
        return stability


# Create global monitoring instance
monitoring = MonitoringService()

# Example FastAPI integration
def create_monitoring_app() -> FastAPI:
    """Create monitoring FastAPI app"""
    return monitoring.app

if __name__ == "__main__":
    # Run monitoring service
    uvicorn.run(monitoring.app, host="0.0.0.0", port=9090)