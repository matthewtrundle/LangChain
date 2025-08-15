"""
Production Observability Metrics
Based on SRE/Observer recommendations
"""
import time
import logging
from typing import Dict, Optional, Callable, Any
from functools import wraps
from datetime import datetime
from contextlib import contextmanager
import asyncio
from collections import defaultdict
from prometheus_client import Counter, Histogram, Gauge, Summary
import json

logger = logging.getLogger(__name__)

# Prometheus metrics
rpc_latency_histogram = Histogram(
    'solana_rpc_latency_seconds',
    'RPC call latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

rpc_error_counter = Counter(
    'solana_rpc_errors_total',
    'Total number of RPC errors',
    ['method', 'endpoint', 'error_type']
)

websocket_connections_gauge = Gauge(
    'solana_websocket_connections_active',
    'Number of active WebSocket connections'
)

websocket_reconnects_counter = Counter(
    'solana_websocket_reconnects_total',
    'Total number of WebSocket reconnection attempts'
)

websocket_message_latency = Histogram(
    'solana_websocket_message_latency_seconds',
    'WebSocket message latency',
    ['message_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5]
)

agent_decision_counter = Counter(
    'solana_agent_decisions_total',
    'Total number of agent decisions',
    ['agent_type', 'decision_type']
)

agent_decision_latency = Histogram(
    'solana_agent_decision_latency_seconds',
    'Agent decision making latency',
    ['agent_type'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

pnl_accuracy_gauge = Gauge(
    'solana_pnl_accuracy_percent',
    'P&L calculation accuracy percentage',
    ['pool_type']
)

pnl_calculation_errors = Counter(
    'solana_pnl_calculation_errors_total',
    'Total P&L calculation errors',
    ['error_type']
)

pool_discovery_counter = Counter(
    'solana_pools_discovered_total',
    'Total pools discovered',
    ['protocol', 'source']
)

position_tracking_gauge = Gauge(
    'solana_positions_tracked',
    'Number of positions being tracked',
    ['status']
)

class MetricsCollector:
    """Central metrics collection and monitoring"""
    
    def __init__(self):
        self.trace_storage = defaultdict(list)
        self.alert_thresholds = {
            'rpc_latency_p95': 0.5,  # 500ms
            'rpc_error_rate': 0.01,   # 1%
            'websocket_reconnects': 10,  # in 5 minutes
            'pnl_accuracy_min': 95.0,    # 95% accuracy
            'agent_decision_latency_p95': 2.0  # 2 seconds
        }
        self.metrics_buffer = defaultdict(list)
        
    @contextmanager
    def track_rpc_call(self, method: str, endpoint: str):
        """Context manager to track RPC call metrics"""
        start_time = time.time()
        
        try:
            yield
            # Success - record latency
            latency = time.time() - start_time
            rpc_latency_histogram.labels(method=method, endpoint=endpoint).observe(latency)
            
            # Buffer for alerting
            self.metrics_buffer['rpc_latency'].append({
                'timestamp': datetime.now(),
                'latency': latency,
                'method': method
            })
            
        except Exception as e:
            # Error - record error metric
            error_type = type(e).__name__
            rpc_error_counter.labels(
                method=method, 
                endpoint=endpoint, 
                error_type=error_type
            ).inc()
            
            logger.error(f"RPC error in {method}: {e}")
            raise
    
    def track_websocket_connection(self, connected: bool):
        """Track WebSocket connection status"""
        if connected:
            websocket_connections_gauge.inc()
        else:
            websocket_connections_gauge.dec()
    
    def track_websocket_reconnect(self):
        """Track WebSocket reconnection attempt"""
        websocket_reconnects_counter.inc()
        
        # Check for excessive reconnects
        self.metrics_buffer['ws_reconnects'].append({
            'timestamp': datetime.now()
        })
        
        # Alert if too many reconnects
        recent_reconnects = self._count_recent_events(
            self.metrics_buffer['ws_reconnects'], 
            minutes=5
        )
        
        if recent_reconnects > self.alert_thresholds['websocket_reconnects']:
            self._send_alert(
                'WebSocket Instability',
                f'{recent_reconnects} reconnects in last 5 minutes'
            )
    
    def track_websocket_message(self, message_type: str, latency: float):
        """Track WebSocket message latency"""
        websocket_message_latency.labels(message_type=message_type).observe(latency)
    
    def track_agent_decision(
        self, 
        agent_type: str, 
        decision_type: str, 
        latency: float,
        trace_id: str,
        decision_data: Dict
    ):
        """Track agent decision with trace ID"""
        agent_decision_counter.labels(
            agent_type=agent_type, 
            decision_type=decision_type
        ).inc()
        
        agent_decision_latency.labels(agent_type=agent_type).observe(latency)
        
        # Store trace data
        self.trace_storage[trace_id].append({
            'timestamp': datetime.now(),
            'agent_type': agent_type,
            'decision_type': decision_type,
            'latency': latency,
            'data': decision_data
        })
        
        # Log with trace ID
        logger.info(
            f"Agent decision",
            extra={
                'trace_id': trace_id,
                'agent_type': agent_type,
                'decision_type': decision_type,
                'latency_ms': latency * 1000
            }
        )
    
    def track_pnl_accuracy(self, pool_type: str, accuracy_percent: float):
        """Track P&L calculation accuracy"""
        pnl_accuracy_gauge.labels(pool_type=pool_type).set(accuracy_percent)
        
        # Alert if accuracy drops
        if accuracy_percent < self.alert_thresholds['pnl_accuracy_min']:
            self._send_alert(
                'P&L Accuracy Low',
                f'{pool_type} accuracy: {accuracy_percent:.1f}%'
            )
    
    def track_pnl_error(self, error_type: str):
        """Track P&L calculation errors"""
        pnl_calculation_errors.labels(error_type=error_type).inc()
    
    def track_pool_discovery(self, protocol: str, source: str):
        """Track new pool discoveries"""
        pool_discovery_counter.labels(protocol=protocol, source=source).inc()
    
    def track_position_count(self, active: int, closed: int, error: int):
        """Track position counts by status"""
        position_tracking_gauge.labels(status='active').set(active)
        position_tracking_gauge.labels(status='closed').set(closed)
        position_tracking_gauge.labels(status='error').set(error)
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """Get all events for a trace ID"""
        return self.trace_storage.get(trace_id, [])
    
    def _count_recent_events(self, events: List[Dict], minutes: int = 5) -> int:
        """Count events in the last N minutes"""
        cutoff = datetime.now().timestamp() - (minutes * 60)
        return sum(1 for e in events if e['timestamp'].timestamp() > cutoff)
    
    def _send_alert(self, alert_type: str, message: str):
        """Send alert (implement your alerting mechanism)"""
        logger.warning(f"ALERT [{alert_type}]: {message}")
        # TODO: Implement actual alerting (PagerDuty, Slack, etc.)
    
    def check_alert_conditions(self):
        """Check all alert conditions"""
        # RPC latency check
        recent_latencies = [
            m['latency'] for m in self.metrics_buffer['rpc_latency']
            if (datetime.now() - m['timestamp']).seconds < 300
        ]
        
        if recent_latencies:
            p95_latency = sorted(recent_latencies)[int(len(recent_latencies) * 0.95)]
            if p95_latency > self.alert_thresholds['rpc_latency_p95']:
                self._send_alert(
                    'High RPC Latency',
                    f'P95 latency: {p95_latency:.2f}s'
                )


# Decorator for tracking async functions
def track_async_operation(operation_type: str):
    """Decorator to track async operation metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = kwargs.get('trace_id', f"{operation_type}_{int(time.time() * 1000)}")
            
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time
                
                logger.info(
                    f"Operation completed: {operation_type}",
                    extra={
                        'trace_id': trace_id,
                        'latency_ms': latency * 1000,
                        'success': True
                    }
                )
                
                return result
                
            except Exception as e:
                latency = time.time() - start_time
                
                logger.error(
                    f"Operation failed: {operation_type}",
                    extra={
                        'trace_id': trace_id,
                        'latency_ms': latency * 1000,
                        'error': str(e),
                        'success': False
                    }
                )
                
                raise
                
        return wrapper
    return decorator


# Structured logging setup
class StructuredLogger:
    """Structured logging with trace IDs"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        handler.setFormatter(self._get_json_formatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def _get_json_formatter(self):
        """Get JSON formatter for structured logs"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                    'trace_id': getattr(record, 'trace_id', None)
                }
                
                # Add extra fields
                for key, value in record.__dict__.items():
                    if key not in ['name', 'msg', 'args', 'created', 'filename', 
                                  'funcName', 'levelname', 'levelno', 'lineno', 
                                  'module', 'msecs', 'pathname', 'process', 
                                  'processName', 'relativeCreated', 'thread', 
                                  'threadName', 'getMessage']:
                        log_obj[key] = value
                
                return json.dumps(log_obj)
        
        return JSONFormatter()
    
    def log_with_trace(self, level: str, message: str, trace_id: str, **kwargs):
        """Log with trace ID and extra fields"""
        extra = {'trace_id': trace_id, **kwargs}
        getattr(self.logger, level)(message, extra=extra)


# Global metrics collector instance
metrics = MetricsCollector()
structured_logger = StructuredLogger('solana_yield_hunter')