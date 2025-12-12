# shared/logger.py
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

class JSONFormatter(logging.Formatter):
    """Formatter JSON optimizado para logs estructurados"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'extra'):
            log_data["extra"] = record.extra
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        return (
            f"{color}[{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')}] "
            f"{record.levelname:<8}{reset} - "
            f"{record.module}.{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}"
        )

def setup_logging(log_level: str = "INFO", 
                 log_file: Optional[str] = None,
                 structured: bool = False) -> None:
    """Configurar logging optimizado y simplificado"""
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if structured:
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter()
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy loggers
    for noisy_logger in ['urllib3', 'requests', 'openai']:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}")
