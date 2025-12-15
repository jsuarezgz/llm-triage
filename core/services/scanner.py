# core/services/scanner.py
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
from ..exceptions import ValidationError, ParsingError

logger = logging.getLogger(__name__)

class DuplicateDetector:
    """
    🔄 Intelligent duplicate detection system
    
    Strategies:
    - strict: Exact match (file, line, type, description hash)
    - moderate: Similar location and type (default)
    - loose: Fuzzy matching on type and description
    """
    
    def __init__(self, strategy: str = 'moderate'):
        self.strategy = strategy
        logger.info(f"🔄 Duplicate detector initialized: strategy={strategy}")
    
    def remove_duplicates(self, vulnerabilities: List[Vulnerability]) -> tuple[List[Vulnerability], int]:
        """Remove duplicates, returns (unique_list, removed_count)"""
        if not vulnerabilities or len(vulnerabilities) <= 1:
            return vulnerabilities, 0
        
        original_count = len(vulnerabilities)
        logger.info(f"🔍 Checking {original_count} vulnerabilities for duplicates ({self.strategy})")
        
        if self.strategy == 'strict':
            unique = self._dedup_strict(vulnerabilities)
        elif self.strategy == 'loose':
            unique = self._dedup_loose(vulnerabilities)
        else:  # moderate
            unique = self._dedup_moderate(vulnerabilities)
        
        removed = original_count - len(unique)
        if removed > 0:
            logger.info(f"✅ Removed {removed} duplicates, kept {len(unique)} unique")
        
        return unique, removed
    
    def _dedup_strict(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Exact match on file+line+type+description"""
        seen: set = set()
        unique = []
        
        for vuln in vulnerabilities:
            sig = f"{vuln.file_path}|{vuln.line_number}|{vuln.type.value}|{hash(vuln.description)}"
            if sig not in seen:
                seen.add(sig)
                unique.append(vuln)
        
        return unique
    
    def _dedup_moderate(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Same file+type, nearby location (±5 lines), similar description"""
        from collections import defaultdict
        
        groups = defaultdict(list)
        for vuln in vulnerabilities:
            key = (vuln.file_path, vuln.type.value)
            groups[key].append(vuln)
        
        unique = []
        for group_vulns in groups.values():
            group_vulns.sort(key=lambda v: v.line_number)
            kept = []
            
            for vuln in group_vulns:
                is_dup = False
                for kept_vuln in kept:
                    if abs(vuln.line_number - kept_vuln.line_number) <= 5:
                        similarity = self._similarity(vuln.description, kept_vuln.description)
                        if similarity > 0.8:
                            is_dup = True
                            break
                
                if not is_dup:
                    kept.append(vuln)
            
            unique.extend(kept)
        
        return unique
    
    def _dedup_loose(self, vulnerabilities: List[Vulnerability]) -> List[Vulnerability]:
        """Same type, similar description (70%+)"""
        from collections import defaultdict
        
        groups = defaultdict(list)
        for vuln in vulnerabilities:
            groups[vuln.type.value].append(vuln)
        
        unique = []
        for group_vulns in groups.values():
            kept = []
            for vuln in group_vulns:
                is_dup = False
                for kept_vuln in kept:
                    if self._similarity(vuln.description, kept_vuln.description) > 0.7:
                        is_dup = True
                        break
                
                if not is_dup:
                    kept.append(vuln)
            
            unique.extend(kept)
        
        return unique
    
    def _similarity(self, text1: str, text2: str) -> float:
        """Simple Jaccard similarity"""
        if text1 == text2:
            return 1.0
        
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0


class UnifiedVulnerabilityParser:
    """Parser unificado que maneja múltiples formatos"""
    
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
    
    def _extract_cvss(self, finding: Dict[str, Any]) -> Optional[float]:
        """Extraer CVSS de múltiples ubicaciones posibles"""
        for key in ['cvss_score', 'cvss', 'score']:
            if key in finding:
                try:
                    score = float(finding[key])
                    if 0 <= score <= 10:
                        return score
                except:
                    pass
        return None
    
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
                'parser_version': '3.0',
                'cvss_score': self._extract_cvss(finding)
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
        """Extract and format code context - SAFE VERSION"""
        context = location.get('context', [])
        line_content = location.get('line_content', '')
        
        if isinstance(context, list) and context:
            # Validar y convertir cada línea a string de forma segura
            safe_lines = []
            for i, line in enumerate(context):
                # Validación robusta
                if line is None:
                    continue  # Saltar None
                elif isinstance(line, (int, float, bool)):
                    line_str = str(line)  # Convertir números a string
                elif isinstance(line, dict):
                    line_str = str(line)  # Convertir dict a string
                elif isinstance(line, str):
                    line_str = line
                else:
                    line_str = repr(line)  # Fallback para tipos extraños
                
                # Solo agregar si no está vacío
                if line_str.strip():
                    safe_lines.append(f"{i+1:3d} | {line_str}")
            
            if safe_lines:
                return '\n'.join(safe_lines)
        
        # Fallback: usar line_content si existe
        if line_content:
            # Validar line_content también
            if isinstance(line_content, str):
                return f">>> {line_content.strip()}"
            else:
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
    """Servicio de escaneo optimizado y consolidado"""
    
    def __init__(self, cache=None, enable_deduplication: bool = True, dedup_strategy: str = 'moderate'):
        self.parser = UnifiedVulnerabilityParser()
        self.cache = cache
        self.dedup_detector = DuplicateDetector(dedup_strategy) if enable_deduplication else None

    
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
        removed_dups = 0
        if self.dedup_detector:
            vulnerabilities, removed_dups = self.dedup_detector.remove_duplicates(vulnerabilities)
            if removed_dups > 0:
                logger.info(f"🔄 Removed {removed_dups} duplicates")
        
        # Create result
        file_info = {
            'filename': Path(file_path).name,
            'full_path': str(Path(file_path).absolute()),
            'size_bytes': Path(file_path).stat().st_size,
            'language': language,
            'tool_hint': tool_hint,
            'duplicates_removed': removed_dups  # 🆕 AÑADIR ESTA LÍNEA
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

# ============================================================================
# AÑADIR ESTA CLASE ANTES DE ScannerService
# ============================================================================

class DuplicateDetector:
    """Detector de duplicados con 3 estrategias"""
    
    def __init__(self, strategy: str = 'moderate'):
        self.strategy = strategy.lower()
    
    def remove_duplicates(self, vulnerabilities: List[Vulnerability]) -> Tuple[List[Vulnerability], int]:
        """Retorna (lista_sin_duplicados, cantidad_removida)"""
        if len(vulnerabilities) <= 1:
            return vulnerabilities, 0
        
        original = len(vulnerabilities)
        
        if self.strategy == 'strict':
            unique = self._strict(vulnerabilities)
        elif self.strategy == 'loose':
            unique = self._loose(vulnerabilities)
        else:
            unique = self._moderate(vulnerabilities)
        
        return unique, original - len(unique)
    
    def _strict(self, vulns):
        """Mismo file+line+type+description"""
        seen = set()
        unique = []
        for v in vulns:
            key = f"{v.file_path}|{v.line_number}|{v.type.value}|{hash(v.description)}"
            if key not in seen:
                seen.add(key)
                unique.append(v)
        return unique
    
    def _moderate(self, vulns):
        """Mismo file+type, ±5 líneas, 80% similar"""
        from collections import defaultdict
        groups = defaultdict(list)
        for v in vulns:
            groups[(v.file_path, v.type.value)].append(v)
        
        unique = []
        for group in groups.values():
            group.sort(key=lambda v: v.line_number)
            kept = []
            for v in group:
                if not any(abs(v.line_number - k.line_number) <= 5 and 
                          self._sim(v.description, k.description) > 0.8 
                          for k in kept):
                    kept.append(v)
            unique.extend(kept)
        return unique
    
    def _loose(self, vulns):
        """Mismo type, 70% similar"""
        from collections import defaultdict
        groups = defaultdict(list)
        for v in vulns:
            groups[v.type.value].append(v)
        
        unique = []
        for group in groups.values():
            kept = []
            for v in group:
                if not any(self._sim(v.description, k.description) > 0.7 for k in kept):
                    kept.append(v)
            unique.extend(kept)
        return unique
    
    def _sim(self, a: str, b: str) -> float:
        """Jaccard similarity"""
        if a == b:
            return 1.0
        t1, t2 = set(a.lower().split()), set(b.lower().split())
        return len(t1 & t2) / len(t1 | t2) if t1 and t2 else 0.0
