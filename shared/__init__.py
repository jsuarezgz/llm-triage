# shared/__init__.py
"""
Shared utilities package
"""

from .logger import setup_logging
from .metrics import MetricsCollector

__all__ = ['setup_logging', 'MetricsCollector']
