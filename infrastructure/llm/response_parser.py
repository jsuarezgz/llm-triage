# infrastructure/llm/response_parser.py
"""
LLM Response Parser - Fixed & Enhanced
======================================
"""

import json
import re
import logging
from typing import Optional, List, Any, Dict
import time

from core.models import TriageResult, RemediationPlan, VulnerabilityType
from core.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """Enhanced response parser with robust JSON extraction"""
    
    def __init__(self, debug_enabled: bool = False):
        self.debug_enabled = debug_enabled
    
    # ════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ════════════════════════════════════════════════════════════════
    
    def parse_triage_response(
        self,
        llm_response: str,
        original_data: str = None
    ) -> TriageResult:
        """Parse triage response to TriageResult"""
        logger.info(f"Parsing triage response ({len(llm_response):,} chars)")
        
        if self.debug_enabled:
            logger.debug(f"Raw response preview:\n{llm_response[:500]}...")
        
        # Clean and extract JSON
        cleaned = self._clean_and_extract(llm_response, required_fields=['decisions'])
        
        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            if self.debug_enabled:
                logger.error(f"JSON decode error: {e}")
                logger.debug(f"Cleaned JSON:\n{cleaned}")
            raise LLMError(f"Invalid JSON in triage response: {e}")
        
        # Validate fields
        self._validate_fields(data, ['decisions'], 'triage')
        
        # Create model (Pydantic validates)
        try:
            result = TriageResult(**data)
            logger.info(f"✅ Triage parsed: {result.total_analyzed} decisions")
            return result
        except Exception as e:
            raise LLMError(f"Invalid triage data: {e}")
    
    def parse_remediation_response(
        self,
        llm_response: str,
        vuln_type: str = None,
        language: str = None
    ) -> RemediationPlan:
        """Parse remediation response to RemediationPlan"""
        logger.info(f"Parsing remediation response ({len(llm_response):,} chars)")
        
        if self.debug_enabled:
            logger.debug(f"Raw response preview:\n{llm_response[:500]}...")
        
        # Clean and extract JSON
        cleaned = self._clean_and_extract(
            llm_response,
            required_fields=['vulnerability_type', 'priority_level', 'steps']
        )
        
        # Parse JSON
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            if self.debug_enabled:
                logger.error(f"JSON decode error: {e}")
                logger.debug(f"Cleaned JSON:\n{cleaned[:1000]}...")
            raise LLMError(f"Invalid JSON in remediation response: {e}")
        
        # Validate fields
        self._validate_fields(
            data,
            ['vulnerability_type', 'priority_level', 'steps'],
            'remediation'
        )
        
        # Normalize data
        data = self._normalize_remediation(data, vuln_type)
        
        # Create model
        try:
            result = RemediationPlan(**data)
            logger.info(f"✅ Remediation parsed: {len(result.steps)} steps")
            return result
        except Exception as e:
            raise LLMError(f"Invalid remediation data: {e}")
    
    # ════════════════════════════════════════════════════════════════
    # CLEANING & EXTRACTION
    # ════════════════════════════════════════════════════════════════
    
    def _clean_and_extract(
        self,
        response: str,
        required_fields: List[str] = None
    ) -> str:
        """
        Clean and extract valid JSON with multiple strategies
        """
        # Strategy 1: Remove markdown wrappers
        cleaned = self._remove_markdown(response)
        
        # Strategy 2: Try direct parse
        if self._is_valid_json(cleaned):
            return cleaned
        
        # Strategy 3: Aggressive extraction
        logger.warning("JSON structure invalid, trying extraction")
        extracted = self._extract_json_aggressive(cleaned, required_fields)
        
        if not extracted:
            if self.debug_enabled:
                logger.error(f"All extraction strategies failed")
                logger.debug(f"Cleaned text:\n{cleaned[:1000]}...")
            raise LLMError("Could not extract valid JSON from response")
        
        return extracted
    
    def _remove_markdown(self, text: str) -> str:
        """Remove markdown code blocks and prefixes"""
        text = text.strip()
        
        # Remove ```json ... ``` wrapper
        patterns = [
            r'^```(?:json)?\s*\n(.+?)\n```$',  # Standard markdown
            r'^```(?:json)?\s*(.+?)```$',       # Without newlines
            r'```(?:json)?\s*\n(.+?)\n```',     # In middle of text
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                text = match.group(1).strip()
                break
        
        # Remove leading markers
        prefixes_to_remove = [
            'json\n',
            'JSON\n',
            'L3##json\n',
            'L3##',
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].lstrip()
        
        # Remove trailing markers
        if text.endswith('```'):
            text = text[:-3].rstrip()
        
        return text.strip()
    
    def _is_valid_json(self, text: str) -> bool:
        """Quick validation using actual JSON parsing"""
        try:
            json.loads(text)
            return True
        except:
            return False
    
    def _extract_json_aggressive(
        self,
        text: str,
        required_fields: List[str] = None
    ) -> Optional[str]:
        """
        Aggressive JSON extraction with multiple strategies
        """
        strategies = [
            self._extract_balanced,
            self._extract_with_stack,
            self._extract_simple,
            self._extract_largest_object,
        ]
        
        for strategy in strategies:
            try:
                result = strategy(text, required_fields)
                if result:
                    logger.info(f"✅ Extracted with strategy: {strategy.__name__}")
                    return result
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {e}")
        
        return None
    
    def _extract_balanced(
        self,
        text: str,
        required_fields: List[str]
    ) -> Optional[str]:
        """Auto-balance unbalanced JSON"""
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        # Already balanced
        if open_braces == close_braces and open_brackets == close_brackets:
            return None
        
        balanced = text.strip()
        
        # Add missing closing brackets
        if open_brackets > close_brackets:
            balanced += ']' * (open_brackets - close_brackets)
        
        # Add missing closing braces
        if open_braces > close_braces:
            balanced += '}' * (open_braces - close_braces)
        
        # Validate
        try:
            parsed = json.loads(balanced)
            if self._has_fields(parsed, required_fields):
                return balanced
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _extract_with_stack(
        self,
        text: str,
        required_fields: List[str]
    ) -> Optional[str]:
        """Extract using stack-based bracket matching"""
        candidates = []
        
        for i in range(len(text)):
            if text[i] == '{':
                stack = ['{']
                start = i
                
                for j in range(i + 1, len(text)):
                    if text[j] == '{':
                        stack.append('{')
                    elif text[j] == '}':
                        stack.pop()
                        if not stack:  # Complete object
                            candidate = text[start:j+1]
                            try:
                                parsed = json.loads(candidate)
                                if self._has_fields(parsed, required_fields):
                                    candidates.append((len(candidate), candidate))
                            except json.JSONDecodeError:
                                pass
                            break
                    
                    if not stack:
                        break
        
        # Return longest valid candidate
        if candidates:
            candidates.sort(reverse=True, key=lambda x: x[0])
            return candidates[0][1]
        
        return None
    
    def _extract_simple(
        self,
        text: str,
        required_fields: List[str]
    ) -> Optional[str]:
        """Simple first/last delimiter extraction"""
        first = text.find('{')
        last = text.rfind('}')
        
        if first >= 0 and last > first:
            candidate = text[first:last+1]
            try:
                parsed = json.loads(candidate)
                if self._has_fields(parsed, required_fields):
                    return candidate
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _extract_largest_object(
        self,
        text: str,
        required_fields: List[str]
    ) -> Optional[str]:
        """Find the largest valid JSON object"""
        # Find all potential JSON objects
        potential_objects = []
        
        for i in range(len(text)):
            if text[i] == '{':
                for j in range(len(text) - 1, i, -1):
                    if text[j] == '}':
                        candidate = text[i:j+1]
                        try:
                            parsed = json.loads(candidate)
                            if self._has_fields(parsed, required_fields):
                                potential_objects.append((len(candidate), candidate))
                                break
                        except json.JSONDecodeError:
                            continue
        
        if potential_objects:
            potential_objects.sort(reverse=True, key=lambda x: x[0])
            return potential_objects[0][1]
        
        return None
    
    # ════════════════════════════════════════════════════════════════
    # VALIDATION & NORMALIZATION
    # ════════════════════════════════════════════════════════════════
    
    def _validate_fields(
        self,
        data: Dict,
        required: List[str],
        response_type: str
    ) -> None:
        """Validate required fields are present"""
        if not isinstance(data, dict):
            raise LLMError(f"{response_type} response is not a dict")
        
        missing = [f for f in required if f not in data]
        
        if missing:
            available = list(data.keys())
            raise LLMError(
                f"{response_type} missing fields: {missing}. "
                f"Available: {available}"
            )
    
    def _has_fields(self,data:  Any, required: List[str]) -> bool:
        """Check if data has required fields"""
        if not required:
            return True
        
        if not isinstance(data, dict):
            return False
        
        return all(field in data for field in required)
    
    def _normalize_remediation(
        self,
        data: Dict,
        vuln_type: str
    ) -> Dict:
        """Normalize remediation data"""
        # Add missing vulnerability_id
        if 'vulnerability_id' not in data:
            data['vulnerability_id'] = f"{vuln_type or 'unknown'}-{int(time.time())}"
        
        # Add missing llm_model_used
        if 'llm_model_used' not in data:
            data['llm_model_used'] = 'unknown'
        
        # Validate steps
        if not data.get('steps') or len(data['steps']) < 1:
            raise LLMError("No remediation steps in response")
        
        return data
