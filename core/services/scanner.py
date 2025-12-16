# core/services/scanner.py
"""
Scanner Service - Clean & Optimized
===================================

Responsibilities:
- Parse vulnerability files
- Normalize formats
- Deduplicate findings
- Cache results
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from functools import lru_cache

from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
from ..exceptions import ValidationError, ParsingError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

SEVERITY_MAPPINGS = {
    'CRITICAL': SeverityLevel.CRITICAL,
    'CRÍTICA': SeverityLevel.CRITICAL,
    'HIGH': SeverityLevel.HIGH,
    'ALTA': SeverityLevel.HIGH,
    'MEDIUM': SeverityLevel.MEDIUM,
    'MEDIA': SeverityLevel.MEDIUM,
    'LOW': SeverityLevel.LOW,
    'BAJA': SeverityLevel.LOW,
    'INFO': SeverityLevel.INFO,
}

VULNERABILITY_TYPE_PATTERNS = {
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


# ═══════════════════════════════════════════════════════════════════
# DEDUPLICATION
# ═══════════════════════════════════════════════════════════════════

class DuplicateDetector:
    """Intelligent duplicate detection with multiple strategies"""
    
    def __init__(self, strategy: str = 'moderate'):
        """
        Args:
            strategy: 'strict', 'moderate', or 'loose'
        """
        self.strategy = strategy.lower()
        self._similarity_cache = {}  # Cache for similarity calculations
    
    def remove_duplicates(
        self, vulnerabilities: List[Vulnerability]
    ) -> Tuple[List[Vulnerability], int]:
        """
        Remove duplicates from vulnerability list
        
        Returns:
            Tuple of (unique_vulnerabilities, count_removed)
        """
        if len(vulnerabilities) <= 1:
            return vulnerabilities, 0
        
        original_count = len(vulnerabilities)
        
        strategies = {
            'strict': self._dedup_strict,
            'moderate': self._dedup_moderate,
            'loose': self._dedup_loose
        }
        
        dedup_func = strategies.get(self.strategy, self._dedup_moderate)
        unique = dedup_func(vulnerabilities)
        
        removed = original_count - len(unique)
        if removed > 0:
            logger.info(f"✅ Removed {removed} duplicates ({self.strategy} strategy)")
        
        return unique, removed
    
    def _dedup_strict(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Exact match: file+line+type+description hash"""
        seen = set()
        unique = []
        
        for v in vulns:
            signature = f"{v.file_path}|{v.line_number}|{v.type.value}|{hash(v.description)}"
            if signature not in seen:
                seen.add(signature)
                unique.append(v)
        
        return unique
    
    def _dedup_moderate(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Same file+type, nearby location (±5 lines), 80% similar description"""
        from collections import defaultdict
        
        # Group by file and type
        groups = defaultdict(list)
        for v in vulns:
            key = (v.file_path, v.type.value)
            groups[key].append(v)
        
        unique = []
        for group_vulns in groups.values():
            # Sort by line number
            group_vulns.sort(key=lambda v: v.line_number)
            kept = []
            
            for v in group_vulns:
                is_duplicate = any(
                    abs(v.line_number - k.line_number) <= 5 and
                    self._similarity(v.description, k.description) > 0.8
                    for k in kept
                )
                
                if not is_duplicate:
                    kept.append(v)
            
            unique.extend(kept)
        
        return unique
    
    def _dedup_loose(self, vulns: List[Vulnerability]) -> List[Vulnerability]:
        """Same type, 70% similar description"""
        from collections import defaultdict
        
        groups = defaultdict(list)
        for v in vulns:
            groups[v.type.value].append(v)
        
        unique = []
        for group_vulns in groups.values():
            kept = []
            for v in group_vulns:
                is_duplicate = any(
                    self._similarity(v.description, k.description) > 0.7
                    for k in kept
                )
                
                if not is_duplicate:
                    kept.append(v)
            
            unique.extend(kept)
        
        return unique
    
    @lru_cache(maxsize=1024)
    def _similarity(self, text1: str, text2: str) -> float:
        """Jaccard similarity with caching"""
        if text1 == text2:
            return 1.0
        
        tokens1 = frozenset(text1.lower().split())
        tokens2 = frozenset(text2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        return intersection / union if union > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════
# VULNERABILITY PARSER
# ═══════════════════════════════════════════════════════════════════

class VulnerabilityParser:
    """Parse vulnerabilities from various SAST tool formats"""
    
    def parse(self, data: Dict[str, Any], tool_hint: Optional[str] = None) -> List[Vulnerability]:
        """
        Parse vulnerabilities from raw data
        
        Args:
             Raw data from SAST tool
            tool_hint: Optional hint about tool format
        
        Returns:
            List of parsed Vulnerability objects
        """
        findings = self._extract_findings(data)
        
        if not findings:
            logger.warning("No findings found in data")
            return []
        
        # Detect format
        parser_strategy = self._detect_format(findings[0], tool_hint)
        logger.info(f"Using parser: {parser_strategy}")
        
        # Parse all findings
        vulnerabilities = []
        for i, finding in enumerate(findings, 1):
            try:
                vuln = self._parse_finding(finding, i, parser_strategy)
                if vuln:
                    vulnerabilities.append(vuln)
            except Exception as e:
                logger.warning(f"Failed to parse finding {i}: {e}")
        
        logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities")
        return vulnerabilities
    
    def _extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract findings from nested structures"""
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
    
    def _detect_format(self, sample: Dict[str, Any], tool_hint: Optional[str]) -> str:
        """Detect SAST tool format"""
        if tool_hint and 'abap' in tool_hint.lower():
            return 'abap'
        
        if 'rule_id' in sample and str(sample.get('rule_id', '')).startswith('abap-'):
            return 'abap'
        
        if 'check_id' in sample:
            return 'semgrep'
        
        if 'ruleId' in sample:
            return 'sonarqube'
        
        return 'generic'
    
    def _parse_finding(self, finding: Dict[str, Any], index: int, strategy: str) -> Optional[Vulnerability]:
        """Parse individual finding based on strategy"""
        try:
            if strategy == 'abap':
                return self._parse_abap(finding, index)
            else:
                return self._parse_generic(finding, index)
        except Exception as e:
            logger.error(f"Failed to parse finding {index}: {e}")
            return None
    
    def _parse_abap(self, finding: Dict[str, Any], index: int) -> Vulnerability:
        """Parse ABAP-specific finding"""
        location = finding.get('location', {})
        
        return Vulnerability(
            id=finding.get('rule_id', f'ABAP-{index}'),
            type=self._normalize_type(finding.get('title', 'Unknown')),
            severity=SEVERITY_MAPPINGS.get(
                finding.get('severity', 'MEDIUM').upper(),
                SeverityLevel.MEDIUM
            ),
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
                'cvss_score': self._extract_cvss(finding),
                'parser_strategy': 'abap',
                'parser_version': '3.0'
            }
        )
    
    def _parse_generic(self, finding: Dict[str, Any], index: int) -> Vulnerability:
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
            meta={'parser_strategy': 'generic'}
        )
    
    def _normalize_type(self, title: str) -> VulnerabilityType:
        """Normalize vulnerability type from title"""
        if not title:
            return VulnerabilityType.OTHER
        
        title_lower = str(title).lower()
        
        for pattern, vuln_type in VULNERABILITY_TYPE_PATTERNS.items():
            if pattern in title_lower:
                return vuln_type
        
        return VulnerabilityType.OTHER
    
    def _extract_code_context(self, location: Dict[str, Any]) -> Optional[str]:
        """Extract code context safely"""
        context = location.get('context', [])
        line_content = location.get('line_content', '')
        
        if isinstance(context, list) and context:
            safe_lines = []
            for i, line in enumerate(context):
                if line is None:
                    continue
                
                # Convert to string safely
                line_str = str(line) if not isinstance(line, str) else line
                
                if line_str.strip():
                    safe_lines.append(f"{i+1:3d} | {line_str}")
            
            if safe_lines:
                return '\n'.join(safe_lines)
        
        if line_content:
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
    
    def _extract_cvss(self, finding: Dict[str, Any]) -> Optional[float]:
        """Extract CVSS score"""
        for key in ['cvss_score', 'cvss', 'score']:
            if key in finding:
                try:
                    score = float(finding[key])
                    if 0 <= score <= 10:
                        return score
                except:
                    pass
        return None


