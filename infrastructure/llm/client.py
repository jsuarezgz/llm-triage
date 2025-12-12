# infrastructure/llm/client.py
import requests
import json
import logging
import time
import os
import uuid
from typing import Dict, Any, Optional

from core.models import TriageResult, RemediationPlan, TriageDecision, AnalysisStatus, RemediationStep, VulnerabilityType
from core.exceptions import LLMError

logger = logging.getLogger(__name__)

class LLMClient:
    """Cliente LLM sin debug por defecto - debug solo cuando se active explícitamente"""
    
    def __init__(self, primary_provider: str = "watsonx", enable_debug: bool = False):
        self.api_key = os.getenv("RESEARCH_API_KEY", "")
        self.primary_provider = primary_provider
        self.base_url = "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
        self.timeout = 300  # 5 minutos
        self.user_email = "franciscojavier.suarez_css@research.com"
        
        # Debug solo si se habilita explícitamente
        self.debug_enabled = enable_debug
        self.debugger = None
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        })
        
        self.endpoints = {
            "watsonx": "/research/llm/wx/clients",
            "openai": "/research/llm/openai/clients"
        }
        
        logger.info(f"LLM Client initialized with {self.primary_provider} (Research API)")
        
        if not self.api_key:
            logger.warning("⚠️ RESEARCH_API_KEY no configurada - usando modo mock")
    
    def enable_debug_mode(self):
        """Habilitar modo debug - solo se llama desde el debugger"""
        self.debug_enabled = True
        try:
            from debug.llm_debugger import get_debugger
            self.debugger = get_debugger()
            logger.info("🔍 Debug mode enabled for LLM Client")
        except ImportError:
            logger.warning("Debug module not available")
            self.debug_enabled = False
    
    def disable_debug_mode(self):
        """Deshabilitar modo debug"""
        self.debug_enabled = False
        self.debugger = None
        logger.info("🔍 Debug mode disabled for LLM Client")
    
    async def analyze_vulnerabilities(self, vulnerabilities_data: str,
                                    language: Optional[str] = None) -> TriageResult:
        """Analyze vulnerabilities using Research API"""
        
        if not self.api_key:
            logger.warning("Using MOCK analysis - no API key configured")
            return self._create_mock_triage_result(vulnerabilities_data)
        
        try:
            # Preparar prompt de sistema para triage
            system_prompt = self._get_triage_system_prompt(language)
            
            # Llamar a Research API
            start_time = time.time()
            response = await self._call_research_api(
                message=f"{system_prompt}\n\nDATA TO ANALYZE:\n{vulnerabilities_data}",
                temperature=0.1
            )
            duration = time.time() - start_time
            
            # Log solo si debug está habilitado
            if self.debug_enabled and self.debugger:
                self.debugger.log_triage_analysis(
                    vulnerabilities_data=vulnerabilities_data,
                    system_prompt=system_prompt,
                    response=response,
                    duration=duration
                )
            
            # Parsear respuesta
            result = self._parse_triage_response(response, vulnerabilities_data)
            
            return result
            
        except Exception as e:
            logger.error(f"LLM triage analysis failed: {e}")
            return self._create_mock_triage_result(vulnerabilities_data)

    async def generate_remediation_plan(self, vulnerability_data: str,
                                      vuln_type: str = None, language: Optional[str] = None) -> RemediationPlan:
        """Generate remediation plan using Research API"""
        
        if not self.api_key:
            logger.warning("Using MOCK remediation - no API key configured")
            return self._create_mock_remediation_plan()
        
        try:
            # Preparar prompt de sistema para remediación
            system_prompt = self._get_remediation_system_prompt(vuln_type, language)
            
            # Llamar a Research API
            start_time = time.time()
            response = await self._call_research_api(
                message=f"{system_prompt}\n\nVULNERABILITY DATA:\n{vulnerability_data}",
                temperature=0.2
            )
            duration = time.time() - start_time
            
            # Log solo si debug está habilitado
            if self.debug_enabled and self.debugger:
                self.debugger.log_remediation_generation(
                    vulnerability_data=vulnerability_data,
                    system_prompt=system_prompt,
                    response=response,
                    duration=duration
                )
            
            # Parsear respuesta
            result = self._parse_remediation_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"LLM remediation generation failed: {e}")
            return self._create_mock_remediation_plan()

    async def _call_research_api(self, message: str, temperature: float = 0.1) -> str:
        """Call Research API - versión LIMPIA sin debug por defecto"""
        
        url = f"{self.base_url}{self.endpoints[self.primary_provider]}"
        session_uuid = str(uuid.uuid4())
        
        # Payload completo
        payload = {
            "message": {
                "role": "user",
                "content": message
            },
            "temperature": temperature,
            "model": "meta-llama/llama-3-3-70b-instruct" if self.primary_provider == "watsonx" else "gpt-4",
            "prompt": None,
            "uuid": session_uuid,
            "language": "es",
            "user": self.user_email
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"Calling Research API: {self.primary_provider}")
            
            # Hacer la llamada HTTP
            response = self.session.post(url, json=payload, timeout=self.timeout)
            duration = time.time() - start_time
            
            # Log HTTP solo si debug está habilitado
            if self.debug_enabled and self.debugger:
                try:
                    from debug.llm_debugger import log_http_details, log_research_api_call
                    
                    log_http_details(
                        url=url,
                        method="POST",
                        headers=dict(self.session.headers),
                        request_body=payload,
                        response_status=response.status_code,
                        response_headers=dict(response.headers),
                        response_body=response.text,
                        duration=duration
                    )
                except ImportError:
                    pass  # Debug module no disponible
            
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Research API error: {error_msg}")
                raise LLMError(f"Research API failed: {error_msg}")
            
            response_text = response.text
            
            # Intentar parsear como JSON
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = response_text
            
            # Extraer contenido de la respuesta
            if isinstance(result, dict):
                content = (result.get('content') or 
                          result.get('response') or 
                          result.get('message') or 
                          result.get('text') or 
                          result.get('output') or
                          str(result))
            else:
                content = str(result)
            
            # Log de Research API solo si debug está habilitado
            if self.debug_enabled and self.debugger:
                try:
                    from debug.llm_debugger import log_research_api_call
                    log_research_api_call(
                        url=url,
                        payload=payload,
                        response=content,
                        duration=duration
                    )
                except ImportError:
                    pass
            
            logger.info(f"Research API call successful - {duration:.2f}s")
            return content
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            error_msg = f"Research API timeout after {self.timeout} seconds"
            
            # Log del error solo si debug está habilitado
            if self.debug_enabled and self.debugger:
                try:
                    from debug.llm_debugger import log_http_details
                    log_http_details(
                        url=url,
                        method="POST", 
                        headers=dict(self.session.headers),
                        request_body=payload,
                        response_status=408,  # Timeout
                        response_headers={},
                        response_body=f"TIMEOUT: {error_msg}",
                        duration=duration
                    )
                except ImportError:
                    pass
            
            raise LLMError(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            error_msg = f"Research API connection error: {e}"
            
            if self.debug_enabled and self.debugger:
                try:
                    from debug.llm_debugger import log_http_details
                    log_http_details(
                        url=url,
                        method="POST",
                        headers=dict(self.session.headers),
                        request_body=payload,
                        response_status=0,  # Connection error
                        response_headers={},
                        response_body=f"CONNECTION ERROR: {error_msg}",
                        duration=duration
                    )
                except ImportError:
                    pass
            
            raise LLMError(error_msg)
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Research API unexpected error: {e}"
            
            if self.debug_enabled and self.debugger:
                try:
                    from debug.llm_debugger import log_http_details
                    log_http_details(
                        url=url,
                        method="POST",
                        headers=dict(self.session.headers),
                        request_body=payload,
                        response_status=-1,  # Unknown error
                        response_headers={},
                        response_body=f"UNEXPECTED ERROR: {error_msg}",
                        duration=duration
                    )
                except ImportError:
                    pass
            
            raise LLMError(error_msg)

    def _get_triage_system_prompt(self, language: Optional[str]) -> str:
        """System prompt for vulnerability triage"""
        return f"""You are a cybersecurity expert analyzing vulnerabilities from SAST tools.

TASK: Analyze each vulnerability and classify as:
- "confirmed": Real security issue needing fixes  
- "false_positive": Scanner false alarm
- "needs_manual_review": Uncertain case requiring human review

OUTPUT: Return ONLY valid JSON in this exact format:
{{
  "decisions": [
    {{
      "vulnerability_id": "vuln_id_here",
      "decision": "confirmed",
      "confidence_score": 0.8,
      "reasoning": "Brief technical explanation",
      "llm_model_used": "research_api"
    }}
  ],
  "analysis_summary": "Overall analysis summary",
  "llm_analysis_time_seconds": 1.5
}}

Language: {language or 'Spanish'}
Be conservative: when uncertain, choose "needs_manual_review"."""

    def _get_remediation_system_prompt(self, vuln_type: str, language: Optional[str]) -> str:
        """System prompt for remediation planning"""
        return f"""You are a senior security engineer creating remediation plans.

TASK: Create step-by-step remediation plan for {vuln_type or 'security'} vulnerabilities.

OUTPUT: Return ONLY valid JSON in this exact format:
{{
  "vulnerability_id": "vuln_id",
  "vulnerability_type": "{vuln_type or 'Other Security Issue'}",
  "priority_level": "high",
  "steps": [
    {{
      "step_number": 1,
      "title": "Step title",
      "description": "Detailed description",
      "code_example": null,
      "estimated_minutes": 30,
      "difficulty": "medium",
      "tools_required": []
    }}
  ],
  "risk_if_not_fixed": "Risk description",
  "references": [],
  "total_estimated_hours": 2.0,
  "complexity_score": 5.0,
  "llm_model_used": "research_api"
}}

Language: {language or 'Spanish'}"""

    def _parse_triage_response(self, llm_response: str, original_data: str) -> TriageResult:
        """Parse LLM response to TriageResult"""
        try:
            if isinstance(llm_response, str):
                response_data = json.loads(llm_response)
            else:
                response_data = llm_response
            
            return TriageResult(**response_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM triage response: {e}")
            return self._create_mock_triage_result(original_data)

    def _parse_remediation_response(self, llm_response: str) -> RemediationPlan:
        """Parse LLM response to RemediationPlan"""
        try:
            if isinstance(llm_response, str):
                response_data = json.loads(llm_response)
            else:
                response_data = llm_response
            
            return RemediationPlan(**response_data)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM remediation response: {e}")
            return self._create_mock_remediation_plan()

    def _create_mock_triage_result(self, vulnerabilities_data: str) -> TriageResult:
        """Create mock triage result for testing"""
        
        # Extraer IDs de vulnerabilidades
        import re
        vuln_ids = re.findall(r'ID:\s*([^\s\n]+)', vulnerabilities_data)
        
        decisions = []
        for i, vuln_id in enumerate(vuln_ids[:5]):  # Limitar a 5 para testing
            decision_types = [AnalysisStatus.CONFIRMED, AnalysisStatus.FALSE_POSITIVE, AnalysisStatus.NEEDS_MANUAL_REVIEW]
            decision = decision_types[i % len(decision_types)]
            
            decisions.append(TriageDecision(
                vulnerability_id=vuln_id,
                decision=decision,
                confidence_score=0.7,
                reasoning=f"Mock analysis for {vuln_id} - classified as {decision.value}",
                llm_model_used="mock_research_api"
            ))
        
        return TriageResult(
            decisions=decisions,
            analysis_summary=f"Mock Research API triage of {len(decisions)} vulnerabilities",
            llm_analysis_time_seconds=1.2
        )

    def _create_mock_remediation_plan(self) -> RemediationPlan:
        """Create mock remediation plan"""
        
        mock_steps = [
            RemediationStep(
                step_number=1,
                title="Identify and validate the security issue",
                description="Review the vulnerability details and confirm the security impact",
                estimated_minutes=30,
                difficulty="medium"
            ),
            RemediationStep(
                step_number=2,
                title="Implement security fix",
                description="Apply the appropriate security control or code change",
                estimated_minutes=120,
                difficulty="hard"
            ),
            RemediationStep(
                step_number=3,
                title="Test and validate fix",
                description="Verify the vulnerability has been properly addressed",
                estimated_minutes=30,
                difficulty="medium"
            )
        ]
        
        return RemediationPlan(
            vulnerability_id="mock_vuln",
            vulnerability_type=VulnerabilityType.OTHER,
            priority_level="medium",
            steps=mock_steps,
            risk_if_not_fixed="Security risk if not addressed - mock assessment",
            total_estimated_hours=3.0,
            complexity_score=5.0,
            llm_model_used="mock_research_api"
        )
