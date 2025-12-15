# application/factory.py - ACTUALIZADO CON CONTROL DE DEBUG
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
    """Factory optimizado con control de debug automático"""
    
    def __init__(self, enable_cache: bool = True, log_level: str = "INFO"):
        # Setup logging
        setup_logging(log_level)
        
        # Initialize shared components
        self.settings = settings
        self.metrics = MetricsCollector() if settings.metrics_enabled else None
        self.cache = AnalysisCache(settings.cache_directory, settings.cache_ttl_hours) if enable_cache else None
        
        # Control de debug
        self.debug_mode = False
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info(f"ServiceFactory initialized with {settings.get_available_llm_provider()}")
    
    def enable_debug_mode(self):
        """Habilitar modo debug - será llamado desde el debugger"""
        self.debug_mode = True
        logger.info("🔍 Debug mode enabled in ServiceFactory")
    
    def disable_debug_mode(self):
        """Deshabilitar modo debug"""
        self.debug_mode = False
        logger.info("🔍 Debug mode disabled in ServiceFactory")
    
    def _validate_configuration(self) -> None:
        """Validate system configuration"""
        if not self.settings.has_llm_provider:
            logger.warning("No LLM providers configured - system will run in basic mode")
        else:
            logger.info(f"LLM provider available: {self.settings.get_available_llm_provider()}")
    
    def create_scanner_service(self) -> ScannerService:
        return ScannerService(
            cache=self.cache,
            enable_deduplication=getattr(self, 'enable_dedup', True),
            dedup_strategy=getattr(self, 'dedup_strategy', 'moderate')
        )
    
    def create_llm_client(self) -> Optional[LLMClient]:
        """Create LLM client with debug control"""
        if not self.settings.has_llm_provider:
            return None
        
        try:
            provider = self.settings.get_available_llm_provider()
            # Pasar el estado de debug al cliente
            client = LLMClient(primary_provider=provider, enable_debug=self.debug_mode)
            
            # Si el debug está habilitado, registrar el cliente automáticamente
            if self.debug_mode:
                try:
                    from debug.llm_debugger import register_llm_client_for_debug
                    register_llm_client_for_debug(client)
                except ImportError:
                    logger.warning("Debug module not available")
            
            return client
        except Exception as e:
            logger.error(f"Failed to create LLM client: {e}")
            return None
   
    def create_triage_service(self) -> Optional[TriageService]:
        """Create triage service with LLM client"""
        llm_client = self.create_llm_client()
        if not llm_client:
            return None
        
        return TriageService(llm_client=llm_client, metrics=self.metrics)
    
    def create_remediation_service(self) -> Optional[RemediationService]:
        """Create remediation service with LLM client"""
        llm_client = self.create_llm_client()
        if not llm_client:
            return None
        
        return RemediationService(llm_client=llm_client, metrics=self.metrics)
    
    def create_reporter_service(self) -> ReporterService:
        """Create reporter service"""
        return ReporterService(metrics=self.metrics)
    
    def create_chunker(self) -> OptimizedChunker:
        """Create optimized chunker"""
        return OptimizedChunker(self.settings.chunking_config)
    
    def get_metrics(self) -> Optional[MetricsCollector]:
        """Get metrics collector"""
        return self.metrics

# Convenience function
def create_factory() -> ServiceFactory:
    """Create factory with default configuration"""
    return ServiceFactory(
        enable_cache=settings.cache_enabled,
        log_level=settings.log_level
    )

# Factory con debug habilitado - para uso desde debugger
def create_debug_factory() -> ServiceFactory:
    """Create factory with debug enabled"""
    factory = create_factory()
    factory.enable_debug_mode()
    return factory
