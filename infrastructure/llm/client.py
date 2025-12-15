# infrastructure/llm/client.py
"""
🤖 LLM Client for Research API - Enhanced Version
Versión robusta con parsing JSON mejorado y manejo de errores completo
"""

import requests
import json
import logging
import time
import os
import uuid
import re
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

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


class LLMClient:
    """
    Cliente LLM para Research API con parsing robusto
    
    Features:
    - ✅ Limpieza avanzada de JSON con markdown wrappers
    - ✅ Validación pre-parsing
    - ✅ Sistema de fallback inteligente
    - ✅ Retry logic con backoff exponencial
    - ✅ Debug mode integrado
    - ✅ Logging exhaustivo
    """
    
    def __init__(self, primary_provider: str = "watsonx", enable_debug: bool = False):
        """
        Initialize LLM Client
        
        Args:
            primary_provider: LLM provider ("watsonx" or "openai")
            enable_debug: Enable debug mode with detailed logging
        """
        self.api_key = os.getenv("RESEARCH_API_KEY", "")
        self.primary_provider = primary_provider
        self.base_url = "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
        self.timeout = 300  # 5 minutos
        self.user_email = os.getenv("LLM_USER_EMAIL", "franciscojavier.suarez_css@research.com")
        
        # Configuración de retry
        self.max_retries = 3
        self.retry_delay_base = 2  # segundos
        
        # Debug mode
        self.debug_enabled = enable_debug
        self.debugger = None
        
        # Configurar sesión HTTP con headers
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        })
        
        # Endpoints según provider
        self.endpoints = {
            "watsonx": "/research/llm/wx/clients",
            "openai": "/research/llm/openai/clients"
        }
        
        # Validación de API key
        if not self.api_key:
            raise ValueError("RESEARCH_API_KEY environment variable is required")
        
        logger.info(f"🤖 LLM Client initialized: {self.primary_provider}")
        logger.debug(f"   Base URL: {self.base_url}")
        logger.debug(f"   Timeout: {self.timeout}s")
        logger.debug(f"   Max retries: {self.max_retries}")
    
    
    # ============================================================================
    # DEBUG MODE CONTROL
    # ============================================================================
    
    def enable_debug_mode(self):
        """Habilitar modo debug con logging detallado"""
        self.debug_enabled = True
        try:
            from debug.llm_debugger import get_debugger
            self.debugger = get_debugger()
            logger.info("🔍 Debug mode ENABLED for LLM Client")
        except ImportError:
            logger.warning("⚠️  Debug module not available")
            self.debug_enabled = False
    
    
    def disable_debug_mode(self):
        """Deshabilitar modo debug"""
        self.debug_enabled = False
        self.debugger = None
        logger.info("🔍 Debug mode DISABLED for LLM Client")
    
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    async def analyze_vulnerabilities(self, 
                                    vulnerabilities_data: str,
                                    language: Optional[str] = None,
                                    framework: Optional[str] = None) -> TriageResult:
        """
        Analizar vulnerabilidades usando Research API
        
        Args:
            vulnerabilities_ Datos de vulnerabilidades en formato texto
            language: Lenguaje de programación (opcional)
            framework: Framework utilizado (opcional)
            
        Returns:
            TriageResult con decisiones de clasificación
            
        Raises:
            LLMError: Si el análisis falla después de reintentos
        """
        
        try:
            logger.info(f"🔍 Starting vulnerability triage analysis")
            logger.debug(f"   Language: {language or 'Auto-detect'}")
            logger.debug(f"   Data length: {len(vulnerabilities_data)} chars")
            
            # Obtener prompt mejorado
            from infrastructure.llm.prompts import PromptManager
            prompt_manager = PromptManager()
            system_prompt = prompt_manager.get_triage_system_prompt(language=language)
            
            logger.info(f"📝 Using enhanced triage prompt ({len(system_prompt)} chars)")
            
            # Construir mensaje completo con instrucciones explícitas
            full_message = self._build_triage_message(system_prompt, vulnerabilities_data)
            
            # Llamar a Research API con retry
            start_time = time.time()
            response = await self._call_research_api_with_retry(
                message=full_message,
                temperature=0.1,
                operation_name="triage_analysis"
            )
            duration = time.time() - start_time
            
            logger.info(f"✅ Triage response received in {duration:.2f}s")
            
            # Log debug si está habilitado
            if self.debug_enabled and self.debugger:
                self.debugger.log_triage_analysis(
                    vulnerabilities_data=vulnerabilities_data,
                    system_prompt=system_prompt,
                    response=response,
                    duration=duration
                )
            
            # Parsear respuesta con validación robusta
            result = self._parse_triage_response(response, vulnerabilities_data)
            
            logger.info(f"✅ Triage completed successfully")
            logger.info(f"   Total analyzed: {result.total_analyzed}")
            logger.info(f"   Confirmed: {result.confirmed_count}")
            logger.info(f"   False positives: {result.false_positive_count}")
            logger.info(f"   Needs review: {result.needs_review_count}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM triage analysis failed: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Triage analysis failed: {e}")
    
    
    async def generate_remediation_plan(self, 
                                      vulnerability_data: str,
                                      vuln_type: str = None, 
                                      language: Optional[str] = None,
                                      severity: str = "HIGH") -> RemediationPlan:
        """
        Generar plan de remediación usando Research API
        
        Args:
            vulnerability_ Datos de la vulnerabilidad
            vuln_type: Tipo de vulnerabilidad
            language: Lenguaje de programación
            severity: Nivel de severidad
            
        Returns:
            RemediationPlan con pasos detallados
            
        Raises:
            LLMError: Si la generación falla después de reintentos
        """
        
        try:
            logger.info(f"🛠️  Starting remediation plan generation")
            logger.debug(f"   Type: {vuln_type or 'Unknown'}")
            logger.debug(f"   Language: {language or 'Generic'}")
            logger.debug(f"   Severity: {severity}")
            
            # Obtener prompt mejorado
            from infrastructure.llm.prompts import PromptManager
            prompt_manager = PromptManager()
            system_prompt = prompt_manager.get_remediation_system_prompt(
                vuln_type=vuln_type or "Security Issue",
                language=language,
                severity=severity
            )
            
            logger.info(f"📝 Using enhanced remediation prompt ({len(system_prompt)} chars)")
            
            # Construir mensaje completo
            full_message = self._build_remediation_message(system_prompt, vulnerability_data)
            
            # Llamar a Research API con retry
            start_time = time.time()
            response = await self._call_research_api_with_retry(
                message=full_message,
                temperature=0.2,  # Ligeramente más alta para creatividad
                operation_name="remediation_generation"
            )
            duration = time.time() - start_time
            
            logger.info(f"✅ Remediation response received in {duration:.2f}s")
            
            # Log debug si está habilitado
            if self.debug_enabled and self.debugger:
                self.debugger.log_remediation_generation(
                    vulnerability_data=vulnerability_data,
                    system_prompt=system_prompt,
                    response=response,
                    duration=duration
                )
            
            # Parsear respuesta con validación robusta
            result = self._parse_remediation_response(response, vuln_type, language)
            
            logger.info(f"✅ Remediation plan created successfully")
            logger.info(f"   Priority: {result.priority_level}")
            logger.info(f"   Steps: {len(result.steps)}")
            logger.info(f"   Estimated hours: {result.total_estimated_hours}h")
            logger.info(f"   Complexity: {result.complexity_score}/10")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ LLM remediation generation failed: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Remediation generation failed: {e}")
    
    
    # ============================================================================
    # RESEARCH API COMMUNICATION
    # ============================================================================
    
    async def _call_research_api_with_retry(self, 
                                          message: str, 
                                          temperature: float = 0.1,
                                          operation_name: str = "llm_call") -> str:
        """
        Llamar a Research API con lógica de reintento
        
        Args:
            message: Mensaje completo para enviar
            temperature: Temperatura del LLM (0.0-1.0)
            operation_name: Nombre de la operación (para logging)
            
        Returns:
            Respuesta del LLM (texto limpio)
            
        Raises:
            LLMError: Si todos los intentos fallan
        """
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries} - {operation_name}")
                
                response = await self._call_research_api(message, temperature)
                
                # Si llegamos aquí, el llamado fue exitoso
                if attempt > 0:
                    logger.info(f"✅ Succeeded on retry {attempt + 1}")
                
                return response
                
            except LLMError as e:
                last_error = e
                
                if attempt < self.max_retries - 1:
                    # Calcular delay con backoff exponencial
                    delay = self.retry_delay_base ** (attempt + 1)
                    logger.warning(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    logger.warning(f"⏳ Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    # Último intento falló
                    logger.error(f"❌ All {self.max_retries} attempts failed")
                    raise
        
        # Si llegamos aquí, todos los reintentos fallaron
        raise last_error or LLMError(f"All {self.max_retries} attempts failed")
    
    
    async def _call_research_api(self, message: str, temperature: float = 0.1) -> str:
        """
        Llamar a Research API (single attempt)
        
        Args:
            message: Mensaje completo
            temperature: Temperatura del LLM
            
        Returns:
            Contenido de la respuesta (limpio)
            
        Raises:
            LLMError: Si la llamada falla
        """
        
        url = f"{self.base_url}{self.endpoints[self.primary_provider]}"
        session_uuid = str(uuid.uuid4())
        
        # Preparar payload
        payload = {
            "message": {
                "role": "user",
                "content": message
            },
            "temperature": temperature,
            "model": "meta-llama/llama-3-3-70b-instruct",
            "prompt": None,
            "uuid": session_uuid,
            "language": "es",
            "user": self.user_email
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"📡 Calling Research API")
            logger.debug(f"   URL: {url}")
            logger.debug(f"   Provider: {self.primary_provider}")
            logger.debug(f"   Temperature: {temperature}")
            logger.debug(f"   Message length: {len(message):,} chars")
            logger.debug(f"   Session UUID: {session_uuid}")
            
            # Hacer la llamada HTTP
            response = self.session.post(url, json=payload, timeout=self.timeout)
            duration = time.time() - start_time
            
            # Logging de respuesta
            logger.info(f"📡 HTTP Status: {response.status_code}")
            logger.info(f"📏 Response size: {len(response.text):,} chars")
            logger.info(f"⏱️  Duration: {duration:.2f}s")
            logger.debug(f"   Response headers: {dict(response.headers)}")
            
            # Log preview de respuesta
            preview_length = min(300, len(response.text))
            logger.debug(f"   Response preview (first {preview_length} chars):")
            logger.debug(f"   {response.text[:preview_length]}")
            
            # Validar status code
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:500]}"
                logger.error(f"❌ Research API error: {error_msg}")
                raise LLMError(f"Research API failed: {error_msg}")
            
            response_text = response.text
            
            # Validar que no esté vacía
            if not response_text or response_text.strip() == "":
                logger.error("❌ Empty response from Research API")
                raise LLMError("Empty response from LLM")
            
            # Intentar parsear como JSON para extraer el contenido real
            try:
                result = response.json()
                logger.debug(f"   Response is valid JSON")
                logger.debug(f"   JSON keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️  Response is not JSON (using as plain text): {e}")
                result = response_text
            
            # Extraer contenido según la estructura de respuesta
            content = self._extract_content_from_response(result)
            
            # Validar contenido extraído
            if not content or (isinstance(content, str) and content.strip() == ""):
                logger.error("❌ No content in LLM response")
                logger.error(f"   Original result type: {type(result)}")
                logger.error(f"   Original result: {str(result)[:500]}")
                raise LLMError("No content in LLM response")
            
            logger.info(f"✅ Content extracted: {len(content):,} chars")
            logger.debug(f"   Content preview (first 300 chars):")
            logger.debug(f"   {content[:300]}")
            logger.info(f"✅ Research API call successful - {duration:.2f}s")
            
            return content
            
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            error_msg = f"Research API timeout after {self.timeout}s"
            logger.error(f"❌ {error_msg}")
            raise LLMError(error_msg)
            
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            error_msg = f"Research API connection error: {e}"
            logger.error(f"❌ {error_msg}")
            raise LLMError(error_msg)
            
        except LLMError:
            # Re-raise LLMError sin envolver
            raise
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Research API unexpected error: {e}"
            logger.error(f"❌ {error_msg}")
            logger.exception("Full traceback:")
            raise LLMError(error_msg)
    
    
    def _extract_content_from_response(self, result: Any) -> str:
        """
        Extraer contenido real de la estructura de respuesta API
        
        Args:
            result: Respuesta cruda (dict, str, etc)
            
        Returns:
            Contenido extraído como string
        """
        
        if isinstance(result, dict):
            logger.debug("Response is dict, searching for content field...")
            
            # Posibles campos donde puede estar el contenido
            possible_keys = [
                'content', 'response', 'message', 'text', 
                'output', 'result', 'data', 'answer', 'completion'
            ]
            
            for key in possible_keys:
                if key in result and result[key]:
                    value = result[key]
                    
                    # Si el valor es un dict, extraer recursivamente
                    if isinstance(value, dict):
                        nested_content = self._extract_content_from_response(value)
                        if nested_content:
                            logger.info(f"✅ Found content in nested field: {key}")
                            return nested_content
                    elif value:
                        logger.info(f"✅ Found content in field: {key}")
                        return str(value)
            
            # Si no encontramos campo conocido, serializar todo el dict
            logger.warning(f"⚠️  No standard content field found")
            logger.debug(f"   Available fields: {list(result.keys())}")
            return json.dumps(result)
        
        else:
            return str(result)
    
    
    # ============================================================================
    # MESSAGE BUILDERS
    # ============================================================================
    
    def _build_triage_message(self, system_prompt: str, vulnerabilities_data: str) -> str:
        """
        Construir mensaje completo para triage
        
        Args:
            system_prompt: Prompt del sistema
            vulnerabilities_ Datos de vulnerabilidades
            
        Returns:
            Mensaje formateado
        """
        
        return f"""{system_prompt}

# VULNERABILITIES TO ANALYZE

{vulnerabilities_data}

# CRITICAL INSTRUCTIONS

1. Return ONLY valid JSON - NO markdown code blocks
2. Do NOT include any text before or after the JSON object
3. Ensure all strings are properly escaped
4. Follow the exact schema provided in the system prompt
5. Each decision MUST have all required fields

Now analyze the vulnerabilities above and return the JSON response:"""
    
    
    def _build_remediation_message(self, system_prompt: str, vulnerability_data: str) -> str:
        """
        Construir mensaje completo para remediation
        
        Args:
            system_prompt: Prompt del sistema
            vulnerability_ Datos de la vulnerabilidad
            
        Returns:
            Mensaje formateado
        """
        
        return f"""{system_prompt}

# VULNERABILITY DATA TO ANALYZE

{vulnerability_data}

# CRITICAL INSTRUCTIONS

1. Return ONLY valid JSON - NO markdown wrapper (no ```json)
2. Do NOT include any text before or after the JSON
3. Include ALL required fields in the schema
4. Each step MUST have detailed description (minimum 100 words)
5. Include specific code examples with before/after
6. Provide concrete validation tests
7. NO placeholder text like "implement security fix"
8. Ensure all strings are properly escaped
9. Keep individual string fields under 1000 characters
10. If a field needs more text, split into structured object

Now generate the remediation plan following the exact JSON schema:"""
    
    
    # ============================================================================
    # JSON CLEANING & PARSING - ENHANCED VERSION
    # ============================================================================
    
    def _clean_json_response(self, response: str) -> str:
        """
        Limpiar respuesta eliminando markdown, prefijos y espacios - VERSIÓN MEJORADA v2
        
        Maneja:
        - Markdown wrappers: ```json ... ```
        - Prefijos anómalos: L3##, etc
        - Líneas no-JSON al inicio/final
        - Caracteres de escape inválidos
        
        Args:
            response: Respuesta cruda del LLM
            
        Returns:
            JSON limpio y válido
            
        Raises:
            ValueError: Si la respuesta está vacía después de limpiar
        """
        
        original_length = len(response)
        cleaned = response.strip()
        
        logger.debug(f"🧹 Starting JSON cleaning (original: {original_length} chars)")
        
        # === PASO 1: Detectar y remover wrapper markdown completo ===
        # Patrón: ```json\n{...}\n``` o ```\n{...}\n```
        markdown_pattern = r'^```(?:json)?\s*\n(.*?)\n```\s*$'
        markdown_match = re.match(markdown_pattern, cleaned, re.DOTALL)
        
        if markdown_match:
            cleaned = markdown_match.group(1).strip()
            logger.debug("✅ Removed complete markdown wrapper (```json ... ```)")
        
        # === PASO 2: Remover prefijos anómalos ===
        anomalous_prefixes = [
            'L3##```json\n',
            'L3##```json',
            'L3##\n',
            'L3##',
            '```json\n',
            '```json',
            '```\n',
            '```',
            'json\n',
        ]
        
        for prefix in anomalous_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].lstrip()
                logger.debug(f"✅ Removed anomalous prefix: '{prefix[:20]}'...")
                break
        
        # === PASO 3: Remover sufijos ===
        anomalous_suffixes = [
            '\n```',
            '```',
            '`',
        ]
        
        for suffix in anomalous_suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].rstrip()
                logger.debug(f"✅ Removed suffix: '{suffix}'")
                break
        
        # === PASO 4: Limpiar líneas no-JSON al inicio ===
        lines = cleaned.split('\n')
        json_start_index = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('{', '[')):
                json_start_index = i
                break
        
        if json_start_index > 0:
            cleaned = '\n'.join(lines[json_start_index:])
            logger.debug(f"✅ Skipped {json_start_index} non-JSON lines at start")
        
        # === PASO 5: Limpiar líneas no-JSON al final ===
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
            logger.debug(f"✅ Skipped {skipped} non-JSON lines at end")
        
        # === PASO 6: Validar que no esté vacío ===
        cleaned = cleaned.strip()
        if not cleaned:
            raise ValueError("Response is empty after cleaning")
        
        # === PASO 7: Limpiar caracteres de escape inválidos ===
        cleaned = self._fix_escape_sequences(cleaned)
        
        # === PASO 8: Log final ===
        final_length = len(cleaned)
        bytes_removed = original_length - final_length
        logger.debug(f"✅ Cleaning complete: {bytes_removed} bytes removed ({original_length} → {final_length})")
        
        return cleaned
        
    def _fix_escape_sequences(self, text: str) -> str:
        r"""
        Corregir secuencias de escape inválidas en JSON - VERSIÓN SIMPLIFICADA
        
        JSON válido solo acepta: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
        
        Args:
            text: Texto con posibles escapes inválidos
            
        Returns:
            Texto con escapes corregidos
        """
        
        result = []
        i = 0
        
        while i < len(text):
            if text[i] == '\\' and i + 1 < len(text):
                next_char = text[i + 1]
                
                # Escapes válidos simples: \", \\, \/, \b, \f, \n, \r, \t
                if next_char in ['"', '\\', '/', 'b', 'f', 'n', 'r', 't']:
                    result.append(text[i:i+2])
                    i += 2
                    continue
                
                # Escape unicode: \uXXXX (4 dígitos hex)
                elif next_char == 'u' and i + 5 < len(text):
                    hex_part = text[i+2:i+6]
                    if re.match(r'^[0-9a-fA-F]{4}$', hex_part):
                        result.append(text[i:i+6])
                        i += 6
                        continue
                
                # Escape inválido - escapar el backslash
                logger.debug(f"🔧 Fixed invalid escape: \\{next_char}")
                result.append('\\\\' + next_char)
                i += 2
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)

    
    def _validate_json_structure(self, text: str) -> Dict[str, Any]:
        """
        Validar estructura JSON antes de parsear
        
        Args:
            text: Texto que debería ser JSON
            
        Returns:
            Dict con información de validación
        """
        
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar delimitadores balanceados
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
        
        # Verificar que empiece con { o [
        if not text.startswith(('{', '[')):
            validation['warnings'].append(f"JSON doesn't start with {{ or [. First char: '{text[0]}'")
        
        # Verificar que termine con } o ]
        if not text.endswith(('}', ']')):
            validation['warnings'].append(f"JSON doesn't end with }} or ]. Last char: '{text[-1]}'")
        
        return validation
    
    
    def _try_extract_json(self, text: str) -> Optional[str]:
        """
        Intentar extraer JSON de texto con ruido - VERSIÓN MEJORADA v2
        
        Estrategias (en orden):
        1. Stack-based balancing (busca el JSON más grande)
        2. Regex con validación de estructura
        3. Simple first/last delimiter
        
        Args:
            text: Texto con JSON mezclado con ruido
            
        Returns:
            JSON extraído o None si falla
        """
        
        logger.info("🔧 Attempting aggressive JSON extraction...")
        
        # === MÉTODO 1: Stack-based balancing (MEJORADO) ===
        try:
            # Buscar TODOS los JSON balanceados posibles
            possible_jsons = []
            
            i = 0
            while i < len(text):
                if text[i] == '{':
                    # Intentar extraer JSON desde aquí
                    stack = ['{']
                    start_pos = i
                    j = i + 1
                    
                    while j < len(text) and stack:
                        if text[j] == '{':
                            stack.append('{')
                        elif text[j] == '}':
                            stack.pop()
                            if not stack:  # JSON completo encontrado
                                end_pos = j + 1
                                candidate = text[start_pos:end_pos]
                                possible_jsons.append({
                                    'json': candidate,
                                    'length': len(candidate),
                                    'start': start_pos
                                })
                                break
                        j += 1
                i += 1
            
            if possible_jsons:
                logger.info(f"   Found {len(possible_jsons)} potential JSON objects")
                
                # Ordenar por tamaño (más grande primero)
                possible_jsons.sort(key=lambda x: x['length'], reverse=True)
                
                # Intentar parsear cada uno
                for idx, candidate_info in enumerate(possible_jsons):
                    candidate = candidate_info['json']
                    try:
                        parsed = json.loads(candidate)
                        
                        # Para remediation, validar que tenga estructura esperada
                        required_fields = ['vulnerability_type', 'priority_level', 'steps']
                        has_required = all(field in parsed for field in required_fields)
                        
                        if has_required:
                            logger.info(f"✅ Stack extraction successful (candidate {idx+1}, {len(candidate)} chars)")
                            logger.debug(f"   Has required fields: {required_fields}")
                            return candidate
                        else:
                            logger.debug(f"   Candidate {idx+1} missing required fields: {list(parsed.keys())}")
                    
                    except json.JSONDecodeError:
                        continue
                
                # Si ninguno tiene los campos requeridos, devolver el más grande que parsee
                for idx, candidate_info in enumerate(possible_jsons):
                    candidate = candidate_info['json']
                    try:
                        json.loads(candidate)
                        logger.warning(f"⚠️  Using largest valid JSON (may be incomplete)")
                        logger.warning(f"   Length: {len(candidate)} chars")
                        return candidate
                    except:
                        continue
            
            logger.debug("   Stack method found no valid JSON")
        
        except Exception as e:
            logger.debug(f"   Stack extraction failed: {e}")
        
        # === MÉTODO 2: Regex pattern matching ===
        logger.info("🔧 Trying regex extraction...")
        
        try:
            # Buscar patrón {...} con contenido (permite anidamiento)
            # Este patrón es más permisivo y captura JSONs grandes
            pattern = r'\{[^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)?\}[^{}]*)*\}'
            matches = re.findall(pattern, text, re.DOTALL)
            
            if matches:
                logger.info(f"   Found {len(matches)} potential JSON objects via regex")
                
                # Ordenar por tamaño
                sorted_matches = sorted(matches, key=len, reverse=True)
                
                for idx, match in enumerate(sorted_matches):
                    try:
                        parsed = json.loads(match)
                        
                        # Validar estructura
                        required_fields = ['vulnerability_type', 'priority_level', 'steps']
                        if all(field in parsed for field in required_fields):
                            logger.info(f"✅ Regex extracted valid JSON (match {idx+1}, {len(match)} chars)")
                            return match
                    
                    except json.JSONDecodeError:
                        continue
                
                # Fallback: devolver el más grande que parsee
                for idx, match in enumerate(sorted_matches):
                    try:
                        json.loads(match)
                        logger.warning(f"⚠️  Using largest parseable JSON from regex")
                        return match
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"   Regex extraction failed: {e}")
        
        # === MÉTODO 3: Simple first/last delimiter ===
        logger.info("🔧 Trying simple first/last delimiter extraction...")
        
        try:
            first_brace = text.find('{')
            last_brace = text.rfind('}')
            
            if first_brace >= 0 and last_brace > first_brace:
                extracted = text[first_brace:last_brace + 1]
                try:
                    json.loads(extracted)
                    logger.info(f"✅ Simple extraction successful ({len(extracted)} chars)")
                    return extracted
                except json.JSONDecodeError as e:
                    logger.debug(f"   Simple extraction not valid JSON: {e}")
        
        except Exception as e:
            logger.debug(f"   Simple extraction failed: {e}")
        
        # Si llegamos aquí, todos los métodos fallaron
        logger.error("❌ All extraction methods failed")
        return None
    
    
    # ============================================================================
    # RESPONSE PARSERS
    # ============================================================================
    
    def _parse_triage_response(self, llm_response: str, original_data: str) -> TriageResult:
        """
        Parsear respuesta LLM a TriageResult con manejo robusto de errores
        
        Args:
            llm_response: Respuesta cruda del LLM
            original_ Datos originales (para contexto en logs)
            
        Returns:
            TriageResult validado
            
        Raises:
            LLMError: Si el parsing falla después de intentos de recuperación
        """
        
        logger.info(f"📥 Parsing triage response...")
        logger.debug(f"   Response type: {type(llm_response)}")
        logger.debug(f"   Response length: {len(llm_response):,} chars")
        
        try:
            # === PASO 1: Limpiar respuesta ===
            cleaned = self._clean_json_response(llm_response)
            
            logger.debug(f"   Cleaned response preview (first 200 chars):")
            logger.debug(f"   {cleaned[:200]}")
            
            # === PASO 2: Validar estructura ===
            validation = self._validate_json_structure(cleaned)
            
            if not validation['is_valid']:
                logger.error(f"❌ JSON structure validation failed:")
                for error in validation['errors']:
                    logger.error(f"   • {error}")
                
                # Intentar recuperación agresiva
                logger.info("🔧 Attempting recovery...")
                extracted = self._try_extract_json(cleaned)
                
                if extracted:
                    cleaned = extracted
                    logger.info("✅ Recovery successful, using extracted JSON")
                else:
                    raise ValueError(f"JSON structure invalid: {validation['errors']}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    logger.warning(f"⚠️  {warning}")
            
            # === PASO 3: Parsear JSON ===
            try:
                response_data = json.loads(cleaned)
                logger.info(f"✅ JSON parsed successfully")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"   Error at position: {e.pos}")
                
                # Contexto del error
                start = max(0, e.pos - 50)
                end = min(len(cleaned), e.pos + 50)
                context = cleaned[start:end]
                logger.error(f"   Context: ...{context}...")
                
                # Último intento de recuperación
                extracted = self._try_extract_json(llm_response)
                if extracted:
                    try:
                        response_data = json.loads(extracted)
                        logger.info("✅ Recovery parse successful")
                    except Exception as recovery_error:
                        logger.error(f"❌ Recovery attempt also failed: {recovery_error}")
                        raise LLMError(f"Failed to parse triage response as JSON: {e}")
                else:
                    raise LLMError(f"Failed to parse triage response as JSON: {e}")
            
            # === PASO 4: Validar estructura de datos ===
            logger.debug(f"   Response keys: {list(response_data.keys())}")
            
            if not isinstance(response_data, dict):
                raise ValueError(f"Response is not a dict: {type(response_data)}")
            
            # Verificar campo crítico
            if 'decisions' not in response_data:
                available = list(response_data.keys())
                raise ValueError(f"'decisions' field missing. Available fields: {available}")
            
            # Verificar que decisions sea una lista
            if not isinstance(response_data['decisions'], list):
                raise ValueError(f"'decisions' must be a list, got {type(response_data['decisions'])}")
            
            # === PASO 5: Crear TriageResult (Pydantic validará) ===
            triage_result = TriageResult(**response_data)
            
            # === PASO 6: Log resultados ===
            logger.info(f"✅ TriageResult created successfully")
            logger.info(f"   Total analyzed: {triage_result.total_analyzed}")
            logger.info(f"   Confirmed: {triage_result.confirmed_count}")
            logger.info(f"   False positives: {triage_result.false_positive_count}")
            logger.info(f"   Needs review: {triage_result.needs_review_count}")
            
            return triage_result
            
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Validation error: {e}")
            raise LLMError(f"Invalid triage response structure: {e}")
            
        except Exception as e:
            logger.error(f"❌ Unexpected parsing error: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Failed to parse triage response: {e}")
    
    
    def _parse_remediation_response(self, 
                                   llm_response: str, 
                                   vuln_type: str = None, 
                                   language: str = None) -> RemediationPlan:
        """
        Parsear respuesta LLM a RemediationPlan con manejo robusto de errores
        
        Args:
            llm_response: Respuesta cruda del LLM
            vuln_type: Tipo de vulnerabilidad (para logging)
            language: Lenguaje (para normalización de code_example)
            
        Returns:
            RemediationPlan validado
            
        Raises:
            LLMError: Si el parsing falla después de intentos de recuperación
        """
        
        logger.info(f"📥 Parsing remediation response...")
        logger.debug(f"   Response type: {type(llm_response)}")
        logger.debug(f"   Response length: {len(llm_response):,} chars")
        
        try:
            # === PASO 1: Limpiar respuesta ===
            cleaned = self._clean_json_response(llm_response)
            
            logger.debug(f"   Cleaned response preview (first 200 chars):")
            logger.debug(f"   {cleaned[:200]}")
            
            # === PASO 2: Validar estructura ===
            validation = self._validate_json_structure(cleaned)
            
            if not validation['is_valid']:
                logger.error(f"❌ JSON structure validation failed:")
                for error in validation['errors']:
                    logger.error(f"   • {error}")
                
                # Intentar recuperación
                logger.info("🔧 Attempting recovery...")
                extracted = self._try_extract_json(cleaned)
                
                if extracted:
                    cleaned = extracted
                    logger.info("✅ Recovery successful")
                else:
                    raise ValueError(f"JSON structure invalid: {validation['errors']}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    logger.warning(f"⚠️  {warning}")
            
            # === PASO 3: Parsear JSON ===
            try:
                response_data = json.loads(cleaned)
                logger.info(f"✅ JSON parsed successfully")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"   Error at position: {e.pos}")
                
                # Contexto del error
                start = max(0, e.pos - 50)
                end = min(len(cleaned), e.pos + 50)
                context = cleaned[start:end]
                logger.error(f"   Context: ...{context}...")
                
                # Último intento de recuperación
                extracted = self._try_extract_json(llm_response)
                if extracted:
                    try:
                        response_data = json.loads(extracted)
                        logger.info("✅ Recovery parse successful")
                    except Exception as recovery_error:
                        logger.error(f"❌ Recovery attempt also failed: {recovery_error}")
                        raise LLMError(f"Failed to parse remediation response as JSON: {e}")
                else:
                    raise LLMError(f"Failed to parse remediation response as JSON: {e}")
            
            # === PASO 4: Validar estructura de datos ===
            logger.debug(f"   Response keys: {list(response_data.keys())}")
            
            if not isinstance(response_data, dict):
                raise ValueError(f"Response is not a dict: {type(response_data)}")
            
            # Verificar campos requeridos
            required_fields = ['vulnerability_type', 'priority_level', 'steps']
            missing = [f for f in required_fields if f not in response_data]
            
            if missing:
                available = list(response_data.keys())
                raise ValueError(f"Missing required fields: {missing}. Available: {available}")
            
            # Verificar que steps tenga contenido
            if not response_data['steps'] or len(response_data['steps']) < 1:
                raise ValueError("Response has no remediation steps")
            
            # === PASO 5: Normalizar datos si es necesario ===
            # Asegurar que vulnerability_id existe
            if 'vulnerability_id' not in response_data:
                response_data['vulnerability_id'] = f"{vuln_type or 'unknown'}-remediation-{int(time.time())}"
                logger.warning(f"⚠️  Added missing vulnerability_id: {response_data['vulnerability_id']}")

            # Asegurar que llm_model_used existe
            if 'llm_model_used' not in response_data:
                response_data['llm_model_used'] = 'meta-llama/llama-3-3-70b-instruct'
                logger.debug("   Added default llm_model_used")
            
            # === PASO 6: Crear RemediationPlan (Pydantic validará) ===
            remediation_plan = RemediationPlan(**response_data)
            
            # === PASO 7: Validar calidad de los steps ===
            for i, step in enumerate(remediation_plan.steps, 1):
                desc_length = len(step.description)
                if desc_length < 50:
                    logger.warning(f"⚠️  Step {i} has short description ({desc_length} chars)")
                if not step.title or len(step.title) < 10:
                    logger.warning(f"⚠️  Step {i} has very short title")
            
            # === PASO 8: Log resultados ===
            logger.info(f"✅ RemediationPlan created successfully")
            logger.info(f"   Vulnerability: {remediation_plan.vulnerability_id}")
            logger.info(f"   Type: {remediation_plan.vulnerability_type.value}")
            logger.info(f"   Priority: {remediation_plan.priority_level}")
            logger.info(f"   Steps: {len(remediation_plan.steps)}")
            logger.info(f"   Estimated hours: {remediation_plan.total_estimated_hours}h")
            logger.info(f"   Complexity: {remediation_plan.complexity_score}/10")
            
            return remediation_plan
            
        except (ValueError, TypeError) as e:
            logger.error(f"❌ Validation error: {e}")
            raise LLMError(f"Invalid remediation response structure: {e}")
            
        except Exception as e:
            logger.error(f"❌ Unexpected parsing error: {e}")
            logger.exception("Full traceback:")
            raise LLMError(f"Failed to parse remediation response: {e}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_llm_client(provider: str = "watsonx", enable_debug: bool = False) -> LLMClient:
    """
    Factory function para crear cliente LLM
    
    Args:
        provider: Provider a usar ("watsonx" o "openai")
        enable_debug: Habilitar modo debug
        
    Returns:
        LLMClient configurado
        
    Example:
        >>> client = create_llm_client(provider="watsonx", enable_debug=True)
        >>> result = await client.analyze_vulnerabilities(data)
    """
    return LLMClient(primary_provider=provider, enable_debug=enable_debug)


def validate_api_key() -> bool:
    """
    Validar que la API key esté configurada
    
    Returns:
        True si la API key está presente
    """
    api_key = os.getenv("RESEARCH_API_KEY", "")
    return bool(api_key and len(api_key) > 0)


# ============================================================================
# TESTING & DEBUGGING
# ============================================================================

async def test_llm_connection(provider: str = "watsonx") -> Dict[str, Any]:
    """
    Probar conexión con el LLM
    
    Args:
        provider: Provider a probar
        
    Returns:
        Dict con resultados de la prueba
        
    Example:
        >>> result = await test_llm_connection("watsonx")
        >>> print(f"Status: {result['status']}")
    """
    
    try:
        logger.info(f"🧪 Testing LLM connection to {provider}...")
        
        client = LLMClient(primary_provider=provider)
        
        # Test simple: pedir que devuelva JSON básico
        test_message = """Return only this JSON object with no additional text:
{
  "test": "success",
  "timestamp": "2024-01-01T00:00:00Z",
  "message": "Connection test successful"
}"""
        
        start_time = time.time()
        response = await client._call_research_api(test_message, temperature=0.0)
        duration = time.time() - start_time
        
        # Intentar parsear
        cleaned = client._clean_json_response(response)
        parsed = json.loads(cleaned)
        
        result = {
            "status": "success",
            "provider": provider,
            "duration_seconds": round(duration, 2),
            "response_length": len(response),
            "parsed_successfully": True,
            "response_preview": str(parsed)[:200]
        }
        
        logger.info(f"✅ Connection test successful")
        return result
        
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return {
            "status": "failed",
            "provider": provider,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ============================================================================
# MAIN - FOR TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test básico del cliente LLM
    
    Usage:
        python infrastructure/llm/client.py
    """
    
    import asyncio
    from shared.logger import setup_logging
    
    # Setup logging
    setup_logging(log_level="DEBUG")
    
    async def main():
        print("\n" + "="*70)
        print("🤖 LLM CLIENT TEST")
        print("="*70 + "\n")
        
        # Test 1: Validar API key
        print("1️⃣  Testing API key validation...")
        if validate_api_key():
            print("   ✅ API key is configured\n")
        else:
            print("   ❌ API key is NOT configured")
            print("   Set RESEARCH_API_KEY environment variable\n")
            return
        
        # Test 2: Test conexión
        print("2️⃣  Testing connection...")
        result = await test_llm_connection("watsonx")
        print(f"   Status: {result['status']}")
        if result['status'] == 'success':
            print(f"   Duration: {result['duration_seconds']}s")
            print(f"   Response length: {result['response_length']} chars")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}\n")
            return
        
        # Test 3: Test triage simple
        print("\n3️⃣  Testing triage analysis...")
        client = LLMClient(primary_provider="watsonx", enable_debug=False)
        
        test_vulnerabilities = """## VULNERABILITY 1
- ID: test-vuln-001
- TYPE: SQL Injection
- SEVERITY: HIGH
- FILE: test.py:42
- TITLE: SQL Injection in login function
- DESCRIPTION: User input is directly concatenated into SQL query without sanitization
- CODE: cursor.execute("SELECT * FROM users WHERE username='" + username + "'")"""
        
        try:
            result = await client.analyze_vulnerabilities(test_vulnerabilities, language="python")
            print(f"   ✅ Triage successful")
            print(f"   Total analyzed: {result.total_analyzed}")
            print(f"   Confirmed: {result.confirmed_count}")
            print(f"   False positives: {result.false_positive_count}")
        except Exception as e:
            print(f"   ❌ Triage failed: {e}")
        
        # Test 4: Test remediation simple
        print("\n4️⃣  Testing remediation generation...")
        
        test_vulnerability = """## VULNERABILITY
- ID: test-vuln-001
- TYPE: SQL Injection
- SEVERITY: HIGH
- FILE: test.py:42
- TITLE: SQL Injection in login function
- DESCRIPTION: User input is directly concatenated into SQL query
- CODE: cursor.execute("SELECT * FROM users WHERE username='" + username + "'")"""
        
        try:
            result = await client.generate_remediation_plan(
                test_vulnerability,
                vuln_type="SQL Injection",
                language="python",
                severity="HIGH"
            )
            print(f"   ✅ Remediation successful")
            print(f"   Priority: {result.priority_level}")
            print(f"   Steps: {len(result.steps)}")
            print(f"   Estimated hours: {result.total_estimated_hours}h")
        except Exception as e:
            print(f"   ❌ Remediation failed: {e}")
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70 + "\n")
    
    # Ejecutar tests
    asyncio.run(main())

    