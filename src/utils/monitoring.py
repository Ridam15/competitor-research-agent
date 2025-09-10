"""
Advanced Error Handling & Monitoring System

This module provides comprehensive error handling, monitoring, and alerting
for the Competitor Research Agent system.
"""

import functools
import traceback
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
from pathlib import Path

from src.utils.logger import logger


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    PARSING_ERROR = "parsing_error"
    FILE_ERROR = "file_error"
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorEvent:
    """Structured error event data"""
    timestamp: str
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    stack_trace: str
    context: Dict[str, Any]
    user_impact: str
    resolution_suggestions: List[str]
    count: int = 1


class ErrorMonitor:
    """Advanced error monitoring and alerting system"""
    
    def __init__(self, max_errors: int = 1000):
        self.max_errors = max_errors
        self.errors: List[ErrorEvent] = []
        self.error_stats: Dict[str, Dict[str, int]] = {}
        self.alert_thresholds = {
            ErrorSeverity.CRITICAL: 1,  # Alert immediately
            ErrorSeverity.HIGH: 3,      # Alert after 3 occurrences
            ErrorSeverity.MEDIUM: 10,   # Alert after 10 occurrences
            ErrorSeverity.LOW: 50       # Alert after 50 occurrences
        }
        
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """Automatically categorize errors based on type and message"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        if any(term in error_str for term in ["api_key", "unauthorized", "authentication", "401", "403"]):
            return ErrorCategory.AUTHENTICATION_ERROR
        elif any(term in error_str for term in ["rate_limit", "429", "quota", "throttled"]):
            return ErrorCategory.RATE_LIMIT_ERROR
        elif any(term in error_str for term in ["network", "connection", "502", "503", "504"]):
            return ErrorCategory.NETWORK_ERROR
        elif any(term in error_str for term in ["timeout", "timed out"]):
            return ErrorCategory.TIMEOUT_ERROR
        elif any(term in error_str for term in ["parse", "json", "xml", "format"]):
            return ErrorCategory.PARSING_ERROR
        elif any(term in error_str for term in ["file", "path", "directory", "permission"]):
            return ErrorCategory.FILE_ERROR
        elif any(term in error_str for term in ["config", "setting", "environment"]):
            return ErrorCategory.CONFIGURATION_ERROR
        elif any(term in error_str for term in ["validation", "invalid", "format"]):
            return ErrorCategory.VALIDATION_ERROR
        elif "api" in error_str:
            return ErrorCategory.API_ERROR
        else:
            return ErrorCategory.UNKNOWN_ERROR
    
    def determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on category and impact"""
        severity_map = {
            ErrorCategory.AUTHENTICATION_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.CONFIGURATION_ERROR: ErrorSeverity.HIGH,
            ErrorCategory.RATE_LIMIT_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.API_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.NETWORK_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.TIMEOUT_ERROR: ErrorSeverity.MEDIUM,
            ErrorCategory.PARSING_ERROR: ErrorSeverity.LOW,
            ErrorCategory.FILE_ERROR: ErrorSeverity.LOW,
            ErrorCategory.VALIDATION_ERROR: ErrorSeverity.LOW,
            ErrorCategory.UNKNOWN_ERROR: ErrorSeverity.MEDIUM,
        }
        return severity_map.get(category, ErrorSeverity.MEDIUM)
    
    def generate_resolution_suggestions(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Generate helpful resolution suggestions based on error category"""
        suggestions_map = {
            ErrorCategory.AUTHENTICATION_ERROR: [
                "Check your API keys in the .env file",
                "Verify API key permissions and quotas",
                "Ensure API keys are not expired",
                "Try regenerating your API keys"
            ],
            ErrorCategory.RATE_LIMIT_ERROR: [
                "Wait before retrying the request",
                "Consider upgrading your API plan",
                "Implement exponential backoff in your requests",
                "Reduce the frequency of API calls"
            ],
            ErrorCategory.NETWORK_ERROR: [
                "Check your internet connection",
                "Try again after a few minutes",
                "Check if the service is experiencing downtime",
                "Consider using a VPN if blocked by geographic restrictions"
            ],
            ErrorCategory.TIMEOUT_ERROR: [
                "Increase timeout settings",
                "Check network connectivity",
                "Try with a smaller request payload",
                "Consider breaking large requests into smaller chunks"
            ],
            ErrorCategory.CONFIGURATION_ERROR: [
                "Review configuration settings",
                "Check environment variables",
                "Validate configuration file syntax",
                "Refer to configuration documentation"
            ],
            ErrorCategory.FILE_ERROR: [
                "Check file permissions",
                "Verify file path exists",
                "Ensure sufficient disk space",
                "Check file is not in use by another process"
            ]
        }
        return suggestions_map.get(category, ["Check logs for more details", "Try restarting the application"])
    
    def record_error(self, error: Exception, context: Dict[str, Any] = None) -> str:
        """Record an error event with full context and analysis"""
        context = context or {}
        
        # Generate unique error ID
        error_content = f"{type(error).__name__}:{str(error)}:{context.get('function', 'unknown')}"
        error_id = hashlib.md5(error_content.encode()).hexdigest()[:8]
        
        # Categorize and analyze error
        category = self.categorize_error(error)
        severity = self.determine_severity(error, category)
        suggestions = self.generate_resolution_suggestions(error, category)
        
        # Check if this is a duplicate error
        existing_error = next((e for e in self.errors if e.error_id == error_id), None)
        
        if existing_error:
            existing_error.count += 1
            existing_error.timestamp = datetime.now().isoformat()
            logger.warning(f"Duplicate error recorded (count: {existing_error.count}): {error_id}")
        else:
            # Create new error event
            error_event = ErrorEvent(
                timestamp=datetime.now().isoformat(),
                error_id=error_id,
                category=category,
                severity=severity,
                message=str(error),
                details={
                    "error_type": type(error).__name__,
                    "args": str(error.args) if error.args else "",
                    "module": getattr(error, '__module__', 'unknown')
                },
                stack_trace=traceback.format_exc(),
                context=context,
                user_impact=self._assess_user_impact(category, severity),
                resolution_suggestions=suggestions
            )
            
            self.errors.append(error_event)
            
            # Maintain max errors limit
            if len(self.errors) > self.max_errors:
                self.errors.pop(0)
            
            # Update statistics
            self._update_stats(category, severity)
            
            # Log error with appropriate level
            self._log_error(error_event)
            
            # Check for alert conditions
            self._check_alert_conditions(error_event)
        
        return error_id
    
    def _assess_user_impact(self, category: ErrorCategory, severity: ErrorSeverity) -> str:
        """Assess the impact of the error on user experience"""
        impact_matrix = {
            (ErrorCategory.AUTHENTICATION_ERROR, ErrorSeverity.HIGH): "Complete service failure - users cannot access any functionality",
            (ErrorCategory.RATE_LIMIT_ERROR, ErrorSeverity.MEDIUM): "Temporary slowdown - users may experience delays",
            (ErrorCategory.NETWORK_ERROR, ErrorSeverity.MEDIUM): "Intermittent failures - some requests may fail",
            (ErrorCategory.API_ERROR, ErrorSeverity.MEDIUM): "Feature degradation - some features may not work",
            (ErrorCategory.PARSING_ERROR, ErrorSeverity.LOW): "Minor data issues - some results may be incomplete",
        }
        
        return impact_matrix.get((category, severity), "Minimal impact on user experience")
    
    def _update_stats(self, category: ErrorCategory, severity: ErrorSeverity):
        """Update error statistics"""
        category_key = category.value
        severity_key = severity.value
        
        if category_key not in self.error_stats:
            self.error_stats[category_key] = {}
        
        if severity_key not in self.error_stats[category_key]:
            self.error_stats[category_key][severity_key] = 0
        
        self.error_stats[category_key][severity_key] += 1
    
    def _log_error(self, error_event: ErrorEvent):
        """Log error with appropriate level and formatting"""
        log_message = f"[{error_event.error_id}] {error_event.message}"
        
        if error_event.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={"error_event": asdict(error_event)})
        elif error_event.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra={"error_event": asdict(error_event)})
        elif error_event.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra={"error_event": asdict(error_event)})
        else:
            logger.info(log_message, extra={"error_event": asdict(error_event)})
    
    def _check_alert_conditions(self, error_event: ErrorEvent):
        """Check if error conditions warrant alerts"""
        threshold = self.alert_thresholds.get(error_event.severity, 10)
        recent_errors = [
            e for e in self.errors 
            if e.category == error_event.category 
            and e.severity == error_event.severity
            and self._is_recent(e.timestamp, hours=1)
        ]
        
        if len(recent_errors) >= threshold:
            self._send_alert(error_event, len(recent_errors))
    
    def _is_recent(self, timestamp_str: str, hours: int = 1) -> bool:
        """Check if timestamp is within recent time window"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return datetime.now() - timestamp <= timedelta(hours=hours)
        except:
            return False
    
    def _send_alert(self, error_event: ErrorEvent, count: int):
        """Send alert for critical error conditions"""
        alert_message = f"Alert: {count} {error_event.severity.value} errors in the last hour"
        logger.critical(alert_message, extra={
            "alert_type": "error_threshold",
            "error_category": error_event.category.value,
            "error_count": count,
            "suggestions": error_event.resolution_suggestions
        })
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive error summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            e for e in self.errors 
            if self._is_recent(e.timestamp, hours)
        ]
        
        summary = {
            "time_period": f"Last {hours} hours",
            "total_errors": len(recent_errors),
            "unique_errors": len(set(e.error_id for e in recent_errors)),
            "by_severity": {},
            "by_category": {},
            "top_errors": [],
            "recommendations": []
        }
        
        # Count by severity
        for severity in ErrorSeverity:
            count = len([e for e in recent_errors if e.severity == severity])
            if count > 0:
                summary["by_severity"][severity.value] = count
        
        # Count by category
        for category in ErrorCategory:
            count = len([e for e in recent_errors if e.category == category])
            if count > 0:
                summary["by_category"][category.value] = count
        
        # Get top recurring errors
        error_counts = {}
        for error in recent_errors:
            error_counts[error.error_id] = error_counts.get(error.error_id, 0) + 1
        
        top_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for error_id, count in top_errors:
            error_details = next((e for e in recent_errors if e.error_id == error_id), None)
            if error_details:
                summary["top_errors"].append({
                    "error_id": error_id,
                    "count": count,
                    "message": error_details.message[:100],
                    "severity": error_details.severity.value,
                    "category": error_details.category.value
                })
        
        # Generate overall recommendations
        if summary["total_errors"] > 50:
            summary["recommendations"].append("High error rate detected - investigate system stability")
        if summary["by_severity"].get("critical", 0) > 0:
            summary["recommendations"].append("Critical errors detected - immediate attention required")
        if summary["by_category"].get("authentication_error", 0) > 5:
            summary["recommendations"].append("Multiple authentication errors - check API key configuration")
        
        return summary
    
    def export_error_report(self, filepath: str, hours: int = 24):
        """Export detailed error report to JSON file"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_error_summary(hours),
            "detailed_errors": [
                asdict(e) for e in self.errors 
                if self._is_recent(e.timestamp, hours)
            ]
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Error report exported to {filepath}")


# Global error monitor instance
error_monitor = ErrorMonitor()


def error_handler(
    category: Optional[ErrorCategory] = None,
    severity: Optional[ErrorSeverity] = None,
    context: Optional[Dict[str, Any]] = None,
    reraise: bool = True
):
    """
    Decorator for comprehensive error handling and monitoring
    
    Usage:
        @error_handler(category=ErrorCategory.API_ERROR)
        def risky_function():
            # Function that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create enriched context
                enriched_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                    **(context or {})
                }
                
                # Record error
                error_id = error_monitor.record_error(e, enriched_context)
                
                # Add error ID to exception for tracking
                e.error_id = error_id
                
                if reraise:
                    raise
                return None
        return wrapper
    return decorator


