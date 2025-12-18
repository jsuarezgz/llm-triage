# infrastructure/llm/response_parser.py
"""
LLM Response Parser - FIXED & ENHANCED with Pydantic
=====================================================

Responsibilities:
- Parse and validate LLM responses
- Handle multiple response formats (WatsonX, OpenAI)
- Robust JSON extraction
- Type-safe conversion using Pydantic
"""

import json
import re
import logging
import time
from typing import Optional, List, Any, Dict, Union
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, field_validator
from core.models import (
    TriageResult, TriageDecision, AnalysisStatus,
    RemediationPlan, RemediationStep, VulnerabilityType
)
from core.exceptions import LLMError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS FOR LLM RESPONSES
# ═══════════════════════════════════════════════════════════════════════

class TriageDecisionRaw(BaseModel):
    """Raw triage decision from LLM (flexible fields)"""
    vulnerability_id: str = Field(alias="id")
    decision: str = "needs_manual_review"
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reasoning: str = "No reasoning provided"
    severity_adjustment: Optional[str] = None
    cwe_ids: Optional[List[str]] = None
    attack_vector: Optional[str] = None
    business_impact: Optional[str] = None
    
    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }
    
    @field_validator('decision', mode='before')
    @classmethod
    def normalize_decision(cls, v):
        """Normalize decision to standard values"""
        v_lower = str(v).lower()
        
        # Map variations to standard decisions
        if v_lower in ['confirmed', 'confirm', 'true', 'real', 'valid']:
            return 'confirmed'
        elif v_lower in ['false_positive', 'false positive', 'fp', 'rejected', 'invalid']:
            return 'false_positive'
        elif v_lower in ['needs_manual_review', 'review', 'manual', 'uncertain', 'unknown']:
            return 'needs_manual_review'
        
        # Default to manual review for unknown values
        logger.warning(f"Unknown decision '{v}', defaulting to needs_manual_review")
        return 'needs_manual_review'


class TriageResponseRaw(BaseModel):
    """Raw triage response from LLM"""
    decisions: List[TriageDecisionRaw] = Field(default_factory=list)
    analysis_summary: Optional[str] = None
    llm_analysis_time_seconds: float = 0.0
    
    model_config = {"extra": "ignore"}


class RemediationStepRaw(BaseModel):
    """Raw remediation step from LLM"""
    step_number: int = Field(ge=1)
    title: str
    description: str
    code_example: Optional[str] = None
    estimated_minutes: Optional[int] = Field(default=30, ge=1)
    difficulty: str = Field(default="medium")
    tools_required: List[str] = Field(default_factory=list)
    
    @field_validator('difficulty', mode='before')
    @classmethod
    def normalize_difficulty(cls, v):
        v_lower = str(v).lower()
        if v_lower in ['easy', 'low', 'simple']:
            return 'easy'
        elif v_lower in ['hard', 'high', 'complex', 'difficult']:
            return 'hard'
        return 'medium'


class RemediationPlanRaw(BaseModel):
    """Raw remediation plan from LLM"""
    vulnerability_id: str
    vulnerability_type: str
    priority_level: str
    complexity_score: float = Field(default=5.0, ge=0.0, le=10.0)
    steps: List[RemediationStepRaw] = Field(min_length=1)
    risk_if_not_fixed: str = "Security vulnerability should be remediated."
    references: List[str] = Field(default_factory=list)
    llm_model_used: str = "unknown"
    
    @field_validator('priority_level', mode='before')
    @classmethod
    def normalize_priority(cls, v):
        v_lower = str(v).lower()
        if v_lower in ['immediate', 'critical', 'urgent']:
            return 'immediate'
        elif v_lower in ['high', 'important']:
            return 'high'
        elif v_lower in ['low', 'minor']:
            return 'low'
        return 'medium'


# ═══════════════════════════════════════════════════════════════════════
# MAIN PARSER CLASS
# ═══════════════════════════════════════════════════════════════════════

