"""
PyX Logging - Zen Mode
Structured logging for PyX applications.
"""
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormatter(logging.Formatter):
    """Custom formatter for structured/pretty logging"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def __init__(self, structured: bool = False, colors: bool = True):
        super().__init__()
        self.structured = structured
        self.colors = colors
    
    def format(self, record):
        if self.structured:
            return self._format_json(record)
        return self._format_pretty(record)
    
    def _format_json(self, record) -> str:
        """Format as JSON for production/log aggregation"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)
    
    def _format_pretty(self, record) -> str:
        """Format as pretty output for development"""
        level = record.levelname
        
        if self.colors:
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            level_str = f"{color}{level:8}{reset}"
        else:
            level_str = f"{level:8}"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = record.getMessage()
        
        # Format extra data
        extra = ""
        if hasattr(record, 'extra_data') and record.extra_data:
            extra_parts = [f"{k}={v}" for k, v in record.extra_data.items()]
            extra = f" | {', '.join(extra_parts)}"
        
        return f"[{timestamp}] {level_str} {message}{extra}"


class ZenLogger:
    """
    Zen Mode Logger - Simple structured logging.
    
    Usage:
        from pyx import log
        
        # Basic logging
        log.info("User created", user_id=1, email="john@example.com")
        log.error("Failed to save", error=str(e))
        log.debug("Processing data", count=100)
        log.warning("Rate limit approaching", current=95, max=100)
        
        # Configure
        log.configure(level="DEBUG", structured=True)
        
        # Child logger
        auth_log = log.child("auth")
        auth_log.info("Login successful")
    """
    
    def __init__(self, name: str = "pyx", level: str = "INFO", structured: bool = False):
        self.name = name
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper()))
        self._structured = structured
        self._setup_handler()
    
    def _setup_handler(self):
        """Setup console handler"""
        # Remove existing handlers
        self._logger.handlers.clear()
        
        handler = logging.StreamHandler()
        handler.setFormatter(LogFormatter(
            structured=self._structured,
            colors=not self._structured
        ))
        self._logger.addHandler(handler)
    
    def configure(
        self,
        level: str = "INFO",
        structured: bool = False,
        file: str = None
    ):
        """
        Configure logger.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            structured: Use JSON format (for production)
            file: Log to file path
        """
        self._logger.setLevel(getattr(logging, level.upper()))
        self._structured = structured
        self._setup_handler()
        
        if file:
            file_handler = logging.FileHandler(file)
            file_handler.setFormatter(LogFormatter(structured=True, colors=False))
            self._logger.addHandler(file_handler)
        
        return self
    
    def child(self, name: str) -> "ZenLogger":
        """Create child logger with prefix"""
        child_name = f"{self.name}.{name}"
        return ZenLogger(child_name, 
                        level=logging.getLevelName(self._logger.level),
                        structured=self._structured)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with extra data"""
        record = self._logger.makeRecord(
            self._logger.name,
            level,
            "(unknown)",
            0,
            message,
            (),
            None
        )
        record.extra_data = kwargs if kwargs else None
        self._logger.handle(record)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, **kwargs)
    
    def warn(self, message: str, **kwargs):
        """Alias for warning"""
        self.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, exc: Exception = None, **kwargs):
        """Log exception with traceback"""
        import traceback
        
        if exc:
            kwargs['exception'] = str(exc)
            kwargs['traceback'] = traceback.format_exc()
        
        self._log(logging.ERROR, message, **kwargs)
    
    # Convenience methods
    def request(self, method: str, path: str, status: int, duration_ms: float, **kwargs):
        """Log HTTP request"""
        self.info(
            f"{method} {path} {status}",
            method=method,
            path=path,
            status=status,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def db_query(self, query: str, duration_ms: float, **kwargs):
        """Log database query"""
        self.debug(
            "DB Query",
            query=query[:100] + "..." if len(query) > 100 else query,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def auth(self, action: str, user_id: Any = None, success: bool = True, **kwargs):
        """Log authentication event"""
        level = logging.INFO if success else logging.WARNING
        self._log(
            level,
            f"Auth: {action}",
            action=action,
            user_id=user_id,
            success=success,
            **kwargs
        )
    
    def metric(self, name: str, value: float, unit: str = "", **kwargs):
        """Log a metric"""
        self.info(
            f"Metric: {name}={value}{unit}",
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            **kwargs
        )
    
    def event(self, name: str, **kwargs):
        """Log an application event"""
        self.info(f"Event: {name}", event_name=name, **kwargs)


# Zen Mode instance
log = ZenLogger()


# Re-export LogLevel
__all__ = ['log', 'ZenLogger', 'LogLevel', 'LogFormatter']
