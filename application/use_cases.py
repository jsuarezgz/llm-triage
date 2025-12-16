# application/use_cases.py
"""
Use Cases - Simplified Version (No Dedup, No CVSS, No BasicMode)
================================================================
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
from core.services.vulnerability_filter import VulnerabilityFilter
from adapters.processing.chunker import OptimizedChunker
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class AnalysisUseCase:
    """Main analysis workflow orchestrator with simplified filtering"""
    
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
        self.filter = VulnerabilityFilter()
    
    async def execute_full_analysis(
        self,
        file_path: str,
        output_file: Optional[str] = None,
        language: Optional[str] = None,
        tool_hint: Optional[str] = None,
        force_chunking: bool = False,
        disable_chunking: bool = False,
        # Filtering parameters (SIMPLIFIED)
        min_severity: Optional[str] = None,
        max_vulns: Optional[int] = None,
        group_similar: bool = False
    ) -> AnalysisReport:
        """
        Execute complete analysis pipeline with simplified filtering
        
        Pipeline:
        1. Scan and normalize
        2. Apply filters (severity, grouping)
        3. Triage with LLM
        4. Generate remediation plans
        5. Create report
        6. Generate HTML output
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
            
            original_count = len(scan_result.vulnerabilities)
            logger.info(f"📊 Found {original_count} vulnerabilities")
            
            # Step 2: FILTERING (Severity + Grouping)
            if min_severity or group_similar or max_vulns:
                logger.info("🔍 Applying filters...")
                scan_result.vulnerabilities = self.filter.apply_filters(
                    scan_result.vulnerabilities,
                    min_cvss=None,  # Not used
                    min_severity=min_severity,
                    max_vulns=max_vulns,
                    group_similar=group_similar
                )
                
                # Log filtering stats
                stats = self.filter.get_statistics()
                logger.info(f"   Filtered: {stats['original_count']} → {stats['filtered_count']}")
                if stats['grouped_count'] > 0:
                    logger.info(f"   Grouped: {stats['grouped_count']} similar vulnerabilities")
                
                # Update metadata
                scan_result.file_info['pre_filter_count'] = original_count
                scan_result.file_info['post_filter_count'] = len(scan_result.vulnerabilities)
                scan_result.file_info['filtering_applied'] = True
            
            if not scan_result.vulnerabilities:
                logger.info("⚠️  All vulnerabilities filtered out")
                return self._create_clean_report(scan_result, start_time)
            
            # Step 3: Triage (if LLM available)
            triage_result = None
            if self.triage:
                triage_result = await self._perform_triage(
                    scan_result, language, force_chunking, disable_chunking
                )
            
            # Step 4: Remediation (for all vulnerabilities)
            remediation_plans = []
            if self.remediation and scan_result.vulnerabilities:
                remediation_plans = await self.remediation.generate_remediation_plans(
                    scan_result.vulnerabilities, language
                )
            
            # Step 5: Create report
            total_time = asyncio.get_event_loop().time() - start_time
            report = self._create_report(
                scan_result, triage_result, remediation_plans,
                total_time, force_chunking, disable_chunking, language, tool_hint,
                filtering_config={
                    'min_severity': min_severity,
                    'max_vulns': max_vulns,
                    'group_similar': group_similar,
                    'filter_stats': self.filter.get_statistics()
                }
            )
            
            # Step 6: Generate HTML
            if output_file and self.reporter:
                await self.reporter.generate_html_report(report, output_file)
            
            # Record metrics
            if self.metrics:
                self.metrics.record_complete_analysis(
                    file_path=file_path,
                    vulnerability_count=original_count,
                    confirmed_count=len(scan_result.vulnerabilities),
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
        
        semaphore = asyncio.Semaphore(2)
        
        async def process_chunk(chunk):
            async with semaphore:
                return await self.triage.analyze_vulnerabilities(
                    chunk.vulnerabilities, language, chunk.id
                )
        
        results = await asyncio.gather(
            *[process_chunk(chunk) for chunk in chunks],
            return_exceptions=True
        )
        
        successful = [r for r in results if not isinstance(r, Exception)]
        
        if not successful:
            raise Exception("All chunk analyses failed")
        
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
    
    def _create_report(
        self,
        scan_result: ScanResult,
        triage_result,
        remediation_plans: List,
        total_time: float,
        force_chunking: bool,
        disable_chunking: bool,
        language: Optional[str],
        tool_hint: Optional[str],
        filtering_config: dict = None
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
                ),
                "filtering": filtering_config or {}
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
        if disable_chunking:
            return False
        
        if force_chunking and self.chunker and scan_result.vulnerabilities:
            return True
        
        if self.chunker and scan_result.vulnerabilities:
            return self.chunker.should_chunk(scan_result)
        
        return False


# ════════════════════════════════════════════════════════════════
# CLI USE CASE
# ════════════════════════════════════════════════════════════════

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
        force_chunking: bool = False,
        disable_chunking: bool = False,
        # Simplified filtering
        min_severity: Optional[str] = None,
        max_vulns: Optional[int] = None,
        group_similar: bool = False
    ) -> bool:
        """Execute CLI analysis with progress reporting"""
        try:
            # Execute analysis
            report = await self.analysis.execute_full_analysis(
                file_path=input_file,
                output_file=output_file,
                language=language,
                force_chunking=force_chunking,
                disable_chunking=disable_chunking,
                min_severity=min_severity,
                max_vulns=max_vulns,
                group_similar=group_similar
            )
            
            # Display summary
            self._display_summary(report)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ CLI analysis failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    def _display_summary(self, report: AnalysisReport) -> None:
        """Display analysis summary to console"""
        print("\n" + "="*60)
        print("📊 ANALYSIS SUMMARY")
        print("="*60)
        
        # Basic stats
        total_vulns = report.scan_result.vulnerability_count
        print(f"\n📋 Total Vulnerabilities: {total_vulns}")
        
        if total_vulns > 0:
            # Severity distribution
            print("\n🎯 Severity Distribution:")
            for severity, count in report.scan_result.severity_distribution.items():
                print(f"   {severity}: {count}")
            
            # High priority
            high_priority = report.scan_result.high_priority_count
            if high_priority > 0:
                print(f"\n⚡ High Priority: {high_priority}")
        
        # Triage results
        if report.triage_result:
            print("\n🤖 LLM Triage:")
            print(f"   Confirmed: {report.triage_result.confirmed_count}")
            print(f"   False Positives: {report.triage_result.false_positive_count}")
            print(f"   Needs Review: {report.triage_result.needs_review_count}")
        
        # Remediation
        if report.remediation_plans:
            print(f"\n🛠️  Remediation Plans: {len(report.remediation_plans)}")
        
        # Filtering stats
        if 'filtering' in report.analysis_config:
            filter_config = report.analysis_config['filtering']
            if filter_config.get('filter_stats'):
                stats = filter_config['filter_stats']
                if stats.get('original_count', 0) != stats.get('filtered_count', 0):
                    print(f"\n🔍 Filtering Applied:")
                    print(f"   Original: {stats.get('original_count', 0)}")
                    print(f"   After Filter: {stats.get('filtered_count', 0)}")
                    if stats.get('grouped_count', 0) > 0:
                        print(f"   Grouped: {stats.get('grouped_count', 0)}")
        
        # Performance
        print(f"\n⏱️  Processing Time: {report.total_processing_time_seconds:.2f}s")
        
        # Chunking info
        if report.chunking_enabled:
            chunks = report.analysis_config.get('chunks_processed', 0)
            print(f"🧩 Chunking: Used ({chunks} chunks)")
        
        print("\n" + "="*60)
        print("✅ Analysis Complete")
        print("="*60)
