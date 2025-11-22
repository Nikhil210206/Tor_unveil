"""
Structured logging utility for the TOR analysis tool.
"""

import logging
import sys
from typing import Optional
from pathlib import Path
import json
from datetime import datetime


class StructuredLogger:
    """Provides structured logging with JSON formatting and multiple handlers."""
    
    def __init__(self, name: str, log_file: Optional[Path] = None, level: int = logging.INFO):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Optional file path for log output
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (JSON format)
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data."""
        self._log(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional structured data."""
        self._log(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data."""
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional structured data."""
        self._log(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data."""
        self._log(logging.CRITICAL, message, kwargs)
    
    def _log(self, level: int, message: str, extra_data: dict):
        """Internal logging method with structured data."""
        if extra_data:
            message = f"{message} | {json.dumps(extra_data)}"
        self.logger.log(level, message)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def get_logger(name: str, log_dir: Optional[Path] = None) -> StructuredLogger:
    """
    Get or create a structured logger.
    
    Args:
        name: Logger name
        log_dir: Optional directory for log files
    
    Returns:
        StructuredLogger instance
    """
    log_file = None
    if log_dir:
        log_file = log_dir / f"{name}.log"
    
    return StructuredLogger(name, log_file)
