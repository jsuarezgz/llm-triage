# infrastructure/config.py - VERSIÓN SIMPLIFICADA TEMPORAL
import os
from typing import Optional, Dict, Any

class UnifiedSettings:
    """Configuración simplificada sin Pydantic Settings"""
    
    def __init__(self):
        # 🔑 API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.watsonx_api_key = os.getenv("RESEARCH_API_KEY")
        
        # 🤖 LLM Configuration
        self.llm_primary_provider = os.getenv("LLM_PRIMARY_PROVIDER", "openai")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT", "180"))
        
        # 🧩 Chunking Configuration
        self.chunking_max_vulnerabilities = int(os.getenv("CHUNKING_MAX_VULNS", "5"))
        self.chunking_max_size_bytes = int(os.getenv("CHUNKING_MAX_SIZE", "8000"))
        self.chunking_overlap = int(os.getenv("CHUNKING_OVERLAP", "1"))
        self.chunking_min_size = int(os.getenv("CHUNKING_MIN_SIZE", "3"))
        
        # 💾 Cache Configuration
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "24"))
        self.cache_directory = os.getenv("CACHE_DIR", ".security_cache")
        
        # 🔒 Security Configuration
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        self.input_validation_enabled = os.getenv("INPUT_VALIDATION", "true").lower() == "true"
        
        # 📊 Reporting Configuration
        self.report_max_code_length = int(os.getenv("REPORT_MAX_CODE_LENGTH", "1000"))
        
        # 📈 Observability
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    
    @property
    def has_llm_provider(self) -> bool:
        """Check if at least one LLM provider is configured"""
        return bool(self.openai_api_key or self.watsonx_api_key)
    
    @property
    def chunking_config(self) -> Dict[str, Any]:
        """Get chunking configuration as dict"""
        return {
            "max_vulnerabilities_per_chunk": self.chunking_max_vulnerabilities,
            "max_size_bytes": self.chunking_max_size_bytes,
            "overlap_vulnerabilities": self.chunking_overlap,
            "min_chunk_size": self.chunking_min_size
        }
    
    def get_available_llm_provider(self) -> str:
        """Get the first available LLM provider"""
        if self.llm_primary_provider == "openai" and self.openai_api_key:
            return "openai"
        elif self.llm_primary_provider == "watsonx" and self.watsonx_api_key:
            return "watsonx"
        elif self.openai_api_key:
            return "openai"
        elif self.watsonx_api_key:
            return "watsonx"
        else:
            raise ValueError("No LLM provider configured")

# Global settings instance
settings = UnifiedSettings()
