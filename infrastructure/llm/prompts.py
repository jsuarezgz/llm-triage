# infrastructure/llm/prompts.py
"""
Prompt Management - Optimized
=============================

Responsibilities:
- Manage LLM prompts
- Provide language-specific guidance
- Ensure consistent prompt structure
"""

from typing import Optional


class PromptManager:
    """Centralized prompt management"""
    
    def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
        """
        Get system prompt for vulnerability triage
        
        Args:
            language: Programming language (optional)
        
        Returns:
            Formatted system prompt
        """
        model_name = "meta-llama/llama-3-3-70b-instruct"
        
        return f"""You are a cybersecurity expert specializing in vulnerability analysis.

TASK: Analyze vulnerabilities and classify each as:
- "confirmed": Real security vulnerability requiring fixing
- "false_positive": Scanner false alarm, not a real issue  
- "needs_manual_review": Uncertain, needs human expert review

CONTEXT: Language/Technology: {language or 'Unknown'}

OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
{{
  "decisions": [
    {{
      "vulnerability_id": "vuln_id_here",
      "decision": "confirmed|false_positive|needs_manual_review",
      "confidence_score": 0.0-1.0,
      "reasoning": "Brief technical explanation",
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
    
    def get_remediation_system_prompt(
        self,
        vuln_type: str,
        language: Optional[str] = None,
        severity: str = "HIGH"
    ) -> str:
        """
        Get system prompt for remediation plan generation
        
        Args:
            vuln_type: Vulnerability type
            language: Programming language (optional)
            severity: Severity level
        
        Returns:
            Formatted system prompt
        """
        lang_guide = self._get_language_guide(language)
        model_name = "meta-llama/llama-3-3-70b-instruct"
        
        return f"""You are a senior security engineer creating DETAILED remediation plans.

# CONTEXT
- Vulnerability: {vuln_type}
- Language: {language or 'Generic'}
- Severity: {severity}
- Target: Mid-level developers (3-5 years experience)

# REQUIREMENTS

Each step MUST include:

1. **Specific Title**: Action-oriented (verb + specific action)
   ❌ BAD: "Implement security fix"
   ✅ GOOD: "Replace string concatenation with parameterized queries"

2. **Detailed Description**: WHY this prevents the vulnerability (100+ words)
   - Security principle
   - How vulnerability is exploited
   - How fix prevents exploitation
   - Edge cases handled

3. **Complete Code Example**: BEFORE and AFTER
   - BEFORE: Exact vulnerable code (5-10 lines)
   - AFTER: Complete working fix (10-20 lines)
   - Include error handling
   - Add inline security comments

4. **Concrete Validation**: Specific test
   ❌ BAD: "Test that it works"
   ✅ GOOD: "Test with input='../../etc/passwd', verify error 'Invalid filename'"

# OUTPUT FORMAT (STRICT JSON)

{{
  "vulnerability_id": "exact_id_from_input",
  "vulnerability_type": "{vuln_type}",
  "priority_level": "immediate|high|medium|low",
  "complexity_score": 6.5,
  
  "steps": [
    {{
      "step_number": 1,
      "title": "Action title",
      "description": "Detailed explanation (min 100 words)",
      "code_example": "BEFORE:\\n...\\n\\nAFTER:\\n...",
      "estimated_minutes": 30,
      "difficulty": "easy|medium|hard",
      "tools_required": ["Tool name"]
    }}
  ],
  
  "risk_if_not_fixed": "Concrete impact with CVE example",
  "references": ["https://owasp.org/...", "https://cwe.mitre.org/..."],
  "llm_model_used": "{model_name}"
}}

{lang_guide}

# QUALITY CHECKS

Before responding, verify:
- [ ] Each step has BEFORE and AFTER code
- [ ] Each AFTER code is COMPLETE (copy-paste ready)
- [ ] Each description is 100+ words
- [ ] Validation tests have exact inputs/outputs
- [ ] No generic phrases like "implement security"
- [ ] Risk mentions specific CVE or real breach
- [ ] All code includes error handling

Now generate the remediation plan:"""
    
    def _get_language_guide(self, language: Optional[str]) -> str:
        """Get language-specific remediation guidance"""
        if not language:
            return ""
        
        lang = language.lower()
        
        guides = {
            'abap': """
## ABAP-SPECIFIC PATTERNS

### Directory Traversal Prevention:
1. Use logical filenames (transaction FILE)
2. Validate with FILE_VALIDATE_NAME and FILE_GET_NAME
3. Character validation: `IF filename CA '/..\\\\':\\x00'. "Block"`
4. Authorization: AUTHORITY-CHECK OBJECT 'S_DATASET'
5. Logging: Use BAL_LOG_CREATE and BAL_LOG_MSG_ADD

### SQL Injection Prevention:
1. NEVER use dynamic WHERE with concatenation
2. Use host variables: SELECT * WHERE username = @lv_username
3. Use SELECT-OPTIONS for dynamic queries

### Best Practices:
- Always check sy-subrc after function calls
- Use MESSAGE TYPE 'E' for security failures
- Log security events to application log (BAL)
- Run Code Vulnerability Analyzer (CVA)
""",
            
            'python': """
## PYTHON-SPECIFIC PATTERNS

### Path Traversal Prevention:
1. Use pathlib.Path.resolve() with is_relative_to()
2. Use secure_filename() from werkzeug
3. Validate: `^[a-zA-Z0-9_-]+\\.[a-z]{2,4}$`

### SQL Injection Prevention:
1. Django ORM: Use .filter(), never .raw() with f-strings
2. SQLAlchemy: Use bound parameters with text()
3. Always use parameterized queries

### Best Practices:
- Use framework auto-escaping for XSS
- Validate inputs with Pydantic
- Use environment variables for secrets
""",
            
            'java': """
## JAVA-SPECIFIC PATTERNS

### SQL Injection Prevention:
1. Always use PreparedStatement (never Statement)
2. JPA: Use named parameters (:name syntax)
3. Hibernate: Avoid native queries with concatenation

### Path Traversal Prevention:
1. Use Path.resolve() with startsWith() check
2. Normalize paths before validation
3. Check canonical path stays within base directory

### Best Practices:
- Disable XXE with DocumentBuilderFactory
- Use @PreAuthorize for method-level security
- Enable CSRF protection in Spring Security
"""
        }
        
        return guides.get(lang, "")
