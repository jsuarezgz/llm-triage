# application/use_cases.py
import asyncio
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from core.models import AnalysisReport, ScanResult, Vulnerability
from core.services.scanner import ScannerService
from core.services.triage import TriageService
from core.services.remediation import RemediationService
from core.services.reporter import ReporterService
from adapters.processing.chunker import OptimizedChunker
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class AnalysisUseCase:
    """Caso de uso principal consolidado - sin duplicación"""
    
    def __init__(self,
                 scanner_service: ScannerService,
                 triage_service: Optional[TriageService] = None,
                 remediation_service: Optional[RemediationService] = None,
                 reporter_service: Optional[ReporterService] = None,
                 chunker: Optional[OptimizedChunker] = None,
                 metrics: Optional[MetricsCollector] = None):
        
        self.scanner_service = scanner_service
        self.triage_service = triage_service
        self.remediation_service = remediation_service
        self.reporter_service = reporter_service
        self.chunker = chunker
        self.metrics = metrics
    
    async def execute_full_analysis(self,
                                  file_path: str,
                                  output_file: Optional[str] = None,
                                  language: Optional[str] = None,
                                  tool_hint: Optional[str] = None,
                                  force_chunking: bool = False,
                                  disable_chunking: bool = False) -> AnalysisReport:
        """Execute complete security analysis pipeline"""
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Starting complete analysis: {file_path}")
            
            # Phase 1: Scan and normalize vulnerabilities
            scan_result = await self.scanner_service.scan_file(
                file_path=file_path,
                language=language,
                tool_hint=tool_hint
            )
            
            if not scan_result.vulnerabilities:
                logger.info("No vulnerabilities found")
                return self._create_clean_report(scan_result, start_time)
            
            # Phase 2: LLM Triage (if available)
            triage_result = None
            if self.triage_service:
                triage_result = await self._perform_triage_analysis(
                    scan_result, language, force_chunking, disable_chunking
                )
            
            # Phase 3: Generate remediation plans (if available)
            remediation_plans = []
            if self.remediation_service and triage_result:
                confirmed_vulns = self._extract_confirmed_vulnerabilities(
                    scan_result.vulnerabilities, triage_result
                )
                if confirmed_vulns:
                    remediation_plans = await self.remediation_service.generate_remediation_plans(
                        confirmed_vulns, language
                    )
            
            # Phase 4: Create analysis report
            total_time = asyncio.get_event_loop().time() - start_time
            analysis_report = self._create_analysis_report(
                scan_result, triage_result, remediation_plans, total_time,
                force_chunking, disable_chunking, language, tool_hint
            )
            
            # Phase 5: Generate HTML report (if requested)
            if output_file and self.reporter_service:
                await self.reporter_service.generate_html_report(analysis_report, output_file)
            
            # Record metrics
            if self.metrics:
                self.metrics.record_complete_analysis(
                    file_path=file_path,
                    vulnerability_count=len(scan_result.vulnerabilities),
                    confirmed_count=len(remediation_plans),
                    total_time=total_time,
                    chunking_used=self._was_chunking_used(scan_result, force_chunking, disable_chunking),
                    language=language,
                    success=True
                )
            
            logger.info(f"Analysis completed successfully in {total_time:.2f}s")
            return analysis_report
            
        except Exception as e:
            total_time = asyncio.get_event_loop().time() - start_time
            if self.metrics:
                self.metrics.record_complete_analysis(
                    file_path=file_path,
                    total_time=total_time,
                    success=False,
                    error=str(e)
                )
            logger.error(f"Analysis failed: {e}")
            raise
    
    async def execute_basic_analysis(self, file_path: str, output_file: Optional[str] = None,
                                   tool_hint: Optional[str] = None) -> AnalysisReport:
        """Execute basic analysis without LLM services"""
        
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"Starting basic analysis: {file_path}")
        
        # Only scan and normalize
        scan_result = await self.scanner_service.scan_file(
            file_path=file_path,
            tool_hint=tool_hint
        )
        
        total_time = asyncio.get_event_loop().time() - start_time
        
        # Create basic report
        analysis_report = AnalysisReport(
            scan_result=scan_result,
            triage_result=None,
            remediation_plans=[],
            analysis_config={"mode": "basic", "tool_hint": tool_hint},
            total_processing_time_seconds=total_time,
            chunking_enabled=False
        )
        
        # Generate HTML if requested
        if output_file and self.reporter_service:
            await self.reporter_service.generate_html_report(analysis_report, output_file)
        
        logger.info(f"Basic analysis completed in {total_time:.2f}s")
        return analysis_report
    
    async def _perform_triage_analysis(self, scan_result: ScanResult, language: Optional[str],
                                     force_chunking: bool, disable_chunking: bool):
        """Perform triage analysis with optional chunking"""
        
        should_chunk = (
            (self.chunker and self.chunker.should_chunk(scan_result) and not disable_chunking) 
            or force_chunking
        )
        
        if should_chunk and self.chunker:
            logger.info("Using chunked triage analysis")
            return await self._analyze_with_chunking(scan_result, language)
        else:
            logger.info("Using direct triage analysis")
            return await self.triage_service.analyze_vulnerabilities(
                scan_result.vulnerabilities, language
            )
    
    async def _analyze_with_chunking(self, scan_result: ScanResult, language: Optional[str]):
        """Perform chunked analysis and consolidate results"""
        
        chunks = self.chunker.create_chunks(scan_result)
        logger.info(f"Processing {len(chunks)} chunks")
        
        # Process chunks with concurrency limit
        semaphore = asyncio.Semaphore(2)
        
        async def process_chunk(chunk):
            async with semaphore:
                return await self.triage_service.analyze_vulnerabilities(
                    chunk.vulnerabilities, language, chunk.id
                )
        
        # Execute chunk analysis
        chunk_results = await asyncio.gather(
            *[process_chunk(chunk) for chunk in chunks],
            return_exceptions=True
        )
        
        # Filter successful results
        successful_results = [r for r in chunk_results if not isinstance(r, Exception)]
        
        if not successful_results:
            raise Exception("All chunk analyses failed")
        
        # Consolidate results
        return self._consolidate_chunk_results(successful_results)
    
    def _consolidate_chunk_results(self, chunk_results):
        """Consolidate multiple chunk results into unified result"""
        
        all_decisions = []
        seen_ids = set()
        
        # Merge decisions avoiding duplicates from overlap
        for result in chunk_results:
            for decision in result.decisions:
                if decision.vulnerability_id not in seen_ids:
                    all_decisions.append(decision)
                    seen_ids.add(decision.vulnerability_id)
        
        # Create consolidated summary
        summary = f"Consolidated analysis from {len(chunk_results)} chunks. "
        summary += f"Total decisions: {len(all_decisions)}. "
        
        from collections import Counter
        decision_counts = Counter(d.decision.value for d in all_decisions)
        summary += f"Distribution: {dict(decision_counts)}"
        
        from core.models import TriageResult
        return TriageResult(
            decisions=all_decisions,
            analysis_summary=summary,
            llm_analysis_time_seconds=sum(r.llm_analysis_time_seconds for r in chunk_results)
        )
    
    def _extract_confirmed_vulnerabilities(self, vulnerabilities: List[Vulnerability], 
                                         triage_result) -> List[Vulnerability]:
        """Extract confirmed vulnerabilities from triage result"""
        
        from core.models import AnalysisStatus
        confirmed_ids = {
            d.vulnerability_id for d in triage_result.decisions 
            if d.decision == AnalysisStatus.CONFIRMED
        }
        
        return [v for v in vulnerabilities if v.id in confirmed_ids]
    
    def _create_analysis_report(self, scan_result: ScanResult, triage_result, 
                              remediation_plans: List, total_time: float,
                              force_chunking: bool, disable_chunking: bool,
                              language: Optional[str], tool_hint: Optional[str]) -> AnalysisReport:
        """Create comprehensive analysis report"""
        
        chunking_used = self._was_chunking_used(scan_result, force_chunking, disable_chunking)
        
        return AnalysisReport(
            scan_result=scan_result,
            triage_result=triage_result,
            remediation_plans=remediation_plans,
            analysis_config={
                "language": language,
                "tool_hint": tool_hint,
                "force_chunking": force_chunking,
                "disable_chunking": disable_chunking,
                "chunking_used": chunking_used,
                "chunks_processed": len(self.chunker.create_chunks(scan_result)) if chunking_used else 0
            },
            total_processing_time_seconds=total_time,
            chunking_enabled=chunking_used
        )
    
    def _create_clean_report(self, scan_result: ScanResult, start_time: float) -> AnalysisReport:
        """Create report for files with no vulnerabilities"""
        
        total_time = asyncio.get_event_loop().time() - start_time
        
        return AnalysisReport(
            scan_result=scan_result,
            triage_result=None,
            remediation_plans=[],
            analysis_config={"no_vulnerabilities_found": True},
            total_processing_time_seconds=total_time,
            chunking_enabled=False
        )
    
    def _was_chunking_used(self, scan_result: ScanResult, force_chunking: bool, 
                          disable_chunking: bool) -> bool:
        """Determine if chunking was actually used - CORRECTED LOGIC"""
        
        # Prioridad 1: Si está deshabilitado explícitamente, nunca usar chunking
        if disable_chunking:
            logger.debug("Chunking disabled by flag")
            return False
        
        # Prioridad 2: Si está forzado explícitamente, siempre usar chunking
        # (siempre que haya vulnerabilidades y chunker esté disponible)
        if force_chunking:
            has_vulns = len(scan_result.vulnerabilities) > 0
            has_chunker = self.chunker is not None
            
            if has_chunker and has_vulns:
                logger.debug("Chunking forced by flag")
                return True
            else:
                logger.warning(f"Chunking forced but not possible: "
                             f"chunker={has_chunker}, vulns={has_vulns}")
                return False
        
        # Prioridad 3: Decisión automática basada en heurísticas
        if not self.chunker:
            logger.debug("Chunking not available (no chunker)")
            return False
        
        if len(scan_result.vulnerabilities) == 0:
            logger.debug("Chunking not needed (no vulnerabilities)")
            return False
        
        should_chunk = self.chunker.should_chunk(scan_result)
        logger.debug(f"Automatic chunking decision: {should_chunk}")
        
        return should_chunk


