# infrastructure/llm/client.py
"""
LLM Client - Clean & Optimized
==============================

Responsibilities:
- HTTP communication with LLM providers
- Request/response handling
- Retry logic
- Error handling

Does NOT handle:
- JSON parsing (delegated to response_parser)
- Prompt construction (delegated to prompts)
"""

import requests
import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional

from core.models import TriageResult, RemediationPlan
from core.exceptions import LLMError
from infrastructure.config import settings
from .response_parser import LLMResponseParser
from .prompts import PromptManager

logger = logging.getLogger(__name__)


class LLMClient:
    """Simplified LLM client with clean separation of concerns"""
    
    def __init__(self, llm_provider: str = "watsonx", enable_debug: bool = False):
        """
        Initialize LLM Client
        
        Args:
            llm_provider: "openai" or "watsonx"
            enable_debug: Enable debug logging
        """
        self.llm_provider = llm_provider.lower()
        self.debug_enabled = enable_debug
        
        # Load configuration from settings
        try:
            self.config = settings.get_llm_config(self.llm_provider)
        except ValueError as e:
            raise ValueError(f"Cannot initialize {llm_provider}: {e}")
        
        # Extract config
        self.api_key = self.config["api_key"]
        self.model_name = self.config["model"]
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]
        self.timeout = self.config["timeout"]
        
        # Provider-specific config
        if self.llm_provider == "watsonx":
            self.base_url = self.config["base_url"]
            self.user_email = self.config["user_email"]
            self.endpoint = "/research/llm/wx/clients"
        else:  # openai
            self.base_url = self.config["base_url"]
            self.endpoint = "/research/llm/openai/clients"
        
        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        })
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay_base = 2
        
        # Dependencies
        self.parser = LLMResponseParser(debug_enabled=enable_debug)
        self.prompt_manager = PromptManager()
        
        logger.info(f"🤖 LLM Client initialized: {self.llm_provider}")
        logger.info(f"   Model: {self.model_name}")
        logger.info(f"   Timeout: {self.timeout}s")
    
    # ════════════════════════════════════════════════════════════════
    # PUBLIC API - High-level methods
    # ════════════════════════════════════════════════════════════════
    
    async def analyze_vulnerabilities(
        self,
        vulnerabilities_data: str,
        language: Optional[str] = None
    ) -> TriageResult:
        """
        Analyze vulnerabilities for triage
        
        Args:
            vulnerabilities_ Formatted vulnerability data
            language: Programming language
        
        Returns:
            TriageResult with decisions
        """
        logger.info("🔍 Starting triage analysis")
        
        # Get prompt
        system_prompt = self.prompt_manager.get_triage_system_prompt(language)
        full_message = self._build_message(system_prompt, vulnerabilities_data)
        
        # Call LLM with retry
        start = time.time()
        response = await self._call_with_retry(full_message, temperature=0.1)
        duration = time.time() - start
        
        logger.info(f"✅ Response received in {duration:.2f}s")
        
        # Parse response
        result = self.parser.parse_triage_response(response, vulnerabilities_data)
        
        return result
    
    async def generate_remediation_plan(
        self,
        vulnerability_data: str,
        vuln_type: str = None,
        language: Optional[str] = None,
        severity: str = "HIGH"
    ) -> RemediationPlan:
        """
        Generate remediation plan
        
        Args:
            vulnerability_ Vulnerability details
            vuln_type: Type of vulnerability
            language: Programming language
            severity: Severity level
        
        Returns:
            RemediationPlan with steps
        """
        logger.info("🛠️  Generating remediation plan")
        
        # Get prompt
        system_prompt = self.prompt_manager.get_remediation_system_prompt(
            vuln_type=vuln_type or "Security Issue",
            language=language,
            severity=severity
        )
        full_message = self._build_message(system_prompt, vulnerability_data)
        
        # Call LLM with retry
        start = time.time()
        response = await self._call_with_retry(full_message, temperature=0.2)
        duration = time.time() - start
        
        logger.info(f"✅ Response received in {duration:.2f}s")
        
        # Parse response
        result = self.parser.parse_remediation_response(response, vuln_type, language)
        
        return result
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE API - HTTP communication
    # ════════════════════════════════════════════════════════════════
    
    async def _call_with_retry(
        self,
        message: str,
        temperature: float = 0.1
    ) -> str:
        """
        Call LLM with exponential backoff retry
        
        Args:
            message: Full message to send
            temperature: Temperature setting
        
        Returns:
            LLM response text
        
        Raises:
            LLMError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{self.max_retries}")
                
                response = await self._call_api(message, temperature)
                
                if attempt > 0:
                    logger.info(f"✅ Succeeded on retry {attempt + 1}")
                
                return response
                
            except LLMError as e:
                last_error = e
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay_base ** (attempt + 1)
                    logger.warning(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    logger.warning(f"⏳ Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"❌ All {self.max_retries} attempts failed")
        
        raise last_error or LLMError(f"All {self.max_retries} attempts failed")
    
    async def _call_api(self, message: str, temperature: float) -> str:
        """
        Single API call (no retry)
        
        Args:
            message: Message to send
            temperature: Temperature setting
        
        Returns:
            Response content
        
        Raises:
            LLMError: On any API error
        """
        url = f"{self.base_url}{self.endpoint}"
        session_uuid = str(uuid.uuid4())
        
        # Build payload
        payload = {
            "message": {"role": "user", "content": message},
            "temperature": temperature,
            "model": self.model_name,
            "prompt": None,
            "uuid": session_uuid,
            "language": "es",
            "user": getattr(self, 'user_email', 'user@research.com')
        }
        
        start = time.time()
        
        try:
            logger.debug(f"📡 POST {url}")
            logger.debug(f"   Model: {self.model_name}")
            logger.debug(f"   Message: {len(message):,} chars")
            
            # Make request
            response = self.session.post(url, json=payload, timeout=self.timeout)
            duration = time.time() - start
            
            logger.info(f"📡 HTTP {response.status_code} ({duration:.2f}s)")
            
            # Check status
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:500]}"
                raise LLMError(error_msg)
            
            # Extract content
            content = self._extract_content(response)
            
            if not content or not content.strip():
                raise LLMError("Empty response from LLM")
            
            logger.info(f"✅ Received {len(content):,} chars")
            return content
            
        except requests.exceptions.Timeout:
            raise LLMError(f"Request timeout after {self.timeout}s")
        
        except requests.exceptions.ConnectionError as e:
            raise LLMError(f"Connection error: {e}")
        
        except LLMError:
            raise
        
        except Exception as e:
            raise LLMError(f"Unexpected error: {e}")
    
    def _extract_content(self, response: requests.Response) -> str:
        """
        Extract content from API response
        
        Args:
            response: HTTP response
        
        Returns:
            Extracted content string
        """
        # Try JSON first
        try:
            data = response.json()
            
            # Search for content in common fields
            for field in ['content', 'response', 'message', 'text', 'output', 'result']:
                if field in data:
                    value = data[field]
                    
                    # Recursive extraction for nested dicts
                    if isinstance(value, dict):
                        nested = self._extract_from_dict(value)
                        if nested:
                            return nested
                    elif value:
                        return str(value)
            
            # No known field, return as JSON string
            return response.text
            
        except ValueError:
            # Not JSON, return as text
            return response.text
    
    def _extract_from_dict(self, data: Dict) -> Optional[str]:
        """Recursively extract content from nested dict"""
        for field in ['content', 'response', 'message', 'text']:
            if field in data and data[field]:
                return str(data[field])
        return None
    
    def _build_message(self, system_prompt: str, user_data: str) -> str:
        """Build complete message from prompt and data"""
        return f"""{system_prompt}

# DATA TO ANALYZE

{user_data}

# INSTRUCTIONS

Return ONLY valid JSON with no markdown wrappers.
Ensure all required fields are present.
"""
    
    def __repr__(self) -> str:
        return f"<LLMClient: {self.llm_provider}, model={self.model_name}>"
