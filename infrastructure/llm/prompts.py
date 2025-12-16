# infrastructure/llm/prompts.py
from typing import Optional

class PromptManager:
    """Gestión centralizada y optimizada de prompts"""
    
    def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
        """System prompt optimizado para triaje"""
        model_name = self._get_model_name()
        
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
      "llm_model_used": "{model_name}"
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


    def get_remediation_system_prompt(self, vuln_type: str, 
                                     language: Optional[str] = None,
                                     severity: str = "HIGH") -> str:
        """Sistema prompt mejorado para remediation - ACCIONABLE Y DETALLADO"""
        
        lang_guide = self._get_language_specific_remediation_guide(language)
        model_name = self._get_model_name()
        lang_or_generic = language or 'generic'
        
        return f"""You are a senior security engineer creating DETAILED, STEP-BY-STEP remediation plans that developers can implement immediately WITHOUT consulting additional documentation.

# CONTEXT
- Vulnerability Type: {vuln_type}
- Programming Language: {language or 'Not specified'}
- Severity Level: {severity}
- Target Audience: Mid-level developers (3-5 years experience)
- Expected Outcome: Production-ready secure code

# CRITICAL REQUIREMENTS FOR EACH STEP

Each remediation step MUST include:

1. **Specific Title**: What exactly to do
   ❌ BAD: "Implement security fix"
   ✅ GOOD: "Replace string concatenation with FILE_VALIDATE_NAME function"

2. **Detailed Description**: WHY this prevents the vulnerability (minimum 100 words)
   - Explain the security principle
   - Explain how the vulnerability is exploited
   - Explain how this fix prevents exploitation
   - Include edge cases handled

3. **Complete Code Example**: BOTH vulnerable and fixed code
   - BEFORE: Exact code showing the vulnerability (5-10 lines with context)
   - AFTER: Complete working code with the fix (10-20 lines)
   - Include ALL necessary declarations
   - Include error handling and validation
   - Add inline comments explaining security improvements

4. **Concrete Validation Test**: Specific test to verify the fix
   ❌ BAD: "Test that it works"
   ✅ GOOD: "Test with input='../../etc/passwd' and verify error 'Invalid filename' with return code 4"

5. **Tools & Prerequisites**: What's needed to implement
   - Specific versions if relevant
   - Configuration requirements
   - Permissions needed

# OUTPUT FORMAT (STRICT JSON)


Return ONLY valid JSON (no markdown, no code block wrapper):
{{
  "vulnerability_id": "exact_id_from_input",
  "vulnerability_type": "{vuln_type}",
  "priority_level": "immediate|high|medium|low",
  
  "complexity_score": 6.5,
  /* Complexity from 0.0 (trivial) to 10.0 (very complex) */
  
  "steps": [
    {{
      "step_number": 1,
      "title": "Action-oriented title (verb + specific action)",
      "description": "Detailed explanation (minimum 100 words) covering: What (specific change), Why (security principle), How (implementation), Edge cases handled",
      "code_example": "Complete code showing BEFORE and AFTER with inline security comments",
      "validation_test": "SPECIFIC TEST: Input 'malicious_value' → Expected: 'error_message'",
      "estimated_minutes": 30,
      "difficulty": "easy|medium|hard",
      "tools_required": ["Tool name version X.Y"],
      "prerequisites": ["Required permission or configuration"]
    }}
  ],
  
  "verification_checklist": [
    "✓ Specific verification item with measurable criteria"
  ],
  
  "risk_if_not_fixed": "CONCRETE IMPACT: Attack scenario, data at risk, business impact, compliance violations, real CVE example, CVSS score",
  
  "common_mistakes": [
    "❌ Specific mistake with explanation why it fails and correct approach"
  ],
  
  "security_testing": {{
    "unit_tests": "Copy-paste test code with expected results",
    "integration_tests": "Step-by-step test procedure",
    "penetration_tests": "Specific payloads with expected blocking behavior"
  }},
  
  "references": [
    "https://owasp.org/specific-page",
    "https://cwe.mitre.org/data/definitions/[number].html"
  ],
  
  "llm_model_used": "{model_name}",
  
  "dependencies": [
    "Specific library name==version or configuration requirement"
  ],
  
  "rollback_plan": "DETAILED ROLLBACK: Backup steps, monitoring metrics, rollback triggers, rollback procedure, time limit"
}}

# LANGUAGE-SPECIFIC GUIDANCE

{lang_guide}

# QUALITY CHECKS BEFORE RESPONDING

Before sending your response, verify:
- [ ] Each step has code example with BOTH before AND after
- [ ] Each "after" code is COMPLETE (can copy-paste and run)
- [ ] Each step description has at least 100 words
- [ ] Validation tests are SPECIFIC with exact inputs and expected outputs
- [ ] No generic phrases like "implement security" or "add validation"
- [ ] Risk section mentions specific CVE or real breach example
- [ ] All code includes error handling
- [ ] Prerequisites list exact requirements

Now analyze the vulnerability data below and create a comprehensive remediation plan following this template:"""

    def _get_language_specific_remediation_guide(self, language: Optional[str]) -> str:
        """Retorna guía detallada específica del lenguaje"""
        
        if not language:
            return ""
        
        lang_lower = language.lower()
        
        if 'abap' in lang_lower:
            return """
## ABAP-SPECIFIC REMEDIATION PATTERNS

### Directory Traversal Prevention:
1. **Use logical filenames** (transaction FILE)
2. **Validate with FILE_VALIDATE_NAME and FILE_GET_NAME**
3. **Character validation:** `IF filename CA '/..\\\\':\\x00'. " Block`
4. **Authorization check:** AUTHORITY-CHECK OBJECT 'S_DATASET' ID 'ACTVT' FIELD '34'
5. **Security logging:** Use BAL_LOG_CREATE and BAL_LOG_MSG_ADD

### SQL Injection Prevention:
1. **NEVER use dynamic WHERE with concatenation**
2. **Use host variables:** SELECT * WHERE username = @lv_username
3. **Use SELECT-OPTIONS** for complex dynamic queries

### Best Practices:
- Always check sy-subrc after function calls
- Use MESSAGE TYPE 'E' for security failures
- Log all security events to application log (BAL)
- Run Code Vulnerability Analyzer (CVA) regularly
"""
        
        elif 'python' in lang_lower:
            return """
## PYTHON-SPECIFIC REMEDIATION PATTERNS

### Path Traversal Prevention:
1. **Use pathlib.Path.resolve()** with is_relative_to() check
2. **Use secure_filename()** from werkzeug
3. **Validate with regex:** `^[a-zA-Z0-9_-]+\\.[a-z]{2,4}$`

### SQL Injection Prevention:
1. **Django ORM:** Use .filter(), never .raw() with f-strings
2. **SQLAlchemy:** Use bound parameters with text()
3. **Flask-SQLAlchemy:** Use parameterized queries

### Best Practices:
- Use framework auto-escaping for XSS prevention
- Validate all user inputs with Pydantic or similar
- Use environment variables for secrets (never hardcode)
"""
        
        elif 'java' in lang_lower:
            return """
## JAVA-SPECIFIC REMEDIATION PATTERNS

### SQL Injection Prevention:
1. **Always use PreparedStatement** (never Statement)
2. **JPA:** Use named parameters (:name syntax)
3. **Hibernate:** Avoid native queries with concatenation

### Path Traversal Prevention:
1. **Use Path.resolve()** with startsWith() check
2. **Normalize paths** before validation
3. **Check canonical path** stays within base directory

### Best Practices:
- Disable XXE with DocumentBuilderFactory features
- Use @PreAuthorize for method-level security
- Enable CSRF protection in Spring Security
"""
        
        else:
            return ""
    
    def _get_model_name(self) -> str:
        """Get current model name for tracking"""
        return "meta-llama/llama-3-3-70b-instruct"
