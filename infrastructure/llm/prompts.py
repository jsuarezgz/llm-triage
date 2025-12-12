# infrastructure/llm/prompts.py

from typing import Optional

class PromptManager:
    """Gestión centralizada y optimizada de prompts"""
    
    def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
        """System prompt optimizado para triaje"""
        return f"""You are a cybersecurity expert specializing in vulnerability analysis.

TASK: Analyze the provided vulnerabilities and classify each one as:
- "confirmed": Real security vulnerability that needs fixing
- "false_positive": Scanner false alarm, not a real issue  
- "needs_manual_review": Uncertain case requiring human expert review

CONTEXT: Language/Technology: {language or 'Unknown'}

OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
{{
  "decisions": [
    {{
      "vulnerability_id": "vuln_id_here",
      "decision": "confirmed|false_positive|needs_manual_review",
      "confidence_score": 0.0-1.0,
      "reasoning": "Brief technical explanation of your decision",
      "llm_model_used": "{self._get_model_name()}"
    }}
  ],
  "analysis_summary": "Overall analysis summary",
  "llm_analysis_time_seconds": 1.5
}}

GUIDELINES:
- Be conservative: when uncertain, choose "needs_manual_review"
- Consider code context, severity, and vulnerability type
- Provide clear, technical reasoning
- Focus on actual exploitability, not theoretical risks"""

    def get_remediation_system_prompt(self, vuln_type: str, language: Optional[str] = None) -> str:
        """System prompt optimizado para remediación"""
        return f"""You are a senior security engineer creating actionable remediation plans.

TASK: Create a detailed, step-by-step remediation plan for {vuln_type} vulnerabilities.

CONTEXT: 
- Vulnerability Type: {vuln_type}
- Language/Technology: {language or 'Unknown'}

OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
{{
  "vulnerability_id": "vuln_id",
  "vulnerability_type": "{vuln_type}",
  "priority_level": "immediate|high|medium|low",
  "steps": [
    {{
      "step_number": 1,
      "title": "Descriptive step title",
      "description": "Clear, actionable description of what to do",
      "code_example": "Concrete code example if applicable",
      "estimated_minutes": 30,
      "difficulty": "easy|medium|hard",
      "tools_required": ["tool1", "tool2"]
    }}
  ],
  "risk_if_not_fixed": "Clear explanation of the security risk",
  "references": ["https://owasp.org/relevant-reference"],
  "total_estimated_hours": 2.0,
  "complexity_score": 1.0-10.0,
  "llm_model_used": "{self._get_model_name()}"
}}

REQUIREMENTS:
- Provide 3-5 specific, actionable steps
- Include code examples when relevant
- Focus on practical implementation
- Consider the specific technology stack
- Prioritize based on severity and impact"""

    def _get_model_name(self) -> str:
        """Get current model name for tracking"""
        return "gpt-4"  # This could be dynamic based on actual provider
