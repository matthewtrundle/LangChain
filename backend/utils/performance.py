"""Performance monitoring utilities"""
from datetime import datetime
from typing import Dict, List, Optional
from functools import wraps
import time
import json

class PerformanceMonitor:
    """Track performance metrics for API calls and agent execution"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
        self.slow_query_threshold = 5.0  # seconds
        
    def track_execution(self, operation: str):
        """Decorator to track execution time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = None
                error = None
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    error = str(e)
                    raise
                finally:
                    execution_time = time.time() - start_time
                    
                    # Record metric
                    self._record_metric(
                        operation=operation,
                        execution_time=execution_time,
                        success=error is None,
                        error=error,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    # Log slow operations
                    if execution_time > self.slow_query_threshold:
                        print(f"[SLOW QUERY] {operation} took {execution_time:.2f}s")
                        
            return wrapper
        return decorator
    
    def _record_metric(self, operation: str, execution_time: float, 
                      success: bool, error: Optional[str], timestamp: str):
        """Record a performance metric"""
        if operation not in self.metrics:
            self.metrics[operation] = []
            
        self.metrics[operation].append({
            "execution_time": execution_time,
            "success": success,
            "error": error,
            "timestamp": timestamp
        })
        
        # Keep only last 100 metrics per operation
        if len(self.metrics[operation]) > 100:
            self.metrics[operation] = self.metrics[operation][-100:]
    
    def get_stats(self, operation: Optional[str] = None) -> Dict:
        """Get performance statistics"""
        if operation:
            metrics = self.metrics.get(operation, [])
            return self._calculate_stats(operation, metrics)
        
        # Return stats for all operations
        all_stats = {}
        for op, metrics in self.metrics.items():
            all_stats[op] = self._calculate_stats(op, metrics)
            
        return all_stats
    
    def _calculate_stats(self, operation: str, metrics: List[Dict]) -> Dict:
        """Calculate statistics for a set of metrics"""
        if not metrics:
            return {
                "operation": operation,
                "count": 0,
                "avg_time": 0,
                "min_time": 0,
                "max_time": 0,
                "success_rate": 0,
                "slow_queries": 0
            }
        
        times = [m["execution_time"] for m in metrics]
        successes = [m["success"] for m in metrics]
        slow_queries = sum(1 for t in times if t > self.slow_query_threshold)
        
        return {
            "operation": operation,
            "count": len(metrics),
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "success_rate": sum(successes) / len(successes) * 100,
            "slow_queries": slow_queries,
            "recent_errors": [m["error"] for m in metrics[-5:] if m["error"]]
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[Dict]:
        """Get recent slow queries"""
        slow_queries = []
        
        for operation, metrics in self.metrics.items():
            for metric in metrics:
                if metric["execution_time"] > self.slow_query_threshold:
                    slow_queries.append({
                        "operation": operation,
                        "execution_time": metric["execution_time"],
                        "timestamp": metric["timestamp"],
                        "error": metric["error"]
                    })
        
        # Sort by execution time (slowest first) and return top N
        slow_queries.sort(key=lambda x: x["execution_time"], reverse=True)
        return slow_queries[:limit]

# Global performance monitor instance
perf_monitor = PerformanceMonitor()