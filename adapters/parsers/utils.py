# adapters/parsers/utils.py
"""
Parser Utilities - Shared helpers for all parsers
================================================

Provides:
- Field extraction with fallbacks
- Vulnerability type detection
- Confidence score calculation
"""

import re
from typing import Any, Optional, Dict
from functools import lru_cache

from core.models import VulnerabilityType
from shared.constants import VULNERABILITY_TYPE_PATTERNS


class FieldExtractor:
    """Safe multi-field extraction with fallbacks"""
    
    @staticmethod
    def get(data: Dict[str, Any], *field_names: str) -> Optional[Any]:
        """
        Extract first available field from multiple options
        
        Args:
             Dictionary to search
            *field_names: Field names in priority order
        
        Returns:
            First non-None value found, or None
        
        Example:
            >>> FieldExtractor.get(data, "file", "path", "filename")
        """
        if not isinstance(data, dict):
            return None
        
        for field in field_names:
            if field in data and data[field] is not None:
                value = data[field]
                # Skip empty strings/lists
                if value == "" or value == [] or value == {}:
                    continue
                return value
        
        return None


class VulnerabilityTypeDetector:
    """Intelligent vulnerability type detection"""
    
    @staticmethod
    @lru_cache(maxsize=256)
    def detect(
        title: str,
        description: str = "",
        rule_id: str = ""
    ) -> VulnerabilityType:
        """
        Detect vulnerability type from text analysis
        
        Args:
            title: Vulnerability title
            description: Vulnerability description
            rule_id: Scanner rule ID
        
        Returns:
            Detected VulnerabilityType
        
        Strategy:
            1. Check rule_id patterns
            2. Check title patterns
            3. Check description patterns
            4. Default to OTHER
        """
        # Combine all text for matching
        text = f"{title} {description} {rule_id}".lower()
        
        # Pattern matching with priority
        for pattern, vuln_type in VULNERABILITY_TYPE_PATTERNS.items():
            if pattern in text:
                return vuln_type
        
        # Specific checks for common patterns
        if any(x in text for x in ['sql', 'injection', 'sqli']):
            return VulnerabilityType.SQL_INJECTION
        
        if any(x in text for x in ['xss', 'cross-site', 'script injection']):
            return VulnerabilityType.XSS
        
        if any(x in text for x in ['path', 'traversal', 'directory', '../']):
            return VulnerabilityType.PATH_TRAVERSAL
        
        if any(x in text for x in ['auth', 'authentication', 'bypass']):
            return VulnerabilityType.AUTH_BYPASS
        
        if any(x in text for x in ['access', 'authorization', 'privilege']):
            return VulnerabilityType.BROKEN_ACCESS_CONTROL
        
        if any(x in text for x in ['crypto', 'encryption', 'weak hash']):
            return VulnerabilityType.INSECURE_CRYPTO
        
        if any(x in text for x in ['sensitive', 'exposure', 'leak']):
            return VulnerabilityType.SENSITIVE_DATA_EXPOSURE
        
        # Default
        return VulnerabilityType.OTHER


class ConfidenceCalculator:
    """Calculate confidence scores with normalization"""
    
    # Confidence mappings
    CONFIDENCE_MAPPINGS = {
        'HIGH': 0.9,
        'ALTA': 0.9,
        'CERTAIN': 0.95,
        'MEDIUM': 0.7,
        'MEDIA': 0.7,
        'MODERATE': 0.7,
        'LOW': 0.5,
        'BAJA': 0.5,
        'UNCERTAIN': 0.3,
    }
    
    @classmethod
    def calculate(cls, confidence_input: Any) -> float:
        """
        Calculate normalized confidence score (0.0-1.0)
        
        Args:
            confidence_input: String, float, or int
        
        Returns:
            Normalized confidence (0.0-1.0)
        
        Examples:
            >>> ConfidenceCalculator.calculate("HIGH")
            0.9
            >>> ConfidenceCalculator.calculate(85)
            0.85
            >>> ConfidenceCalculator.calculate(0.75)
            0.75
        """
        if confidence_input is None:
            return 0.7  # Default moderate confidence
        
        # String mapping
        if isinstance(confidence_input, str):
            normalized = confidence_input.upper().strip()
            return cls.CONFIDENCE_MAPPINGS.get(normalized, 0.7)
        
        # Numeric normalization
        if isinstance(confidence_input, (int, float)):
            value = float(confidence_input)
            
            # Already normalized (0.0-1.0)
            if 0.0 <= value <= 1.0:
                return value
            
            # Percentage (0-100)
            if 0 < value <= 100:
                return value / 100.0
            
            # Out of range, clamp
            return max(0.0, min(1.0, value))
        
        # Unknown type
        return 0.7


# Convenience functions
def safe_extract_field( Dict, *fields: str) -> Optional[str]:
    """Extract field and convert to string safely"""
    value = FieldExtractor.get(data, *fields)
    return str(value) if value is not None else None


def detect_vuln_type_from_cwe(cwe_id: Optional[str]) -> Optional[VulnerabilityType]:
    """
    Map CWE ID to vulnerability type
    
    Common mappings:
    - CWE-89 → SQL Injection
    - CWE-79 → XSS
    - CWE-22 → Path Traversal
    """
    if not cwe_id:
        return None
    
    cwe_map = {
        '89': VulnerabilityType.SQL_INJECTION,
        '79': VulnerabilityType.XSS,
        '22': VulnerabilityType.PATH_TRAVERSAL,
        '78': VulnerabilityType.CODE_INJECTION,
        '94': VulnerabilityType.CODE_INJECTION,
        '287': VulnerabilityType.AUTH_BYPASS,
        '285': VulnerabilityType.BROKEN_ACCESS_CONTROL,
        '327': VulnerabilityType.INSECURE_CRYPTO,
        '200': VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
    }
    
    # Extract number from CWE-XXX
    match = re.search(r'(\d+)', cwe_id)
    if match:
        cwe_num = match.group(1)
        return cwe_map.get(cwe_num)
    
    return None
