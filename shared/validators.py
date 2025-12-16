# shared/validators.py
"""
Reusable Validators
==================

Common validation functions used across the application.
"""

import re
from pathlib import Path
from typing import Optional, List, Any

from core.exceptions import ValidationError
from shared.constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES


def validate_file_path(file_path: str) -> Path:
    """
    Validate file path
    
    Args:
        file_path: Path to validate
    
    Returns:
        Validated Path object
    
    Raises:
        ValidationError: If validation fails
    """
    path = Path(file_path)
    
    # Check exists
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")
    
    # Check is file
    if not path.is_file():
        raise ValidationError(f"Not a file: {file_path}")
    
    # Check extension
    if path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type: {path.suffix}. "
            f"Allowed: {', '.join(ALLOWED_FILE_EXTENSIONS)}"
        )
    
    # Check size
    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / 1024 / 1024
        max_mb = MAX_FILE_SIZE_BYTES / 1024 / 1024
        raise ValidationError(f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)")
    
    return path


def validate_cwe_id(cwe: Optional[str]) -> Optional[str]:
    """
    Validate and normalize CWE ID
    
    Args:
        cwe: CWE ID string
    
    Returns:
        Normalized CWE ID or None
    """
    if not cwe:
        return None
    
    cwe_str = str(cwe).strip()
    
    # Already in correct format
    if re.match(r'^CWE-\d+$', cwe_str):
        return cwe_str
    
    # Just a number
    if cwe_str.isdigit():
        return f"CWE-{cwe_str}"
    
    return None


def validate_cvss_score(score: Any) -> Optional[float]:
    """
    Validate CVSS score
    
    Args:
        score: CVSS score (any type)
    
    Returns:
        Valid score (0.0-10.0) or None
    """
    if score is None:
        return None
    
    try:
        score_float = float(score)
        if 0.0 <= score_float <= 10.0:
            return score_float
    except (ValueError, TypeError):
        pass
    
    return None


def validate_confidence(confidence: Any) -> Optional[float]:
    """
    Validate confidence level
    
    Args:
        confidence: Confidence value (any type)
    
    Returns:
        Valid confidence (0.0-1.0) or None
    """
    if confidence is None:
        return None
    
    try:
        # Handle percentage strings
        if isinstance(confidence, str) and '%' in confidence:
            value = float(confidence.replace('%', ''))
            return value / 100.0
        
        # Handle numeric values
        conf_float = float(confidence)
        
        # If already 0-1, return as is
        if 0.0 <= conf_float <= 1.0:
            return conf_float
        
        # If 0-100, convert to 0-1
        if 0.0 <= conf_float <= 100.0:
            return conf_float / 100.0
        
    except (ValueError, TypeError):
        pass
    
    return None


def validate_temperature(temperature: float) -> float:
    """
    Validate LLM temperature
    
    Args:
        temperature: Temperature value
    
    Returns:
        Valid temperature
    
    Raises:
        ValidationError: If invalid
    """
    if not isinstance(temperature, (int, float)):
        raise ValidationError(f"Temperature must be numeric, got {type(temperature)}")
    
    if not (0.0 <= temperature <= 2.0):
        raise ValidationError(f"Temperature must be 0.0-2.0, got {temperature}")
    
    return float(temperature)


def validate_provider(provider: str) -> str:
    """
    Validate LLM provider
    
    Args:
        provider: Provider name
    
    Returns:
        Normalized provider name
    
    Raises:
        ValidationError: If invalid
    """
    if not provider:
        raise ValidationError("Provider cannot be empty")
    
    provider_lower = provider.lower()
    
    valid_providers = ['openai', 'watsonx']
    if provider_lower not in valid_providers:
        raise ValidationError(
            f"Invalid provider: {provider}. "
            f"Valid: {', '.join(valid_providers)}"
        )
    
    return provider_lower


def validate_json_fields(
    data: dict,
    required_fields: List[str],
    optional_fields: List[str] = None
) -> None:
    """
    Validate JSON data has required fields
    
    Args:
         JSON data dict
        required_fields: List of required field names
        optional_fields: List of optional field names
    
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError(f"Data must be dict, got {type(data)}")
    
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        available = list(data.keys())
        raise ValidationError(
            f"Missing required fields: {missing}. "
            f"Available: {available}"
        )
