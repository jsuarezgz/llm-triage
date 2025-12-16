# adapters/output/html_generator.py
"""
HTML Report Generator - Optimized
=================================

Responsibilities:
- Generate HTML reports from analysis results
- Apply templates with Jinja2
- Handle fallback generation
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.models import AnalysisReport, Vulnerability
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class OptimizedHTMLGenerator:
    """Optimized HTML generator with Jinja2 templates"""
    
    def __init__(
        self,
        template_dir: Optional[Path] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """
        Initialize HTML generator
        
        Args:
            template_dir: Templates directory
            metrics: Optional metrics collector
        """
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.metrics = metrics
        
        # Configure Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register filters
        self._register_filters()
        
        logger.info("📄 HTML Generator initialized")
    
    def generate_report(
        self,
        analysis_report: AnalysisReport,
        output_file: str
    ) -> bool:
        """
        Generate HTML report
        
        Args:
            analysis_report: Complete analysis report
            output_file: Output file path
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"📝 Generating HTML: {output_file}")
            
            # Prepare context
            context = self._prepare_context(analysis_report)
            
            # Render template
            template = self.env.get_template('report.html')
            html_content = template.render(**context)
            
            # Write file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Record metrics
            file_size = output_path.stat().st_size
            if self.metrics:
                self.metrics.record_report_generation(
                    "html",
                    file_size,
                    len(analysis_report.scan_result.vulnerabilities),
                    True
                )
            
            logger.info(f"✅ Report generated: {output_file} ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ HTML generation failed: {e}")
            if self.metrics:
                self.metrics.record_report_generation("html", success=False, error=str(e))
            
            # Try fallback
            return self._generate_fallback(analysis_report, output_file)
    
    # ════════════════════════════════════════════════════════════════
    # PRIVATE HELPERS
    # ════════════════════════════════════════════════════════════════
    
    def _prepare_context(self, report: AnalysisReport) -> Dict[str, Any]:
        """Prepare template context"""
        scan = report.scan_result
        vulns = scan.vulnerabilities
        
        # Calculate metrics
        severity_stats = self._calc_severity_stats(vulns)
        risk_score = self._calc_risk_score(vulns)
        
        return {
            # Main data
            'report': report,
            'scan_result': scan,
            'triage_result': report.triage_result,
            'remediation_plans': report.remediation_plans,
            
            # Metrics
            'total_vulnerabilities': len(vulns),
            'high_priority_count': len([v for v in vulns if v.is_high_priority]),
            'severity_stats': severity_stats,
            'risk_score': risk_score,
            
            # Metadata
            'generation_timestamp': datetime.now(),
            'report_version': '3.0',
            'platform_name': 'Security Analysis Platform v3.0'
        }
    
    def _calc_severity_stats(self, vulns: list) -> Dict[str, int]:
        """Calculate severity distribution"""
        from collections import Counter
        return dict(Counter(v.severity.value for v in vulns))
    
    def _calc_risk_score(self, vulns: list) -> float:
        """Calculate risk score (0-10)"""
        if not vulns:
            return 0.0
        
        from shared.constants import SEVERITY_WEIGHTS
        
        total = sum(SEVERITY_WEIGHTS.get(v.severity.value, 0) for v in vulns)
        max_possible = len(vulns) * 10.0
        
        normalized = (total / max_possible) * 10.0 if max_possible > 0 else 0.0
        return round(min(normalized, 10.0), 1)
    
    def _generate_fallback(
        self,
        report: AnalysisReport,
        output_file: str
    ) -> bool:
        """Generate minimal fallback report"""
        logger.warning("⚠️  Generating fallback report")
        
        try:
            scan = report.scan_result
            vuln_count = len(scan.vulnerabilities)
            
            html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Security Analysis Report - Fallback</title>
    <style>
        body {{ font-family: system-ui; margin: 20px; line-height: 1.6; }}
        .header {{ background: #4f46e5; color: white; padding: 20px; border-radius: 8px; }}
        .summary {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .vuln {{ background: #fef2f2; padding: 15px; margin: 10px 0; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Security Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>File:</strong> {scan.file_info.get('filename', 'Unknown')}</p>
        <p><strong>Vulnerabilities:</strong> {vuln_count}</p>
        <p><strong>Time:</strong> {report.total_processing_time_seconds:.2f}s</p>
    </div>
"""
            
            if vuln_count > 0:
                html += '<div class="summary"><h2>🚨 Vulnerabilities</h2>'
                
                for i, vuln in enumerate(scan.vulnerabilities[:10], 1):
                    html += f'''
    <div class="vuln">
        <h3>{i}. {vuln.title}</h3>
        <p><strong>Severity:</strong> {vuln.severity.value}</p>
        <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number}</p>
        <p>{vuln.description[:200]}...</p>
    </div>'''
                
                if vuln_count > 10:
                    html += f'<p><em>... and {vuln_count - 10} more vulnerabilities</em></p>'
                
                html += '</div>'
            else:
                html += '''
    <div class="summary">
        <h2>✅ No Vulnerabilities Found</h2>
    </div>'''
            
            html += '''
    <div class="summary">
        <p>⚠️ Simplified report due to template error</p>
        <p>Generated by Security Analysis Platform v3.0</p>
    </div>
</body>
</html>'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ Fallback report generated: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Even fallback failed: {e}")
            return False
    
    def _register_filters(self):
        """Register Jinja2 filters"""
        from shared.formatters import (
            format_bytes, format_duration, format_severity_icon, truncate_text
        )
        
        self.env.filters['format_bytes'] = format_bytes
        self.env.filters['format_duration'] = format_duration
        self.env.filters['severity_icon'] = format_severity_icon
        self.env.filters['truncate_smart'] = truncate_text
        
        # Severity class filter
        def severity_class(severity):
            classes = {
                'CRÍTICA': 'critical',
                'ALTA': 'high',
                'MEDIA': 'medium',
                'BAJA': 'low',
                'INFO': 'info'
            }
            sev_str = severity if isinstance(severity, str) else str(severity)
            return classes.get(sev_str.upper(), 'default')
        
        self.env.filters['severity_class'] = severity_class
