# infrastructure/llm/response_parser.py
"""
LLM Response Parser - Cleaning, validation and parsing of JSON responses

Features:
- Advanced cleaning with markdown wrappers
- Intelligent extraction with stack balancing
- Pre-parsing validation
- Parsing to Pydantic models
- Invalid escape correction
"""

import json
import re
import logging
import time
from typing import Dict, Any, Optional, List

from core.models import (
    TriageResult, 
    RemediationPlan, 
    TriageDecision, 
    AnalysisStatus, 
    RemediationStep, 
    VulnerabilityType
)
from core.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """
    Specialized parser for LLM responses
    
    Responsibilities:
    - Cleaning JSON with markdown/noise
    - JSON structure validation
    - Intelligent JSON extraction
    - Parsing to domain models (TriageResult, RemediationPlan)
    """
    
    def __init__(self, debug_enabled: bool = False):
        self.debug_enabled = debug_enabled
    
    
    # ============================================================================
    # PUBLIC API - PARSING METHODS
    # ============================================================================
    
    def parse_triage_response(self, llm_response: str, original_data: str = None) -> TriageResult:
        """
        Parse LLM response to TriageResult
        
        Args:
            llm_response: Raw LLM response
            original_ Original data (for context in errors)
            
        Returns:
            Validated TriageResult
            
        Raises:
            LLMError: If parsing fails after recovery attempts
        """
        
        logger.info(f"Parsing triage response ({len(llm_response):,} chars)...")
        
        try:
            # Step 1: Clean response
            cleaned = self.clean_json_response(llm_response)
            
            # Step 2: Validate structure
            validation = self.validate_json_structure(cleaned)
            
            if not validation['is_valid']:
                logger.error(f"JSON structure validation failed:")
                for error in validation['errors']:
                    logger.error(f"   - {error}")
                
                # Attempt recovery
                logger.info("Attempting recovery...")
                extracted = self.extract_json(
                    cleaned, 
                    required_fields=['decisions', 'analysis_summary']
                )
                
                if extracted:
                    cleaned = extracted
                    logger.info("Recovery successful")
                else:
                    raise LLMError(f"JSON structure invalid: {validation['errors']}")
            
            # Step 3: Parse JSON
            try:
                response_data = json.loads(cleaned)
                logger.info(f"JSON parsed successfully")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                
                # Last recovery attempt
                extracted = self.extract_json(
                    llm_response,
                    required_fields=['decisions', 'analysis_summary']
                )
                
                if extracted:
                    try:
                        response_data = json.loads(extracted)
                        logger.info("Recovery parse successful")
                    except Exception:
                        raise LLMError(f"Failed to parse triage response: {e}")
                else:
                    raise LLMError(f"Failed to parse triage response: {e}")
            
            # Step 4: Validate required fields
            self._validate_required_fields(
                response_data,
                required_fields=['decisions'],
                response_type='triage'
            )
            
            # Step 5: Create TriageResult (Pydantic will validate)
            triage_result = TriageResult(**response_data)
            
            # Step 6: Log results
            logger.info(f"TriageResult created successfully")
            logger.info(f"   Total analyzed: {triage_result.total_analyzed}")
            logger.info(f"   Confirmed: {triage_result.confirmed_count}")
            logger.info(f"   False positives: {triage_result.false_positive_count}")
            logger.info(f"   Needs review: {triage_result.needs_review_count}")
            
            return triage_result
            
        except Exception as e:
            logger.error(f"Triage parsing failed: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Failed to parse triage response: {e}")
    
    
    def parse_remediation_response(self, 
                                   llm_response: str, 
                                   vuln_type: str = None, 
                                   language: str = None) -> RemediationPlan:
        """
        Parse LLM response to RemediationPlan
        
        Args:
            llm_response: Raw LLM response
            vuln_type: Vulnerability type (for logging)
            language: Language (for normalization)
            
        Returns:
            Validated RemediationPlan
            
        Raises:
            LLMError: If parsing fails
        """
        
        logger.info(f"Parsing remediation response ({len(llm_response):,} chars)...")
        
        try:
            # Step 1: Clean response
            cleaned = self.clean_json_response(llm_response)
            
            # Step 2: Validate structure
            validation = self.validate_json_structure(cleaned)
            
            if not validation['is_valid']:
                logger.error(f"JSON structure validation failed:")
                for error in validation['errors']:
                    logger.error(f"   - {error}")
                
                # Attempt recovery
                extracted = self.extract_json(
                    cleaned,
                    required_fields=['vulnerability_type', 'priority_level', 'steps']
                )
                
                if extracted:
                    cleaned = extracted
                    logger.info("Recovery successful")
                else:
                    raise LLMError(f"JSON structure invalid: {validation['errors']}")
            
            # Step 3: Parse JSON
            try:
                response_data = json.loads(cleaned)
                logger.info(f"JSON parsed successfully")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                
                # Last attempt
                extracted = self.extract_json(
                    llm_response,
                    required_fields=['vulnerability_type', 'priority_level', 'steps']
                )
                
                if extracted:
                    try:
                        response_data = json.loads(extracted)
                        logger.info("Recovery parse successful")
                    except Exception:
                        raise LLMError(f"Failed to parse remediation response: {e}")
                else:
                    raise LLMError(f"Failed to parse remediation response: {e}")
            
            # Step 4: Validate required fields
            self._validate_required_fields(
                response_data,
                required_fields=['vulnerability_type', 'priority_level', 'steps'],
                response_type='remediation'
            )
            
            # Step 5: Normalize data
            response_data = self._normalize_remediation_data(response_data, vuln_type)
            
            # Step 6: Create RemediationPlan
            remediation_plan = RemediationPlan(**response_data)
            
            # Step 7: Validate quality
            self._validate_remediation_quality(remediation_plan)
            
            # Step 8: Log results
            logger.info(f"RemediationPlan created successfully")
            logger.info(f"   Type: {remediation_plan.vulnerability_type.value}")
            logger.info(f"   Priority: {remediation_plan.priority_level}")
            logger.info(f"   Steps: {len(remediation_plan.steps)}")
            
            return remediation_plan
            
        except Exception as e:
            logger.error(f"Remediation parsing failed: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Failed to parse remediation response: {e}")
    
    
    # ============================================================================
    # JSON CLEANING & EXTRACTION
    # ============================================================================
    
    def clean_json_response(self, response: str) -> str:
        """
        Clean response by removing markdown, prefixes and noise
        
        Handles:
        - Markdown wrappers: ```json ... ```
        - Anomalous prefixes: L3##, etc
        - Non-JSON lines at start/end
        - Invalid escape characters
        
        Args:
            response: Raw LLM response
            
        Returns:
            Clean and valid JSON
        """
        
        original_length = len(response)
        cleaned = response.strip()
        
        if self.debug_enabled:
            logger.debug(f"Starting JSON cleaning (original: {original_length} chars)")
        
        # Step 1: Remove complete markdown wrapper
        markdown_pattern = r'^```(?:json)?\s*\n(.*?)\n\s*```$'
        markdown_match = re.match(markdown_pattern, cleaned, re.DOTALL)
        
        if markdown_match:
            cleaned = markdown_match.group(1).strip()
            if self.debug_enabled:
                logger.debug("Removed markdown wrapper (```json ...```)")
        
        # Step 2: Remove anomalous prefixes
        anomalous_prefixes = [
            'L3##```json\n', 'L3##json', 'L3##\n', 'L3##',
            '```json\n', '```json', '```\n', '```', 'json\n'
        ]
        
        for prefix in anomalous_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].lstrip()
                if self.debug_enabled:
                    logger.debug(f"Removed prefix: '{prefix[:15]}'")
                break
        
        # Step 3: Remove suffixes
        anomalous_suffixes = ['\n```', '```', '`']
        
        for suffix in anomalous_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].rstrip()
                if self.debug_enabled:
                    logger.debug(f"Removed suffix: '{suffix}'")
                break
        
        # Step 4: Clean non-JSON lines at start
        lines = cleaned.split('\n')
        json_start_index = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('{', '[')):
                json_start_index = i
                break
        
        if json_start_index > 0:
            cleaned = '\n'.join(lines[json_start_index:])
            if self.debug_enabled:
                logger.debug(f"Skipped {json_start_index} non-JSON lines at start")
        
        # Step 5: Clean non-JSON lines at end
        lines = cleaned.split('\n')
        json_end_index = len(lines)
        
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped.endswith(('}', ']')):
                json_end_index = i + 1
                break
        
        if json_end_index < len(lines):
            skipped = len(lines) - json_end_index
            cleaned = '\n'.join(lines[:json_end_index])
            if self.debug_enabled:
                logger.debug(f"Skipped {skipped} non-JSON lines at end")
        
        # Step 6: Validate not empty
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Response is empty after cleaning")
        
        # Step 7: Fix invalid escapes
        cleaned = self._fix_escape_sequences(cleaned)
        
        # Final log
        final_length = len(cleaned)
        bytes_removed = original_length - final_length
        if self.debug_enabled:
            logger.debug(f"Cleaning complete: {bytes_removed} bytes removed ({original_length} -> {final_length})")
        
        return cleaned
    
    
    def validate_json_structure(self, text: str) -> Dict[str, Any]:
        """
        Validate JSON structure before parsing
        
        Args:
            text: Text that should be JSON
            
        Returns:
            Dict with validation info:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check balanced delimiters
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        if open_braces != close_braces:
            validation['is_valid'] = False
            validation['errors'].append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        if open_brackets != close_brackets:
            validation['is_valid'] = False
            validation['errors'].append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
        
        # Check starts with { or [
        if not text.startswith(('{', '[')):
            validation['warnings'].append(f"JSON doesn't start with {{ or [")
        
        # Check ends with } or ]
        if not text.endswith(('}', ']')):
            validation['warnings'].append(f"JSON doesn't end with }} or ]")
        
        return validation
    
    def extract_json(self, text: str, required_fields: List[str] = None) -> Optional[str]:
        """
        Extract JSON from noisy text using multiple strategies
        
        Strategies (in priority order):
        1. Stack-based balancing with structure validation
        2. Regex pattern matching
        3. Simple first/last delimiter
        
        Args:
            text: Text with JSON mixed with noise
            required_fields: Required fields to consider JSON valid
            
        Returns:
            Extracted JSON or None if fails
        """
        
        logger.info("Attempting aggressive JSON extraction...")
        if required_fields:
            logger.debug(f"   Required fields: {required_fields}")
        
        # === METHOD 0: Try to balance brackets/braces FIRST ===
        try:
            logger.info("Trying auto-balance method...")
            balanced = self._balance_json_delimiters(text)
            if balanced and balanced != text:  # Only if changes were made
                try:
                    parsed = json.loads(balanced)
                    has_required = self._has_required_fields(parsed, required_fields)
                    
                    if has_required:
                        logger.info(f"Auto-balance successful with all required fields ({len(balanced)} chars)")
                        return balanced
                    else:
                        logger.warning("Auto-balanced JSON missing required fields")
                        # Continue to other methods
                except json.JSONDecodeError as e:
                    logger.debug(f"   Auto-balanced JSON invalid: {e}")
        except Exception as e:
            logger.debug(f"   Balance attempt failed: {e}")
        
        # === METHOD 1: Stack-based balancing (existing code) ===
        try:
            possible_jsons = []
            
            i = 0
            while i < len(text):
                if text[i] == '{':
                    stack = ['{']
                    start_pos = i
                    j = i + 1
                    
                    while j < len(text) and stack:
                        if text[j] == '{':
                            stack.append('{')
                        elif text[j] == '}':
                            stack.pop()
                            if not stack:  # Complete JSON found
                                end_pos = j + 1
                                candidate = text[start_pos:end_pos]
                                
                                # Try to parse and validate
                                try:
                                    parsed = json.loads(candidate)
                                    has_required = self._has_required_fields(parsed, required_fields)
                                    
                                    possible_jsons.append({
                                        'json': candidate,
                                        'parsed': parsed,
                                        'length': len(candidate),
                                        'start': start_pos,
                                        'has_required_fields': has_required,
                                        'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
                                    })
                                except json.JSONDecodeError:
                                    pass
                                
                                break
                        j += 1
                i += 1
            
            if possible_jsons:
                logger.info(f"   Found {len(possible_jsons)} valid JSON objects")
                
                # Prioritize by: required fields > size
                possible_jsons.sort(key=lambda x: (
                    x['has_required_fields'],
                    x['length']
                ), reverse=True)
                
                best_candidate = possible_jsons[0]
                
                if best_candidate['has_required_fields']:
                    logger.info(f"Stack extraction successful ({best_candidate['length']} chars)")
                    logger.debug(f"   Fields found: {best_candidate['available_fields']}")
                    return best_candidate['json']
                else:
                    logger.warning(f"Best candidate missing required fields")
                    logger.warning(f"   Required: {required_fields}")
                    logger.warning(f"   Available: {best_candidate['available_fields']}")
                    logger.info(f"   Using largest JSON anyway ({best_candidate['length']} chars)")
                    return best_candidate['json']
            
            logger.debug("   Stack method found no valid JSON")
        
        except Exception as e:
            logger.debug(f"   Stack extraction failed: {e}")
        
        # === METHOD 2: Regex pattern matching ===
        logger.info("Trying regex extraction...")
        
        try:
            # Search for {...} pattern with content
            pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(pattern, text, re.DOTALL)
            
            if matches:
                logger.info(f"   Found {len(matches)} potential JSON objects via regex")
                
                valid_matches = []
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        has_required = self._has_required_fields(parsed, required_fields)
                        
                        valid_matches.append({
                            'json': match,
                            'parsed': parsed,
                            'length': len(match),
                            'has_required_fields': has_required,
                            'available_fields': list(parsed.keys()) if isinstance(parsed, dict) else []
                        })
                    except json.JSONDecodeError:
                        continue
                
                if valid_matches:
                    # Sort by required fields + size
                    valid_matches.sort(key=lambda x: (
                        x['has_required_fields'],
                        x['length']
                    ), reverse=True)
                    
                    best = valid_matches[0]
                    
                    if best['has_required_fields']:
                        logger.info(f"Regex extracted valid JSON ({best['length']} chars)")
                        return best['json']
                    else:
                        logger.warning(f"Using largest regex match without required fields")
                        return best['json']
        
        except Exception as e:
            logger.debug(f"   Regex extraction failed: {e}")
        
        # === METHOD 3: Simple first/last delimiter ===
        logger.info("Trying simple first/last delimiter...")
        
        try:
            first_brace = text.find('{')
            last_brace = text.rfind('}')
            
            if first_brace >= 0 and last_brace > first_brace:
                extracted = text[first_brace:last_brace + 1]
                try:
                    parsed = json.loads(extracted)
                    has_required = self._has_required_fields(parsed, required_fields)
                    
                    if has_required or not required_fields:
                        logger.info(f"Simple extraction successful ({len(extracted)} chars)")
                        return extracted
                    else:
                        logger.warning(f"Simple extraction missing required fields")
                        return extracted
                
                except json.JSONDecodeError as e:
                    logger.debug(f"   Simple extraction not valid JSON: {e}")
        
        except Exception as e:
            logger.debug(f"   Simple extraction failed: {e}")
        
        # All methods failed
        logger.error("All extraction methods failed")
        return None
    
    def _balance_json_delimiters(self, text: str) -> Optional[str]:
        """
        Attempt to balance unbalanced JSON by adding missing delimiters
        
        This handles cases where LLM responses are truncated or incomplete.
        
        Args:
            text: Potentially unbalanced JSON
            
        Returns:
            Balanced JSON or None
        """
        
        # Count all delimiters
        open_braces = text.count('{')
        close_braces = text.count('}')
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        
        if self.debug_enabled:
            logger.debug(f"   Delimiters: {{:{open_braces}/{close_braces}, [:{open_brackets}/{close_brackets}")
        
        # If already balanced, return None (no changes needed)
        if open_braces == close_braces and open_brackets == close_brackets:
            return None
        
        balanced = text.strip()
        changes_made = False
        
        # Add missing closing brackets (for arrays)
        if open_brackets > close_brackets:
            missing = open_brackets - close_brackets
            logger.info(f"   ?? Adding {missing} closing bracket(s) ]")
            balanced += '\n' + ('  ' * (missing - 1)) + ']' * missing
            changes_made = True
        
        # Add missing closing braces (for objects)
        if open_braces > close_braces:
            missing = open_braces - close_braces
            logger.info(f"   ?? Adding {missing} closing brace(s) }}")
            # Add with proper indentation
            for i in range(missing):
                indent = '  ' * (missing - i - 1)
                balanced += '\n' + indent + '}'
            changes_made = True
        
        # Handle excess closing delimiters (less common but possible)
        if close_brackets > open_brackets:
            excess = close_brackets - open_brackets
            logger.warning(f"   ?? Removing {excess} excess closing bracket(s)")
            # Remove from end
            for _ in range(excess):
                last_bracket = balanced.rfind(']')
                if last_bracket >= 0:
                    balanced = balanced[:last_bracket] + balanced[last_bracket+1:]
            changes_made = True
        
        if close_braces > open_braces:
            excess = close_braces - open_braces
            logger.warning(f"   ?? Removing {excess} excess closing brace(s)")
            for _ in range(excess):
                last_brace = balanced.rfind('}')
                if last_brace >= 0:
                    balanced = balanced[:last_brace] + balanced[last_brace+1:]
            changes_made = True
        
        if changes_made:
            if self.debug_enabled:
                logger.debug(f"   Balanced result ({len(balanced)} chars)")
            return balanced
        
        return None

    # ============================================================================
    # HELPER METHODS - PRIVATE
    # ============================================================================
    
    def _fix_escape_sequences(self, text: str) -> str:
        """
        Fix invalid escape sequences in JSON
        
        Valid JSON only accepts: \\", \\\\, \\/, \\b, \\f, \\n, \\r, \\t, \\uXXXX
        
        Args:
            text: Text with possible invalid escapes
            
        Returns:
            Text with corrected escapes
        """
        
        result = []
        i = 0
        
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                next_char = text[i + 1]
                
                # Valid simple escapes
                if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
                    result.append(text[i:i+2])
                    i += 2
                    continue
                
                # Unicode escape: \uXXXX
                elif next_char == 'u' and i + 5 < len(text):
                    hex_part = text[i+2:i+6]
                    if re.match(r'^[0-9a-fA-F]{4}$', hex_part):
                        result.append(text[i:i+6])
                        i += 6
                        continue
                
                # Invalid escape - escape the backslash
                if self.debug_enabled:
                    logger.debug(f"Fixed invalid escape: \\{next_char}")
                result.append('\\\\' + next_char)
                i += 2
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    
    def _has_required_fields(self, parsed: Any, required_fields: Optional[List[str]]) -> bool:
        """
        Check if a parsed object has required fields
        
        Args:
            parsed: Parsed object (dict, list, etc)
            required_fields: List of required fields
            
        Returns:
            True if has all required fields (or if no fields required)
        """
        
        if not required_fields:
            return True
        
        if not isinstance(parsed, dict):
            return False
        
        return all(field in parsed for field in required_fields)
    
    
    def _validate_required_fields(self, 
                                   response_data: Dict[str, Any],  # ? CORREGIDO
                                   required_fields: List[str],
                                   response_type: str) -> None:
        """
        Validate that a dict has required fields
        
        Args:
            response_data: Dict with parsed response
            required_fields: Fields that must be present
            response_type: Response type (for error messages)
            
        Raises:
            LLMError: If required fields are missing
        """
        
        if not isinstance(response_data, dict):
            raise LLMError(f"{response_type} response is not a dict: {type(response_data)}")
        
        missing = [f for f in required_fields if f not in response_data]
        
        if missing:
            available = list(response_data.keys())
            raise LLMError(
                f"{response_type} response missing required fields: {missing}. "
                f"Available: {available}"
            )
        
        logger.debug(f"All required fields present: {required_fields}")
    
    
    def _normalize_remediation_data(self, 
                                      response_data: Dict[str, Any],
                                      vuln_type: str = None) -> Dict[str, Any]:
        """
        Normalizar datos de remediación para asegurar compatibilidad con RemediationPlan
        
        Args:
            response_data: Datos parseados del LLM
            vuln_type: Tipo de vulnerabilidad (fallback)
            
        Returns:
            Datos normalizados
        """
        
        # Asegurar que vulnerability_id existe
        if 'vulnerability_id' not in response_data:
            response_data['vulnerability_id'] = f"{vuln_type or 'unknown'}-remediation-{int(time.time())}"
            logger.warning(f"⚠️ Added missing vulnerability_id: {response_data['vulnerability_id']}")

        # Asegurar que llm_model_used existe
        if 'llm_model_used' not in response_data:
            response_data['llm_model_used'] = 'meta-llama/llama-3-3-70b-instruct'
            logger.debug("   Added default llm_model_used")

        # Validar que steps tenga contenido
        if not response_data.get('steps') or len(response_data['steps']) < 1:
            raise LLMError("Response has no remediation steps")

        return response_data

    
    def _validate_remediation_quality(self, plan: RemediationPlan) -> None:
        """
        Validate quality of remediation plan steps
        
        Args:
            plan: Remediation plan to validate
            
        Warnings:
            Generates warnings if steps have low quality
        """
        
        for i, step in enumerate(plan.steps, 1):
            desc_length = len(step.description)
            if desc_length < 50:
                logger.warning(f"Step {i} has short description ({desc_length} chars)")
            
            if not step.title or len(step.title) < 10:
                logger.warning(f"Step {i} has very short title")


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_response_parser(debug_enabled: bool = False) -> LLMResponseParser:
    """
    Factory function to create parser
    
    Args:
        debug_enabled: Enable detailed debug logging
        
    Returns:
        Configured LLMResponseParser
    """
    return LLMResponseParser(debug_enabled=debug_enabled)