class LLMResponseParser:
    """Enhanced response parser with Pydantic validation"""
    
    def __init__(self, debug_enabled: bool = True):
        self.debug_enabled = debug_enabled
        self.model_name = "meta-llama/llama-3-3-70b-instruct"
    
    # ═══════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ═══════════════════════════════════════════════════════════════════
    
    def parse_triage_response(
        self,
        llm_response: str,
        original_vulnerabilities: str
    ) -> TriageResult:
        """
        Parse triage response to TriageResult
        
        Args:
            llm_response: Raw LLM response
            original_vulnerabilities: Original vulnerability data
        
        Returns:
            TriageResult with validated decisions
        """
        logger.info(f"📋 Parsing triage response ({len(llm_response):,} chars)")
        
        if self.debug_enabled:
            logger.debug(f"Raw response preview:\n{llm_response[:500]}...")
        
        # Step 1: Clean response
        cleaned = self._clean_response(llm_response)
        
        # Step 2: Extract JSON
        json_str = self._extract_json_robust(cleaned)
        
        if not json_str:
            raise LLMError("Could not extract valid JSON from triage response")
        
        # Step 3: Parse with Pydantic
        try:
            raw_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            if self.debug_enabled:
                logger.debug(f"Failed JSON:\n{json_str[:1000]}...")
            raise LLMError(f"Invalid JSON in triage response: {e}")
        
        # Step 4: Normalize format (WatsonX vs Standard)
        normalized = self._normalize_triage_format(raw_data)
        
        # Step 5: Validate with Pydantic
        try:
            raw_response = TriageResponseRaw(**normalized)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise LLMError(f"Invalid triage response structure: {e}")
        
        # Step 6: Convert to domain models
        result = self._convert_to_triage_result(raw_response)
        
        # Step 7: Validate completeness
        self._validate_triage_completeness(result, original_vulnerabilities)
        
        logger.info(f"✅ Triage parsed: {result.total_analyzed} decisions")
        return result
    
    def parse_remediation_response(
        self,
        llm_response: str,
        vuln_type: str = None,
        language: str = None
    ) -> RemediationPlan:
        """
        Parse remediation response to RemediationPlan
        
        Args:
            llm_response: Raw LLM response
            vuln_type: Vulnerability type
            language: Programming language
        
        Returns:
            RemediationPlan with validated steps
        """
        logger.info(f"🛠️ Parsing remediation response ({len(llm_response):,} chars)")
        
        # Step 1: Clean response
        cleaned = self._clean_response(llm_response)
        
        # Step 2: Extract JSON
        json_str = self._extract_json_robust(cleaned)
        
        if not json_str:
            raise LLMError("Could not extract valid JSON from remediation response")
        
        # Step 3: Parse JSON
        try:
            raw_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON in remediation response: {e}")
        
        # Step 4: Add defaults
        if 'vulnerability_id' not in raw_data:
            raw_data['vulnerability_id'] = f"{vuln_type or 'unknown'}_{int(time.time())}"
        
        if 'llm_model_used' not in raw_data:
            raw_data['llm_model_used'] = self.model_name
        
        # Step 5: Validate with Pydantic
        try:
            raw_plan = RemediationPlanRaw(**raw_data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise LLMError(f"Invalid remediation plan structure: {e}")
        
        # Step 6: Convert to domain model
        result = self._convert_to_remediation_plan(raw_plan, vuln_type)
        
        logger.info(f"✅ Remediation parsed: {len(result.steps)} steps")
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # RESPONSE CLEANING
    # ═══════════════════════════════════════════════════════════════════
    
    def _clean_response(self, response: str) -> str:
        """Clean LLM response from markdown and prefixes"""
        text = response.strip()
        
        # Remove markdown code blocks
        patterns = [
            r'^```(?:json)?\s*\n(.+?)\n```$',  # Standard: ```json ... ```
            r'^```(?:json)?(.+?)```$',         # Without newlines
            r'```(?:json)?\s*\n(.+?)\n```',    # In middle of text
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                text = match.group(1).strip()
                logger.debug("🧹 Removed markdown wrapper")
                break
        
        # Remove prefixes
        prefixes = ['json\n', 'JSON\n', 'L3##json\n', 'L3##', 'L##']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].lstrip()
                logger.debug(f"🧹 Removed prefix: {prefix}")
        
        # Remove trailing markers
        if text.endswith('```'):
            text = text[:-3].rstrip()
        
        return text.strip()
    
    def _extract_json_robust(self, text: str) -> Optional[str]:
        """
        Extract JSON with multiple strategies
        
        Strategies (in order):
        1. Direct parse (already valid JSON)
        2. Balanced extraction (auto-fix unbalanced braces)
        3. Stack-based extraction (find complete objects)
        4. Regex extraction (find JSON-like structures)
        """
        # Strategy 1: Direct parse
        if self._is_valid_json(text):
            return text
        
        # Strategy 2: Balanced extraction
        balanced = self._try_balance_json(text)
        if balanced and self._is_valid_json(balanced):
            logger.info("✅ Extracted with balanced strategy")
            return balanced
        
        # Strategy 3: Stack-based extraction
        stack_extracted = self._extract_with_stack(text)
        if stack_extracted:
            logger.info("✅ Extracted with stack strategy")
            return stack_extracted
        
        # Strategy 4: Regex extraction
        regex_extracted = self._extract_with_regex(text)
        if regex_extracted:
            logger.info("✅ Extracted with regex strategy")
            return regex_extracted
        
        logger.error("❌ All extraction strategies failed")
        return None
    
    def _is_valid_json(self, text: str) -> bool:
        """Check if text is valid JSON"""
        try:
            json.loads(text)
            return True
        except:
            return False
    
    def _try_balance_json(self, text: str) -> Optional[str]:
        """Try to balance unbalanced JSON"""
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        # Already balanced
        if open_braces == close_braces and open_brackets == close_brackets:
            return None
        
        balanced = text
        
        # Add missing closing brackets
        if open_brackets > close_brackets:
            balanced += ']' * (open_brackets - close_brackets)
        
        # Add missing closing braces
        if open_braces > close_braces:
            balanced += '}' * (open_braces - close_braces)
        
        return balanced if self._is_valid_json(balanced) else None
    
    def _extract_with_stack(self, text: str) -> Optional[str]:
        """Extract JSON using stack-based bracket matching"""
        candidates = []
                
        for i in range(len(text)):
            if text[i] == '{':
                stack = ['{']
                start = i
                
                for j in range(i + 1, len(text)):
                    if text[j] == '{':
                        stack.append('{')
                    elif text[j] == '}':
                        if stack:
                            stack.pop()
                            if not stack:  # Complete object found
                                candidate = text[start:j+1]
                                if self._is_valid_json(candidate):
                                    candidates.append((len(candidate), candidate))
                                break
                    
                    if j - start > 50000:  # Safety limit
                        break
        
        # Return longest valid candidate
        if candidates:
            candidates.sort(reverse=True, key=lambda x: x[0])
            return candidates[0][1]
        
        return None
    
    def _extract_with_regex(self, text: str) -> Optional[str]:
        """Extract JSON using regex patterns"""
        # Pattern 1: Find largest {...} block
        pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for match in sorted(matches, key=len, reverse=True):
            if self._is_valid_json(match):
                return match
        
        # Pattern 2: Simple first to last delimiter
        first = text.find('{')
        last = text.rfind('}')
        
        if first >= 0 and last > first:
            candidate = text[first:last+1]
            if self._is_valid_json(candidate):
                return candidate
        
        return None
    
    # ═══════════════════════════════════════════════════════════════════
    # FORMAT NORMALIZATION
    # ═══════════════════════════════════════════════════════════════════
    
    def _normalize_triage_format(self, raw_data: Dict) -> Dict:
        """
        Normalize different LLM response formats to standard format
        
        Handles:
        - WatsonX format: {"decisions": [...]}
        - OpenAI format: {"analysis": [...]}
        - Direct list format: [...]
        """
        # Case 1: Already standard format with "decisions"
        if "decisions" in raw_data and isinstance(raw_data["decisions"], list):
            # Normalize each decision
            normalized_decisions = []
            for dec in raw_data["decisions"]:
                normalized_dec = {
                    "vulnerability_id": dec.get("vulnerability_id", dec.get("id", "unknown")),
                    "decision": dec.get("decision", "needs_manual_review"),
                    "confidence_score": float(dec.get("confidence_score", dec.get("confidence", 0.5))),
                    "reasoning": dec.get("reasoning", "No reasoning provided")
                }
                normalized_decisions.append(normalized_dec)
            
            return {
                "decisions": normalized_decisions,
                "analysis_summary": raw_data.get("analysis_summary", "Analysis completed"),
                "llm_analysis_time_seconds": float(raw_data.get("llm_analysis_time_seconds", 0.0))
            }
        
        # Case 2: OpenAI/alternative format with "analysis"
        if "analysis" in raw_data and isinstance(raw_data["analysis"], list):
            logger.info("🔄 Converting 'analysis' format to 'decisions'")
            normalized_decisions = []
            
            for item in raw_data["analysis"]:
                # Convert is_false_positive to decision
                is_fp = item.get("is_false_positive", False)
                if is_fp:
                    decision = "false_positive"
                else:
                    decision = "confirmed"
                
                normalized_dec = {
                    "vulnerability_id": item.get("id", "unknown"),
                    "decision": decision,
                    "confidence_score": float(item.get("confidence", 0.5)),
                    "reasoning": item.get("reasoning", "No reasoning provided")
                }
                normalized_decisions.append(normalized_dec)
            
            return {
                "decisions": normalized_decisions,
                "analysis_summary": raw_data.get("summary", "Analysis completed"),
                "llm_analysis_time_seconds": 0.0
            }
        
        # Case 3: Direct list format
        if isinstance(raw_data, list):
            logger.info("🔄 Converting list format to 'decisions'")
            normalized_decisions = []
            
            for item in raw_data:
                if isinstance(item, dict):
                    normalized_dec = {
                        "vulnerability_id": item.get("vulnerability_id", item.get("id", "unknown")),
                        "decision": item.get("decision", "needs_manual_review"),
                        "confidence_score": float(item.get("confidence_score", 0.5)),
                        "reasoning": item.get("reasoning", "No reasoning")
                    }
                    normalized_decisions.append(normalized_dec)
            
            return {
                "decisions": normalized_decisions,
                "analysis_summary": "Analysis completed",
                "llm_analysis_time_seconds": 0.0
            }
        
        # Case 4: Unknown format - raise error
        raise LLMError(
            f"Unknown triage response format. "
            f"Available keys: {list(raw_data.keys()) if isinstance(raw_data, dict) else 'not a dict'}"
        )
    
    # ═══════════════════════════════════════════════════════════════════
    # CONVERSION TO DOMAIN MODELS
    # ═══════════════════════════════════════════════════════════════════
    
    def _convert_to_triage_result(self, raw_response: TriageResponseRaw) -> TriageResult:
        """Convert Pydantic raw response to domain TriageResult"""
        decisions = []
        
        for raw_dec in raw_response.decisions:
            # Map decision string to AnalysisStatus enum
            decision_map = {
                'confirmed': AnalysisStatus.CONFIRMED,
                'false_positive': AnalysisStatus.FALSE_POSITIVE,
                'needs_manual_review': AnalysisStatus.NEEDS_MANUAL_REVIEW
            }
            
            decision_status = decision_map.get(
                raw_dec.decision.lower(),
                AnalysisStatus.NEEDS_MANUAL_REVIEW
            )
            
            # Create domain TriageDecision
            decision = TriageDecision(
                vulnerability_id=raw_dec.vulnerability_id,
                decision=decision_status,
                confidence_score=raw_dec.confidence_score,
                reasoning=raw_dec.reasoning,
                llm_model_used=self.model_name
            )
            
            decisions.append(decision)
        
        # Create TriageResult
        return TriageResult(
            decisions=decisions,
            analysis_summary=raw_response.analysis_summary or "Analysis completed",
            llm_analysis_time_seconds=raw_response.llm_analysis_time_seconds
        )
    
    def _convert_to_remediation_plan(
        self,
        raw_plan: RemediationPlanRaw,
        vuln_type: str
    ) -> RemediationPlan:
        """Convert Pydantic raw plan to domain RemediationPlan"""
        
        # Convert steps
        steps = []
        for raw_step in raw_plan.steps:
            step = RemediationStep(
                step_number=raw_step.step_number,
                title=raw_step.title,
                description=raw_step.description,
                code_example=raw_step.code_example,
                estimated_minutes=raw_step.estimated_minutes,
                difficulty=raw_step.difficulty,
                tools_required=raw_step.tools_required
            )
            steps.append(step)
        
        # Determine VulnerabilityType
        vuln_type_enum = self._parse_vulnerability_type(raw_plan.vulnerability_type or vuln_type)
        
        # Create RemediationPlan
        return RemediationPlan(
            vulnerability_id=raw_plan.vulnerability_id,
            vulnerability_type=vuln_type_enum,
            priority_level=raw_plan.priority_level,
            complexity_score=raw_plan.complexity_score,
            steps=steps,
            risk_if_not_fixed=raw_plan.risk_if_not_fixed,
            references=raw_plan.references,
            llm_model_used=raw_plan.llm_model_used
        )
    
    def _parse_vulnerability_type(self, type_str: str) -> VulnerabilityType:
        """Parse vulnerability type string to enum"""
        type_lower = type_str.lower()
        
        mappings = {
            'sql injection': VulnerabilityType.SQL_INJECTION,
            'sql': VulnerabilityType.SQL_INJECTION,
            'xss': VulnerabilityType.XSS,
            'cross-site scripting': VulnerabilityType.XSS,
            'path traversal': VulnerabilityType.PATH_TRAVERSAL,
            'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
            'code injection': VulnerabilityType.CODE_INJECTION,
            'command injection': VulnerabilityType.CODE_INJECTION,
            'auth': VulnerabilityType.AUTH_BYPASS,
            'authentication': VulnerabilityType.AUTH_BYPASS,
            'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
            'access control': VulnerabilityType.BROKEN_ACCESS_CONTROL,
            'crypto': VulnerabilityType.INSECURE_CRYPTO,
            'encryption': VulnerabilityType.INSECURE_CRYPTO,
            'sensitive data': VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
            'data exposure': VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
            'misconfiguration': VulnerabilityType.SECURITY_MISCONFIGURATION
        }
        
        for key, vuln_type in mappings.items():
            if key in type_lower:
                return vuln_type
        
        return VulnerabilityType.OTHER
    
    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════════
    
    def _validate_triage_completeness(
        self,
        result: TriageResult,
        original_data: str
    ) -> None:
        """
        Validate that all vulnerabilities were analyzed
        
        Adds conservative decisions for missing vulnerabilities
        """
        # Extract IDs from original data
        original_ids = self._extract_vulnerability_ids(original_data)
        
        if not original_ids:
            logger.warning("⚠️ Could not extract vulnerability IDs from original data")
            return
        
        # Get analyzed IDs
        analyzed_ids = {d.vulnerability_id for d in result.decisions}
        
        # Find missing
        missing_ids = original_ids - analyzed_ids
        
        if missing_ids:
            logger.warning(f"⚠️ LLM missed {len(missing_ids)} vulnerabilities")
            
            # Add conservative decisions for missing
            for missing_id in missing_ids:
                conservative_decision = TriageDecision(
                    vulnerability_id=missing_id,
                    decision=AnalysisStatus.NEEDS_MANUAL_REVIEW,
                    confidence_score=0.5,
                    reasoning="Conservative fallback: Not analyzed by LLM",
                    llm_model_used="fallback"
                )
                result.decisions.append(conservative_decision)
            
            logger.info(f"✅ Added {len(missing_ids)} conservative decisions")
    
    def _extract_vulnerability_ids(self, original_data: str) -> set:
        """Extract vulnerability IDs from original data string"""
        ids = set()
        
        # Pattern 1: "ID: xxx"
        pattern1 = r'(?:ID|id):\s*([A-Za-z0-9_-]+)'
        matches = re.findall(pattern1, original_data)
        ids.update(matches)
        
        # Pattern 2: "vulnerability_id": "xxx"
        pattern2 = r'"(?:vulnerability_id|id)":\s*"([^"]+)"'
        matches = re.findall(pattern2, original_data)
        ids.update(matches)
        
        return ids