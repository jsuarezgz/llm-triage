# adapters/parsers/abap_parser.py
"""
ABAP Parser - Adaptador para ABAP Security Scanner
==================================================
"""

from typing import Dict, Any, List, Optional

from .base import BaseVulnerabilityParser, ParserMetadata
from .utils import FieldExtractor, VulnerabilityTypeDetector, ConfidenceCalculator
from core.models import Vulnerability


class ABAPParser(BaseVulnerabilityParser):
    """
    Adapter para parsear resultados de ABAP Security Scanner
    
    Soporta:
    - Formato JSON estándar de ABAP Scanner
    - Formato con scan_metadata
    - Lista directa de findings
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = ParserMetadata(
            name="ABAPParser",
            version="3.0",
            supported_tools=["ABAP Security Scanner", "ABAP Code Checker"],
            format_indicators=["scan_metadata", "rule_id: abap-*", "security_metadata"]
        )
    
    def can_parse(self, data: Dict[str, Any]) -> bool:
        """
        Detecta si es formato ABAP
        
        Indicadores:
        1. Tiene "scan_metadata" y "findings"
        2. Los findings tienen "rule_id" que empieza con "abap-"
        3. Tiene "security_metadata" en findings
        """
        # Formato estándar con scan_metadata
        if isinstance(data, dict):
            if "scan_metadata" in data and "findings" in data:
                return True
            
            # Formato alternativo con findings directo
            if "findings" in data:
                findings = data["findings"]
                if isinstance(findings, list) and findings:
                    first = findings[0]
                    if "rule_id" in first and str(first["rule_id"]).startswith("abap-"):
                        return True
        
        # Lista directa de findings ABAP
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                rule_id = first.get("rule_id", "")
                if str(rule_id).startswith("abap-"):
                    return True
                
                # Verificar security_metadata típico de ABAP
                if "security_metadata" in first:
                    return True
        
        return False
    
    def extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrae findings de formato ABAP"""
        # Formato estándar con findings
        if isinstance(data, dict):
            if "findings" in data:
                findings = data["findings"]
                if isinstance(findings, list):
                    return findings
        
        # Lista directa
        if isinstance(data, list):
            return data
        
        return []
    
    def parse_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """
        Parsea un finding ABAP a Vulnerability
        
        Estructura esperada:
        {
            "rule_id": "abap-sql-injection",
            "title": "SQL Injection Vulnerability",
            "message": "Potential SQL injection detected",
            "severity": "HIGH",
            "location": {
                "file": "ZTEST_PROGRAM.abap",
                "line": 42,
                "line_content": "SELECT * FROM table WHERE id = lv_input.",
                "context": [...]
            },
            "cwe": "CWE-89",
            "security_metadata": {
                "confidence": "HIGH",
                "exploitability": "EASY"
            }
        }
        """
        location = finding.get("location", {})
        security_meta = finding.get("security_metadata", {})
        
        # ID y regla
        rule_id = finding.get("rule_id", f"ABAP-{index}")
        vuln_id = rule_id
        
        # Título limpio
        title = self._clean_title(
            finding.get("title", finding.get("name", "ABAP Security Issue"))
        )
        
        # Descripción completa
        description = self._build_description(finding, security_meta)
        
        # Severidad
        severity_str = finding.get("severity", "MEDIUM")
        severity = self.normalize_severity(severity_str)
        
        # Tipo de vulnerabilidad
        vuln_type = VulnerabilityTypeDetector.detect(
            title,
            finding.get("message", ""),
            rule_id
        )
        
        # Ubicación del archivo
        file_path = FieldExtractor.get(
            location,
            "file",
            "path",
            "filename",
            "source_file"
        ) or "Unknown ABAP file"
        
        line_number = self.safe_int(
            FieldExtractor.get(
                location,
                "line",
                "line_number",
                "start_line"
            )
        )
        
        # Código vulnerable con contexto
        code_snippet = self._extract_code_context(location, finding)
        
        # CWE
        cwe_id = self.normalize_cwe(
            FieldExtractor.get(finding, "cwe", "cwe_id", "cwe_number")
        )
        
        # Confianza
        confidence = ConfidenceCalculator.calculate(
            security_meta.get("confidence")
        )
        
        # Remediación
        remediation = self._extract_remediation(finding)
        
        # Referencias
        references = self._extract_references(finding)
        
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
            source_tool="ABAP Security Scanner",
            rule_id=rule_id,
            confidence_level=confidence,
            remediation_advice=remediation,
            references=references,
            meta={
                "security_metadata": security_meta,
                "parser": "abap",
                "parser_version": self.parser_version,
                "scan_metadata": finding.get("scan_metadata"),
                "exploitability": security_meta.get("exploitability"),
                "impact": security_meta.get("impact")
            }
        )
    
    def _clean_title(self, title: str) -> str:
        """Limpia el título removiendo sufijos comunes"""
        title = str(title).strip()
        
        # Remover sufijos comunes
        suffixes = [
            " Vulnerability",
            " vulnerability",
            " Issue",
            " issue",
            " Detection",
            " detection"
        ]
        
        for suffix in suffixes:
            if title.endswith(suffix):
                title = title[:-len(suffix)].strip()
        
        return title
    
    def _build_description(
        self,
        finding: Dict[str, Any],
        security_meta: Dict[str, Any]
    ) -> str:
        """Construye descripción completa"""
        parts = []
        
        # Mensaje principal
        message = finding.get("message")
        if message:
            parts.append(message)
        
        # Descripción detallada
        detail = finding.get("description")
        if detail and detail != message:
            parts.append(f"\n{detail}")
        
        # Impacto de seguridad
        impact = security_meta.get("impact")
        if impact:
            parts.append(f"\n**Impact:** {impact}")
        
        # Explotabilidad
        exploitability = security_meta.get("exploitability")
        if exploitability:
            parts.append(f"**Exploitability:** {exploitability}")
        
        # Categoría OWASP
        owasp = security_meta.get("owasp_category")
        if owasp:
            parts.append(f"**OWASP Category:** {owasp}")
        
        return "\n".join(parts) if parts else "No description available"
    
    def _extract_code_context(
        self,
        location: Dict[str, Any],
        finding: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extrae contexto de código con formato
        
        Prioridades:
        1. context (array de líneas con contexto)
        2. line_content (línea individual)
        3. matched_text (texto exacto que coincidió)
        4. code_snippet (snippet directo)
        """
        # Método 1: Context completo (preferido)
        context = location.get("context")
        if isinstance(context, list) and context:
            lines = []
            current_line = location.get("line", 0)
            
            for i, line in enumerate(context):
                if line is None:
                    continue
                
                line_str = str(line).rstrip()
                
                # Calcular número de línea
                offset = i - (len(context) // 2)
                line_num = current_line + offset
                
                # Marcar línea vulnerable
                if ">>" in line_str or i == len(context) // 2:
                    lines.append(f"{line_num:4d} >>> {line_str.replace('>>', '').strip()}")
                else:
                    lines.append(f"{line_num:4d}     {line_str}")
            
            if lines:
                result = "\n".join(lines)
                
                # Agregar matched_text si existe
                matched = location.get("matched_text")
                if matched:
                    result += f"\n\n# Matched Pattern: {matched}"
                
                return result
        
        # Método 2: Line content simple
        line_content = location.get("line_content")
        if line_content:
            line_num = location.get("line", 0)
            result = f"{line_num:4d} >>> {str(line_content).strip()}"
            
            matched = location.get("matched_text")
            if matched:
                result += f"\n\n# Matched: {matched}"
            
            return result
        
        # Método 3: Code snippet directo
        code_snippet = finding.get("code_snippet")
        if code_snippet:
            return str(code_snippet).strip()
        
        # Método 4: Matched text solo
        matched = location.get("matched_text")
        if matched:
            return f"Matched: {matched}"
        
        return None
    
    def _extract_remediation(self, finding: Dict[str, Any]) -> Optional[str]:
        """Extrae consejo de remediación"""
        # Campos posibles
        remediation = FieldExtractor.get(
            finding,
            "remediation",
            "fix",
            "recommendation",
            "solution"
        )
        
        if remediation:
            return str(remediation).strip()
        
        # Construir desde security_metadata
        security_meta = finding.get("security_metadata", {})
        fix_complexity = security_meta.get("fix_complexity")
        
        if fix_complexity:
            return f"Fix Complexity: {fix_complexity}"
        
        return None
    
    def _extract_references(self, finding: Dict[str, Any]) -> Optional[List[str]]:
        """Extrae referencias útiles"""
        refs = []
        
        # Referencias directas
        references = finding.get("references")
        if references:
            if isinstance(references, list):
                refs.extend(references)
            elif isinstance(references, str):
                refs.append(references)
        
        # Security metadata links
        security_meta = finding.get("security_metadata", {})
        
        reference_url = security_meta.get("reference_url")
        if reference_url:
            refs.append(reference_url)
        
        documentation = security_meta.get("documentation")
        if documentation:
            refs.append(documentation)
        
        # OWASP reference
        owasp = security_meta.get("owasp_category")
        if owasp and ":" in owasp:
            owasp_code = owasp.split(":")[0].strip()
            refs.append(f"https://owasp.org/Top10/{owasp_code}/")
        
        return refs if refs else None
