# infrastructure/llm/client.py
"""
🤖 LLM Client - Comunicación con Research API

Features:
- ✅ Comunicación HTTP con Research API
- ✅ Retry logic con backoff exponencial
- ✅ Debug mode integrado
- ✅ Manejo robusto de errores
- ✅ Métodos de alto nivel para triage y remediation
"""

import requests
import json
import logging
import time
import os
import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from core.models import TriageResult, RemediationPlan
from core.exceptions import LLMError
from .response_parser import LLMResponseParser
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Cliente LLM para Research API
    
    Responsabilidades:
    - Comunicación HTTP con Research API
    - Manejo de reintentos y timeouts
    - Control de debug mode
    - Métodos de alto nivel (analyze_vulnerabilities, generate_remediation_plan)
    
    No maneja parsing - delega a LLMResponseParser
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
        
        # Parser y prompt manager
        self.parser = LLMResponseParser(debug_enabled=enable_debug)
        self.prompt_manager = PromptManager()
        
        # Configurar sesión HTTP
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
        self.parser.debug_enabled = True
        
        try:
            from debug.llm_debugger import get_debugger
            self.debugger = get_debugger()
            logger.info("🔍 Debug mode ENABLED for LLM Client")
        except ImportError:
            logger.warning("⚠️ Debug module not available")
            self.debug_enabled = False
    
    
    def disable_debug_mode(self):
        """Deshabilitar modo debug"""
        self.debug_enabled = False
        self.parser.debug_enabled = False
        self.debugger = None
        logger.info("🔍 Debug mode DISABLED for LLM Client")
    
    
    # ============================================================================
    # PUBLIC API - HIGH-LEVEL METHODS
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
            
            # Obtener prompt optimizado
            system_prompt = self.prompt_manager.get_triage_system_prompt(language=language)
            logger.info(f"📝 Using enhanced triage prompt ({len(system_prompt)} chars)")
            
            # Construir mensaje completo
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
            
            # Parsear respuesta (delegar a parser)
            result = self.parser.parse_triage_response(response, vulnerabilities_data)
            
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
            logger.info(f"🛠️ Starting remediation plan generation")
            logger.debug(f"   Type: {vuln_type or 'Unknown'}")
            logger.debug(f"   Language: {language or 'Generic'}")
            logger.debug(f"   Severity: {severity}")
            
            # Obtener prompt optimizado
            system_prompt = self.prompt_manager.get_remediation_system_prompt(
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
            
            # Parsear respuesta (delegar a parser)
            result = self.parser.parse_remediation_response(response, vuln_type, language)
            
            logger.info(f"✅ Remediation plan created successfully")
            logger.info(f"   Priority: {result.priority_level}")
            logger.info(f"   Steps: {len(result.steps)}")
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
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
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
            logger.info(f"⏱️ Duration: {duration:.2f}s")
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
                logger.warning(f"⚠️ Response is not JSON (using as plain text): {e}")
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
            logger.warning(f"⚠️ No standard content field found")
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
# FACTORY FUNCTIONS
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
        cleaned = client.parser.clean_json_response(response)
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
        print("\n" + "="*70 + "\n")
        print("🤖 LLM Client Test Suite")
        print("="*70 + "\n")
        
        # Test 1: Validar API key
        print("1️⃣ Testing API key validation...")
        if validate_api_key():
            print("   ✅ API key is configured\n")
        else:
            print("   ❌ API key is NOT configured")
            print("   Set RESEARCH_API_KEY environment variable\n")
            return
        
        # Test 2: Test conexión
        print("2️⃣ Testing connection...")
        result = await test_llm_connection("watsonx")
        print(f"   Status: {result['status']}")
        if result['status'] == 'success':
            print(f"   Duration: {result['duration_seconds']}s")
            print(f"   Response length: {result['response_length']} chars")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}\n")
            return
        
        # Test 3: Test triage simple
        print("\n3️⃣ Testing triage analysis...")
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
        print("\n4️⃣ Testing remediation generation...")
        
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
        print("✅ Test Suite Completed")
        print("="*70 + "\n")
    
    # Ejecutar tests
    asyncio.run(main())

