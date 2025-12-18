# adapters/parsers/parser_factory.py
"""
Parser Factory - Selecciona el parser correcto automáticamente
==============================================================
"""

import logging
from typing import Dict, Any, List, Optional

from .base import BaseVulnerabilityParser
from .abap_parser import ABAPParser
from .semgrep_parser import SemgrepParser
from core.models import Vulnerability
from core.exceptions import ParsingError

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory para detectar y usar el parser correcto
    
    Sigue el patrón Chain of Responsibility:
    - Cada parser intenta detectar si puede parsear los datos
    - El primer parser que pueda, será usado
    - Si ninguno puede, se lanza excepción
    """
    
    def __init__(self):
        # Registrar parsers en orden de prioridad
        self._parsers: List[BaseVulnerabilityParser] = [
            SemgrepParser(),  # Más común
            ABAPParser(),
            # Agregar más parsers aquí:
            # SonarQubeParser(),
            # CheckmarxParser(),
            # BanditParser(),
        ]
        
        logger.info(f"✅ ParserFactory initialized with {len(self._parsers)} parsers")
    
    def parse(
        self,
        data: Dict[str, Any],
        tool_hint: Optional[str] = None
    ) -> List[Vulnerability]:
        """
        Parsea datos usando el parser correcto
        
        Args:
             Datos JSON crudos
            tool_hint: Hint opcional del tool (ej: "semgrep", "abap")
        
        Returns:
            Lista de vulnerabilidades parseadas
        
        Raises:
            ParsingError: Si no se encuentra parser compatible
        
        Examples:
            >>> factory = ParserFactory()
            >>> vulns = factory.parse(json_data)
            >>> # O con hint:
            >>> vulns = factory.parse(json_data, tool_hint="semgrep")
        """
        # Si hay hint, intentar con ese parser primero
        if tool_hint:
            parser = self._get_parser_by_hint(tool_hint)
            if parser and parser.can_parse(data):
                logger.info(f"🎯 Using hinted parser: {parser.parser_name}")
                return self._safe_parse(parser, data)
        
        # Detectar automáticamente
        for parser in self._parsers:
            try:
                if parser.can_parse(data):
                    logger.info(f"🎯 Auto-detected parser: {parser.parser_name}")
                    return self._safe_parse(parser, data)
            except Exception as e:
                logger.warning(f"⚠️  Parser {parser.parser_name} detection failed: {e}")
                continue
        
        # No se encontró parser compatible
        raise ParsingError(
            "No compatible parser found for the provided data. "
            "Supported formats: Semgrep, ABAP Security Scanner"
        )
    
    def detect_format(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Detecta el formato de los datos sin parsear
        
        Args:
             Datos JSON crudos
        
        Returns:
            Nombre del formato detectado o None
        
        Examples:
            >>> factory = ParserFactory()
            >>> format_name = factory.detect_format(json_data)
            >>> print(format_name)  # "Semgrep" or "ABAP Security Scanner"
        """
        for parser in self._parsers:
            try:
                if parser.can_parse(data):
                    return parser.metadata.name if parser.metadata else parser.parser_name
            except Exception:
                continue
        
        return None
    
    def get_supported_formats(self) -> List[str]:
        """
        Obtiene lista de formatos soportados
        
        Returns:
            Lista de nombres de parsers
        """
        return [
            parser.metadata.name if parser.metadata else parser.parser_name
            for parser in self._parsers
        ]
    
    def _get_parser_by_hint(self, hint: str) -> Optional[BaseVulnerabilityParser]:
        """
        Obtiene parser por hint de nombre
        
        Args:
            hint: Nombre del tool (case-insensitive)
        
        Returns:
            Parser correspondiente o None
        """
        hint_lower = hint.lower()
        
        for parser in self._parsers:
            parser_name = parser.parser_name.lower()
            
            # Coincidencia exacta
            if hint_lower in parser_name:
                return parser
            
            # Coincidencia en supported tools
            if parser.metadata:
                for tool in parser.metadata.supported_tools:
                    if hint_lower in tool.lower():
                        return parser
        
        return None
    
    def _safe_parse(
        self,
        parser: BaseVulnerabilityParser,
        data: Dict[str, Any]
    ) -> List[Vulnerability]:
        """
        Parsea datos de forma segura con manejo de errores
        
        Args:
            parser: Parser a usar
             Datos a parsear
        
        Returns:
            Lista de vulnerabilidades
        
        Raises:
            ParsingError: Si el parseo falla
        """
        try:
            vulnerabilities = parser.parse(data)
            
            logger.info(
                f"✅ Successfully parsed {len(vulnerabilities)} vulnerabilities "
                f"using {parser.parser_name}"
            )
            
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Parser {parser.parser_name} failed: {e}")
            raise ParsingError(f"Failed to parse data with {parser.parser_name}: {str(e)}")
