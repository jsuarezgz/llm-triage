# infrastructure/llm/exceptions.py
"""
🚨 Excepciones específicas para LLM Client
"""

class LLMClientError(Exception):
    """Error base para cliente LLM"""
    pass

class LLMConnectionError(LLMClientError):
    """Error de conexión con LLM"""
    pass

class LLMTimeoutError(LLMClientError):
    """Timeout en llamada LLM"""
    pass

class LLMParsingError(LLMClientError):
    """Error al parsear respuesta LLM"""
    def __init__(self, message: str, raw_response: str = None, partial_data: dict = None):
        self.raw_response = raw_response
        self.partial_data = partial_data
        super().__init__(message)

class LLMValidationError(LLMClientError):
    """Error de validación de respuesta LLM"""
    def __init__(self, message: str, missing_fields: list = None, available_fields: list = None):
        self.missing_fields = missing_fields or []
        self.available_fields = available_fields or []
        super().__init__(message)
