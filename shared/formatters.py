# shared/formatters.py
"""
Reusable Formatters
==================

Common formatting functions for display and logging.
"""

from datetime import datetime, timedelta
from typing import Any, Optional


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes to human-readable format
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def format_duration(seconds: float) -> str:
    """
    Format duration to human-readable format
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining = seconds % 60
        return f"{minutes}m {remaining:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_seconds = seconds % 3600
        minutes = int(remaining_seconds // 60)
        return f"{hours}h {minutes}m"


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object (default: now)
        fmt: Format string
    
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime(fmt)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format float as percentage
    
    Args:
        value: Value (0.0-1.0)
        decimals: Decimal places
    
    Returns:
        Formatted percentage (e.g., "75.5%")
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(value: int, separator: str = ",") -> str:
    """
    Format number with thousands separator
    
    Args:
        value: Number to format
        separator: Thousands separator
    
    Returns:
        Formatted number (e.g., "1,234,567")
    """
    return f"{value:,}".replace(",", separator)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_severity_icon(severity: str) -> str:
    """
    Get emoji icon for severity
    
    Args:
        severity: Severity level
    
    Returns:
        Emoji icon
    """
    from shared.constants import SEVERITY_ICONS
    return SEVERITY_ICONS.get(severity.upper(), "•")


def format_list(items: list, separator: str = ", ", last_separator: str = " and ") -> str:
    """
    Format list to human-readable string
    
    Args:
        items: List of items
        separator: Separator between items
        last_separator: Separator before last item
    
    Returns:
        Formatted string (e.g., "a, b and c")
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return str(items[0])
    
    if len(items) == 2:
        return f"{items[0]}{last_separator}{items[1]}"
    
    return separator.join(str(i) for i in items[:-1]) + f"{last_separator}{items[-1]}"
