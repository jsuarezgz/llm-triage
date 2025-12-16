# core/services/triage.py
"""
Triage Service - Simplified
===========================

Responsibilities:
- Orchestrate vulnerability triage
- Handle chunked analysis
- Create conservative fallbacks
"""

import logging
import asyncio
from typing import List, Optional

from ..models import Vulnerability, TriageResult, TriageDecision, AnalysisStatus
from ..exceptions import LLMError
from infrastructure.llm.client import LLMClient
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class TriageService:
    """Simplified triage service with clean dependencies"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        metrics: Optional[MetricsCollector] = None
    ):
        self.llm_client = llm_client
        self.metrics = metrics
    
    async def analyze_vulnerabilities(
        self,
        vulnerabilities: List[Vulnerability],
        language: Optional[str] = None,
        chunk_id: Optional[int] = None
    ) -> TriageResult:
        """
        Analyze vulnerabilities with LLM triage
        
        Args:
            vulnerabilities: List of vulnerabilities to analyze
            language: Programming language
            chunk_id: Optional chunk identifier
        
        Returns:
            TriageResult with decisions
        """
        # Handle empty list
        if not vulnerabilities:
            return self._create_empty_result()
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🔍 Analyzing {len(vulnerabilities)} vulnerabilities")
            
            # Prepare request
            request = self._prepare_request(vulnerabilities, language, chunk_id)
            
            # Get LLM analysis
            llm_response = await self.llm_client.analyze_vulnerabilities(
                request, language
            )
            
            # Validate and complete result
            validated = self._validate_result(llm_response, vulnerabilities)
            
            # Record metrics
            analysis_time = asyncio.get_event_loop().time() - start_time
            if self.metrics:
                self.metrics.record_triage_analysis(
                    len(vulnerabilities), analysis_time, True, chunk_id
                )
            
            logger.info(f"✅ Triage complete: {validated.confirmed_count} confirmed")
            return validated
            
        except Exception as e:
            analysis_time = asyncio.get_event_loop().time() - start_time
            if self.metrics:
                self.metrics.record_triage_analysis(
                    len(vulnerabilities), analysis_time, False, chunk_id, str(e)
                )
            
            logger.error(f"❌ Triage failed: {e}")
            return self._create_fallback_result(vulnerabilities, str(e))
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    def _prepare_request(
        self,
        vulnerabilities: List[Vulnerability],
        language: Optional[str],
        chunk_id: Optional[int]
    ) -> str:
        """Prepare structured analysis request"""
        header = f"# VULNERABILITY TRIAGE REQUEST\n"
        if chunk_id:
            header += f"Chunk ID: {chunk_id}\n"
        header += f"Language: {language or 'Unknown'}\n"
        header += f"Total: {len(vulnerabilities)}\n\n"
        
        vuln_blocks = []
        for i, vuln in enumerate(vulnerabilities, 1):
            block = f"""## VULNERABILITY {i}
- ID: {vuln.id}
- TYPE: {vuln.type.value}
- SEVERITY: {vuln.severity.value}
- FILE: {vuln.file_path}:{vuln.line_number}
- TITLE: {vuln.title}
- DESCRIPTION: {vuln.description}"""
            
            if vuln.code_snippet:
                snippet = vuln.code_snippet[:300]
                block += f"\n- CODE: {snippet}"
            
            if vuln.cwe_id:
                block += f"\n- CWE: {vuln.cwe_id}"
            
            vuln_blocks.append(block)
        
        return header + "\n\n".join(vuln_blocks)
    
    def _validate_result(
        self,
        llm_result: TriageResult,
        original_vulns: List[Vulnerability]
    ) -> TriageResult:
        """Validate and complete LLM result"""
        original_ids = {v.id for v in original_vulns}
        analyzed_ids = {d.vulnerability_id for d in llm_result.decisions}
        
        # Find missing vulnerabilities
        missing_ids = original_ids - analyzed_ids
        
        if missing_ids:
            logger.warning(f"⚠️  LLM missed {len(missing_ids)} vulnerabilities")
            
            # Add conservative decisions for missing
            for missing_id in missing_ids:
                vuln = next(v for v in original_vulns if v.id == missing_id)
                conservative = self._create_conservative_decision(vuln)
                llm_result.decisions.append(conservative)
        
        return llm_result
    
    def _create_conservative_decision(
        self,
        vulnerability: Vulnerability
    ) -> TriageDecision:
        """Create conservative decision for unanalyzed vulnerability"""
        # High severity = confirmed, others = review
        if vulnerability.is_high_priority:
            decision = AnalysisStatus.CONFIRMED
            confidence = 0.7
            reasoning = f"Conservative: {vulnerability.severity.value} assumed confirmed"
        else:
            decision = AnalysisStatus.NEEDS_MANUAL_REVIEW
            confidence = 0.5
            reasoning = "Conservative: requires manual review"
        
        return TriageDecision(
            vulnerability_id=vulnerability.id,
            decision=decision,
            confidence_score=confidence,
            reasoning=reasoning,
            llm_model_used="conservative_fallback"
        )
    
    def _create_fallback_result(
        self,
        vulnerabilities: List[Vulnerability],
        error: str
    ) -> TriageResult:
        """Create fallback result when LLM fails"""
        logger.warning("⚠️  Creating conservative fallback result")
        
        decisions = [
            self._create_conservative_decision(vuln)
            for vuln in vulnerabilities
        ]
        
        return TriageResult(
            decisions=decisions,
            analysis_summary=f"Conservative fallback due to LLM error: {error}",
            llm_analysis_time_seconds=0.0
        )
    
    def _create_empty_result(self) -> TriageResult:
        """Create empty result for no vulnerabilities"""
        return TriageResult(
            decisions=[],
            analysis_summary="No vulnerabilities to analyze",
            llm_analysis_time_seconds=0.0
        )
