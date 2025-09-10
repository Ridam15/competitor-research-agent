"""
Enhanced logging configuration for the Competitor Research Agent

Provides structured logging with multiple handlers, log levels, and formatting options.
Supports both development and production logging configurations.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
                
        return json.dumps(log_entry, default=str)

class EnhancedLogger:
    """Enhanced logger with multiple handlers and configurations"""
    
    def __init__(self, name: str = "competitor_research_agent"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
            
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers based on environment"""
        
        # Get log level from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Use colored formatter for console
        console_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        if sys.stdout.isatty():  # Only use colors if output is a terminal
            console_formatter = ColoredFormatter(console_format)
        else:
            console_formatter = logging.Formatter(console_format)
        
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logging
        self._setup_file_handler(log_level)
        
        # Structured logging for production
        if os.getenv('APP_ENV') == 'production':
            self._setup_structured_handler()
    
    def _setup_file_handler(self, log_level: str):
        """Setup file logging handler"""
        try:
            # Create logs directory
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            # Create rotating file handler
            from logging.handlers import RotatingFileHandler
            
            log_file = log_dir / f"{self.name}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            
            # File format with more details
            file_format = (
                '%(asctime)s - %(levelname)s - %(name)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
            )
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            # Fallback if file logging fails
            self.logger.warning(f"Failed to setup file logging: {e}")
    
    def _setup_structured_handler(self):
        """Setup structured JSON logging for production"""
        try:
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            from logging.handlers import RotatingFileHandler
            
            structured_file = log_dir / f"{self.name}_structured.jsonl"
            structured_handler = RotatingFileHandler(
                structured_file,
                maxBytes=20 * 1024 * 1024,  # 20MB
                backupCount=10
            )
            
            structured_handler.setLevel(logging.INFO)
            structured_handler.setFormatter(StructuredFormatter())
            
            self.logger.addHandler(structured_handler)
            
        except Exception as e:
            self.logger.warning(f"Failed to setup structured logging: {e}")
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance"""
        return self.logger

# Create global logger instance
_enhanced_logger = EnhancedLogger()
logger = _enhanced_logger.get_logger()

# Convenience functions for different log levels
def debug(message: str, **kwargs):
    """Log debug message with optional extra fields"""
    logger.debug(message, extra=kwargs)

def info(message: str, **kwargs):
    """Log info message with optional extra fields"""
    logger.info(message, extra=kwargs)

def warning(message: str, **kwargs):
    """Log warning message with optional extra fields"""
    logger.warning(message, extra=kwargs)

def error(message: str, **kwargs):
    """Log error message with optional extra fields"""
    logger.error(message, extra=kwargs)

def critical(message: str, **kwargs):
    """Log critical message with optional extra fields"""
    logger.critical(message, extra=kwargs)

def log_function_call(func_name: str, args: Optional[dict] = None, **kwargs):
    """Log function call with arguments"""
    extra_data = {'function_call': func_name}
    if args:
        extra_data['arguments'] = args
    extra_data.update(kwargs)
    
    logger.debug(f"Function call: {func_name}", extra=extra_data)

def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    extra_data = {
        'operation': operation,
        'duration_seconds': duration,
        'performance_log': True
    }
    extra_data.update(kwargs)
    
    logger.info(f"Performance: {operation} took {duration:.2f}s", extra=extra_data)

def log_api_call(provider: str, model: str, tokens: Optional[int] = None, **kwargs):
    """Log API call details"""
    extra_data = {
        'api_provider': provider,
        'model': model,
        'api_call': True
    }
    if tokens:
        extra_data['tokens_used'] = tokens
    extra_data.update(kwargs)
    
    logger.info(f"API call to {provider} using {model}", extra=extra_data)

def log_workflow_step(step: str, agent: str, status: str, **kwargs):
    """Log workflow step execution"""
    extra_data = {
        'workflow_step': step,
        'agent': agent,
        'status': status,
        'workflow_log': True
    }
    extra_data.update(kwargs)
    
    logger.info(f"Workflow: {agent} - {step} ({status})", extra=extra_data)

# Context manager for timing operations
class LogTimer:
    """Context manager for logging operation timing"""
    
    def __init__(self, operation: str, **kwargs):
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type:
            logger.error(f"Failed: {self.operation} after {duration:.2f}s", 
                        extra={'operation': self.operation, 'duration': duration, 'error': str(exc_val)})
        else:
            log_performance(self.operation, duration, **self.kwargs)

# Example usage:
# with LogTimer("data_processing", records=1000):
#     process_data()

# Configure third-party loggers to reduce noise
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("playwright").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Log initialization
logger.info("Enhanced logging system initialized", 
           extra={'version': '2.0', 'log_level': os.getenv('LOG_LEVEL', 'INFO')})