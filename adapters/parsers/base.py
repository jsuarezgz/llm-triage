# adapters/parsers/base.py
"""
Base Parser - Puerto (Interface) para parsers de vulnerabilidades
=================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from core.models import Vulnerability, SeverityLevel


@dataclass
class ParserMetadata:
    """Metadata del parser"""
    name: str
    version: str
    supported_tools: List[str]
    format_indicators: List[str]


class BaseVulnerabilityParser(ABC):
    """
    Puerto (Interface) para parsers de vulnerabilidades
    
    Todos los parsers deben implementar esta interfaz para
    garantizar consistencia y permitir intercambiabilidad.
    """
    
    def __init__(self):
        self.parser_name = self.__class__.__name__
        self.parser_version = "3.0"
        self.metadata: Optional[ParserMetadata] = None
    
    @abstractmethod
    def can_parse(self, data: Dict[str, Any]) -> bool:
        """
        Determina si este parser puede procesar los datos
        
        Args:
             Datos JSON crudos
        
        Returns:
            True si puede parsear, False en caso contrario
        """
        pass
    
    @abstractmethod
    def extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae la lista de findings del JSON
        
        Args:
             Datos JSON crudos
        
        Returns:
            Lista de findings crudos
        """
        pass
    
    @abstractmethod
    def parse_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """
        Parsea un finding individual a objeto Vulnerability del dominio
        
        Args:
            finding: Datos crudos del finding
            index: Índice del finding
        
        Returns:
            Objeto Vulnerability del dominio
        """
        pass
    
    def parse(self, data: Dict[str, Any]) -> List[Vulnerability]:
        """
        Método público de parseo (Template Method)
        
        Args:
             Datos JSON crudos
        
        Returns:
            Lista de vulnerabilidades del dominio
        """
        vulnerabilities = []
        
        # Validar que podemos parsear
        if not self.can_parse(data):
            return vulnerabilities
        
        # Extraer findings
        findings = self.extract_findings(data)
        
        # Parsear cada finding
        for index, finding in enumerate(findings, start=1):
            try:
                vuln = self.parse_finding(finding, index)
                if vuln:
                    vulnerabilities.append(vuln)
            except Exception as e:
                print(f"⚠️  [{self.parser_name}] Error parsing finding {index}: {e}")
                continue
        
        return vulnerabilities
    
    # Helper methods comunes
    @staticmethod
    def normalize_severity(severity_str: str) -> SeverityLevel:
        """Normaliza string de severidad a enum del dominio"""
        mapping = {
            'CRITICAL': SeverityLevel.CRITICAL,
            'HIGH': SeverityLevel.HIGH,
            'ERROR': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'WARNING': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW,
            'INFO': SeverityLevel.INFO,
        }
        return mapping.get(severity_str.upper(), SeverityLevel.MEDIUM)
    
    @staticmethod
    def normalize_cwe(cwe: Any) -> Optional[str]:
        """Normaliza CWE ID"""
        if not cwe:
            return None
        
        cwe_str = str(cwe).strip()
        
        if cwe_str.isdigit():
            return f"CWE-{cwe_str}"
        elif cwe_str.startswith("CWE-"):
            return cwe_str.split(":")[0].strip()
        
        return None
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Convierte valor a int de forma segura"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
