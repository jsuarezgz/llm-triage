# application/use_cases.py
"""
Use Cases - Application Logic
=============================

Responsibilities:
- Orchestrate analysis workflow
- Handle errors gracefully
- Manage chunking decisions
- Generate reports
"""

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


# ════════════════════════════════════════════════════════════════════
# MAIN ANALYSIS USE CASE
# ════════════════════════════════════════════════════════════════════

class AnalysisUseCase:
    """Main analysis workflow orchestrator"""
    
    def __init__(
        self,
        scanner_service: ScannerService,
        triage_service: Optional[TriageService] = None,
        remediation_service: Optional[RemediationService] = None,
        reporter_service: Optional[ReporterService] = None,
        chunker: Optional[OptimizedChunker] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        self.scanner = scanner_service
        self.triage = triage_service
        self.remediation = remediation_service
        self.reporter = reporter_service
        self.chunker = chunker
        self.metrics = metrics
    
    async def execute_full_analysis(
        self,
        file_path: str,
        output_file: Optional[str] = None,
        language: Optional[str] = None,
        tool_hint: Optional[str] = None,
        force_chunking: bool = False,
        disable_chunking: bool = False
    ) -> AnalysisReport:
        """
        Execute complete analysis pipeline
        
        Steps:
        1. Scan and normalize
        2. Triage with LLM (optional)
        3. Generate remediation plans (optional)
        4. Create report
        5. Generate HTML output (optional)
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🚀 Starting analysis: {file_path}")
            
            # Step 1: Scan
            scan_result = await self.scanner.scan_file(
                file_path=file_path,
                language=language,
                tool_hint=tool_hint
            )
            
            if not scan_result.vulnerabilities:
                logger.info("✅ No vulnerabilities found")
                return self._create_clean_report(scan_result, start_time)
            
            # Step 2: Triage (if LLM available)
            triage_result = None
            if self.triage:
                triage_result = await self._perform_triage(
                    scan_result, language, force_chunking, disable_chunking
                )
            
            # Step 3: Remediation (if triage confirmed vulns)
            remediation_plans = []
            if self.remediation and triage_result:
                confirmed_vulns = self._get_confirmed_vulns(
                    scan_result.vulnerabilities, triage_result
                )
                if confirmed_vulns:
                    remediation_plans = await self.remediation.generate_remediation_plans(
                        confirmed_vulns, language
                    )
            
            # Step 4: Create report
            total_time = asyncio.get_event_loop().time() - start_time
            report = self._create_report(
                scan_result, triage_result, remediation_plans,
                total_time, force_chunking, disable_chunking, language, tool_hint
            )
            
            # Step 5: Generate HTML (if requested)
            if output_file and self.reporter:
                await self.reporter.generate_html_report(report, output_file)
            
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
            
            logger.info(f"✅ Analysis complete in {total_time:.2f}s")
            return report
            
        except Exception as e:
            total_time = asyncio.get_event_loop().time() - start_time
            if self.metrics:
                self.metrics.record_complete_analysis(
                    file_path=file_path,
                    total_time=total_time,
                    success=False,
                    error=str(e)
                )
            logger.error(f"❌ Analysis failed: {e}")
            raise
    
    async def execute_basic_analysis(
        self,
        file_path: str,
        output_file: Optional[str] = None,
        tool_hint: Optional[str] = None
    ) -> AnalysisReport:
        """Execute basic analysis without LLM"""
        start_time = asyncio.get_event_loop().time()
        
        logger.info(f"🚀 Starting basic analysis: {file_path}")
        
        # Only scan
        scan_result = await self.scanner.scan_file(
            file_path=file_path,
            tool_hint=tool_hint
        )
        
        total_time = asyncio.get_event_loop().time() - start_time
        
        # Create basic report
        report = AnalysisReport(
            scan_result=scan_result,
            triage_result=None,
            remediation_plans=[],
            analysis_config={"mode": "basic", "tool_hint": tool_hint},
            total_processing_time_seconds=total_time,
            chunking_enabled=False
        )
        
        # Generate HTML if requested
        if output_file and self.reporter:
            await self.reporter.generate_html_report(report, output_file)
        
        logger.info(f"✅ Basic analysis complete in {total_time:.2f}s")
        return report
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    async def _perform_triage(
        self,
        scan_result: ScanResult,
        language: Optional[str],
        force_chunking: bool,
        disable_chunking: bool
    ):
        """Perform triage with optional chunking"""
        should_chunk = (
            self.chunker and
            self.chunker.should_chunk(scan_result) and
            not disable_chunking
        ) or force_chunking
        
        if should_chunk and self.chunker:
            logger.info("🧩 Using chunked analysis")
            return await self._analyze_with_chunking(scan_result, language)
        else:
            logger.info("📊 Using direct analysis")
            return await self.triage.analyze_vulnerabilities(
                scan_result.vulnerabilities, language
            )
    
    async def _analyze_with_chunking(self, scan_result: ScanResult, language: Optional[str]):
        """Analyze with chunking"""
        chunks = self.chunker.create_chunks(scan_result)
        logger.info(f"📦 Processing {len(chunks)} chunks")
        
        # Process with concurrency limit
        semaphore = asyncio.Semaphore(2)
        
        async def process_chunk(chunk):
            async with semaphore:
                return await self.triage.analyze_vulnerabilities(
                    chunk.vulnerabilities, language, chunk.id
                )
        
        # Execute
        results = await asyncio.gather(
            *[process_chunk(chunk) for chunk in chunks],
            return_exceptions=True
        )
        
        # Filter successful
        successful = [r for r in results if not isinstance(r, Exception)]
        
        if not successful:
            raise Exception("All chunk analyses failed")
        
        # Consolidate
        return self._consolidate_results(successful)
    
    def _consolidate_results(self, chunk_results):
        """Consolidate multiple chunk results"""
        all_decisions = []
        seen_ids = set()
        
        for result in chunk_results:
            for decision in result.decisions:
                if decision.vulnerability_id not in seen_ids:
                    all_decisions.append(decision)
                    seen_ids.add(decision.vulnerability_id)
        
        from collections import Counter
        from core.models import TriageResult
        
        decision_counts = Counter(d.decision.value for d in all_decisions)
        summary = (
            f"Consolidated from {len(chunk_results)} chunks. "
            f"Total: {len(all_decisions)}. "
            f"Distribution: {dict(decision_counts)}"
        )
        
        return TriageResult(
            decisions=all_decisions,
            analysis_summary=summary,
            llm_analysis_time_seconds=sum(r.llm_analysis_time_seconds for r in chunk_results)
        )
    
    def _get_confirmed_vulns(
        self,
        vulnerabilities: List[Vulnerability],
        triage_result
    ) -> List[Vulnerability]:
        """Extract confirmed vulnerabilities"""
        from core.models import AnalysisStatus
        
        confirmed_ids = {
            d.vulnerability_id for d in triage_result.decisions
            if d.decision == AnalysisStatus.CONFIRMED
        }
        
        return [v for v in vulnerabilities if v.id in confirmed_ids]
    
    def _create_report(
        self,
        scan_result: ScanResult,
        triage_result,
        remediation_plans: List,
        total_time: float,
        force_chunking: bool,
        disable_chunking: bool,
        language: Optional[str],
        tool_hint: Optional[str]
    ) -> AnalysisReport:
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
                "chunks_processed": (
                    len(self.chunker.create_chunks(scan_result)) if chunking_used else 0
                )
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
    
    def _was_chunking_used(
        self,
        scan_result: ScanResult,
        force_chunking: bool,
        disable_chunking: bool
    ) -> bool:
        """Determine if chunking was used"""
        # Priority 1: Explicitly disabled
        if disable_chunking:
            return False
        
        # Priority 2: Explicitly forced
        if force_chunking and self.chunker and scan_result.vulnerabilities:
            return True
        
        # Priority 3: Automatic decision
        if self.chunker and scan_result.vulnerabilities:
            return self.chunker.should_chunk(scan_result)
        
        return False


# ════════════════════════════════════════════════════════════════════
# CLI USE CASE
# ════════════════════════════════════════════════════════════════════

class CLIUseCase:
    """CLI-specific use case with user-friendly output"""
    
    def __init__(self, analysis_use_case: AnalysisUseCase):
        self.analysis = analysis_use_case
    
    async def execute_cli_analysis(
        self,
        input_file: str,
        output_file: str = "security_report.html",
        language: Optional[str] = None,
        verbose: bool = False,
        disable_llm: bool = False,
        force_chunking: bool = False,
        disable_chunking: bool = False
    ) -> bool:
        """Execute analysis with CLI-friendly output"""
        
        try:
            # Validate input
            input_path = Path(input_file)
            if not input_path.exists():
                print(f"❌ File not found: {input_file}")
                return False
            
            print(f"🔍 Analyzing: {input_path.name}")
            
            # Execute analysis
            if disable_llm:
                result = await self.analysis.execute_basic_analysis(input_file, output_file)
                print("✅ Basic analysis completed")
            else:
                result = await self.analysis.execute_full_analysis(
                    file_path=input_file,
                    output_file=output_file,
                    language=language,
                    force_chunking=force_chunking,
                    disable_chunking=disable_chunking
                )
                print("✅ Full analysis completed")
            
            # Display results
            self._display_results(result, output_file)
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _display_results(self, result: AnalysisReport, output_file: str) -> None:
        """Display results in CLI format"""
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULTS")
        print("="*60)
        
        # Basic stats
        scan = result.scan_result
        print(f"\n📁 File: {scan.file_info['filename']}")
        print(f"🔢 Total vulnerabilities: {len(scan.vulnerabilities)}")
        
        # Deduplication stats
        if 'duplicates_removed' in scan.file_info:
            dups = scan.file_info['duplicates_removed']
            if dups > 0:
                print(f"🔄 Duplicates removed: {dups}")
        
        # Severity distribution
        if scan.vulnerabilities:
            print("\n📈 Severity Distribution:")
            for severity, count in scan.severity_distribution.items():
                if count > 0:
                    icons = {"CRÍTICA": "🔥", "ALTA": "⚡", "MEDIA": "⚠️", "BAJA": "📝", "INFO": "ℹ️"}
                    icon = icons.get(severity, "•")
                    print(f"   {icon} {severity}: {count}")
        
        # Triage results
        if result.triage_result:
            triage = result.triage_result
            print(f"\n🤖 LLM Analysis:")
            print(f"   ✅ Confirmed: {triage.confirmed_count}")
            print(f"   ❌ False positives: {triage.false_positive_count}")
            print(f"   🔍 Need review: {triage.needs_review_count}")
        
        # Remediation plans
        if result.remediation_plans:
            print(f"\n🛠️  Remediation plans: {len(result.remediation_plans)}")
        
        # Performance
        print(f"\n⏱️  Processing time: {result.total_processing_time_seconds:.2f}s")
        if result.chunking_enabled:
            print("🧩 Chunking: Enabled")
        
        # Output file
        if Path(output_file).exists():
            size_kb = Path(output_file).stat().st_size / 1024
            print(f"\n📄 Report: {output_file} ({size_kb:.1f} KB)")
        
        print("\n💡 Open the HTML file in your browser to view the detailed report")
        print("="*60)
