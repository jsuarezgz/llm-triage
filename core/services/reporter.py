# core/services/reporter.py
"""
Reporter Service - Simplified
=============================

Responsibilities:
- Generate HTML reports
- Track metrics
"""

import logging
from pathlib import Path
from typing import Optional

from ..models import AnalysisReport
from adapters.output.html_generator import OptimizedHTMLGenerator
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class ReporterService:
    """Simplified reporter service"""
    
    def __init__(
        self,
        html_generator: Optional[OptimizedHTMLGenerator] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        self.html_generator = html_generator or OptimizedHTMLGenerator()
        self.metrics = metrics
    
    async def generate_html_report(
        self,
        analysis_report: AnalysisReport,
        output_file: str
    ) -> bool:
        """
        Generate HTML report with metrics
        
        Args:
            analysis_report: Complete analysis report
            output_file: Output file path
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"📄 Generating HTML report: {output_file}")
            
            # Generate report
            success = self.html_generator.generate_report(
                analysis_report,
                output_file
            )
            
            if success:
                file_size = Path(output_file).stat().st_size
                
                # Record metrics
                if self.metrics:
                    self.metrics.record_report_generation(
                        "html",
                        file_size,
                        len(analysis_report.scan_result.vulnerabilities),
                        True
                    )
                
                logger.info(f"✅ Report generated: {output_file} ({file_size:,} bytes)")
            else:
                if self.metrics:
                    self.metrics.record_report_generation("html", success=False)
                
                logger.error(f"❌ Failed to generate: {output_file}")
            
            return success
            
        except Exception as e:
            if self.metrics:
                self.metrics.record_report_generation(
                    "html", success=False, error=str(e)
                )
            
            logger.error(f"❌ Report generation failed: {e}")
            return False
