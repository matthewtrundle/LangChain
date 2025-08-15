"""
Observability Module
Production monitoring, metrics, and logging for Solana Yield Hunter
"""

from .metrics import (
    metrics,
    structured_logger,
    track_async_operation,
    MetricsCollector
)

from .monitoring_service import (
    monitoring,
    MonitoringService,
    create_monitoring_app
)

from .logging_config import (
    setup_logging,
    trace_context,
    get_current_trace_id,
    set_trace_id,
    correlate_logs,
    AgentLogger,
    TransactionLogger
)

__all__ = [
    # Metrics
    'metrics',
    'structured_logger', 
    'track_async_operation',
    'MetricsCollector',
    
    # Monitoring
    'monitoring',
    'MonitoringService',
    'create_monitoring_app',
    
    # Logging
    'setup_logging',
    'trace_context',
    'get_current_trace_id',
    'set_trace_id',
    'correlate_logs',
    'AgentLogger',
    'TransactionLogger'
]

# Production observability checklist
OBSERVABILITY_CHECKLIST = {
    "metrics": {
        "rpc_latency": "Track p50, p95, p99 latencies",
        "rpc_errors": "Count by error type and endpoint",
        "websocket_health": "Active connections and reconnects",
        "agent_performance": "Decision latency and success rate",
        "pnl_accuracy": "Track calculation accuracy vs actual"
    },
    "logging": {
        "structured": "JSON format with trace IDs",
        "correlated": "Link related events with trace IDs",
        "searchable": "Index by trace_id, agent, timestamp",
        "retention": "30 days for debugging, 90 days for compliance"
    },
    "monitoring": {
        "health_checks": "/health endpoint for all services",
        "dashboards": "Grafana dashboards for key metrics",
        "alerts": "PagerDuty for critical issues",
        "slos": "99.9% uptime, <500ms p95 latency"
    },
    "tracing": {
        "distributed": "Trace across agent boundaries",
        "sampling": "100% for errors, 10% for success",
        "visualization": "Jaeger or similar for trace analysis"
    }
}

def initialize_observability():
    """Initialize all observability components"""
    # Setup is done on import, but this can be called explicitly
    pass