"""
Production Logging Configuration
Structured logging with trace IDs and correlation
"""
import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import uuid
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

# Context variable for trace IDs
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)

class TraceIDFilter(logging.Filter):
    """Add trace ID to log records"""
    
    def filter(self, record):
        trace_id = trace_id_var.get()
        if trace_id:
            record.trace_id = trace_id
        else:
            # Generate new trace ID if none exists
            record.trace_id = f"auto_{uuid.uuid4().hex[:16]}"
        return True

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add source location
        log_record['source'] = {
            'file': record.filename,
            'line': record.lineno,
            'function': record.funcName
        }
        
        # Add service metadata
        log_record['service'] = {
            'name': 'solana-yield-hunter',
            'environment': 'production',
            'version': '1.0.0'
        }
        
        # Move trace_id to top level if it exists
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id
        
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'pathname', 'process', 
                          'processName', 'relativeCreated', 'thread', 
                          'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'getMessage', 'trace_id']:
                # Add to extra fields
                if 'extra' not in log_record:
                    log_record['extra'] = {}
                log_record['extra'][key] = value

class AgentLogger:
    """Specialized logger for agent decisions"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f'agent.{agent_name}')
    
    def log_decision(
        self, 
        decision_type: str, 
        decision_data: Dict[str, Any],
        confidence: float = 1.0,
        reasoning: Optional[str] = None
    ):
        """Log agent decision with structured data"""
        self.logger.info(
            f"Agent decision: {decision_type}",
            extra={
                'agent_name': self.agent_name,
                'decision_type': decision_type,
                'decision_data': decision_data,
                'confidence': confidence,
                'reasoning': reasoning,
                'decision_id': uuid.uuid4().hex[:8]
            }
        )
    
    def log_analysis(
        self,
        target: str,
        metrics: Dict[str, Any],
        result: str
    ):
        """Log agent analysis result"""
        self.logger.info(
            f"Agent analysis: {target}",
            extra={
                'agent_name': self.agent_name,
                'analysis_target': target,
                'metrics': metrics,
                'result': result
            }
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ):
        """Log agent error with context"""
        self.logger.error(
            f"Agent error: {error_type}",
            extra={
                'agent_name': self.agent_name,
                'error_type': error_type,
                'error_message': error_message,
                'error_context': context or {}
            }
        )

class TransactionLogger:
    """Logger for blockchain transactions"""
    
    def __init__(self):
        self.logger = logging.getLogger('blockchain.transactions')
    
    def log_transaction(
        self,
        tx_type: str,
        signature: str,
        status: str,
        details: Dict[str, Any]
    ):
        """Log blockchain transaction"""
        self.logger.info(
            f"Transaction: {tx_type}",
            extra={
                'tx_type': tx_type,
                'signature': signature,
                'status': status,
                'details': details,
                'blockchain': 'solana'
            }
        )
    
    def log_pool_update(
        self,
        pool_address: str,
        update_type: str,
        metrics: Dict[str, Any]
    ):
        """Log pool update event"""
        self.logger.info(
            f"Pool update: {update_type}",
            extra={
                'pool_address': pool_address,
                'update_type': update_type,
                'metrics': metrics
            }
        )

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup production logging configuration"""
    
    # Create formatters
    json_formatter = CustomJsonFormatter()
    
    # Create filters
    trace_filter = TraceIDFilter()
    
    # Handler configuration
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['trace_id'],
            'stream': sys.stdout
        }
    }
    
    # Add file handler if specified
    if log_file:
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json',
            'filters': ['trace_id'],
            'filename': log_file,
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 10
        }
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJsonFormatter
            }
        },
        'filters': {
            'trace_id': {
                '()': TraceIDFilter
            }
        },
        'handlers': handlers,
        'loggers': {
            '': {  # Root logger
                'handlers': list(handlers.keys()),
                'level': log_level,
                'propagate': False
            },
            'agent': {
                'handlers': list(handlers.keys()),
                'level': 'DEBUG',
                'propagate': False
            },
            'blockchain': {
                'handlers': list(handlers.keys()),
                'level': 'INFO',
                'propagate': False
            },
            'observability': {
                'handlers': list(handlers.keys()),
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup
    logger = logging.getLogger('observability.logging')
    logger.info(
        "Logging system initialized",
        extra={
            'log_level': log_level,
            'handlers': list(handlers.keys()),
            'log_file': log_file
        }
    )

# Context managers for trace IDs
class trace_context:
    """Context manager for trace IDs"""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or f"trace_{uuid.uuid4().hex}"
        self.token = None
    
    def __enter__(self):
        self.token = trace_id_var.set(self.trace_id)
        return self.trace_id
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        trace_id_var.reset(self.token)

def get_current_trace_id() -> Optional[str]:
    """Get current trace ID from context"""
    return trace_id_var.get()

def set_trace_id(trace_id: str):
    """Set trace ID in context"""
    trace_id_var.set(trace_id)

# Correlation helpers
def correlate_logs(operation: str):
    """Decorator to correlate logs for an operation"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with trace_context() as trace_id:
                logger = logging.getLogger(func.__module__)
                logger.info(
                    f"Starting operation: {operation}",
                    extra={'operation': operation}
                )
                
                try:
                    result = func(*args, **kwargs)
                    logger.info(
                        f"Completed operation: {operation}",
                        extra={'operation': operation, 'success': True}
                    )
                    return result
                    
                except Exception as e:
                    logger.error(
                        f"Failed operation: {operation}",
                        extra={
                            'operation': operation,
                            'success': False,
                            'error': str(e)
                        },
                        exc_info=True
                    )
                    raise
        
        return wrapper
    return decorator

# Initialize logging on import
setup_logging()