# core/services/scanner.py
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.models import ScanResult, Vulnerability
from core.exceptions import ValidationError, ParsingError
from adapters.parsers.parser_factory import ParserFactory  # ✅ USAR FACTORY
from .scanner_helpers import DuplicateDetector  # Movemos dedup a helpers

logger = logging.getLogger(__name__)


class ScannerService:
    """Main scanner service - orchestrates parsing and deduplication"""
    
    def __init__(
        self,
        cache=None,
        enable_deduplication: bool = True,
        dedup_strategy: str = 'moderate'
    ):
        # ✅ Usar ParserFactory en lugar de parser interno
        self.parser_factory = ParserFactory()
        self.cache = cache
        self.dedup_detector = (
            DuplicateDetector(dedup_strategy) if enable_deduplication else None
        )
        
        # Log parsers disponibles
        supported = self.parser_factory.get_supported_formats()
        logger.info(f"📦 Scanner initialized with parsers: {', '.join(supported)}")
    
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
            tool_hint: SAST tool hint (optional) - "semgrep", "abap", etc.
        
        Returns:
            ScanResult with parsed vulnerabilities
        """
        logger.info(f"📁 Scanning file: {file_path}")
        start_time = datetime.now()
        
        # 1. Validate file
        self._validate_file(file_path)
        
        # 2. Check cache
        if self.cache:
            cached_result = await self._check_cache(file_path, language, tool_hint)
            if cached_result:
                logger.info("✅ Using cached result")
                return cached_result
        
        # 3. Load JSON
        raw_data = self._load_file(file_path)
        
        # 4. ✅ USAR PARSER FACTORY con auto-detección
        vulnerabilities = self._parse_with_factory(raw_data, tool_hint)
        
        # 5. Deduplicate
        removed_dups = 0
        if self.dedup_detector:
            vulnerabilities, removed_dups = self.dedup_detector.remove_duplicates(
                vulnerabilities
            )
        
        # 6. Create result
        file_info = self._create_file_info(file_path, language, tool_hint, removed_dups)
        scan_duration = (datetime.now() - start_time).total_seconds()
        
        scan_result = ScanResult(
            file_info=file_info,
            vulnerabilities=vulnerabilities,
            scan_duration_seconds=scan_duration,
            language_detected=language
        )
        
        # 7. Cache result
        if self.cache:
            await self._save_to_cache(file_path, scan_result, language, tool_hint)
        
        logger.info(
            f"✅ Scan complete: {len(vulnerabilities)} vulnerabilities "
            f"in {scan_duration:.2f}s"
        )
        return scan_result
    
    # ═══════════════════════════════════════════════════════════════
    # PARSING CON FACTORY
    # ═══════════════════════════════════════════════════════════════
    
    def _parse_with_factory(
        self,
        raw_data: Dict[str, Any],
        tool_hint: Optional[str] = None
    ) -> List[Vulnerability]:
        """
        Parse vulnerabilities using ParserFactory
        
        Args:
            raw_ Raw JSON data
            tool_hint: Optional tool hint ("semgrep", "abap")
        
        Returns:
            List of parsed vulnerabilities
        """
        try:
            # Auto-detect format si no hay hint
            if not tool_hint:
                detected_format = self.parser_factory.detect_format(raw_data)
                if detected_format:
                    logger.info(f"🎯 Auto-detected format: {detected_format}")
                else:
                    logger.warning("⚠️ Format not detected, trying all parsers")
            
            # Parse usando factory
            vulnerabilities = self.parser_factory.parse(
                data=raw_data,
                tool_hint=tool_hint
            )
            
            # Validate results
            if not vulnerabilities:
                logger.warning("⚠️ No vulnerabilities parsed from file")
                return []
            
            # Log parsing stats
            logger.info(f"✅ Parsed {len(vulnerabilities)} vulnerabilities")
            self._log_parsing_stats(vulnerabilities)
            
            return vulnerabilities
            
        except ParsingError as e:
            logger.error(f"❌ Parsing failed: {e}")
            raise
        
        except Exception as e:
            logger.error(f"❌ Unexpected parsing error: {e}")
            raise ParsingError(f"Failed to parse vulnerabilities: {e}")
    
    def _log_parsing_stats(self, vulnerabilities: List[Vulnerability]) -> None:
        """Log parsing statistics"""
        if not vulnerabilities:
            return
        
        # Severity distribution
        from collections import Counter
        severity_dist = Counter(v.severity.value for v in vulnerabilities)
        
        logger.info("📊 Severity distribution:")
        for severity, count in severity_dist.most_common():
            logger.info(f"   {severity}: {count}")
        
        # Parser sources
        sources = Counter(v.source_tool for v in vulnerabilities if v.source_tool)
        if sources:
            logger.info(f"🔧 Sources: {dict(sources)}")
    
    # ═══════════════════════════════════════════════════════════════
    # FILE OPERATIONS (MEJORADAS)
    # ═══════════════════════════════════════════════════════════════
    
    def _validate_file(self, file_path: str) -> None:
        """Validate input file with enhanced checks"""
        path = Path(file_path)
        
        # Single stat call for multiple checks
        try:
            stat = path.stat()
        except FileNotFoundError:
            raise ValidationError(f"File not found: {file_path}")
        except PermissionError:
            raise ValidationError(f"Permission denied: {file_path}")
        
        # Is file check
        if not path.is_file():
            raise ValidationError(f"Not a file: {file_path}")
        
        # Extension check
        if path.suffix.lower() != '.json':
            raise ValidationError(
                f"Unsupported file type: {path.suffix}. Expected .json"
            )
        
        # Size limit (100MB) - already have stat
        size_bytes = stat.st_size
        max_size = 100 * 1024 * 1024
        
        if size_bytes > max_size:
            size_mb = size_bytes / (1024 * 1024)
            max_mb = max_size / (1024 * 1024)
            raise ValidationError(
                f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)"
            )
        
        logger.debug(f"✅ File validated: {path.name} ({size_bytes:,} bytes)")
    
    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Load and parse JSON file with safety limits"""
        import json
        
        max_depth = 50  # Prevenir JSON anidado infinito
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse con límite de profundidad
            data = self._safe_json_parse(content, max_depth)
            
            # Validate root structure
            if not isinstance(data, (dict, list)):
                raise ParsingError(
                    f"Invalid JSON root: {type(data).__name__}. "
                    "Expected dict or list"
                )
            
            logger.debug(f"✅ JSON loaded: {type(data).__name__}")
            return data
            
        except json.JSONDecodeError as e:
            raise ParsingError(
                f"Invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}"
            )
        
        except UnicodeDecodeError as e:
            raise ParsingError(f"Encoding error: {e}. Expected UTF-8")
        
        except Exception as e:
            raise ParsingError(f"Error reading file: {e}")
    
    def _safe_json_parse(self, content: str, max_depth: int) -> Any:
        """Parse JSON with depth limit to prevent stack overflow"""
        import json
        
        data = json.loads(content)
        
        # Check depth
        def check_depth(obj, depth=0):
            if depth > max_depth:
                raise ParsingError(f"JSON nesting exceeds {max_depth} levels")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)
        
        check_depth(data)
        return data
    
    def _create_file_info(
        self,
        file_path: str,
        language: Optional[str],
        tool_hint: Optional[str],
        removed_dups: int
    ) -> Dict[str, Any]:
        """Create file info metadata"""
        path = Path(file_path)
        
        return {
            'filename': path.name,
            'full_path': str(path.absolute()),
            'size_bytes': path.stat().st_size,
            'language': language,
            'tool_hint': tool_hint,
            'duplicates_removed': removed_dups,
            'parser_used': 'ParserFactory',
            'scan_timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════
    # CACHE OPERATIONS (sin cambios)
    # ═══════════════════════════════════════════════════════════════
    
    async def _check_cache(
        self,
        file_path: str,
        language: Optional[str],
        tool_hint: Optional[str]
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
            logger.debug("💾 Result cached")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
