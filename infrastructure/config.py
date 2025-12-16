# infrastructure/config.py
"""
⚙️ Configuration Management - Simplified & Fixed
================================================
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Settings:
    """Simplified settings manager with smart defaults"""
    
    def __init__(self):
        """Load configuration from environment"""
        
        # Load .env if available
        self._load_dotenv()
        
        # ═══════════════════════════════════════════════════════════
        # LLM CONFIGURATION
        # ═══════════════════════════════════════════════════════════
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.watsonx_api_key = os.getenv("RESEARCH_API_KEY", "").strip()
        self.llm_primary_provider = os.getenv("LLM_PRIMARY_PROVIDER", "openai").lower()
        
        # LLM parameters
        self.llm_temperature = self._get_float("LLM_TEMPERATURE", 0.1)
        self.llm_max_tokens = self._get_int("LLM_MAX_TOKENS", 2048)
        self.llm_timeout = self._get_int("LLM_TIMEOUT", 180)
        self.llm_user_email = os.getenv("LLM_USER_EMAIL", "franciscojavier.suarez_css@research.com")
        
        # Models
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5")
        self.watsonx_model = os.getenv("WATSONX_MODEL", "meta-llama/llama-3-3-70b-instruct")
        
        # Research API URL
        self.research_api_url = os.getenv(
            "RESEARCH_API_URL",
            "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
        )
        
        # ═══════════════════════════════════════════════════════════
        # FEATURE FLAGS
        # ═══════════════════════════════════════════════════════════
        
        self.cache_enabled = self._get_bool("CACHE_ENABLED", True)
        self.metrics_enabled = self._get_bool("METRICS_ENABLED", True)
        self.dedup_enabled = self._get_bool("DEDUP_ENABLED", True)
        
        # ═══════════════════════════════════════════════════════════
        # PARAMETERS
        # ═══════════════════════════════════════════════════════════
        
        self.chunking_max_vulnerabilities = self._get_int("CHUNKING_MAX_VULNS", 5)
        self.cache_ttl_hours = self._get_int("CACHE_TTL_HOURS", 24)
        self.cache_directory = os.getenv("CACHE_DIR", ".security_cache")
        self.dedup_strategy = os.getenv("DEDUP_STRATEGY", "moderate").lower()
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # ═══════════════════════════════════════════════════════════
        # VALIDATE & LOG
        # ═══════════════════════════════════════════════════════════
        
        self._validate()
        self._log_config()
    
    # ════════════════════════════════════════════════════════════════
    # PROPERTIES
    # ════════════════════════════════════════════════════════════════
    
    @property
    def has_llm_provider(self) -> bool:
        """Check if at least one LLM provider is configured"""
        return bool(self.openai_api_key or self.watsonx_api_key)
    
    @property
    def chunking_config(self) -> Dict[str, Any]:
        """Get chunking configuration"""
        return {
            "max_vulnerabilities_per_chunk": self.chunking_max_vulnerabilities,
            "max_size_bytes": 8000,
            "overlap_vulnerabilities": 1,
            "min_chunk_size": 3
        }
    
    # ════════════════════════════════════════════════════════════════
    # PUBLIC API
    # ════════════════════════════════════════════════════════════════
    
    def get_available_llm_provider(self) -> str:
        """Get first available LLM provider"""
        # Priority 1: Primary provider if has key
        if self.llm_primary_provider == "openai" and self.openai_api_key:
            return "openai"
        
        if self.llm_primary_provider == "watsonx" and self.watsonx_api_key:
            return "watsonx"
        
        # Priority 2: Fallback to any available
        if self.openai_api_key:
            return "openai"
        
        if self.watsonx_api_key:
            return "watsonx"
        
        # No provider available
        raise ValueError(
            "No LLM provider configured. Set OPENAI_API_KEY or RESEARCH_API_KEY"
        )
    
    def has_provider(self, provider: str) -> bool:
        """Check if specific provider is available"""
        if provider.lower() == "openai":
            return bool(self.openai_api_key)
        elif provider.lower() == "watsonx":
            return bool(self.watsonx_api_key)
        return False
    
    def get_llm_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for specific provider"""
        if provider is None:
            provider = self.get_available_llm_provider()
        
        provider = provider.lower()
        
        if provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
                "timeout": self.llm_timeout,
                "base_url": self.research_api_url  # Research API también para OpenAI
            }
        
        elif provider == "watsonx":
            return {
                "provider": "watsonx",
                "api_key": self.watsonx_api_key,
                "model": self.watsonx_model,
                "temperature": self.llm_temperature,
                "max_tokens": self.llm_max_tokens,
                "timeout": self.llm_timeout,
                "base_url": self.research_api_url,
                "user_email": self.llm_user_email
            }
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    def _load_dotenv(self):
        """Load .env file if available"""
        try:
            from dotenv import load_dotenv
            if Path(".env").exists():
                load_dotenv()
        except ImportError:
            pass
    
    def _get_int(self, key: str, default: int) -> int:
        """Get integer from environment"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid int for {key}='{value}', using default: {default}")
            return default
    
    def _get_float(self, key: str, default: float) -> float:
        """Get float from environment"""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float for {key}='{value}', using default: {default}")
            return default
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get boolean from environment"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def _validate(self):
        """Validate configuration"""
        # Validate temperature
        if not (0.0 <= self.llm_temperature <= 2.0):
            logger.warning(f"Invalid temperature {self.llm_temperature}, using 0.1")
            self.llm_temperature = 0.1
        
        # Validate dedup strategy
        if self.dedup_strategy not in ('strict', 'moderate', 'loose'):
            logger.warning(f"Invalid dedup_strategy '{self.dedup_strategy}', using 'moderate'")
            self.dedup_strategy = 'moderate'
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level not in valid_levels:
            logger.warning(f"Invalid log_level '{self.log_level}', using 'INFO'")
            self.log_level = 'INFO'
        
        # Create cache directory
        if self.cache_enabled:
            Path(self.cache_directory).mkdir(parents=True, exist_ok=True)
    
    def _log_config(self):
        """Log configuration summary - FIXED"""
        # Don't log during initial setup if logger not configured
        try:
            logger.info("="*60)
            logger.info("⚙️  Configuration Loaded")
            logger.info("="*60)
            
            # LLM Status
            if self.has_llm_provider:
                try:
                    provider = self.get_available_llm_provider()
                    logger.info(f"🤖 LLM Provider: {provider.upper()}")
                    
                    config = self.get_llm_config(provider)
                    logger.info(f"   Model: {config['model']}")
                    logger.info(f"   Temperature: {config['temperature']}")
                    logger.info(f"   Max Tokens: {config['max_tokens']}")
                    logger.info(f"   Timeout: {config['timeout']}s")
                except ValueError:
                    logger.warning("⚠️  LLM: No provider configured")
            else:
                logger.warning("⚠️  LLM: No provider configured (basic mode only)")
            
            # Features
            logger.info("🔧 Features:")
            logger.info(f"   Cache: {'✅' if self.cache_enabled else '❌'}")
            logger.info(f"   Deduplication: {'✅' if self.dedup_enabled else '❌'} ({self.dedup_strategy})")
            logger.info(f"   Metrics: {'✅' if self.metrics_enabled else '❌'}")
            
            # Chunking
            logger.info("🧩 Chunking:")
            logger.info(f"   Max vulns/chunk: {self.chunking_max_vulnerabilities}")
            
            logger.info("="*60)
        except Exception as e:
            # Silently ignore logging errors during initialization
            pass
    
    def __repr__(self) -> str:
        """String representation"""
        provider_status = "configured" if self.has_llm_provider else "not configured"
        return f"<Settings: LLM={provider_status}, Log={self.log_level}>"


# ════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ════════════════════════════════════════════════════════════════════

settings = Settings()


# ════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def get_config() -> Settings:
    """Get global settings instance"""
    return settings


def reload_config() -> Settings:
    """Reload configuration"""
    global settings
    settings = Settings()
    return settings


def validate_llm_config(provider: str) -> bool:
    """Validate LLM provider configuration"""
    try:
        config = settings.get_llm_config(provider)
        return bool(config["api_key"])
    except (ValueError, KeyError):
        return False
