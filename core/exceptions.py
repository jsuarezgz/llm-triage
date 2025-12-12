# core/exceptions.py
"""Excepciones específicas del dominio"""
class SecurityAnalysisError(Exception):
    """Excepción base del sistema"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
class ValidationError(SecurityAnalysisError):
    """Error de validación de datos"""
    pass
class ParsingError(SecurityAnalysisError):
    """Error de parsing de vulnerabilidades"""
    pass
class LLMError(SecurityAnalysisError):
    """Error del proveedor LLM"""
    pass
class ChunkingError(SecurityAnalysisError):
    """Error en el proceso de chunking"""
    pass