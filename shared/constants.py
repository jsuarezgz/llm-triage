# shared/constants.py
"""
Global Constants - Single Source of Truth
=========================================

All constants used across the application.
"""

from core.models import SeverityLevel, VulnerabilityType

# ════════════════════════════════════════════════════════════════════
# SEVERITY MAPPINGS
# ════════════════════════════════════════════════════════════════════

SEVERITY_MAPPINGS = {
    'CRITICAL': SeverityLevel.CRITICAL,
    'CRÍTICA': SeverityLevel.CRITICAL,
    'BLOCKER': SeverityLevel.CRITICAL,
    'HIGH': SeverityLevel.HIGH,
    'ALTA': SeverityLevel.HIGH,
    'MAJOR': SeverityLevel.HIGH,
    'MEDIUM': SeverityLevel.MEDIUM,
    'MEDIA': SeverityLevel.MEDIUM,
    'LOW': SeverityLevel.LOW,
    'BAJA': SeverityLevel.LOW,
    'MINOR': SeverityLevel.MEDIUM,
    'INFO': SeverityLevel.INFO,
}

SEVERITY_WEIGHTS = {
    'CRÍTICA': 10.0,
    'ALTA': 7.0,
    'MEDIA': 4.0,
    'BAJA': 2.0,
    'INFO': 0.5
}

SEVERITY_ICONS = {
    'CRÍTICA': '🔥',
    'ALTA': '⚡',
    'MEDIA': '⚠️',
    'BAJA': '📝',
    'INFO': 'ℹ️'
}

# ════════════════════════════════════════════════════════════════════
# VULNERABILITY TYPE PATTERNS
# ════════════════════════════════════════════════════════════════════

VULNERABILITY_TYPE_PATTERNS = {
    'sql injection': VulnerabilityType.SQL_INJECTION,
    'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
    'path traversal': VulnerabilityType.PATH_TRAVERSAL,
    'code injection': VulnerabilityType.CODE_INJECTION,
    'cross-site scripting': VulnerabilityType.XSS,
    'xss': VulnerabilityType.XSS,
    'authentication': VulnerabilityType.AUTH_BYPASS,
    'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
    'crypto': VulnerabilityType.INSECURE_CRYPTO,
}

# ════════════════════════════════════════════════════════════════════
# FILE VALIDATION
# ════════════════════════════════════════════════════════════════════

ALLOWED_FILE_EXTENSIONS = ['.json']
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_VULNERABILITIES = 10000

# ════════════════════════════════════════════════════════════════════
# LLM DEFAULTS
# ════════════════════════════════════════════════════════════════════

DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TIMEOUT = 180

# ════════════════════════════════════════════════════════════════════
# CHUNKING DEFAULTS
# ════════════════════════════════════════════════════════════════════

DEFAULT_CHUNK_SIZE = 5
DEFAULT_CHUNK_OVERLAP = 1
DEFAULT_MIN_CHUNK_SIZE = 3
DEFAULT_MAX_CHUNK_BYTES = 8000

# ════════════════════════════════════════════════════════════════════
# CACHE DEFAULTS
# ════════════════════════════════════════════════════════════════════

DEFAULT_CACHE_TTL_HOURS = 24
DEFAULT_CACHE_DIR = ".security_cache"

# ════════════════════════════════════════════════════════════════════
# DEDUPLICATION
# ════════════════════════════════════════════════════════════════════

DEDUP_STRATEGIES = ['strict', 'moderate', 'loose']
DEFAULT_DEDUP_STRATEGY = 'moderate'

# Similarity thresholds
DEDUP_THRESHOLD_STRICT = 1.0   # Exact match
DEDUP_THRESHOLD_MODERATE = 0.8  # 80% similar
DEDUP_THRESHOLD_LOOSE = 0.7     # 70% similar

# Line proximity for moderate strategy
DEDUP_LINE_PROXIMITY = 5  # ±5 lines