def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator for automatic retry with error monitoring
    
    Usage:
        @with_retry(max_retries=3, delay=1.0)
        def unreliable_function():
            # Function that might need retrying
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Record retry attempt
                    error_monitor.record_error(e, {
                        "function": func.__name__,
                        "attempt": attempt + 1,
                        "max_retries": max_retries,
                        "is_retry": True
                    })
                    
                    if attempt < max_retries:
                        if on_retry:
                            on_retry(e, attempt + 1, current_delay)
                        
                        logger.warning(f"Retrying {func.__name__} in {current_delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"Final retry failed for {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.health_checks = {}
        self.last_check_time = None
        self.health_status = "unknown"
    
    def register_check(self, name: str, check_func: Callable[[], bool], timeout: int = 30):
        """Register a health check function"""
        self.health_checks[name] = {
            "function": check_func,
            "timeout": timeout,
            "last_result": None,
            "last_check": None
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_config in self.health_checks.items():
            try:
                start_time = time.time()
                result = check_config["function"]()
                duration = time.time() - start_time
                
                results[name] = {
                    "healthy": result,
                    "duration_ms": round(duration * 1000, 2),
                    "last_check": datetime.now().isoformat()
                }
                
                check_config["last_result"] = result
                check_config["last_check"] = datetime.now().isoformat()
                
                if not result:
                    overall_healthy = False
                    
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "duration_ms": 0,
                    "last_check": datetime.now().isoformat()
                }
                overall_healthy = False
                
                error_monitor.record_error(e, {
                    "health_check": name,
                    "check_type": "system_health"
                })
        
        self.health_status = "healthy" if overall_healthy else "unhealthy"
        self.last_check_time = datetime.now().isoformat()
        
        return {
            "overall_status": self.health_status,
            "last_check": self.last_check_time,
            "checks": results,
            "error_summary": error_monitor.get_error_summary(hours=1)
        }


# Global health checker instance
health_checker = HealthChecker()


def setup_default_health_checks():
    """Setup default health checks for the system"""
    
    def check_api_keys():
        """Check if required API keys are configured"""
        from src.utils.config import config
        try:
            config.get_model_config()
            return True
        except ValueError:
            return False
    
    def check_disk_space():
        """Check available disk space"""
        import shutil
        free_space_gb = shutil.disk_usage('.').free / (1024**3)
        return free_space_gb > 1.0  # At least 1GB free
    
    def check_memory_usage():
        """Check memory usage"""
        import psutil
        memory_usage = psutil.virtual_memory().percent
        return memory_usage < 90  # Less than 90% memory usage
    
    # Register health checks
    health_checker.register_check("api_keys", check_api_keys)
    health_checker.register_check("disk_space", check_disk_space)
    health_checker.register_check("memory_usage", check_memory_usage)


# Initialize default health checks
try:
    setup_default_health_checks()
except ImportError:
    logger.warning("Some health checks skipped due to missing dependencies")
