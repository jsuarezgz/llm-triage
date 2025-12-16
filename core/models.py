# core/models.py
"""
Domain Models - Simplified & Optimized
=====================================

Clean domain models with validation and computed properties.
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════════════════
# ENUMS - Centralized
# ═══════════════════════════════════════════════════════════════════

class SeverityLevel(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "CRÍTICA"
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"
    INFO = "INFO"
    
    @property
    def weight(self) -> float:
        """Numeric weight for scoring"""
        weights = {
            self.CRITICAL: 10.0,
            self.HIGH: 7.0,
            self.MEDIUM: 4.0,
            self.LOW: 2.0,
            self.INFO: 0.5
        }
        return weights[self]


class VulnerabilityType(str, Enum):
    """Common vulnerability types"""
    SQL_INJECTION = "SQL Injection"
    XSS = "Cross-Site Scripting"
    PATH_TRAVERSAL = "Directory Traversal"
    CODE_INJECTION = "Code Injection"
    AUTH_BYPASS = "Authentication Bypass"
    BROKEN_ACCESS_CONTROL = "Broken Access Control"
    INSECURE_CRYPTO = "Insecure Cryptography"
    SENSITIVE_DATA_EXPOSURE = "Sensitive Data Exposure"
    SECURITY_MISCONFIGURATION = "Security Misconfiguration"
    OTHER = "Other Security Issue"


class AnalysisStatus(str, Enum):
    """Triage analysis status"""
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"


# ═══════════════════════════════════════════════════════════════════
# VULNERABILITY MODEL
# ═══════════════════════════════════════════════════════════════════

class Vulnerability(BaseModel):
    """Core vulnerability model with validation"""
    
    # Identity
    id: str = Field(..., min_length=1)
    type: VulnerabilityType
    severity: SeverityLevel
    
    # Description
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    
    # Location
    file_path: str = Field(..., min_length=1)
    line_number: int = Field(ge=0, default=0)
    code_snippet: Optional[str] = None
    
    # Security metadata
    cwe_id: Optional[str] = Field(None, pattern=r"^CWE-\d+$")
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Source
    source_tool: Optional[str] = None
    rule_id: Optional[str] = None
    
    # Remediation
    impact_description: Optional[str] = None
    remediation_advice: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v) -> SeverityLevel:
        """Normalize severity from various formats"""
        if isinstance(v, SeverityLevel):
            return v
        
        if isinstance(v, str):
            # Mapping table
            severity_map = {
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
            return severity_map.get(v.upper(), SeverityLevel.MEDIUM)
        
        return SeverityLevel.MEDIUM
    
    @computed_field
    @property
    def priority_score(self) -> int:
        """Priority score for sorting (0-100)"""
        base = int(self.severity.weight * 10)
        if self.confidence_level:
            base = int(base * self.confidence_level)
        return base
    
    @computed_field
    @property
    def is_high_priority(self) -> bool:
        """Check if high priority"""
        return self.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]


# ═══════════════════════════════════════════════════════════════════
# TRIAGE MODELS
# ═══════════════════════════════════════════════════════════════════

class TriageDecision(BaseModel):
    """Single triage decision"""
    vulnerability_id: str
    decision: AnalysisStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=10)
    llm_model_used: str
    analyzed_at: datetime = Field(default_factory=datetime.now)


class TriageResult(BaseModel):
    """Complete triage analysis result"""
    decisions: List[TriageDecision] = Field(default_factory=list)
    analysis_summary: str
    llm_analysis_time_seconds: float = Field(ge=0.0)
    
    @computed_field
    @property
    def total_analyzed(self) -> int:
        return len(self.decisions)
    
    @computed_field
    @property
    def confirmed_count(self) -> int:
        return sum(1 for d in self.decisions if d.decision == AnalysisStatus.CONFIRMED)
    
    @computed_field
    @property
    def false_positive_count(self) -> int:
        return sum(1 for d in self.decisions if d.decision == AnalysisStatus.FALSE_POSITIVE)
    
    @computed_field
    @property
    def needs_review_count(self) -> int:
        return sum(1 for d in self.decisions if d.decision == AnalysisStatus.NEEDS_MANUAL_REVIEW)


# ═══════════════════════════════════════════════════════════════════
# REMEDIATION MODELS
# ═══════════════════════════════════════════════════════════════════

class RemediationStep(BaseModel):
    """Single remediation step"""
    step_number: int = Field(ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    code_example: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=1)
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
    tools_required: List[str] = Field(default_factory=list)


class RemediationPlan(BaseModel):
    """Complete remediation plan"""
    vulnerability_id: str
    vulnerability_type: VulnerabilityType
    priority_level: str = Field(..., pattern=r"^(immediate|high|medium|low)$")
    complexity_score: float = Field(ge=0.0, le=10.0, default=5.0)
    steps: List[RemediationStep] = Field(..., min_length=1)
    risk_if_not_fixed: str = "Security vulnerability should be remediated."
    references: List[str] = Field(default_factory=list)
    llm_model_used: str
    created_at: datetime = Field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════════════
# SCAN RESULT
# ═══════════════════════════════════════════════════════════════════

class ScanResult(BaseModel):
    """Scan result with statistics"""
    file_info: Dict[str, Any]
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)
    scan_timestamp: datetime = Field(default_factory=datetime.now)
    scan_duration_seconds: float = Field(ge=0.0, default=0.0)
    language_detected: Optional[str] = None
    
    @computed_field
    @property
    def vulnerability_count(self) -> int:
        return len(self.vulnerabilities)
    
    @computed_field
    @property
    def severity_distribution(self) -> Dict[str, int]:
        """Count by severity"""
        from collections import Counter
        return dict(Counter(v.severity.value for v in self.vulnerabilities))
    
    @computed_field
    @property
    def high_priority_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.is_high_priority)


# ═══════════════════════════════════════════════════════════════════
# ANALYSIS REPORT
# ═══════════════════════════════════════════════════════════════════

class AnalysisReport(BaseModel):
    """Final analysis report"""
    report_id: str = Field(
        default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    generated_at: datetime = Field(default_factory=datetime.now)
    scan_result: ScanResult
    triage_result: Optional[TriageResult] = None
    remediation_plans: List[RemediationPlan] = Field(default_factory=list)
    analysis_config: Dict[str, Any] = Field(default_factory=dict)
    total_processing_time_seconds: float = Field(ge=0.0)
    chunking_enabled: bool = False
    
    @computed_field
    @property
    def executive_summary(self) -> Dict[str, Any]:
        """Auto-generated executive summary"""
        return {
            "total_vulnerabilities": self.scan_result.vulnerability_count,
            "high_priority_count": self.scan_result.high_priority_count,
            "severity_distribution": self.scan_result.severity_distribution,
            "processing_time": f"{self.total_processing_time_seconds:.2f}s",
            "confirmed_vulnerabilities": (
                self.triage_result.confirmed_count if self.triage_result else 0
            ),
            "remediation_plans_generated": len(self.remediation_plans)
        }
