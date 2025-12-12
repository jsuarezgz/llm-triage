# core/services/scanner.py
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
from ..exceptions import ValidationError, ParsingError

logger = logging.getLogger(__name__)

class UnifiedVulnerabilityParser:
    """Parser unificado que maneja múltiples formatos - CORREGIDO"""
    
    def parse(self, data: Dict[str, Any], tool_hint: Optional[str] = None) -> List[Vulnerability]:
        """Parse vulnerabilities from any supported format"""
        
        # Extract findings from different structures
        findings = self._extract_findings(data)
        if not findings:
            logger.warning("No findings found in data")
            return []
        
        # Determine parser strategy
        parser_strategy = self._detect_format(findings[0], tool_hint)
        logger.info(f"Using parser strategy: {parser_strategy}")
        
        vulnerabilities = []
        for i, finding in enumerate(findings):
            try:
                vuln = self._parse_finding(finding, i + 1, parser_strategy)
                if vuln:
                    vulnerabilities.append(vuln)
            except Exception as e:
                logger.warning(f"Failed to parse finding {i+1}: {e}")
        
        logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities
    
    def _extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract findings from various container structures"""
        
        # Direct list
        if isinstance(data, list):
            return data
        
        # Single object
        if isinstance(data, dict) and 'rule_id' in data:
            return [data]
        
        # Nested containers
        if isinstance(data, dict):
            for key in ['findings', 'vulnerabilities', 'issues', 'results', 'scan_results']:
                if key in data and isinstance(data[key], list):
                    return data[key]
        
        return []
    
    def _detect_format(self, sample_finding: Dict[str, Any], tool_hint: Optional[str]) -> str:
        """Detect the format of findings"""
        
        if tool_hint:
            if 'abap' in tool_hint.lower():
                return 'abap'
        
        # Auto-detection based on structure
        if 'rule_id' in sample_finding and str(sample_finding.get('rule_id', '')).startswith('abap-'):
            return 'abap'
        
        if 'check_id' in sample_finding:
            return 'semgrep'
        
        if 'ruleId' in sample_finding:
            return 'sonarqube'
        
        return 'generic'
    
    def _parse_finding(self, finding: Dict[str, Any], index: int, strategy: str) -> Optional[Vulnerability]:
        """Parse individual finding based on strategy"""
        
        try:
            if strategy == 'abap':
                return self._parse_abap_finding(finding, index)
            else:
                return self._parse_generic_finding(finding, index)
        
        except Exception as e:
            logger.error(f"Failed to parse finding {index}: {e}")
            return None
    
    def _parse_abap_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """Parse ABAP-specific finding"""
        
        location = finding.get('location', {})
        
        return Vulnerability(
            id=finding.get('rule_id', f'ABAP-{index}'),
            type=self._normalize_vulnerability_type(finding.get('title', 'Unknown')),
            severity=self._normalize_severity(finding.get('severity', 'MEDIUM')),
            title=str(finding.get('title', 'ABAP Security Issue')).replace(' Vulnerability', '').strip(),
            description=finding.get('message', 'No description provided'),
            file_path=location.get('file', 'Unknown file'),
            line_number=int(location.get('line', 0)) if location.get('line') else 0,
            code_snippet=self._extract_code_context(location),
            cwe_id=self._normalize_cwe(finding.get('cwe')),
            source_tool='ABAP Security Scanner',
            rule_id=finding.get('rule_id'),
            confidence_level=self._extract_confidence(finding),
            remediation_advice=finding.get('remediation'),
            meta={
                'original_finding': finding,
                'parser_strategy': 'abap',
                'parser_version': '3.0'
            }
        )
    
    def _parse_generic_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """Parse generic finding format"""
        
        return Vulnerability(
            id=finding.get('id', f'GENERIC-{index}'),
            type=VulnerabilityType.OTHER,
            severity=SeverityLevel.MEDIUM,
            title=str(finding.get('title', finding.get('message', 'Security Issue')))[:100],
            description=finding.get('description', finding.get('message', 'No description')),
            file_path=finding.get('file', finding.get('path', 'Unknown')),
            line_number=finding.get('line', 0),
            source_tool=finding.get('tool', 'Generic Scanner'),
            meta={'original_finding': finding, 'parser_strategy': 'generic'}
        )
    
    def _normalize_vulnerability_type(self, title: str) -> VulnerabilityType:
        """Smart vulnerability type mapping"""
        if not title:
            return VulnerabilityType.OTHER
            
        title_lower = str(title).lower()
        
        mappings = {
            'sql injection': VulnerabilityType.SQL_INJECTION,
            'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
            'path traversal': VulnerabilityType.PATH_TRAVERSAL,
            'code injection': VulnerabilityType.CODE_INJECTION,
            'cross-site scripting': VulnerabilityType.XSS,
            'xss': VulnerabilityType.XSS,
            'authentication': VulnerabilityType.AUTH_BYPASS,
            'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
            'crypto': VulnerabilityType.INSECURE_CRYPTO,
        }
        
        for pattern, vuln_type in mappings.items():
            if pattern in title_lower:
                return vuln_type
        
        return VulnerabilityType.OTHER
    
    def _normalize_severity(self, severity: str) -> SeverityLevel:
        """Normalize severity levels"""
        if not severity:
            return SeverityLevel.MEDIUM
        
        severity_upper = str(severity).upper().strip()
        mappings = {
            'CRITICAL': SeverityLevel.CRITICAL,
            'HIGH': SeverityLevel.HIGH,
            'MEDIUM': SeverityLevel.MEDIUM,
            'LOW': SeverityLevel.LOW,
            'INFO': SeverityLevel.INFO,
            'CRÍTICA': SeverityLevel.CRITICAL,
            'ALTA': SeverityLevel.HIGH,
            'MEDIA': SeverityLevel.MEDIUM,
            'BAJA': SeverityLevel.LOW,
        }
        
        return mappings.get(severity_upper, SeverityLevel.MEDIUM)
    
    def _extract_code_context(self, location: Dict[str, Any]) -> Optional[str]:
        """Extract and format code context"""
        context = location.get('context', [])
        line_content = location.get('line_content', '')
        
        if isinstance(context, list) and context:
            return '\n'.join(f"{i+1:3d} | {line}" for i, line in enumerate(context) if line)
        elif line_content:
            return f">>> {str(line_content).strip()}"
        
        return None
    
    def _normalize_cwe(self, cwe: Optional[str]) -> Optional[str]:
        """Normalize CWE ID format"""
        if not cwe:
            return None
        
        cwe_str = str(cwe).strip()
        if cwe_str.isdigit():
            return f"CWE-{cwe_str}"
        elif cwe_str.startswith('CWE-'):
            return cwe_str
        
        return None
    
    def _extract_confidence(self, finding: Dict[str, Any]) -> Optional[float]:
        """Extract confidence level"""
        confidence = finding.get('confidence')
        if confidence:
            try:
                if isinstance(confidence, str) and '%' in confidence:
                    return float(confidence.replace('%', '')) / 100.0
                return float(confidence)
            except (ValueError, TypeError):
                pass
        return None

class ScannerService:
    """Servicio de escaneo optimizado y consolidado - CORREGIDO"""
    
    def __init__(self, cache=None):  # Tipo Optional removido para evitar import circular
        self.parser = UnifiedVulnerabilityParser()
        self.cache = cache
    
    async def scan_file(self, 
                       file_path: str,
                       language: Optional[str] = None,
                       tool_hint: Optional[str] = None) -> ScanResult:
        """Scan and normalize vulnerability file"""
        
        logger.info(f"Scanning file: {file_path}")
        start_time = datetime.now()
        
        # Validate file
        self._validate_file(file_path)
        
        # Check cache
        if self.cache:
            cached_result = await self._check_cache(file_path, language, tool_hint)
            if cached_result:
                logger.info("Using cached scan result")
                return cached_result
        
        # Load and parse
        raw_data = self._load_file(file_path)
        vulnerabilities = self.parser.parse(raw_data, tool_hint)
        
        # Create result
        file_info = {
            'filename': Path(file_path).name,
            'full_path': str(Path(file_path).absolute()),
            'size_bytes': Path(file_path).stat().st_size,
            'language': language,
            'tool_hint': tool_hint
        }
        
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        scan_result = ScanResult(
            file_info=file_info,
            vulnerabilities=vulnerabilities,
            scan_duration_seconds=scan_duration,
            language_detected=language
        )
        
        # Cache result
        if self.cache:
            await self._save_to_cache(file_path, scan_result, language, tool_hint)
        
        logger.info(f"Scan completed: {len(vulnerabilities)} vulnerabilities in {scan_duration:.2f}s")
        return scan_result
    
    def _validate_file(self, file_path: str) -> None:
        """Validate input file"""
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in ['.json']:
            raise ValidationError(f"Unsupported file type: {path.suffix}")
        
        if path.stat().st_size > 100 * 1024 * 1024:  # 100MB
            raise ValidationError(f"File too large: {path.stat().st_size / 1024 / 1024:.1f}MB")
    
    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise ParsingError(f"Error reading {file_path}: {e}")
    
    async def _check_cache(self, file_path: str, language: Optional[str], tool_hint: Optional[str]):
        """Check cache for existing result"""
        if not self.cache:
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            cached_data = self.cache.get(content, language, tool_hint)
            if cached_data:
                return ScanResult(**cached_data)
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        
        return None
    
    async def _save_to_cache(self, file_path: str, scan_result: ScanResult, 
                           language: Optional[str], tool_hint: Optional[str]) -> None:
        """Save result to cache"""
        if not self.cache:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Usar model_dump en lugar de dict()
            self.cache.put(content, scan_result.model_dump(), language, tool_hint)
            logger.debug("Scan result cached")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
