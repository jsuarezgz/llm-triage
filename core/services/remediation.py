# core/services/remediation.py
"""
Remediation Service - Simplified
================================

Responsibilities:
- Generate remediation plans
- Prioritize plans
- Customize steps per vulnerability
"""

import logging
import asyncio
from typing import List, Optional, Dict
from collections import defaultdict

from ..models import (
    Vulnerability, RemediationPlan, RemediationStep, VulnerabilityType
)
from ..exceptions import LLMError
from infrastructure.llm.client import LLMClient
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class RemediationService:
    """Simplified remediation service"""
    
    def __init__(
        self,
        llm_client: LLMClient,
        metrics: Optional[MetricsCollector] = None
    ):
        self.llm_client = llm_client
        self.metrics = metrics
    
    async def generate_remediation_plans(
        self,
        vulnerabilities: List[Vulnerability],
        language: Optional[str] = None
    ) -> List[RemediationPlan]:
        """
        Generate remediation plans for confirmed vulnerabilities
        
        Args:
            vulnerabilities: List of confirmed vulnerabilities
            language: Programming language
        
        Returns:
            List of prioritized remediation plans
        """
        if not vulnerabilities:
            logger.info("No vulnerabilities - no plans needed")
            return []
        
        logger.info(f"🛠️  Generating plans for {len(vulnerabilities)} vulnerabilities")
        
        # Group by type for efficient batch processing
        grouped = self._group_by_type(vulnerabilities)
        
        all_plans = []
        for vuln_type, vulns in grouped.items():
            try:
                plans = await self._generate_for_type(vuln_type, vulns, language)
                all_plans.extend(plans)
            except Exception as e:
                logger.error(f"Failed to generate plans for {vuln_type}: {e}")
                # Add fallback plans
                fallback = self._create_fallback_plans(vulns)
                all_plans.extend(fallback)
        
        # Prioritize
        prioritized = self._prioritize_plans(all_plans)
        
        logger.info(f"✅ Generated {len(prioritized)} remediation plans")
        return prioritized
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    def _group_by_type(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> Dict[VulnerabilityType, List[Vulnerability]]:
        """Group vulnerabilities by type"""
        groups = defaultdict(list)
        for vuln in vulnerabilities:
            groups[vuln.type].append(vuln)
        return dict(groups)
    
    async def _generate_for_type(
        self,
        vuln_type: VulnerabilityType,
        vulnerabilities: List[Vulnerability],
        language: Optional[str]
    ) -> List[RemediationPlan]:
        """Generate plans for specific vulnerability type"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Prepare request
            request = self._prepare_request(vuln_type, vulnerabilities, language)
            
            # Get LLM response
            response = await self.llm_client.generate_remediation_plan(
                request, vuln_type.value, language
            )
            
            # Create individual plans from template
            plans = self._create_individual_plans(response, vulnerabilities)
            
            # Record metrics
            if self.metrics:
                generation_time = asyncio.get_event_loop().time() - start_time
                self.metrics.record_remediation_generation(
                    vuln_type.value, len(vulnerabilities), generation_time, True
                )
            
            return plans
            
        except Exception as e:
            if self.metrics:
                generation_time = asyncio.get_event_loop().time() - start_time
                self.metrics.record_remediation_generation(
                    vuln_type.value, len(vulnerabilities), generation_time, False, str(e)
                )
            raise
    
    def _prepare_request(
        self,
        vuln_type: VulnerabilityType,
        vulnerabilities: List[Vulnerability],
        language: Optional[str]
    ) -> str:
        """Prepare structured remediation request"""
        header = f"# REMEDIATION PLAN REQUEST\n"
        header += f"Type: {vuln_type.value}\n"
        header += f"Language: {language or 'Unknown'}\n"
        header += f"Count: {len(vulnerabilities)}\n\n"
        
        vuln_details = []
        for i, vuln in enumerate(vulnerabilities, 1):
            detail = f"""## VULNERABILITY {i} - {vuln.id}
- Severity: {vuln.severity.value}
- File: {vuln.file_path}:{vuln.line_number}
- Title: {vuln.title}
- Description: {vuln.description}"""
            
            if vuln.code_snippet:
                detail += f"\n- Code:\n{vuln.code_snippet[:500]}"
            
            vuln_details.append(detail)
        
        return header + "\n\n".join(vuln_details)
    
    def _create_individual_plans(
        self,
        template_plan: RemediationPlan,
        vulnerabilities: List[Vulnerability]
    ) -> List[RemediationPlan]:
        """Create individual plans from template"""
        plans = []
        
        for vuln in vulnerabilities:
            customized = RemediationPlan(
                vulnerability_id=vuln.id,
                vulnerability_type=vuln.type,
                priority_level=self._calculate_priority(vuln),
                steps=self._customize_steps(template_plan.steps, vuln),
                risk_if_not_fixed=template_plan.risk_if_not_fixed,
                references=template_plan.references,
                complexity_score=self._adjust_complexity(
                    template_plan.complexity_score, vuln
                ),
                llm_model_used=template_plan.llm_model_used
            )
            plans.append(customized)
        
        return plans
    
    def _calculate_priority(self, vuln: Vulnerability) -> str:
        """Calculate priority level"""
        priority_map = {
            "CRÍTICA": "immediate",
            "ALTA": "high",
            "MEDIA": "medium",
            "BAJA": "low",
            "INFO": "low"
        }
        return priority_map.get(vuln.severity.value, "medium")
    
    def _customize_steps(
        self,
        template_steps: List[RemediationStep],
        vulnerability: Vulnerability
    ) -> List[RemediationStep]:
        """Customize steps for specific vulnerability"""
        customized = []
        
        for step in template_steps:
            try:
                # Try to format with placeholders
                formatted_title = step.title.format(
                    file=vulnerability.file_path,
                    line=vulnerability.line_number,
                    vuln_type=vulnerability.type.value
                )
                formatted_desc = step.description.format(
                    vulnerability_id=vulnerability.id,
                    file_path=vulnerability.file_path,
                    severity=vulnerability.severity.value
                )
            except KeyError:
                # No placeholders, use original
                formatted_title = step.title
                formatted_desc = step.description
            
            customized_step = RemediationStep(
                step_number=step.step_number,
                title=formatted_title,
                description=formatted_desc,
                code_example=step.code_example,
                estimated_minutes=step.estimated_minutes,
                difficulty=step.difficulty,
                tools_required=step.tools_required
            )
            customized.append(customized_step)
        
        return customized
    
    def _adjust_complexity(
        self,
        base_complexity: float,
        vulnerability: Vulnerability
    ) -> float:
        """Adjust complexity based on vulnerability"""
        # Severity multipliers
        multipliers = {
            "CRÍTICA": 1.2,
            "ALTA": 1.1,
            "MEDIA": 1.0,
            "BAJA": 0.9,
            "INFO": 0.8
        }
        
        multiplier = multipliers.get(vulnerability.severity.value, 1.0)
        adjusted = base_complexity * multiplier
        
        # Clamp to 1-10 range
        return min(max(adjusted, 1.0), 10.0)
    
    def _create_fallback_plans(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> List[RemediationPlan]:
        """Create basic fallback plans when LLM fails"""
        logger.warning("⚠️  Creating fallback remediation plans")
        
        fallback_plans = []
        
        for vuln in vulnerabilities:
            basic_steps = [
                RemediationStep(
                    step_number=1,
                    title="Manual Security Review",
                    description=f"Review {vuln.type.value} in {vuln.file_path}",
                    estimated_minutes=30,
                    difficulty="medium"
                ),
                RemediationStep(
                    step_number=2,
                    title="Research Best Practices",
                    description=f"Research security best practices for {vuln.type.value}",
                    estimated_minutes=15,
                    difficulty="easy"
                ),
                RemediationStep(
                    step_number=3,
                    title="Implement Fix",
                    description="Apply appropriate security fix",
                    estimated_minutes=120,
                    difficulty="hard"
                ),
                RemediationStep(
                    step_number=4,
                    title="Validate Fix",
                    description="Test that vulnerability is fixed",
                    estimated_minutes=30,
                    difficulty="medium"
                )
            ]
            
            plan = RemediationPlan(
                vulnerability_id=vuln.id,
                vulnerability_type=vuln.type,
                priority_level=self._calculate_priority(vuln),
                steps=basic_steps,
                risk_if_not_fixed=f"Security risk: {vuln.type.value}",
                complexity_score=5.0,
                llm_model_used="fallback"
            )
            
            fallback_plans.append(plan)
        
        return fallback_plans
    
    def _prioritize_plans(
        self,
        plans: List[RemediationPlan]
    ) -> List[RemediationPlan]:
        """Sort plans by priority and complexity"""
        priority_weights = {
            "immediate": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        return sorted(
            plans,
            key=lambda p: (
                priority_weights.get(p.priority_level, 0),
                -p.complexity_score  # Lower complexity = higher priority
            ),
            reverse=True
        )