# ═══════════════════════════════════════════════════════════════════
# SCANNER SERVICE
# ═══════════════════════════════════════════════════════════════════

class ScannerService:
    """Main scanner service - orchestrates parsing and deduplication"""
    
    def __init__(
        self,
        cache=None,
        enable_deduplication: bool = True,
        dedup_strategy: str = 'moderate'
    ):
        self.parser = VulnerabilityParser()
        self.cache = cache
        self.dedup_detector = (
            DuplicateDetector(dedup_strategy) if enable_deduplication else None
        )
    
    async def scan_file(
        self,
        file_path: str,
        language: Optional[str] = None,
        tool_hint: Optional[str] = None
    ) -> ScanResult:
        """
        Scan and normalize vulnerability file
        
        Args:
            file_path: Path to vulnerability file
            language: Programming language (optional)
            tool_hint: SAST tool hint (optional)
        
        Returns:
            ScanResult with parsed vulnerabilities
        """
        logger.info(f"📁 Scanning file: {file_path}")
        start_time = datetime.now()
        
        # Validate file
        self._validate_file(file_path)
        
        # Check cache
        if self.cache:
            cached_result = await self._check_cache(file_path, language, tool_hint)
            if cached_result:
                logger.info("✅ Using cached result")
                return cached_result
        
        # Load and parse
        raw_data = self._load_file(file_path)
        vulnerabilities = self.parser.parse(raw_data, tool_hint)
        
        # Deduplicate
        removed_dups = 0
        if self.dedup_detector:
            vulnerabilities, removed_dups = self.dedup_detector.remove_duplicates(vulnerabilities)
        
        # Create result
        file_info = {
            'filename': Path(file_path).name,
            'full_path': str(Path(file_path).absolute()),
            'size_bytes': Path(file_path).stat().st_size,
            'language': language,
            'tool_hint': tool_hint,
            'duplicates_removed': removed_dups
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
        
        logger.info(f"✅ Scan complete: {len(vulnerabilities)} vulnerabilities in {scan_duration:.2f}s")
        return scan_result
    
    def _validate_file(self, file_path: str) -> None:
        """Validate input file"""
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"File not found: {file_path}")
        
        if path.suffix.lower() != '.json':
            raise ValidationError(f"Unsupported file type: {path.suffix}")
        
        # 100MB limit
        if path.stat().st_size > 100 * 1024 * 1024:
            raise ValidationError(f"File too large: {path.stat().st_size / 1024 / 1024:.1f}MB")
    
    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ParsingError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ParsingError(f"Error reading file: {e}")
        
    async def _check_cache(
        self, file_path: str, language: Optional[str], tool_hint: Optional[str]
    ) -> Optional[ScanResult]:
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
    
    async def _save_to_cache(
        self,
        file_path: str,
        scan_result: ScanResult,
        language: Optional[str],
        tool_hint: Optional[str]
    ) -> None:
        """Save result to cache"""
        if not self.cache:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.cache.put(content, scan_result.model_dump(), language, tool_hint)
            logger.debug("✅ Result cached")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
