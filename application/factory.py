# application/factory.py
"""
Service Factory - Clean & Simple
================================

Responsibilities:
- Create and configure services
- Handle provider overrides from CLI
- Manage shared dependencies (cache, metrics)
"""

import logging
from typing import Optional

from core.services.scanner import ScannerService
from core.services.triage import TriageService
from core.services.remediation import RemediationService
from core.services.reporter import ReporterService
from infrastructure.llm.client import LLMClient
from infrastructure.cache import AnalysisCache
from infrastructure.config import settings
from adapters.processing.chunker import OptimizedChunker
from shared.metrics import MetricsCollector
from shared.logger import setup_logging

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Simplified service factory with clean dependencies"""
    
    def __init__(
        self,
        enable_cache: bool = True,
        log_level: str = "INFO",
        llm_provider_override: Optional[str] = None,
        llm_model_override: Optional[str] = None
    ):
        # Setup logging
        setup_logging(log_level)
        
        # Store settings reference
        self.settings = settings
        
        # Overrides from CLI
        self.llm_provider_override = llm_provider_override
        self.llm_model_override = llm_model_override
        
        # Shared components
        self.metrics = MetricsCollector() if settings.metrics_enabled else None
        self.cache = self._create_cache() if enable_cache else None
        
        # Deduplication config (set by CLI)
        self.enable_dedup = True
        self.dedup_strategy = 'moderate'
        
        # Debug mode
        self.debug_mode = False
        
        # Validate and log
        self._log_initialization()
    
    def _create_cache(self) -> Optional[AnalysisCache]:
        """Create cache instance"""
        try:
            return AnalysisCache(
                cache_dir=settings.cache_directory,
                ttl_hours=settings.cache_ttl_hours
            )
        except Exception as e:
            logger.warning(f"Cache creation failed: {e}")
            return None
    
    def _log_initialization(self):
        """Log factory initialization"""
        provider = self._get_effective_provider()
        logger.info(f"🏭 Factory initialized: {provider}")
        
        if self.llm_provider_override:
            logger.info(f"   Provider override: {self.llm_provider_override}")
        
        if self.llm_model_override:
            logger.info(f"   Model override: {self.llm_model_override}")
    
    def _get_effective_provider(self) -> str:
        """Get effective LLM provider"""
        if self.llm_provider_override:
            return self.llm_provider_override
        
        if settings.has_llm_provider:
            return settings.get_available_llm_provider()
        
        return "none"
    
    # ════════════════════════════════════════════════════════════════
    # SERVICE CREATION
    # ════════════════════════════════════════════════════════════════
    
    def create_scanner_service(self) -> ScannerService:
        """Create scanner service"""
        return ScannerService(
            cache=self.cache,
            enable_deduplication=self.enable_dedup,
            dedup_strategy=self.dedup_strategy
        )
    
    def create_llm_client(self) -> Optional[LLMClient]:
        """Create LLM client with overrides"""
        # Determine provider
        if self.llm_provider_override:
            provider = self.llm_provider_override
        else:
            if not settings.has_llm_provider:
                return None
            provider = settings.get_available_llm_provider()
        
        try:
            # Create client
            client = LLMClient(
                llm_provider=provider,
                enable_debug=self.debug_mode
            )
            
            # Override model if specified
            if self.llm_model_override:
                logger.info(f"🔄 Model override: {self.llm_model_override}")
                client.model_name = self.llm_model_override
                client.model[provider] = self.llm_model_override
            
            return client
            
        except Exception as e:
            logger.error(f"Failed to create LLM client: {e}")
            return None
    
    def create_triage_service(self) -> Optional[TriageService]:
        """Create triage service"""
        llm_client = self.create_llm_client()
        if not llm_client:
            return None
        
        return TriageService(llm_client=llm_client, metrics=self.metrics)
    
    def create_remediation_service(self) -> Optional[RemediationService]:
        """Create remediation service"""
        llm_client = self.create_llm_client()
        if not llm_client:
            return None
        
        return RemediationService(llm_client=llm_client, metrics=self.metrics)
    
    def create_reporter_service(self) -> ReporterService:
        """Create reporter service"""
        return ReporterService(metrics=self.metrics)
    
    def create_chunker(self) -> OptimizedChunker:
        """Create chunker"""
        return OptimizedChunker(settings.chunking_config)
    
    def get_metrics(self) -> Optional[MetricsCollector]:
        """Get metrics collector"""
        return self.metrics
    
    # ════════════════════════════════════════════════════════════════
    # DEBUG MODE
    # ════════════════════════════════════════════════════════════════
    
    def enable_debug_mode(self):
        """Enable debug mode"""
        self.debug_mode = True
        logger.info("🔍 Debug mode enabled")
    
    def disable_debug_mode(self):
        """Disable debug mode"""
        self.debug_mode = False
        logger.info("🔍 Debug mode disabled")


# ════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ════════════════════════════════════════════════════════════════════

def create_factory(
    llm_provider_override: Optional[str] = None,
    llm_model_override: Optional[str] = None
) -> ServiceFactory:
    """
    Create factory with optional CLI overrides
    
    Args:
        llm_provider_override: Override provider (openai|watsonx)
        llm_model_override: Override model name
    
    Returns:
        Configured ServiceFactory
    """
    return ServiceFactory(
        enable_cache=settings.cache_enabled,
        log_level=settings.log_level,
        llm_provider_override=llm_provider_override,
        llm_model_override=llm_model_override
    )


def create_debug_factory(
    llm_provider_override: Optional[str] = None
) -> ServiceFactory:
    """Create factory with debug enabled"""
    factory = create_factory(llm_provider_override=llm_provider_override)
    factory.enable_debug_mode()
    return factory
