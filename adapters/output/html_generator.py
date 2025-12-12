# adapters/output/html_generator.py
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.models import AnalysisReport, Vulnerability
from shared.metrics import MetricsCollector

logger = logging.getLogger(__name__)

class OptimizedHTMLGenerator:
    """Generador HTML optimizado y simplificado"""
    
    def __init__(self, template_dir: Optional[Path] = None, metrics: Optional[MetricsCollector] = None):
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.metrics = metrics
        
        # Configure Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register optimized filters
        self._register_filters()
        
        logger.info(f"HTML Generator initialized")
    
    def generate_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
        """Generate optimized HTML report"""
        
        try:
            logger.info(f"Generating HTML report: {output_file}")
            
            # Prepare template context
            context = self._prepare_context(analysis_report)
            
            # Render main template
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
                    "html", file_size, len(analysis_report.scan_result.vulnerabilities), True
                )
            
            logger.info(f"HTML report generated: {output_file} ({file_size:,} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            if self.metrics:
                self.metrics.record_report_generation("html", success=False, error=str(e))
            
            # Try fallback generation
            return self._generate_fallback_report(analysis_report, output_file)
    
    def _prepare_context(self, analysis_report: AnalysisReport) -> Dict[str, Any]:
        """Prepare optimized template context"""
        
        scan_result = analysis_report.scan_result
        vulnerabilities = scan_result.vulnerabilities
        
        # Calculate derived metrics
        severity_stats = self._calculate_severity_stats(vulnerabilities)
        risk_score = self._calculate_risk_score(vulnerabilities)
        
        return {
            # Main data
            'report': analysis_report,
            'scan_result': scan_result,
            'triage_result': analysis_report.triage_result,
            'remediation_plans': analysis_report.remediation_plans,
            
            # Calculated metrics
            'total_vulnerabilities': len(vulnerabilities),
            'high_priority_count': len([v for v in vulnerabilities if v.is_high_priority]),
            'severity_stats': severity_stats,
            'risk_score': risk_score,
            
            # Report metadata
            'generation_timestamp': datetime.now(),
            'report_version': '3.0',
            'platform_name': 'Security Analysis Platform v3.0',
            
            # Configuration
            'show_code_snippets': True,
            'enable_interactive_features': True
        }
    
    def _calculate_severity_stats(self, vulnerabilities: list[Vulnerability]) -> Dict[str, int]:
        """Calculate severity distribution"""
        from collections import Counter
        return dict(Counter(v.severity.value for v in vulnerabilities))
    
    def _calculate_risk_score(self, vulnerabilities: list[Vulnerability]) -> float:
        """Calculate overall risk score (0-10)"""
        if not vulnerabilities:
            return 0.0
        
        severity_weights = {
            'CRÍTICA': 10.0, 'ALTA': 7.0, 'MEDIA': 4.0, 'BAJA': 2.0, 'INFO': 0.5
        }
        
        total_score = sum(severity_weights.get(v.severity.value, 0) for v in vulnerabilities)
        max_possible = len(vulnerabilities) * 10.0
        
        normalized = (total_score / max_possible) * 10.0 if max_possible > 0 else 0.0
        return round(min(normalized, 10.0), 1)
    
    def _generate_fallback_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
        """Generate minimal fallback report"""
        
        try:
            logger.warning("Generating minimal fallback report")
            
            scan_result = analysis_report.scan_result
            vuln_count = len(scan_result.vulnerabilities)
            
            fallback_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛡️ Security Analysis Report</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #4f46e5; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .summary {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #4f46e5; }}
        .vuln {{ background: #fef2f2; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ef4444; }}
        .no-vulns {{ background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #22c55e; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Security Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <p><strong>File:</strong> {scan_result.file_info.get('filename', 'Unknown')}</p>
        <p><strong>Total Vulnerabilities:</strong> {vuln_count}</p>
        <p><strong>Analysis Time:</strong> {analysis_report.total_processing_time_seconds:.2f}s</p>
    </div>
"""
            
            if vuln_count > 0:
                fallback_html += '<div class="summary"><h2>🚨 Vulnerabilities Found</h2>'
                
                # Mostrar primeras 10 vulnerabilidades
                for i, vuln in enumerate(scan_result.vulnerabilities[:10], 1):
                    fallback_html += f'''
    <div class="vuln">
        <h3>{i}. {vuln.title}</h3>
        <p><strong>Severity:</strong> {vuln.severity.value}</p>
        <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number}</p>
        <p><strong>Description:</strong> {vuln.description[:200]}...</p>
    </div>'''
                
                if vuln_count > 10:
                    fallback_html += f'<p><em>... and {vuln_count - 10} more vulnerabilities</em></p>'
                
                fallback_html += '</div>'
            else:
                fallback_html += '''
    <div class="no-vulns">
        <h2>✅ No Vulnerabilities Found</h2>
        <p>Great! No security vulnerabilities were detected.</p>
    </div>'''
            
            fallback_html += '''
    <div class="summary">
        <h2>ℹ️ Simplified Report</h2>
        <p>This is a simplified report due to template rendering issues.</p>
        <p>Generated by Security Analysis Platform v3.0 - Fallback Mode</p>
    </div>
</body>
</html>'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(fallback_html)
            
            logger.info(f"Fallback report generated: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Even fallback generation failed: {e}")
            return False
    
    def _register_filters(self):
        """Register optimized Jinja2 filters - CORREGIDO"""
        
        def format_bytes(value):
            """Format bytes in human readable format"""
            if not value:
                return "0 bytes"
            try:
                value = int(value)
                if value >= 1024 * 1024:
                    return f"{value / (1024 * 1024):.2f} MB"
                elif value >= 1024:
                    return f"{value / 1024:.2f} KB"
                return f"{value} bytes"
            except (ValueError, TypeError):
                return str(value)
        
        def format_duration(seconds):
            """Format duration in human readable format"""
            if not seconds:
                return "0s"
            try:
                seconds = float(seconds)
                if seconds >= 60:
                    minutes = int(seconds // 60)
                    remaining = seconds % 60
                    return f"{minutes}m {remaining:.1f}s"
                return f"{seconds:.2f}s"
            except (ValueError, TypeError):
                return str(seconds)
        
        def severity_icon(severity):
            """Get icon for severity level"""
            if not severity:
                return '📄'
            icons = {
                'CRÍTICA': '🔥', 'ALTA': '⚡', 'MEDIA': '⚠️', 
                'BAJA': '📝', 'INFO': 'ℹ️'
            }
            return icons.get(str(severity).upper(), '📄')
        
        def severity_class(severity):
            """Get CSS class for severity"""
            if not severity:
                return 'default'
            classes = {
                'CRÍTICA': 'critical', 'ALTA': 'high', 'MEDIA': 'medium',
                'BAJA': 'low', 'INFO': 'info'
            }
            return classes.get(str(severity).upper(), 'default')
        
        def truncate_smart(text, length=300):
            """Smart truncation preserving word boundaries"""
            if not text:
                return ""
            text = str(text)
            if len(text) <= length:
                return text
            return text[:length].rsplit(' ', 1)[0] + "..."
        
        # CORREGIR: Usar self.env.filters en lugar de @self.env.filter
        self.env.filters['format_bytes'] = format_bytes
        self.env.filters['format_duration'] = format_duration
        self.env.filters['severity_icon'] = severity_icon
        self.env.filters['severity_class'] = severity_class
        self.env.filters['truncate_smart'] = truncate_smart

                