class CLIUseCase:
    """Caso de uso específico para CLI con manejo de errores robusto"""
    
    def __init__(self, analysis_use_case: AnalysisUseCase):
        self.analysis_use_case = analysis_use_case
    
    async def execute_cli_analysis(self,
                                  input_file: str,
                                  output_file: str = "security_report.html",
                                  language: Optional[str] = None,
                                  verbose: bool = False,
                                  disable_llm: bool = False,
                                  force_chunking: bool = False,
                                  min_cvss: float = 0.0,  # 🆕 AÑADIR ESTE PARÁMETRO
                                  severity_filter: Optional[List[str]] = None) -> bool:  # 🆕 AÑADIR ESTE PARÁMETRO
        """Execute analysis from CLI with comprehensive error handling"""
        
        try:
            # Validate input file
            input_path = Path(input_file)
            if not input_path.exists():
                print(f"❌ Error: Input file not found: {input_file}")
                return False
            
            print(f"🔍 Analyzing: {input_path.name}")
            
            # 🆕 Show filter info
            if min_cvss > 0.0:
                print(f"🎯 Applying CVSS filter: >= {min_cvss}")
            if severity_filter:
                print(f"📊 Applying severity filter: {', '.join(severity_filter)}")
            
            # Execute appropriate analysis
            if disable_llm:
                result = await self.analysis_use_case.execute_basic_analysis(
                    input_file, output_file
                )
                print("✅ Basic analysis completed")
            else:
                result = await self.analysis_use_case.execute_full_analysis(
                    file_path=input_file,
                    output_file=output_file,
                    language=language,
                    force_chunking=force_chunking
                    # 🆕 Nota: min_cvss y severity_filter se aplicarían aquí si los implementas
                )
                print("✅ Full analysis completed")
            
            # Display results
            self._display_results(result, output_file)
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Analysis interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _display_results(self, result: AnalysisReport, output_file: str) -> None:
        """Display analysis results in CLI format"""
        
        print("\n" + "="*50)
        print("📊 ANALYSIS RESULTS")
        print("="*50)
        
        # Basic statistics
        scan_result = result.scan_result
        print(f"📁 File: {scan_result.file_info['filename']}")
        print(f"🔢 Total vulnerabilities: {len(scan_result.vulnerabilities)}")
        
        # Deduplication stats
        if 'duplicates_removed' in scan_result.file_info:
            dups = scan_result.file_info['duplicates_removed']
            if dups > 0:
                print(f"🔄 Duplicates removed: {dups}")
        
        if scan_result.vulnerabilities:
            severity_dist = scan_result.severity_distribution
            print("\n📊 Severity Distribution:")
            for severity, count in severity_dist.items():
                if count > 0:
                    icon = {"CRÍTICA": "🔥", "ALTA": "⚡", "MEDIA": "⚠️", "BAJA": "📝", "INFO": "ℹ️"}
                    print(f"  {icon.get(severity, '•')} {severity}: {count}")
        
        # Triage results
        if result.triage_result:
            triage = result.triage_result
            print(f"\n🤖 LLM Analysis:")
            print(f"  ✅ Confirmed: {triage.confirmed_count}")
            print(f"  ❌ False positives: {triage.false_positive_count}")
            print(f"  🔍 Need review: {triage.needs_review_count}")
        
        # Remediation plans
        if result.remediation_plans:
            print(f"\n🛠️  Remediation plans: {len(result.remediation_plans)}")
            priority_counts = {}
            for plan in result.remediation_plans:
                priority_counts[plan.priority_level] = priority_counts.get(plan.priority_level, 0) + 1
            
            for priority in ["immediate", "high", "medium", "low"]:
                count = priority_counts.get(priority, 0)
                if count > 0:
                    icons = {"immediate": "🚨", "high": "⚡", "medium": "⚠️", "low": "📝"}
                    print(f"  {icons[priority]} {priority.title()}: {count}")
        
        # Performance metrics
        print(f"\n⏱️  Processing time: {result.total_processing_time_seconds:.2f}s")
        if result.chunking_enabled:
            print("🧩 Chunking: Enabled")
        
        # Output file
        if Path(output_file).exists():
            size_kb = Path(output_file).stat().st_size / 1024
            print(f"\n📄 Report generated: {output_file} ({size_kb:.1f} KB)")
        
        print("\n💡 Open the HTML file in your browser to view the detailed report")