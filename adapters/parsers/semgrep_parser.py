# adapters/parsers/semgrep_parser.py
"""
Semgrep Parser - Adaptador para Semgrep
=======================================
"""

from typing import Dict, Any, List, Optional

from .base import BaseVulnerabilityParser, ParserMetadata
from .utils import FieldExtractor, VulnerabilityTypeDetector, ConfidenceCalculator
from core.models import Vulnerability


class SemgrepParser(BaseVulnerabilityParser):
    """
    Adapter para parsear resultados de Semgrep
    
    Soporta:
    - Formato JSON estándar de Semgrep
    - Formato de línea de comandos (--json)
    - Formato CI/CD
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = ParserMetadata(
            name="SemgrepParser",
            version="3.0",
            supported_tools=["Semgrep", "Semgrep OSS", "Semgrep Pro"],
            format_indicators=["results + errors", "check_id", "extra.metadata"]
        )
    
    def can_parse(self, data: Dict[str, Any]) -> bool:
        """
        Detecta si es formato Semgrep
        
        Indicadores:
        1. Tiene "results" y "errors" en raíz
        2. Los results tienen "check_id" y "extra"
        3. Versión de Semgrep en "version"
        """
        # Formato estándar
        if isinstance(data, dict):
            # Estructura típica
            if "results" in data:
                # Validar versión (opcional)
                if "version" in data:
                    return True
                
                # Validar estructura de results
                results = data["results"]
                if isinstance(results, list) and results:
                    first = results[0]
                    if "check_id" in first and "extra" in first:
                        return True
        
        # Lista directa de resultados Semgrep
        if isinstance(data, list) and data:
            first = data[0]
            if "check_id" in first and "extra" in first and "path" in first:
                return True
        
        return False
    
    def extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae findings de formato Semgrep"""
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        
        if isinstance(data, list):
            return data
        
        return []
    
    def parse_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """
        Parsea un finding de Semgrep a Vulnerability
        
        Estructura esperada:
        {
            "check_id": "java.sql-injection...",
            "path": "/path/to/file.java",
            "start": {"line": 42, "col": 10},
            "end": {"line": 42, "col": 50},
            "extra": {
                "message": "SQL Injection detected",
                "severity": "ERROR",
                "metadata": {
                    "cwe": ["CWE-89"],
                    "owasp": ["A03:2021"],
                    "confidence": "HIGH"
                }
            }
        }
        """
        extra = finding.get("extra", {})
        metadata = extra.get("metadata", {})
        start = finding.get("start", {})
        
        # ID único
        check_id = finding.get("check_id", f"SEMGREP-{index}")
        vuln_id = check_id
        
        # Título y descripción
        title = self._extract_title(check_id, extra)
        description = self._build_description(extra, metadata)
        
        # Severidad
        severity_str = extra.get("severity", "WARNING")
        severity = self.normalize_severity(severity_str)
        
        # Tipo de vulnerabilidad
        vuln_type = VulnerabilityTypeDetector.detect(
            check_id,
            extra.get("message", ""),
            str(metadata.get("category", ""))
        )
        
        # Ubicación
        file_path = finding.get("path", "Unknown file")
        line_number = self.safe_int(start.get("line", 0))
        
        # Código vulnerable
        code_snippet = self._extract_code(finding, extra)
        
        # CWE
        cwe_list = metadata.get("cwe", [])
        cwe_id = self._extract_cwe(cwe_list)
        
        # Confianza
        confidence = ConfidenceCalculator.calculate(
            metadata.get("confidence")
        )
        
        # Referencias y remediación
        references = self._extract_references(metadata)
        remediation = metadata.get("fix") or metadata.get("remediation")
        
        return Vulnerability(
            id=vuln_id,
            type=vuln_type,
            severity=severity,
            title=title,
            description=description,
            file_path=file_path,
            line_number=line_number,
            code_snippet=code_snippet,
            cwe_id=cwe_id,
            source_tool="Semgrep",
            rule_id=check_id,
            confidence_level=confidence,
            remediation_advice=remediation,
            references=references,
            meta={
                "metadata": metadata,
                "parser": "semgrep",
                "parser_version": self.parser_version,
                "engine_kind": finding.get("engine_kind"),
                "validation_state": finding.get("validation_state")
            }
        )
    
    def _extract_title(self, check_id: str, extra: Dict[str, Any]) -> str:
        """Extrae título legible"""
        # Usar mensaje si está disponible
        message = extra.get("message")
        if message and len(message) < 100:
            return message
        
        # Convertir check_id a título legible
        # java.sql-injection.tainted-sql → SQL Injection (Tainted SQL)
        parts = check_id.split('.')
        if len(parts) >= 2:
            # Tomar la parte principal (ej: sql-injection)
            main_part = parts[-2] if len(parts) > 2 else parts[-1]
            title = main_part.replace('-', ' ').replace('_', ' ').title()
            return title
        
        return check_id
    
    def _build_description(self, extra: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Construye descripción completa"""
        parts = []
        
        # Mensaje principal
        message = extra.get("message")
        if message:
            parts.append(message)
        
        # Información de categoría
        category = metadata.get("category")
        if category:
            parts.append(f"\n**Category:** {category}")
        
        # OWASP
        owasp = metadata.get("owasp", [])
        if owasp:
            owasp_str = ", ".join(owasp)
            parts.append(f"**OWASP:** {owasp_str}")
        
        # Impacto y probabilidad
        impact = metadata.get("impact")
        likelihood = metadata.get("likelihood")
        if impact or likelihood:
            risk_parts = []
            if impact:
                risk_parts.append(f"Impact: {impact}")
            if likelihood:
                risk_parts.append(f"Likelihood: {likelihood}")
            parts.append(f"**Risk:** {' | '.join(risk_parts)}")
        
        # Tecnología
        technology = metadata.get("technology", [])
        if technology:
            tech_str = ", ".join(technology)
            parts.append(f"**Technology:** {tech_str}")
        
        return "\n".join(parts) if parts else "No description available"
    
    def _extract_code(self, finding: Dict[str, Any], extra: Dict[str, Any]) -> Optional[str]:
        """Extrae snippet de código vulnerable"""
        # Método 1: Campo lines en extra
        lines = extra.get("lines")
        if lines and lines != "requires login":
            return str(lines).strip()
        
        # Método 2: Extraer del archivo (si está disponible)
        start = finding.get("start", {})
        end = finding.get("end", {})
        
        start_line = start.get("line")
        end_line = end.get("line")
        start_col = start.get("col")
        end_col = end.get("col")
        
        if start_line and end_line:
            # Construir representación visual
            if start_line == end_line:
                return f"Line {start_line}, Col {start_col}-{end_col}"
            else:
                return f"Lines {start_line}-{end_line}"
        
        return None
    
    def _extract_cwe(self, cwe_list: List) -> Optional[str]:
        """Extrae primer CWE de la lista"""
        if not cwe_list or not isinstance(cwe_list, list):
            return None
        
        for cwe in cwe_list:
            normalized = self.normalize_cwe(cwe)
            if normalized:
                return normalized
        
        return None
    
    def _extract_references(self, metadata: Dict[str, Any]) -> Optional[List[str]]:
        """Extrae referencias útiles"""
        refs = []
        
        # Referencias explícitas
        if "references" in metadata:
            meta_refs = metadata["references"]
            if isinstance(meta_refs, list):
                refs.extend(meta_refs)
            elif isinstance(meta_refs, str):
                refs.append(meta_refs)
        
        # Source rule URL
        source_url = metadata.get("source")
        if source_url and source_url not in refs:
            refs.append(source_url)
        
        # Short link
        shortlink = metadata.get("shortlink")
        if shortlink and shortlink not in refs:
            refs.append(shortlink)
        
        return refs if refs else None
