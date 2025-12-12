# core/models.py
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# === ENUMS CONSOLIDADOS ===
class SeverityLevel(str, Enum):
    CRITICAL = "CRÍTICA"
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"
    INFO = "INFO"
    
class VulnerabilityType(str, Enum):
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
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"

class LLMProvider(str, Enum):
    OPENAI = "openai"
    WATSONX = "watsonx"

class ChunkingStrategy(str, Enum):
    NO_CHUNKING = "no_chunking"
    BY_COUNT = "by_vulnerability_count"
    BY_SIZE = "by_size"
    ADAPTIVE = "adaptive"

class Vulnerability(BaseModel):
    """Modelo central optimizado de vulnerabilidad"""
    id: str = Field(..., description="ID único de la vulnerabilidad")
    type: VulnerabilityType
    severity: SeverityLevel
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    
    # Ubicación
    file_path: str = Field(..., min_length=1)
    line_number: int = Field(ge=0, default=0)
    code_snippet: Optional[str] = None
    
    # Metadatos de seguridad
    cwe_id: Optional[str] = Field(None, pattern=r"^CWE-\d+$")
    confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Origen
    source_tool: Optional[str] = None
    rule_id: Optional[str] = None
    
    # Contexto adicional
    impact_description: Optional[str] = None
    remediation_advice: Optional[str] = None
    
    # Metadatos
    created_at: datetime = Field(default_factory=datetime.now)
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('severity', mode='before')
    @classmethod
    def normalize_severity(cls, v):
        """Normalización inteligente de severidad"""
        if isinstance(v, str):
            mapping = {
                'CRITICAL': SeverityLevel.CRITICAL, 'HIGH': SeverityLevel.HIGH,
                'MEDIUM': SeverityLevel.MEDIUM, 'LOW': SeverityLevel.LOW,
                'INFO': SeverityLevel.INFO, 'BLOCKER': SeverityLevel.CRITICAL,
                'MAJOR': SeverityLevel.HIGH, 'MINOR': SeverityLevel.MEDIUM,
                'CRÍTICA': SeverityLevel.CRITICAL, 'ALTA': SeverityLevel.HIGH,
                'MEDIA': SeverityLevel.MEDIUM, 'BAJA': SeverityLevel.LOW
            }
            return mapping.get(v.upper(), SeverityLevel.MEDIUM)
        return v
    
    @computed_field
    @property
    def priority_score(self) -> int:
        """Score para ordenamiento por prioridad"""
        base_score = {
            SeverityLevel.CRITICAL: 100, SeverityLevel.HIGH: 80,
            SeverityLevel.MEDIUM: 60, SeverityLevel.LOW: 40, SeverityLevel.INFO: 20
        }[self.severity]
        
        # Ajustar por confianza
        if self.confidence_level:
            base_score = int(base_score * self.confidence_level)
        
        return base_score
    
    @computed_field
    @property
    def is_high_priority(self) -> bool:
        """Determinar si es alta prioridad"""
        return self.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]

class TriageDecision(BaseModel):
    """Decisión de triaje optimizada"""
    vulnerability_id: str
    decision: AnalysisStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=10)
    llm_model_used: str
    analyzed_at: datetime = Field(default_factory=datetime.now)

class TriageResult(BaseModel):
    """Resultado de triaje con validación automática"""
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

class RemediationStep(BaseModel):
    """Paso de remediación optimizado"""
    step_number: int = Field(ge=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    code_example: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=1)
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
    tools_required: List[str] = Field(default_factory=list)

class RemediationPlan(BaseModel):
    """Plan de remediación consolidado"""
    vulnerability_id: str
    vulnerability_type: VulnerabilityType
    priority_level: str = Field(..., pattern=r"^(immediate|high|medium|low)$")
    steps: List[RemediationStep] = Field(..., min_length=1)
    risk_if_not_fixed: str
    references: List[str] = Field(default_factory=list)
    total_estimated_hours: Optional[float] = Field(None, ge=0.1)
    complexity_score: float = Field(ge=0.0, le=10.0, default=5.0)
    llm_model_used: str
    created_at: datetime = Field(default_factory=datetime.now)

class ScanResult(BaseModel):
    """Resultado de escaneo optimizado"""
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
        from collections import Counter
        return dict(Counter(v.severity.value for v in self.vulnerabilities))
    
    @computed_field
    @property
    def high_priority_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.is_high_priority)

class AnalysisReport(BaseModel):
    """Reporte de análisis completo"""
    report_id: str = Field(default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
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
        """Resumen ejecutivo automático"""
        return {
            "total_vulnerabilities": self.scan_result.vulnerability_count,
            "high_priority_count": self.scan_result.high_priority_count,
            "severity_distribution": self.scan_result.severity_distribution,
            "processing_time": f"{self.total_processing_time_seconds:.2f}s",
            "confirmed_vulnerabilities": self.triage_result.confirmed_count if self.triage_result else 0,
            "remediation_plans_generated": len(self.remediation_plans)
        }
