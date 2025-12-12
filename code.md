# Análisis de Código - .

**Fecha de generación:** 2025-11-16 17:15:48

**Directorio analizado:** `.`

**Total de archivos procesados:** 24

---

### main.py

**Ruta:** `main.py`

```py
0001 | #!/usr/bin/env python3
0002 | """
0003 | 🛡️ Security Analysis Platform v3.0
0004 | Advanced Security Vulnerability Analysis with AI-Powered Triage
0005 | 
0006 | Entry point for the security analysis platform.
0007 | """
0008 | 
0009 | import sys
0010 | from pathlib import Path
0011 | 
0012 | # Add project root to Python path
0013 | project_root = Path(__file__).parent
0014 | sys.path.insert(0, str(project_root))
0015 | 
0016 | # Import and run CLI
0017 | from application.cli import cli
0018 | 
0019 | if __name__ == '__main__':
0020 |     cli()
```

---

### setup.py

**Ruta:** `setup.py`

```py
0001 | # setup.py
0002 | from setuptools import setup, find_packages
0003 | from pathlib import Path
0004 | 
0005 | # Read README
0006 | readme_path = Path(__file__).parent / "README.md"
0007 | long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
0008 | 
0009 | setup(
0010 |     name="security-analysis-platform",
0011 |     version="3.0.0",
0012 |     description="Advanced Security Vulnerability Analysis with AI-Powered Triage",
0013 |     long_description=long_description,
0014 |     long_description_content_type="text/markdown",
0015 |     author="Security Team",
0016 |     author_email="security@yourcompany.com",
0017 |     url="https://github.com/your-org/security-analyzer",
0018 |     packages=find_packages(),
0019 |     include_package_data=True,
0020 |     install_requires=[
0021 |         "pydantic>=2.0.0",
0022 |         "click>=8.0.0", 
0023 |         "jinja2>=3.0.0",
0024 |         "openai>=1.0.0",
0025 |         "asyncio-compat>=0.1.2",
0026 |     ],
0027 |     extras_require={
0028 |         "dev": [
0029 |             "pytest>=7.0.0",
0030 |             "pytest-asyncio>=0.21.0",
0031 |             "black>=23.0.0",
0032 |             "mypy>=1.0.0",
0033 |             "pre-commit>=3.0.0",
0034 |         ],
0035 |         "watsonx": [
0036 |             "ibm-watson-machine-learning>=1.0.0",
0037 |         ]
0038 |     },
0039 |     entry_points={
0040 |         "console_scripts": [
0041 |             "security-analyzer=application.cli:cli",
0042 |         ],
0043 |     },
0044 |     classifiers=[
0045 |         "Development Status :: 5 - Production/Stable",
0046 |         "Intended Audience :: Developers",
0047 |         "Topic :: Security",
0048 |         "License :: OSI Approved :: MIT License",
0049 |         "Programming Language :: Python :: 3",
0050 |         "Programming Language :: Python :: 3.8",
0051 |         "Programming Language :: Python :: 3.9",
0052 |         "Programming Language :: Python :: 3.10",
0053 |         "Programming Language :: Python :: 3.11",
0054 |     ],
0055 |     python_requires=">=3.8",
0056 |     package_data={
0057 |         "adapters.output": ["templates/*.html"],
0058 |     },
0059 | )
```

---

### adapters\output\html_generator.py

**Ruta:** `adapters\output\html_generator.py`

```py
0001 | # adapters/output/html_generator.py
0002 | import logging
0003 | from pathlib import Path
0004 | from datetime import datetime
0005 | from typing import Dict, Any, Optional
0006 | from jinja2 import Environment, FileSystemLoader, select_autoescape
0007 | 
0008 | from core.models import AnalysisReport, Vulnerability
0009 | from shared.metrics import MetricsCollector
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class OptimizedHTMLGenerator:
0014 |     """Generador HTML optimizado y simplificado"""
0015 |     
0016 |     def __init__(self, template_dir: Optional[Path] = None, metrics: Optional[MetricsCollector] = None):
0017 |         self.template_dir = template_dir or Path(__file__).parent / "templates"
0018 |         self.metrics = metrics
0019 |         
0020 |         # Configure Jinja2 environment
0021 |         self.env = Environment(
0022 |             loader=FileSystemLoader(str(self.template_dir)),
0023 |             autoescape=select_autoescape(['html', 'xml']),
0024 |             trim_blocks=True,
0025 |             lstrip_blocks=True
0026 |         )
0027 |         
0028 |         # Register optimized filters
0029 |         self._register_filters()
0030 |         
0031 |         logger.info(f"HTML Generator initialized")
0032 |     
0033 |     def generate_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
0034 |         """Generate optimized HTML report"""
0035 |         
0036 |         try:
0037 |             logger.info(f"Generating HTML report: {output_file}")
0038 |             
0039 |             # Prepare template context
0040 |             context = self._prepare_context(analysis_report)
0041 |             
0042 |             # Render main template
0043 |             template = self.env.get_template('report.html')
0044 |             html_content = template.render(**context)
0045 |             
0046 |             # Write file
0047 |             output_path = Path(output_file)
0048 |             output_path.parent.mkdir(parents=True, exist_ok=True)
0049 |             
0050 |             with open(output_path, 'w', encoding='utf-8') as f:
0051 |                 f.write(html_content)
0052 |             
0053 |             # Record metrics
0054 |             file_size = output_path.stat().st_size
0055 |             if self.metrics:
0056 |                 self.metrics.record_report_generation(
0057 |                     "html", file_size, len(analysis_report.scan_result.vulnerabilities), True
0058 |                 )
0059 |             
0060 |             logger.info(f"HTML report generated: {output_file} ({file_size:,} bytes)")
0061 |             return True
0062 |             
0063 |         except Exception as e:
0064 |             logger.error(f"HTML generation failed: {e}")
0065 |             if self.metrics:
0066 |                 self.metrics.record_report_generation("html", success=False, error=str(e))
0067 |             
0068 |             # Try fallback generation
0069 |             return self._generate_fallback_report(analysis_report, output_file)
0070 |     
0071 |     def _prepare_context(self, analysis_report: AnalysisReport) -> Dict[str, Any]:
0072 |         """Prepare optimized template context"""
0073 |         
0074 |         scan_result = analysis_report.scan_result
0075 |         vulnerabilities = scan_result.vulnerabilities
0076 |         
0077 |         # Calculate derived metrics
0078 |         severity_stats = self._calculate_severity_stats(vulnerabilities)
0079 |         risk_score = self._calculate_risk_score(vulnerabilities)
0080 |         
0081 |         return {
0082 |             # Main data
0083 |             'report': analysis_report,
0084 |             'scan_result': scan_result,
0085 |             'triage_result': analysis_report.triage_result,
0086 |             'remediation_plans': analysis_report.remediation_plans,
0087 |             
0088 |             # Calculated metrics
0089 |             'total_vulnerabilities': len(vulnerabilities),
0090 |             'high_priority_count': len([v for v in vulnerabilities if v.is_high_priority]),
0091 |             'severity_stats': severity_stats,
0092 |             'risk_score': risk_score,
0093 |             
0094 |             # Report metadata
0095 |             'generation_timestamp': datetime.now(),
0096 |             'report_version': '3.0',
0097 |             'platform_name': 'Security Analysis Platform v3.0',
0098 |             
0099 |             # Configuration
0100 |             'show_code_snippets': True,
0101 |             'enable_interactive_features': True
0102 |         }
0103 |     
0104 |     def _calculate_severity_stats(self, vulnerabilities: list[Vulnerability]) -> Dict[str, int]:
0105 |         """Calculate severity distribution"""
0106 |         from collections import Counter
0107 |         return dict(Counter(v.severity.value for v in vulnerabilities))
0108 |     
0109 |     def _calculate_risk_score(self, vulnerabilities: list[Vulnerability]) -> float:
0110 |         """Calculate overall risk score (0-10)"""
0111 |         if not vulnerabilities:
0112 |             return 0.0
0113 |         
0114 |         severity_weights = {
0115 |             'CRÍTICA': 10.0, 'ALTA': 7.0, 'MEDIA': 4.0, 'BAJA': 2.0, 'INFO': 0.5
0116 |         }
0117 |         
0118 |         total_score = sum(severity_weights.get(v.severity.value, 0) for v in vulnerabilities)
0119 |         max_possible = len(vulnerabilities) * 10.0
0120 |         
0121 |         normalized = (total_score / max_possible) * 10.0 if max_possible > 0 else 0.0
0122 |         return round(min(normalized, 10.0), 1)
0123 |     
0124 |     def _generate_fallback_report(self, analysis_report: AnalysisReport, output_file: str) -> bool:
0125 |         """Generate minimal fallback report"""
0126 |         
0127 |         try:
0128 |             logger.warning("Generating minimal fallback report")
0129 |             
0130 |             scan_result = analysis_report.scan_result
0131 |             vuln_count = len(scan_result.vulnerabilities)
0132 |             
0133 |             fallback_html = f"""<!DOCTYPE html>
0134 | <html lang="es">
0135 | <head>
0136 |     <meta charset="UTF-8">
0137 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0138 |     <title>🛡️ Security Analysis Report</title>
0139 |     <style>
0140 |         body {{ font-family: system-ui, sans-serif; margin: 20px; line-height: 1.6; }}
0141 |         .header {{ background: #4f46e5; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
0142 |         .summary {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #4f46e5; }}
0143 |         .vuln {{ background: #fef2f2; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ef4444; }}
0144 |         .no-vulns {{ background: #f0fdf4; padding: 20px; border-radius: 8px; border-left: 4px solid #22c55e; text-align: center; }}
0145 |     </style>
0146 | </head>
0147 | <body>
0148 |     <div class="header">
0149 |         <h1>🛡️ Security Analysis Report</h1>
0150 |         <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
0151 |     </div>
0152 |     
0153 |     <div class="summary">
0154 |         <h2>📊 Summary</h2>
0155 |         <p><strong>File:</strong> {scan_result.file_info.get('filename', 'Unknown')}</p>
0156 |         <p><strong>Total Vulnerabilities:</strong> {vuln_count}</p>
0157 |         <p><strong>Analysis Time:</strong> {analysis_report.total_processing_time_seconds:.2f}s</p>
0158 |     </div>
0159 | """
0160 |             
0161 |             if vuln_count > 0:
0162 |                 fallback_html += '<div class="summary"><h2>🚨 Vulnerabilities Found</h2>'
0163 |                 
0164 |                 # Mostrar primeras 10 vulnerabilidades
0165 |                 for i, vuln in enumerate(scan_result.vulnerabilities[:10], 1):
0166 |                     fallback_html += f'''
0167 |     <div class="vuln">
0168 |         <h3>{i}. {vuln.title}</h3>
0169 |         <p><strong>Severity:</strong> {vuln.severity.value}</p>
0170 |         <p><strong>File:</strong> {vuln.file_path}:{vuln.line_number}</p>
0171 |         <p><strong>Description:</strong> {vuln.description[:200]}...</p>
0172 |     </div>'''
0173 |                 
0174 |                 if vuln_count > 10:
0175 |                     fallback_html += f'<p><em>... and {vuln_count - 10} more vulnerabilities</em></p>'
0176 |                 
0177 |                 fallback_html += '</div>'
0178 |             else:
0179 |                 fallback_html += '''
0180 |     <div class="no-vulns">
0181 |         <h2>✅ No Vulnerabilities Found</h2>
0182 |         <p>Great! No security vulnerabilities were detected.</p>
0183 |     </div>'''
0184 |             
0185 |             fallback_html += '''
0186 |     <div class="summary">
0187 |         <h2>ℹ️ Simplified Report</h2>
0188 |         <p>This is a simplified report due to template rendering issues.</p>
0189 |         <p>Generated by Security Analysis Platform v3.0 - Fallback Mode</p>
0190 |     </div>
0191 | </body>
0192 | </html>'''
0193 |             
0194 |             with open(output_file, 'w', encoding='utf-8') as f:
0195 |                 f.write(fallback_html)
0196 |             
0197 |             logger.info(f"Fallback report generated: {output_file}")
0198 |             return True
0199 |             
0200 |         except Exception as e:
0201 |             logger.error(f"Even fallback generation failed: {e}")
0202 |             return False
0203 |     
0204 |     def _register_filters(self):
0205 |         """Register optimized Jinja2 filters - CORREGIDO"""
0206 |         
0207 |         def format_bytes(value):
0208 |             """Format bytes in human readable format"""
0209 |             if not value:
0210 |                 return "0 bytes"
0211 |             try:
0212 |                 value = int(value)
0213 |                 if value >= 1024 * 1024:
0214 |                     return f"{value / (1024 * 1024):.2f} MB"
0215 |                 elif value >= 1024:
0216 |                     return f"{value / 1024:.2f} KB"
0217 |                 return f"{value} bytes"
0218 |             except (ValueError, TypeError):
0219 |                 return str(value)
0220 |         
0221 |         def format_duration(seconds):
0222 |             """Format duration in human readable format"""
0223 |             if not seconds:
0224 |                 return "0s"
0225 |             try:
0226 |                 seconds = float(seconds)
0227 |                 if seconds >= 60:
0228 |                     minutes = int(seconds // 60)
0229 |                     remaining = seconds % 60
0230 |                     return f"{minutes}m {remaining:.1f}s"
0231 |                 return f"{seconds:.2f}s"
0232 |             except (ValueError, TypeError):
0233 |                 return str(seconds)
0234 |         
0235 |         def severity_icon(severity):
0236 |             """Get icon for severity level"""
0237 |             if not severity:
0238 |                 return '📄'
0239 |             icons = {
0240 |                 'CRÍTICA': '🔥', 'ALTA': '⚡', 'MEDIA': '⚠️', 
0241 |                 'BAJA': '📝', 'INFO': 'ℹ️'
0242 |             }
0243 |             return icons.get(str(severity).upper(), '📄')
0244 |         
0245 |         def severity_class(severity):
0246 |             """Get CSS class for severity"""
0247 |             if not severity:
0248 |                 return 'default'
0249 |             classes = {
0250 |                 'CRÍTICA': 'critical', 'ALTA': 'high', 'MEDIA': 'medium',
0251 |                 'BAJA': 'low', 'INFO': 'info'
0252 |             }
0253 |             return classes.get(str(severity).upper(), 'default')
0254 |         
0255 |         def truncate_smart(text, length=300):
0256 |             """Smart truncation preserving word boundaries"""
0257 |             if not text:
0258 |                 return ""
0259 |             text = str(text)
0260 |             if len(text) <= length:
0261 |                 return text
0262 |             return text[:length].rsplit(' ', 1)[0] + "..."
0263 |         
0264 |         # CORREGIR: Usar self.env.filters en lugar de @self.env.filter
0265 |         self.env.filters['format_bytes'] = format_bytes
0266 |         self.env.filters['format_duration'] = format_duration
0267 |         self.env.filters['severity_icon'] = severity_icon
0268 |         self.env.filters['severity_class'] = severity_class
0269 |         self.env.filters['truncate_smart'] = truncate_smart
0270 | 
0271 |                 ```

---

### adapters\output\templates\report.html

**Ruta:** `adapters\output\templates\report.html`

```html
0001 |  <!-- adapters/output/templates/report.html -->
0002 | <!DOCTYPE html>
0003 | <html lang="es">
0004 | <head>
0005 |     <meta charset="UTF-8">
0006 |     <meta name="viewport" content="width=device-width, initial-scale=1.0">
0007 |     <title>🛡️ {{ platform_name }} - Report</title>
0008 |     {% include 'styles.html' %}
0009 | </head>
0010 | <body>
0011 |     <div class="container">
0012 |         <!-- Header -->
0013 |         <header class="header">
0014 |             <div class="header-content">
0015 |                 <h1>🛡️ Security Analysis Report</h1>
0016 |                 <div class="header-grid">
0017 |                     <div class="header-item">
0018 |                         <div class="header-label">📁 File</div>
0019 |                         <div class="header-value">{{ scan_result.file_info.filename }}</div>
0020 |                     </div>
0021 |                     <div class="header-item">
0022 |                         <div class="header-label">📊 Total Vulnerabilities</div>
0023 |                         <div class="header-value">{{ total_vulnerabilities }}</div>
0024 |                     </div>
0025 |                     <div class="header-item">
0026 |                         <div class="header-label">⚡ High Priority</div>
0027 |                         <div class="header-value">{{ high_priority_count }}</div>
0028 |                     </div>
0029 |                     <div class="header-item">
0030 |                         <div class="header-label">🎯 Risk Score</div>
0031 |                         <div class="header-value">{{ risk_score }}/10</div>
0032 |                     </div>
0033 |                 </div>
0034 |             </div>
0035 |         </header>
0036 | 
0037 |         <main class="content">
0038 |             <!-- Executive Summary -->
0039 |             <section class="section">
0040 |                 <h2 class="section-title">📈 Executive Summary</h2>
0041 |                 
0042 |                 <div class="metrics-grid">
0043 |                     {% for severity, count in severity_stats.items() %}
0044 |                     {% if count > 0 %}
0045 |                     <div class="metric-card {{ severity | severity_class }}">
0046 |                         <div class="metric-icon">{{ severity | severity_icon }}</div>
0047 |                         <div class="metric-value">{{ count }}</div>
0048 |                         <div class="metric-label">{{ severity }}</div>
0049 |                     </div>
0050 |                     {% endif %}
0051 |                     {% endfor %}
0052 |                 </div>
0053 | 
0054 |                 <div class="summary-info">
0055 |                     <p><strong>Analysis completed in {{ report.total_processing_time_seconds | format_duration }}</strong></p>
0056 |                     {% if report.chunking_enabled %}
0057 |                     <p>🧩 Advanced chunking was used for optimal analysis</p>
0058 |                     {% endif %}
0059 |                     {% if triage_result %}
0060 |                     <p>🤖 AI-powered triage analyzed {{ triage_result.total_analyzed }} vulnerabilities</p>
0061 |                     {% endif %}
0062 |                 </div>
0063 |             </section>
0064 | 
0065 |             <!-- Vulnerabilities -->
0066 |             {% if scan_result.vulnerabilities %}
0067 |             <section class="section">
0068 |                 <h2 class="section-title">🚨 Security Vulnerabilities</h2>
0069 |                 
0070 |                 <div class="vulnerabilities-list">
0071 |                     {% for vuln in scan_result.vulnerabilities %}
0072 |                     <div class="vulnerability-card {{ vuln.severity.value | severity_class }}">
0073 |                         <div class="vuln-header">
0074 |                             <h3 class="vuln-title">
0075 |                                 {{ vuln.severity | severity_icon }} {{ loop.index }}. {{ vuln.title }}
0076 |                             </h3>
0077 |                             <div class="vuln-badges">
0078 |                                 <span class="badge severity-{{ vuln.severity.value | severity_class }}">
0079 |                                     {{ vuln.severity.value }}
0080 |                                 </span>
0081 |                                 <span class="badge type-badge">{{ vuln.type.value }}</span>
0082 |                             </div>
0083 |                         </div>
0084 |                         
0085 |                         <div class="vuln-body">
0086 |                             <div class="vuln-meta">
0087 |                                 <div class="meta-item">
0088 |                                     <span class="meta-label">📍 Location</span>
0089 |                                     <span class="meta-value">{{ vuln.file_path }}:{{ vuln.line_number }}</span>
0090 |                                 </div>
0091 |                                 <div class="meta-item">
0092 |                                     <span class="meta-label">🆔 ID</span>
0093 |                                     <span class="meta-value">{{ vuln.id }}</span>
0094 |                                 </div>
0095 |                                 {% if vuln.cwe_id %}
0096 |                                 <div class="meta-item">
0097 |                                     <span class="meta-label">🔗 CWE</span>
0098 |                                     <span class="meta-value">
0099 |                                         <a href="https://cwe.mitre.org/data/definitions/{{ vuln.cwe_id.replace('CWE-', '') }}.html" target="_blank">
0100 |                                             {{ vuln.cwe_id }}
0101 |                                         </a>
0102 |                                     </span>
0103 |                                 </div>
0104 |                                 {% endif %}
0105 |                             </div>
0106 |                             
0107 |                             <div class="vuln-description">
0108 |                                 <h4>📝 Description</h4>
0109 |                                 <p>{{ vuln.description }}</p>
0110 |                             </div>
0111 |                             
0112 |                             {% if vuln.code_snippet %}
0113 |                             <div class="vuln-code">
0114 |                                 <h4>💻 Code Context</h4>
0115 |                                 <pre class="code-block">{{ vuln.code_snippet | truncate_smart(500) }}</pre>
0116 |                             </div>
0117 |                             {% endif %}
0118 |                             
0119 |                             {% if vuln.remediation_advice %}
0120 |                             <div class="vuln-remediation">
0121 |                                 <h4>💡 Remediation Advice</h4>
0122 |                                 <div class="advice-content">{{ vuln.remediation_advice }}</div>
0123 |                             </div>
0124 |                             {% endif %}
0125 |                         </div>
0126 |                     </div>
0127 |                     {% endfor %}
0128 |                 </div>
0129 |             </section>
0130 |             {% else %}
0131 |             <section class="section">
0132 |                 <div class="no-vulnerabilities">
0133 |                     <div class="no-vulns-icon">✅</div>
0134 |                     <h2>No Vulnerabilities Found</h2>
0135 |                     <p>Excellent! No security vulnerabilities were detected in the analyzed code.</p>
0136 |                 </div>
0137 |             </section>
0138 |             {% endif %}
0139 | 
0140 |             <!-- Remediation Plans -->
0141 |             {% if remediation_plans %}
0142 |             <section class="section">
0143 |                 <h2 class="section-title">🛠️ Remediation Plans</h2>
0144 |                 
0145 |                 <div class="remediation-summary">
0146 |                     <p>{{ remediation_plans | length }} actionable remediation plans generated, prioritized by risk and complexity.</p>
0147 |                 </div>
0148 |                 
0149 |                 <div class="remediation-plans">
0150 |                     {% for plan in remediation_plans %}
0151 |                     <div class="remediation-card">
0152 |                         <div class="plan-header">
0153 |                             <h3>🔧 {{ plan.vulnerability_type.value }}</h3>
0154 |                             <span class="priority-badge priority-{{ plan.priority_level }}">
0155 |                                 {{ plan.priority_level.upper() }}
0156 |                             </span>
0157 |                         </div>
0158 |                         
0159 |                         <div class="plan-meta">
0160 |                             <span class="plan-stat">⏱️ {{ plan.total_estimated_hours }}h</span>
0161 |                             <span class="plan-stat">📊 Complexity: {{ plan.complexity_score }}/10</span>
0162 |                             <span class="plan-stat">📋 {{ plan.steps | length }} steps</span>
0163 |                         </div>
0164 |                         
0165 |                         <div class="plan-steps">
0166 |                             <h4>Implementation Steps:</h4>
0167 |                             <ol>
0168 |                                 {% for step in plan.steps %}
0169 |                                 <li class="remediation-step">
0170 |                                     <div class="step-header">
0171 |                                         <strong>{{ step.title }}</strong>
0172 |                                         <span class="step-meta">{{ step.estimated_minutes }}min • {{ step.difficulty }}</span>
0173 |                                     </div>
0174 |                                     <div class="step-description">{{ step.description }}</div>
0175 |                                     {% if step.code_example %}
0176 |                                     <pre class="step-code">{{ step.code_example | truncate_smart(200) }}</pre>
0177 |                                     {% endif %}
0178 |                                 </li>
0179 |                                 {% endfor %}
0180 |                             </ol>
0181 |                         </div>
0182 |                         
0183 |                         {% if plan.risk_if_not_fixed %}
0184 |                         <div class="risk-warning">
0185 |                             <h5>⚠️ Risk if not addressed:</h5>
0186 |                             <p>{{ plan.risk_if_not_fixed }}</p>
0187 |                         </div>
0188 |                         {% endif %}
0189 |                     </div>
0190 |                     {% endfor %}
0191 |                 </div>
0192 |             </section>
0193 |             {% endif %}
0194 | 
0195 |             <!-- Technical Details -->
0196 |             <section class="section">
0197 |                 <details class="technical-details">
0198 |                     <summary class="details-toggle">🔍 Technical Analysis Details</summary>
0199 |                     <div class="details-content">
0200 |                         <div class="tech-grid">
0201 |                             <div class="tech-item">
0202 |                                 <h4>📊 Analysis Statistics</h4>
0203 |                                 <ul>
0204 |                                     <li>Processing time: {{ report.total_processing_time_seconds | format_duration }}</li>
0205 |                                     <li>File size: {{ scan_result.file_info.size_bytes | format_bytes }}</li>
0206 |                                     <li>Language: {{ scan_result.language_detected or 'Auto-detected' }}</li>
0207 |                                     <li>Chunking: {{ 'Enabled' if report.chunking_enabled else 'Disabled' }}</li>
0208 |                                 </ul>
0209 |                             </div>
0210 |                             
0211 |                             {% if triage_result %}
0212 |                             <div class="tech-item">
0213 |                                 <h4>🤖 LLM Triage Results</h4>
0214 |                                 <ul>
0215 |                                     <li>Confirmed vulnerabilities: {{ triage_result.confirmed_count }}</li>
0216 |                                     <li>False positives: {{ triage_result.false_positive_count }}</li>
0217 |                                     <li>Need manual review: {{ triage_result.needs_review_count }}</li>
0218 |                                     <li>Analysis time: {{ triage_result.llm_analysis_time_seconds | format_duration }}</li>
0219 |                                 </ul>
0220 |                             </div>
0221 |                             {% endif %}
0222 |                         </div>
0223 |                         
0224 |                         {% if triage_result and triage_result.analysis_summary %}
0225 |                         <div class="analysis-summary">
0226 |                             <h4>📋 Analysis Summary</h4>
0227 |                             <pre>{{ triage_result.analysis_summary }}</pre>
0228 |                         </div>
0229 |                         {% endif %}
0230 |                     </div>
0231 |                 </details>
0232 |             </section>
0233 |         </main>
0234 | 
0235 |         <!-- Footer -->
0236 |         <footer class="footer">
0237 |             <div class="footer-content">
0238 |                 <p>Generated by <strong>{{ platform_name }}</strong> on {{ generation_timestamp.strftime('%Y-%m-%d at %H:%M:%S') }}</p>
0239 |                 <p>For questions about this report, contact your security team.</p>
0240 |             </div>
0241 |         </footer>
0242 |     </div>
0243 | 
0244 |     {% include 'scripts.html' %}
0245 | </body>
0246 | </html>
```

---

### adapters\output\templates\scripts.html

**Ruta:** `adapters\output\templates\scripts.html`

```html
0001 | <!-- adapters/output/templates/scripts.html -->
0002 | <script>
0003 | document.addEventListener('DOMContentLoaded', function() {
0004 |     console.log('🛡️ Security Analysis Report v3.0 loaded');
0005 |     
0006 |     // Enhanced interactivity
0007 |     initializeAnimations();
0008 |     setupCopyFunctionality();
0009 |     setupSearchFunctionality();
0010 |     setupKeyboardNavigation();
0011 |     
0012 |     // Report statistics
0013 |     logReportStatistics();
0014 | });
0015 | 
0016 | function initializeAnimations() {
0017 |     // Intersection Observer for scroll animations
0018 |     const observerOptions = {
0019 |         threshold: 0.1,
0020 |         rootMargin: '0px 0px -50px 0px'
0021 |     };
0022 | 
0023 |     const observer = new IntersectionObserver(function(entries) {
0024 |         entries.forEach(function(entry) {
0025 |             if (entry.isIntersecting) {
0026 |                 entry.target.style.opacity = '1';
0027 |                 entry.target.style.transform = 'translateY(0)';
0028 |             }
0029 |         });
0030 |     }, observerOptions);
0031 | 
0032 |     // Apply to vulnerability cards
0033 |     document.querySelectorAll('.vulnerability-card, .remediation-card').forEach(function(el) {
0034 |         el.style.opacity = '0';
0035 |         el.style.transform = 'translateY(20px)';
0036 |         el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
0037 |         observer.observe(el);
0038 |     });
0039 | }
0040 | 
0041 | function setupCopyFunctionality() {
0042 |     // Add copy buttons to vulnerability IDs and CWE links
0043 |     document.querySelectorAll('.meta-value').forEach(function(element) {
0044 |         const text = element.textContent.trim();
0045 |         
0046 |         if (text.match(/^(VULN-|ABAP-|CWE-)/)) {
0047 |             element.style.cursor = 'pointer';
0048 |             element.title = 'Click to copy ' + text;
0049 |             
0050 |             element.addEventListener('click', function() {
0051 |                 copyToClipboard(text);
0052 |                 showToast('✅ Copied: ' + text);
0053 |             });
0054 |         }
0055 |     });
0056 | }
0057 | 
0058 | function setupSearchFunctionality() {
0059 |     // Create search box
0060 |     const searchBox = document.createElement('div');
0061 |     searchBox.innerHTML = `
0062 |         <div style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
0063 |             <input type="text" id="vulnerabilitySearch" placeholder="🔍 Search vulnerabilities..." 
0064 |                    style="border: 1px solid #ddd; padding: 8px; border-radius: 4px; width: 250px;">
0065 |         </div>
0066 |     `;
0067 |     document.body.appendChild(searchBox);
0068 |     
0069 |     const searchInput = document.getElementById('vulnerabilitySearch');
0070 |     searchInput.addEventListener('input', function(e) {
0071 |         const query = e.target.value.toLowerCase();
0072 |         filterVulnerabilities(query);
0073 |     });
0074 | }
0075 | 
0076 | function setupKeyboardNavigation() {
0077 |     document.addEventListener('keydown', function(e) {
0078 |         // Ctrl+F or Cmd+F to focus search
0079 |         if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
0080 |             e.preventDefault();
0081 |             const searchInput = document.getElementById('vulnerabilitySearch');
0082 |             if (searchInput) {
0083 |                 searchInput.focus();
0084 |             }
0085 |         }
0086 |         
0087 |         // Escape to clear search
0088 |         if (e.key === 'Escape') {
0089 |             const searchInput = document.getElementById('vulnerabilitySearch');
0090 |             if (searchInput && searchInput === document.activeElement) {
0091 |                 searchInput.value = '';
0092 |                 filterVulnerabilities('');
0093 |                 searchInput.blur();
0094 |             }
0095 |         }
0096 |     });
0097 | }
0098 | 
0099 | function filterVulnerabilities(query) {
0100 |     const cards = document.querySelectorAll('.vulnerability-card');
0101 |     let visibleCount = 0;
0102 |     
0103 |     cards.forEach(function(card) {
0104 |         const text = card.textContent.toLowerCase();
0105 |         const isVisible = query === '' || text.includes(query);
0106 |         
0107 |         card.style.display = isVisible ? 'block' : 'none';
0108 |         if (isVisible) visibleCount++;
0109 |     });
0110 |     
0111 |     // Update search results indicator
0112 |     updateSearchResults(visibleCount, cards.length, query);
0113 | }
0114 | 
0115 | function updateSearchResults(visible, total, query) {
0116 |     let indicator = document.getElementById('searchResults');
0117 |     
0118 |     if (!indicator) {
0119 |         indicator = document.createElement('div');
0120 |         indicator.id = 'searchResults';
0121 |         indicator.style.cssText = `
0122 |             position: fixed;
0123 |             bottom: 20px;
0124 |             right: 20px;
0125 |             background: #4f46e5;
0126 |             color: white;
0127 |             padding: 8px 12px;
0128 |             border-radius: 6px;
0129 |             font-size: 0.875rem;
0130 |             z-index: 1000;
0131 |             transition: opacity 0.3s;
0132 |         `;
0133 |         document.body.appendChild(indicator);
0134 |     }
0135 |     
0136 |     if (query) {
0137 |         indicator.textContent = `Found ${visible} of ${total} vulnerabilities`;
0138 |         indicator.style.opacity = '1';
0139 |     } else {
0140 |         indicator.style.opacity = '0';
0141 |     }
0142 | }
0143 | 
0144 | function copyToClipboard(text) {
0145 |     if (navigator.clipboard) {
0146 |         navigator.clipboard.writeText(text).catch(function() {
0147 |             fallbackCopy(text);
0148 |         });
0149 |     } else {
0150 |         fallbackCopy(text);
0151 |     }
0152 | }
0153 | 
0154 | function fallbackCopy(text) {
0155 |     const textArea = document.createElement('textarea');
0156 |     textArea.value = text;
0157 |     textArea.style.position = 'fixed';
0158 |     textArea.style.left = '-9999px';
0159 |     document.body.appendChild(textArea);
0160 |     textArea.focus();
0161 |     textArea.select();
0162 |     
0163 |     try {
0164 |         document.execCommand('copy');
0165 |     } catch (err) {
0166 |         console.warn('Copy failed:', err);
0167 |     }
0168 |     
0169 |     document.body.removeChild(textArea);
0170 | }
0171 | 
0172 | function showToast(message) {
0173 |     const toast = document.createElement('div');
0174 |     toast.textContent = message;
0175 |     toast.style.cssText = `
0176 |         position: fixed;
0177 |         top: 20px;
0178 |         left: 50%;
0179 |         transform: translateX(-50%);
0180 |         background: #10b981;
0181 |         color: white;
0182 |         padding: 12px 20px;
0183 |         border-radius: 8px;
0184 |         z-index: 9999;
0185 |         animation: slideInDown 0.3s ease-out;
0186 |         font-weight: 500;
0187 |     `;
0188 |     
0189 |     document.body.appendChild(toast);
0190 |     
0191 |     setTimeout(function() {
0192 |         toast.style.animation = 'slideOutUp 0.3s ease-out';
0193 |         setTimeout(function() {
0194 |             document.body.removeChild(toast);
0195 |         }, 300);
0196 |     }, 2000);
0197 | }
0198 | 
0199 | function logReportStatistics() {
0200 |     const stats = {
0201 |         totalVulnerabilities: {{ total_vulnerabilities }},
0202 |         highPriority: {{ high_priority_count }},
0203 |         riskScore: {{ risk_score }},
0204 |         processingTime: '{{ report.total_processing_time_seconds | format_duration }}',
0205 |         chunking: {{ 'true' if report.chunking_enabled else 'false' }},
0206 |         llmAnalysis: {{ 'true' if triage_result else 'false' }},
0207 |         reportVersion: '{{ report_version }}'
0208 |     };
0209 |     
0210 |     console.log('📊 Report Statistics:', stats);
0211 |     
0212 |     // Performance metrics
0213 |     console.log('⚡ Performance Metrics:');
0214 |     console.log('  • DOM Ready:', performance.now().toFixed(2) + 'ms');
0215 |     console.log('  • Interactive elements:', document.querySelectorAll('[onclick], [data-action]').length);
0216 |     console.log('  • Vulnerability cards:', document.querySelectorAll('.vulnerability-card').length);
0217 | }
0218 | 
0219 | // CSS animations for toasts
0220 | const additionalStyles = `
0221 | @keyframes slideInDown {
0222 |     from {
0223 |         opacity: 0;
0224 |         transform: translate(-50%, -100%);
0225 |     }
0226 |     to {
0227 |         opacity: 1;
0228 |         transform: translate(-50%, 0);
0229 |     }
0230 | }
0231 | 
0232 | @keyframes slideOutUp {
0233 |     from {
0234 |         opacity: 1;
0235 |         transform: translate(-50%, 0);
0236 |     }
0237 |     to {
0238 |         opacity: 0;
0239 |         transform: translate(-50%, -100%);
0240 |     }
0241 | }
0242 | `;
0243 | 
0244 | const styleSheet = document.createElement('style');
0245 | styleSheet.textContent = additionalStyles;
0246 | document.head.appendChild(styleSheet);
0247 | </script>
```

---

### adapters\output\templates\styles.html

**Ruta:** `adapters\output\templates\styles.html`

```html
0001 | <!-- adapters/output/templates/styles.html -->
0002 | <style>
0003 | /* === RESET & BASE === */
0004 | * {
0005 |     margin: 0;
0006 |     padding: 0;
0007 |     box-sizing: border-box;
0008 | }
0009 | 
0010 | body {
0011 |     font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
0012 |     line-height: 1.6;
0013 |     color: #1f2937;
0014 |     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
0015 |     min-height: 100vh;
0016 | }
0017 | 
0018 | /* === LAYOUT === */
0019 | .container {
0020 |     max-width: 1200px;
0021 |     margin: 20px auto;
0022 |     background: white;
0023 |     border-radius: 16px;
0024 |     box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
0025 |     overflow: hidden;
0026 | }
0027 | 
0028 | /* === HEADER === */
0029 | .header {
0030 |     background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
0031 |     color: white;
0032 |     padding: 2rem;
0033 |     position: relative;
0034 | }
0035 | 
0036 | .header::before {
0037 |     content: '';
0038 |     position: absolute;
0039 |     top: 0;
0040 |     left: 0;
0041 |     right: 0;
0042 |     bottom: 0;
0043 |     background: url('image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
0044 |     opacity: 0.3;
0045 | }
0046 | 
0047 | .header-content {
0048 |     position: relative;
0049 |     z-index: 1;
0050 |     text-align: center;
0051 | }
0052 | 
0053 | .header h1 {
0054 |     font-size: 2.5rem;
0055 |     font-weight: 700;
0056 |     margin-bottom: 1rem;
0057 |     text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
0058 | }
0059 | 
0060 | .header-grid {
0061 |     display: grid;
0062 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0063 |     gap: 1rem;
0064 |     margin-top: 1.5rem;
0065 | }
0066 | 
0067 | .header-item {
0068 |     background: rgba(255, 255, 255, 0.15);
0069 |     padding: 1rem;
0070 |     border-radius: 12px;
0071 |     backdrop-filter: blur(10px);
0072 |     border: 1px solid rgba(255, 255, 255, 0.2);
0073 | }
0074 | 
0075 | .header-label {
0076 |     font-size: 0.875rem;
0077 |     opacity: 0.9;
0078 |     margin-bottom: 0.25rem;
0079 | }
0080 | 
0081 | .header-value {
0082 |     font-size: 1.25rem;
0083 |     font-weight: 600;
0084 | }
0085 | 
0086 | /* === CONTENT === */
0087 | .content {
0088 |     padding: 2rem;
0089 | }
0090 | 
0091 | .section {
0092 |     margin-bottom: 3rem;
0093 | }
0094 | 
0095 | .section-title {
0096 |     font-size: 1.875rem;
0097 |     font-weight: 700;
0098 |     color: #1f2937;
0099 |     margin-bottom: 1.5rem;
0100 |     padding-bottom: 0.75rem;
0101 |     border-bottom: 3px solid #4f46e5;
0102 |     position: relative;
0103 | }
0104 | 
0105 | .section-title::after {
0106 |     content: '';
0107 |     position: absolute;
0108 |     bottom: -3px;
0109 |     left: 0;
0110 |     width: 60px;
0111 |     height: 3px;
0112 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0113 | }
0114 | 
0115 | /* === METRICS === */
0116 | .metrics-grid {
0117 |     display: grid;
0118 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0119 |     gap: 1.5rem;
0120 |     margin-bottom: 2rem;
0121 | }
0122 | 
0123 | .metric-card {
0124 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0125 |     border-radius: 16px;
0126 |     padding: 1.5rem;
0127 |     text-align: center;
0128 |     transition: transform 0.3s ease, box-shadow 0.3s ease;
0129 |     position: relative;
0130 |     overflow: hidden;
0131 | }
0132 | 
0133 | .metric-card::before {
0134 |     content: '';
0135 |     position: absolute;
0136 |     top: 0;
0137 |     left: 0;
0138 |     right: 0;
0139 |     height: 4px;
0140 |     background: linear-gradient(90deg, #4f46e5, #7c3aed);
0141 | }
0142 | 
0143 | .metric-card:hover {
0144 |     transform: translateY(-4px);
0145 |     box-shadow: 0 20px 25px rgba(0, 0, 0, 0.1);
0146 | }
0147 | 
0148 | .metric-icon {
0149 |     font-size: 2rem;
0150 |     margin-bottom: 0.5rem;
0151 | }
0152 | 
0153 | .metric-value {
0154 |     font-size: 2.5rem;
0155 |     font-weight: 700;
0156 |     margin-bottom: 0.5rem;
0157 |     background: linear-gradient(135deg, #4f46e5, #7c3aed);
0158 |     -webkit-background-clip: text;
0159 |     -webkit-text-fill-color: transparent;
0160 |     background-clip: text;
0161 | }
0162 | 
0163 | .metric-label {
0164 |     color: #64748b;
0165 |     font-size: 0.875rem;
0166 |     font-weight: 500;
0167 |     text-transform: uppercase;
0168 |     letter-spacing: 0.05em;
0169 | }
0170 | 
0171 | /* === VULNERABILITIES === */
0172 | .vulnerabilities-list {
0173 |     display: grid;
0174 |     gap: 1.5rem;
0175 | }
0176 | 
0177 | .vulnerability-card {
0178 |     background: white;
0179 |     border: 1px solid #e5e7eb;
0180 |     border-radius: 16px;
0181 |     overflow: hidden;
0182 |     transition: all 0.3s ease;
0183 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0184 | }
0185 | 
0186 | .vulnerability-card:hover {
0187 |     box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
0188 |     transform: translateY(-2px);
0189 | }
0190 | 
0191 | .vulnerability-card.critical {
0192 |     border-left: 6px solid #dc2626;
0193 | }
0194 | 
0195 | .vulnerability-card.high {
0196 |     border-left: 6px solid #ea580c;
0197 | }
0198 | 
0199 | .vulnerability-card.medium {
0200 |     border-left: 6px solid #d97706;
0201 | }
0202 | 
0203 | .vulnerability-card.low {
0204 |     border-left: 6px solid #16a34a;
0205 | }
0206 | 
0207 | .vulnerability-card.info {
0208 |     border-left: 6px solid #0ea5e9;
0209 | }
0210 | 
0211 | .vuln-header {
0212 |     background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
0213 |     padding: 1.5rem;
0214 |     border-bottom: 1px solid #e5e7eb;
0215 |     display: flex;
0216 |     justify-content: space-between;
0217 |     align-items: flex-start;
0218 |     gap: 1rem;
0219 | }
0220 | 
0221 | .vuln-title {
0222 |     font-size: 1.25rem;
0223 |     font-weight: 600;
0224 |     color: #1f2937;
0225 |     flex: 1;
0226 | }
0227 | 
0228 | .vuln-badges {
0229 |     display: flex;
0230 |     gap: 0.5rem;
0231 |     flex-shrink: 0;
0232 | }
0233 | 
0234 | .badge {
0235 |     padding: 0.25rem 0.75rem;
0236 |     border-radius: 12px;
0237 |     font-size: 0.75rem;
0238 |     font-weight: 600;
0239 |     text-transform: uppercase;
0240 |     letter-spacing: 0.05em;
0241 | }
0242 | 
0243 | .badge.severity-critical {
0244 |     background: #dc2626;
0245 |     color: white;
0246 | }
0247 | 
0248 | .badge.severity-high {
0249 |     background: #ea580c;
0250 |     color: white;
0251 | }
0252 | 
0253 | .badge.severity-medium {
0254 |     background: #d97706;
0255 |     color: white;
0256 | }
0257 | 
0258 | .badge.severity-low {
0259 |     background: #16a34a;
0260 |     color: white;
0261 | }
0262 | 
0263 | .badge.severity-info {
0264 |     background: #0ea5e9;
0265 |     color: white;
0266 | }
0267 | 
0268 | .badge.type-badge {
0269 |     background: #6b7280;
0270 |     color: white;
0271 | }
0272 | 
0273 | .vuln-body {
0274 |     padding: 1.5rem;
0275 | }
0276 | 
0277 | .vuln-meta {
0278 |     display: grid;
0279 |     grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
0280 |     gap: 1rem;
0281 |     margin-bottom: 1.5rem;
0282 | }
0283 | 
0284 | .meta-item {
0285 |     background: #f8fafc;
0286 |     padding: 0.75rem;
0287 |     border-radius: 8px;
0288 |     border: 1px solid #e5e7eb;
0289 | }
0290 | 
0291 | .meta-label {
0292 |     font-size: 0.75rem;
0293 |     font-weight: 600;
0294 |     color: #6b7280;
0295 |     text-transform: uppercase;
0296 |     letter-spacing: 0.05em;
0297 |     margin-bottom: 0.25rem;
0298 | }
0299 | 
0300 | .meta-value {
0301 |     font-weight: 500;
0302 |     color: #1f2937;
0303 | }
0304 | 
0305 | .meta-value a {
0306 |     color: #4f46e5;
0307 |     text-decoration: none;
0308 | }
0309 | 
0310 | .meta-value a:hover {
0311 |     text-decoration: underline;
0312 | }
0313 | 
0314 | .vuln-description,
0315 | .vuln-code,
0316 | .vuln-remediation {
0317 |     margin-bottom: 1.5rem;
0318 | }
0319 | 
0320 | .vuln-description h4,
0321 | .vuln-code h4,
0322 | .vuln-remediation h4 {
0323 |     font-size: 1rem;
0324 |     font-weight: 600;
0325 |     color: #374151;
0326 |     margin-bottom: 0.75rem;
0327 |     display: flex;
0328 |     align-items: center;
0329 |     gap: 0.5rem;
0330 | }
0331 | 
0332 | .code-block {
0333 |     background: #0f172a;
0334 |     color: #e2e8f0;
0335 |     padding: 1rem;
0336 |     border-radius: 8px;
0337 |     font-family: 'JetBrains Mono', 'Fira Code', Monaco, monospace;
0338 |     font-size: 0.875rem;
0339 |     overflow-x: auto;
0340 |     line-height: 1.5;
0341 |     border: 1px solid #334155;
0342 | }
0343 | 
0344 | .advice-content {
0345 |     background: #dbeafe;
0346 |     padding: 1rem;
0347 |     border-radius: 8px;
0348 |     border-left: 4px solid #3b82f6;
0349 |     color: #1e40af;
0350 | }
0351 | 
0352 | /* === NO VULNERABILITIES === */
0353 | .no-vulnerabilities {
0354 |     text-align: center;
0355 |     padding: 4rem 2rem;
0356 |     background: linear-gradient(135deg, #22c55e, #16a34a);
0357 |     color: white;
0358 |     border-radius: 16px;
0359 | }
0360 | 
0361 | .no-vulns-icon {
0362 |     font-size: 4rem;
0363 |     margin-bottom: 1rem;
0364 | }
0365 | 
0366 | .no-vulnerabilities h2 {
0367 |     font-size: 2rem;
0368 |     margin-bottom: 1rem;
0369 | }
0370 | 
0371 | /* === REMEDIATION === */
0372 | .remediation-summary {
0373 |     background: #f0f9ff;
0374 |     padding: 1rem;
0375 |     border-radius: 8px;
0376 |     border-left: 4px solid #0ea5e9;
0377 |     margin-bottom: 2rem;
0378 | }
0379 | 
0380 | .remediation-plans {
0381 |     display: grid;
0382 |     gap: 2rem;
0383 | }
0384 | 
0385 | .remediation-card {
0386 |     background: white;
0387 |     border: 1px solid #e5e7eb;
0388 |     border-radius: 12px;
0389 |     padding: 1.5rem;
0390 |     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
0391 | }
0392 | 
0393 | .plan-header {
0394 |     display: flex;
0395 |     justify-content: space-between;
0396 |     align-items: center;
0397 |     margin-bottom: 1rem;
0398 | }
0399 | 
0400 | .plan-header h3 {
0401 |     font-size: 1.25rem;
0402 |     font-weight: 600;
0403 |     color: #1f2937;
0404 | }
0405 | 
0406 | .priority-badge {
0407 |     padding: 0.25rem 0.75rem;
0408 |     border-radius: 20px;
0409 |     font-size: 0.75rem;
0410 |     font-weight: 600;
0411 |     text-transform: uppercase;
0412 | }
0413 | 
0414 | .priority-badge.priority-immediate {
0415 |     background: #dc2626;
0416 |     color: white;
0417 | }
0418 | 
0419 | .priority-badge.priority-high {
0420 |     background: #ea580c;
0421 |     color: white;
0422 | }
0423 | 
0424 | .priority-badge.priority-medium {
0425 |     background: #d97706;
0426 |     color: white;
0427 | }
0428 | 
0429 | .priority-badge.priority-low {
0430 |     background: #16a34a;
0431 |     color: white;
0432 | }
0433 | 
0434 | .plan-meta {
0435 |     display: flex;
0436 |     gap: 1rem;
0437 |     margin-bottom: 1.5rem;
0438 |     flex-wrap: wrap;
0439 | }
0440 | 
0441 | .plan-stat {
0442 |     background: #f3f4f6;
0443 |     padding: 0.5rem 1rem;
0444 |     border-radius: 6px;
0445 |     font-size: 0.875rem;
0446 |     font-weight: 500;
0447 | }
0448 | 
0449 | .plan-steps {
0450 |     margin-bottom: 1.5rem;
0451 | }
0452 | 
0453 | .plan-steps h4 {
0454 |     font-size: 1rem;
0455 |     font-weight: 600;
0456 |     margin-bottom: 1rem;
0457 |     color: #374151;
0458 | }
0459 | 
0460 | .plan-steps ol {
0461 |     list-style: none;
0462 |     counter-reset: step-counter;
0463 | }
0464 | 
0465 | .remediation-step {
0466 |     counter-increment: step-counter;
0467 |     margin-bottom: 1rem;
0468 |     padding: 1rem;
0469 |     background: #f8fafc;
0470 |     border-radius: 8px;
0471 |     border-left: 4px solid #4f46e5;
0472 |     position: relative;
0473 |     padding-left: 3rem;
0474 | }
0475 | 
0476 | .remediation-step::before {
0477 |     content: counter(step-counter);
0478 |     position: absolute;
0479 |     left: 1rem;
0480 |     top: 1rem;
0481 |     background: #4f46e5;
0482 |     color: white;
0483 |     width: 1.5rem;
0484 |     height: 1.5rem;
0485 |     border-radius: 50%;
0486 |     display: flex;
0487 |     align-items: center;
0488 |     justify-content: center;
0489 |     font-weight: 600;
0490 |     font-size: 0.875rem;
0491 | }
0492 | 
0493 | .step-header {
0494 |     display: flex;
0495 |     justify-content: space-between;
0496 |     align-items: flex-start;
0497 |     margin-bottom: 0.5rem;
0498 | }
0499 | 
0500 | .step-meta {
0501 |     font-size: 0.75rem;
0502 |     color: #6b7280;
0503 |     background: #e5e7eb;
0504 |     padding: 0.25rem 0.5rem;
0505 |     border-radius: 4px;
0506 | }
0507 | 
0508 | .step-description {
0509 |     color: #4b5563;
0510 |     margin-bottom: 0.75rem;
0511 | }
0512 | 
0513 | .step-code {
0514 |     background: #f3f4f6;
0515 |     color: #374151;
0516 |     padding: 0.75rem;
0517 |     border-radius: 6px;
0518 |     font-family: 'JetBrains Mono', monospace;
0519 |     font-size: 0.8rem;
0520 |     border: 1px solid #d1d5db;
0521 | }
0522 | 
0523 | .risk-warning {
0524 |     background: #fef2f2;
0525 |     padding: 1rem;
0526 |     border-radius: 8px;
0527 |     border-left: 4px solid #ef4444;
0528 |     color: #991b1b;
0529 | }
0530 | 
0531 | .risk-warning h5 {
0532 |     font-weight: 600;
0533 |     margin-bottom: 0.5rem;
0534 | }
0535 | 
0536 | /* === TECHNICAL DETAILS === */
0537 | .technical-details {
0538 |     background: #f8fafc;
0539 |     border: 1px solid #e5e7eb;
0540 |     border-radius: 12px;
0541 |     overflow: hidden;
0542 | }
0543 | 
0544 | .details-toggle {
0545 |     background: #f1f5f9;
0546 |     padding: 1rem 1.5rem;
0547 |     cursor: pointer;
0548 |     font-weight: 600;
0549 |     color: #374151;
0550 |     display: flex;
0551 |     align-items: center;
0552 |     gap: 0.5rem;
0553 |     border: none;
0554 |     width: 100%;
0555 |     text-align: left;
0556 |     transition: background 0.2s;
0557 | }
0558 | 
0559 | .details-toggle:hover {
0560 |     background: #e2e8f0;
0561 | }
0562 | 
0563 | .details-toggle::after {
0564 |     content: '▶';
0565 |     margin-left: auto;
0566 |     transition: transform 0.3s;
0567 | }
0568 | 
0569 | .technical-details[open] .details-toggle::after {
0570 |     transform: rotate(90deg);
0571 | }
0572 | 
0573 | .details-content {
0574 |     padding: 1.5rem;
0575 | }
0576 | 
0577 | .tech-grid {
0578 |     display: grid;
0579 |     grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
0580 |     gap: 1.5rem;
0581 |     margin-bottom: 1.5rem;
0582 | }
0583 | 
0584 | .tech-item h4 {
0585 |     font-weight: 600;
0586 |     color: #374151;
0587 |     margin-bottom: 0.75rem;
0588 | }
0589 | 
0590 | .tech-item ul {
0591 |     list-style: none;
0592 |     padding-left: 0;
0593 | }
0594 | 
0595 | .tech-item li {
0596 |     padding: 0.25rem 0;
0597 |     color: #6b7280;
0598 | }
0599 | 
0600 | .analysis-summary {
0601 |     background: white;
0602 |     padding: 1rem;
0603 |     border-radius: 8px;
0604 |     border: 1px solid #e5e7eb;
0605 | }
0606 | 
0607 | .analysis-summary h4 {
0608 |     font-weight: 600;
0609 |     color: #374151;
0610 |     margin-bottom: 0.75rem;
0611 | }
0612 | 
0613 | .analysis-summary pre {
0614 |     background: #f8fafc;
0615 |     padding: 1rem;
0616 |     border-radius: 6px;
0617 |     font-size: 0.875rem;
0618 |     color: #4b5563;
0619 |     white-space: pre-wrap;
0620 |     word-wrap: break-word;
0621 | }
0622 | 
0623 | /* === FOOTER === */
0624 | .footer {
0625 |     background: #1f2937;
0626 |     color: white;
0627 |     padding: 2rem;
0628 |     text-align: center;
0629 | }
0630 | 
0631 | .footer-content p {
0632 |     margin-bottom: 0.5rem;
0633 | }
0634 | 
0635 | /* === RESPONSIVE DESIGN === */
0636 | @media (max-width: 768px) {
0637 |     .container {
0638 |         margin: 10px;
0639 |         border-radius: 8px;
0640 |     }
0641 |     
0642 |     .header {
0643 |         padding: 1.5rem;
0644 |     }
0645 |     
0646 |     .header h1 {
0647 |         font-size: 2rem;
0648 |     }
0649 |     
0650 |     .header-grid {
0651 |         grid-template-columns: 1fr;
0652 |     }
0653 |     
0654 |     .content {
0655 |         padding: 1.5rem;
0656 |     }
0657 |     
0658 |     .metrics-grid {
0659 |         grid-template-columns: 1fr;
0660 |     }
0661 |     
0662 |     .vuln-header {
0663 |         flex-direction: column;
0664 |         align-items: flex-start;
0665 |     }
0666 |     
0667 |     .vuln-meta {
0668 |         grid-template-columns: 1fr;
0669 |     }
0670 |     
0671 |     .plan-header {
0672 |         flex-direction: column;
0673 |         align-items: flex-start;
0674 |         gap: 0.5rem;
0675 |     }
0676 |     
0677 |     .plan-meta {
0678 |         flex-direction: column;
0679 |     }
0680 |     
0681 |     .step-header {
0682 |         flex-direction: column;
0683 |         align-items: flex-start;
0684 |     }
0685 | }
0686 | 
0687 | /* === ANIMATIONS === */
0688 | @keyframes fadeIn {
0689 |     from {
0690 |         opacity: 0;
0691 |         transform: translateY(20px);
0692 |     }
0693 |     to {
0694 |         opacity: 1;
0695 |         transform: translateY(0);
0696 |     }
0697 | }
0698 | 
0699 | .section {
0700 |     animation: fadeIn 0.6s ease-out;
0701 | }
0702 | 
0703 | /* === PRINT STYLES === */
0704 | @media print {
0705 |     body {
0706 |         background: white;
0707 |     }
0708 |     
0709 |     .container {
0710 |         box-shadow: none;
0711 |         margin: 0;
0712 |     }
0713 |     
0714 |     .header {
0715 |         background: #4f46e5 !important;
0716 |         -webkit-print-color-adjust: exact;
0717 |         color-adjust: exact;
0718 |     }
0719 |     
0720 |     .technical-details {
0721 |         border: 1px solid #ccc;
0722 |     }
0723 |     
0724 |     .details-content {
0725 |         display: block !important;
0726 |     }
0727 |     
0728 |     .details-toggle {
0729 |         display: none;
0730 |     }
0731 |     
0732 |     .vulnerability-card {
0733 |         break-inside: avoid;
0734 |         page-break-inside: avoid;
0735 |         margin-bottom: 1rem;
0736 |     }
0737 | }
0738 | </style>
```

---

### adapters\processing\chunker.py

**Ruta:** `adapters\processing\chunker.py`

```py
0001 | # adapters/processing/chunker.py
0002 | import logging
0003 | import math
0004 | from typing import List, Dict, Any, Optional
0005 | from dataclasses import dataclass
0006 | 
0007 | from core.models import ScanResult, Vulnerability, ChunkingStrategy
0008 | from core.exceptions import ChunkingError
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | @dataclass
0013 | class ChunkMetadata:
0014 |     """Metadatos optimizados de chunk"""
0015 |     id: int
0016 |     strategy: str
0017 |     total_chunks: int
0018 |     vulnerability_count: int
0019 |     estimated_size_bytes: int
0020 |     has_overlap: bool = False
0021 | 
0022 | @dataclass
0023 | class VulnerabilityChunk:
0024 |     """Chunk optimizado de vulnerabilidades"""
0025 |     id: int
0026 |     vulnerabilities: List[Vulnerability]
0027 |     metadata: ChunkMetadata
0028 |     
0029 |     @property
0030 |     def size_estimate(self) -> int:
0031 |         """Estimación rápida de tamaño"""
0032 |         return sum(len(v.title) + len(v.description) + len(v.code_snippet or "") 
0033 |                   for v in self.vulnerabilities)
0034 | 
0035 | class OptimizedChunker:
0036 |     """Chunker optimizado con estrategias inteligentes"""
0037 |     
0038 |     def __init__(self, config: Dict[str, Any]):
0039 |         self.max_vulns_per_chunk = config.get("max_vulnerabilities_per_chunk", 5)
0040 |         self.max_size_bytes = config.get("max_size_bytes", 8000)
0041 |         self.overlap_vulns = config.get("overlap_vulnerabilities", 1)
0042 |         self.min_chunk_size = config.get("min_chunk_size", 3)
0043 |     
0044 |     def should_chunk(self, scan_result: ScanResult) -> bool:
0045 |         """Determinar si se necesita chunking con heurísticas optimizadas"""
0046 |         
0047 |         vuln_count = len(scan_result.vulnerabilities)
0048 |         
0049 |         # Chunking por cantidad
0050 |         if vuln_count > self.max_vulns_per_chunk:
0051 |             logger.info(f"Chunking needed: {vuln_count} vulnerabilities > {self.max_vulns_per_chunk}")
0052 |             return True
0053 |         
0054 |         # Chunking por tamaño estimado
0055 |         estimated_size = self._estimate_total_size(scan_result.vulnerabilities)
0056 |         if estimated_size > self.max_size_bytes:
0057 |             logger.info(f"Chunking needed: {estimated_size} bytes > {self.max_size_bytes}")
0058 |             return True
0059 |         
0060 |         return False
0061 |     
0062 |     def create_chunks(self, scan_result: ScanResult) -> List[VulnerabilityChunk]:
0063 |         """Crear chunks usando estrategia óptima"""
0064 |         
0065 |         vulnerabilities = scan_result.vulnerabilities
0066 |         
0067 |         if not vulnerabilities:
0068 |             return []
0069 |         
0070 |         if not self.should_chunk(scan_result):
0071 |             # Chunk único
0072 |             return [VulnerabilityChunk(
0073 |                 id=1,
0074 |                 vulnerabilities=vulnerabilities,
0075 |                 metadata=ChunkMetadata(
0076 |                     id=1, strategy="no_chunking", total_chunks=1,
0077 |                     vulnerability_count=len(vulnerabilities),
0078 |                     estimated_size_bytes=self._estimate_total_size(vulnerabilities)
0079 |                 )
0080 |             )]
0081 |         
0082 |         # Seleccionar estrategia óptima
0083 |         strategy = self._select_strategy(vulnerabilities)
0084 |         
0085 |         try:
0086 |             if strategy == "by_count":
0087 |                 return self._chunk_by_count(vulnerabilities)
0088 |             else:  # by_size
0089 |                 return self._chunk_by_size(vulnerabilities)
0090 |         
0091 |         except Exception as e:
0092 |             logger.error(f"Chunking failed: {e}")
0093 |             return self._emergency_chunking(vulnerabilities)
0094 |     
0095 |     def _select_strategy(self, vulnerabilities: List[Vulnerability]) -> str:
0096 |         """Seleccionar estrategia óptima basada en características"""
0097 |         
0098 |         avg_desc_length = sum(len(v.description) for v in vulnerabilities) / len(vulnerabilities)
0099 |         
0100 |         # Si las descripciones son muy largas, usar estrategia por tamaño
0101 |         if avg_desc_length > 300:
0102 |             return "by_size"
0103 |         
0104 |         return "by_count"
0105 |     
0106 |     def _chunk_by_count(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0107 |         """Chunking optimizado por cantidad"""
0108 |         
0109 |         chunks = []
0110 |         chunk_size = self.max_vulns_per_chunk
0111 |         
0112 |         for i in range(0, len(vulnerabilities), chunk_size - self.overlap_vulns):
0113 |             chunk_vulns = vulnerabilities[i:i + chunk_size]
0114 |             
0115 |             # Evitar chunks muy pequeños al final
0116 |             if i > 0 and len(chunk_vulns) < self.min_chunk_size:
0117 |                 if chunks:
0118 |                     chunks[-1].vulnerabilities.extend(chunk_vulns)
0119 |                     chunks[-1].metadata.vulnerability_count += len(chunk_vulns)
0120 |                 break
0121 |             
0122 |             chunk = VulnerabilityChunk(
0123 |                 id=len(chunks) + 1,
0124 |                 vulnerabilities=chunk_vulns,
0125 |                 metadata=ChunkMetadata(
0126 |                     id=len(chunks) + 1,
0127 |                     strategy="by_count",
0128 |                     total_chunks=math.ceil(len(vulnerabilities) / chunk_size),
0129 |                     vulnerability_count=len(chunk_vulns),
0130 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns),
0131 |                     has_overlap=i > 0 and self.overlap_vulns > 0
0132 |                 )
0133 |             )
0134 |             chunks.append(chunk)
0135 |         
0136 |         # Actualizar total_chunks
0137 |         for chunk in chunks:
0138 |             chunk.metadata.total_chunks = len(chunks)
0139 |         
0140 |         logger.info(f"Created {len(chunks)} chunks by count strategy")
0141 |         return chunks
0142 |     
0143 |     def _chunk_by_size(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0144 |         """Chunking optimizado por tamaño"""
0145 |         
0146 |         chunks = []
0147 |         current_vulns = []
0148 |         current_size = 0
0149 |         
0150 |         for vuln in vulnerabilities:
0151 |             vuln_size = self._estimate_vuln_size(vuln)
0152 |             
0153 |             if current_size + vuln_size > self.max_size_bytes and current_vulns:
0154 |                 # Crear chunk actual
0155 |                 chunk = VulnerabilityChunk(
0156 |                     id=len(chunks) + 1,
0157 |                     vulnerabilities=current_vulns.copy(),
0158 |                     metadata=ChunkMetadata(
0159 |                         id=len(chunks) + 1,
0160 |                         strategy="by_size",
0161 |                         total_chunks=0,  # Se actualizará después
0162 |                         vulnerability_count=len(current_vulns),
0163 |                         estimated_size_bytes=current_size
0164 |                     )
0165 |                 )
0166 |                 chunks.append(chunk)
0167 |                 
0168 |                 # Nuevo chunk con overlap
0169 |                 overlap_vulns = current_vulns[-self.overlap_vulns:] if self.overlap_vulns > 0 else []
0170 |                 current_vulns = overlap_vulns + [vuln]
0171 |                 current_size = sum(self._estimate_vuln_size(v) for v in current_vulns)
0172 |             else:
0173 |                 current_vulns.append(vuln)
0174 |                 current_size += vuln_size
0175 |         
0176 |         # Último chunk
0177 |         if current_vulns:
0178 |             chunk = VulnerabilityChunk(
0179 |                 id=len(chunks) + 1,
0180 |                 vulnerabilities=current_vulns,
0181 |                 metadata=ChunkMetadata(
0182 |                     id=len(chunks) + 1,
0183 |                     strategy="by_size",
0184 |                     total_chunks=0,
0185 |                     vulnerability_count=len(current_vulns),
0186 |                     estimated_size_bytes=current_size
0187 |                 )
0188 |             )
0189 |             chunks.append(chunk)
0190 |         
0191 |         # Actualizar total_chunks
0192 |         for chunk in chunks:
0193 |             chunk.metadata.total_chunks = len(chunks)
0194 |         
0195 |         logger.info(f"Created {len(chunks)} chunks by size strategy")
0196 |         return chunks
0197 |     
0198 |     def _emergency_chunking(self, vulnerabilities: List[Vulnerability]) -> List[VulnerabilityChunk]:
0199 |         """Chunking de emergencia ultra-conservador"""
0200 |         
0201 |         logger.warning("Using emergency chunking with very small chunks")
0202 |         
0203 |         emergency_size = 3  # Chunks muy pequeños
0204 |         chunks = []
0205 |         
0206 |         for i in range(0, len(vulnerabilities), emergency_size):
0207 |             chunk_vulns = vulnerabilities[i:i + emergency_size]
0208 |             
0209 |             chunk = VulnerabilityChunk(
0210 |                 id=len(chunks) + 1,
0211 |                 vulnerabilities=chunk_vulns,
0212 |                 metadata=ChunkMetadata(
0213 |                     id=len(chunks) + 1,
0214 |                     strategy="emergency",
0215 |                     total_chunks=math.ceil(len(vulnerabilities) / emergency_size),
0216 |                     vulnerability_count=len(chunk_vulns),
0217 |                     estimated_size_bytes=self._estimate_total_size(chunk_vulns)
0218 |                 )
0219 |             )
0220 |             chunks.append(chunk)
0221 |         
0222 |         return chunks
0223 |     
0224 |     def _estimate_total_size(self, vulnerabilities: List[Vulnerability]) -> int:
0225 |         """Estimación rápida de tamaño total"""
0226 |         return sum(self._estimate_vuln_size(v) for v in vulnerabilities)
0227 |     
0228 |     def _estimate_vuln_size(self, vulnerability: Vulnerability) -> int:
0229 |         """Estimación optimizada de tamaño de vulnerabilidad"""
0230 |         base_size = len(vulnerability.title) + len(vulnerability.description)
0231 |         code_size = len(vulnerability.code_snippet or "")
0232 |         
0233 |         # Factor de multiplicación para metadatos JSON (reducido)
0234 |         return int((base_size + code_size) * 1.3)
0235 | 
0236 |         
0237 |         ```

---

### application\cli.py

**Ruta:** `application\cli.py`

```py
0001 | # application/cli.py
0002 | #!/usr/bin/env python3
0003 | """
0004 | 🛡️ Security Analysis Platform v3.0 - Unified CLI
0005 | Análisis completo con arquitectura optimizada
0006 | """
0007 | 
0008 | import asyncio
0009 | import sys
0010 | import os
0011 | from pathlib import Path
0012 | from typing import Optional
0013 | import click
0014 | 
0015 | # Add project root to path
0016 | sys.path.insert(0, str(Path(__file__).parent.parent))
0017 | 
0018 | from application.factory import create_factory
0019 | from application.use_cases import AnalysisUseCase, CLIUseCase
0020 | from infrastructure.config import settings
0021 | 
0022 | @click.group()
0023 | @click.version_option("3.0", prog_name="Security Analysis Platform")
0024 | def cli():
0025 |     """🛡️ Security Analysis Platform v3.0 - Advanced Security Analysis"""
0026 |     pass
0027 | 
0028 | @cli.command()
0029 | @click.argument('input_file', type=click.Path(exists=True, readable=True))
0030 | @click.option('--output', '-o', default='security_report.html',
0031 |               help='Output HTML file')
0032 | @click.option('--language', '-l', 
0033 |               help='Programming language hint (abap, java, python, etc.)')
0034 | @click.option('--verbose', '-v', is_flag=True,
0035 |               help='Enable verbose logging')
0036 | @click.option('--basic-mode', is_flag=True,
0037 |               help='Run in basic mode without LLM analysis')
0038 | @click.option('--force-chunking', is_flag=True,
0039 |               help='Force chunking even for small files')
0040 | @click.option('--disable-chunking', is_flag=True,
0041 |               help='Disable chunking completely')
0042 | @click.option('--tool-hint',
0043 |               help='Scanner tool hint (abap_custom, semgrep, etc.)')
0044 | @click.option('--open-browser', is_flag=True,
0045 |               help='Open report in browser after generation')
0046 | def analyze(input_file, output, language, verbose, basic_mode, force_chunking, 
0047 |            disable_chunking, tool_hint, open_browser):
0048 |     """Analyze security vulnerabilities from SAST tool outputs"""
0049 |     
0050 |     # Display banner
0051 |     click.echo("""
0052 | ╔══════════════════════════════════════════════════════════════╗
0053 | ║    🛡️  SECURITY ANALYSIS PLATFORM v3.0                      ║
0054 | ║                                                              ║
0055 | ║    🤖 AI-Powered Triage • 🧩 Smart Chunking • 📊 Rich Reports ║
0056 | ╚══════════════════════════════════════════════════════════════╝
0057 |     """)
0058 |     
0059 |     # Normalize output file
0060 |     if not output.lower().endswith('.html'):
0061 |         output = f"{output}.html"
0062 |     
0063 |     # Show configuration
0064 |     click.echo(f"📁 Input: {Path(input_file).name}")
0065 |     click.echo(f"📄 Output: {output}")
0066 |     if language:
0067 |         click.echo(f"🔤 Language: {language}")
0068 |     if tool_hint:
0069 |         click.echo(f"🔧 Tool: {tool_hint}")
0070 |     
0071 |     mode_desc = "Basic (No LLM)" if basic_mode else "Full AI Analysis"
0072 |     click.echo(f"⚙️  Mode: {mode_desc}")
0073 |     
0074 |     if verbose:
0075 |         click.echo("📝 Verbose logging enabled")
0076 |     
0077 |     click.echo()
0078 |     
0079 |     # Execute analysis
0080 |     try:
0081 |         success = asyncio.run(_run_analysis(
0082 |             input_file, output, language, verbose, basic_mode,
0083 |             force_chunking, disable_chunking, tool_hint
0084 |         ))
0085 |         
0086 |         if success and open_browser:
0087 |             _open_in_browser(output)
0088 |         
0089 |         sys.exit(0 if success else 1)
0090 |         
0091 |     except KeyboardInterrupt:
0092 |         click.echo("\n🛑 Analysis interrupted by user")
0093 |         sys.exit(1)
0094 |     except Exception as e:
0095 |         click.echo(f"\n❌ Unexpected error: {e}")
0096 |         if verbose:
0097 |             import traceback
0098 |             traceback.print_exc()
0099 |         sys.exit(1)
0100 | 
0101 | async def _run_analysis(input_file: str, output: str, language: Optional[str],
0102 |                        verbose: bool, basic_mode: bool, force_chunking: bool,
0103 |                        disable_chunking: bool, tool_hint: Optional[str]) -> bool:
0104 |     """Execute analysis with proper error handling"""
0105 |     
0106 |     try:
0107 |         # Create factory and services
0108 |         factory = create_factory()
0109 |         
0110 |         if basic_mode or not settings.has_llm_provider:
0111 |             if not basic_mode:
0112 |                 click.echo("⚠️  No LLM provider configured - running in basic mode")
0113 |             
0114 |             # Basic analysis
0115 |             analysis_use_case = AnalysisUseCase(
0116 |                 scanner_service=factory.create_scanner_service(),
0117 |                 reporter_service=factory.create_reporter_service(),
0118 |                 metrics=factory.get_metrics()
0119 |             )
0120 |             
0121 |             cli_use_case = CLIUseCase(analysis_use_case)
0122 |             return await cli_use_case.execute_cli_analysis(
0123 |                 input_file, output, language, verbose, disable_llm=True
0124 |             )
0125 |         
0126 |         else:
0127 |             # Full analysis with LLM
0128 |             analysis_use_case = AnalysisUseCase(
0129 |                 scanner_service=factory.create_scanner_service(),
0130 |                 triage_service=factory.create_triage_service(),
0131 |                 remediation_service=factory.create_remediation_service(),
0132 |                 reporter_service=factory.create_reporter_service(),
0133 |                 chunker=factory.create_chunker(),
0134 |                 metrics=factory.get_metrics()
0135 |             )
0136 |             
0137 |             cli_use_case = CLIUseCase(analysis_use_case)
0138 |             return await cli_use_case.execute_cli_analysis(
0139 |                 input_file, output, language, verbose, disable_llm=False, 
0140 |                 force_chunking=force_chunking
0141 |             )
0142 |     
0143 |     except Exception as e:
0144 |         click.echo(f"❌ Analysis failed: {e}")
0145 |         if verbose:
0146 |             import traceback
0147 |             traceback.print_exc()
0148 |         return False
0149 | 
0150 | def _open_in_browser(output_file: str):
0151 |     """Open report in default browser"""
0152 |     try:
0153 |         import webbrowser
0154 |         file_url = f"file://{Path(output_file).absolute()}"
0155 |         webbrowser.open(file_url)
0156 |         click.echo(f"🌐 Opening report in browser: {file_url}")
0157 |     except Exception as e:
0158 |         click.echo(f"⚠️  Could not open browser: {e}")
0159 | 
0160 | @cli.command()
0161 | def setup():
0162 |     """Setup and validate system configuration"""
0163 |     click.echo("🔧 Setting up Security Analysis Platform v3.0...")
0164 |     
0165 |     # Check dependencies
0166 |     missing_deps = []
0167 |     required_packages = ['pydantic', 'click', 'jinja2']
0168 |     
0169 |     for package in required_packages:
0170 |         try:
0171 |             __import__(package)
0172 |         except ImportError:
0173 |             missing_deps.append(package)
0174 |     
0175 |     if missing_deps:
0176 |         click.echo(f"❌ Missing dependencies: {', '.join(missing_deps)}")
0177 |         click.echo("Install with: pip install " + ' '.join(missing_deps))
0178 |         return
0179 |     
0180 |     click.echo("✅ Dependencies: OK")
0181 |     
0182 |     # Check API keys
0183 |     click.echo("\n🔑 API Key Status:")
0184 |     click.echo(f"  OpenAI: {'✅ Configured' if settings.openai_api_key else '❌ Missing'}")
0185 |     click.echo(f"  WatsonX: {'✅ Configured' if settings.watsonx_api_key else '❌ Missing'}")
0186 |     
0187 |     if not settings.has_llm_provider:
0188 |         click.echo("\n⚠️  No API keys configured!")
0189 |         click.echo("Set at least one API key:")
0190 |         click.echo("  export OPENAI_API_KEY='sk-your-key-here'")
0191 |         click.echo("  export RESEARCH_API_KEY='your-watsonx-key'")
0192 |         click.echo("\n💡 You can still run basic analysis without API keys")
0193 |     else:
0194 |         click.echo(f"\n✅ LLM Provider: {settings.get_available_llm_provider()}")
0195 |     
0196 |     # Test basic functionality
0197 |     click.echo("\n🧪 Testing system...")
0198 |     try:
0199 |         factory = create_factory()
0200 |         scanner = factory.create_scanner_service()
0201 |         click.echo("✅ Scanner service: OK")
0202 |         
0203 |         if settings.has_llm_provider:
0204 |             triage = factory.create_triage_service()
0205 |             remediation = factory.create_remediation_service()
0206 |             if triage and remediation:
0207 |                 click.echo("✅ LLM services: OK")
0208 |         
0209 |         click.echo("\n🎉 Setup completed successfully!")
0210 |         click.echo("\nNext steps:")
0211 |         click.echo("1. Run analysis: security-analyzer analyze your_file.json")
0212 |         click.echo("2. View help: security-analyzer --help")
0213 |         
0214 |     except Exception as e:
0215 |         click.echo(f"❌ Setup test failed: {e}")
0216 | 
0217 | @cli.command()
0218 | @click.argument('input_file', type=click.Path(exists=True))
0219 | def validate(input_file):
0220 |     """Validate input file format and structure"""
0221 |     click.echo(f"🔍 Validating: {input_file}")
0222 |     
0223 |     try:
0224 |         from core.services.scanner import ScannerService
0225 |         
0226 |         scanner = ScannerService()
0227 |         
0228 |         # Basic validation
0229 |         scanner._validate_file(input_file)
0230 |         click.echo("✅ File validation: PASSED")
0231 |         
0232 |         # Load and analyze structure
0233 |         raw_data = scanner._load_file(input_file)
0234 |         click.echo("✅ JSON format: VALID")
0235 |         
0236 |         # Analyze structure
0237 |         if isinstance(raw_data, list):
0238 |             click.echo(f"📊 Format: List with {len(raw_data)} items")
0239 |         elif isinstance(raw_data, dict):
0240 |             keys = list(raw_data.keys())[:5]
0241 |             click.echo(f"📊 Format: Object with keys: {keys}")
0242 |             
0243 |             # Look for vulnerability containers
0244 |             for container_key in ['findings', 'vulnerabilities', 'issues', 'results']:
0245 |                 if container_key in raw_data and isinstance(raw_data[container_key], list):
0246 |                     count = len(raw_data[container_key])
0247 |                     click.echo(f"🎯 Found {count} items in '{container_key}'")
0248 |                     
0249 |                     # Sample first item
0250 |                     if count > 0:
0251 |                         sample = raw_data[container_key][0]
0252 |                         if isinstance(sample, dict):
0253 |                             sample_keys = list(sample.keys())[:3]
0254 |                             click.echo(f"📋 Sample item keys: {sample_keys}")
0255 |                     break
0256 |         
0257 |         # Test parsing
0258 |         parser = scanner.parser
0259 |         vulnerabilities = parser.parse(raw_data)
0260 |         click.echo(f"✅ Parsing test: Found {len(vulnerabilities)} vulnerabilities")
0261 |         
0262 |         if vulnerabilities:
0263 |             severity_dist = {}
0264 |             for vuln in vulnerabilities:
0265 |                 sev = vuln.severity.value
0266 |                 severity_dist[sev] = severity_dist.get(sev, 0) + 1
0267 |             
0268 |             click.echo("📈 Severity distribution:")
0269 |             for severity, count in severity_dist.items():
0270 |                 click.echo(f"  • {severity}: {count}")
0271 |     
0272 |     except Exception as e:
0273 |         click.echo(f"❌ Validation failed: {e}")
0274 | 
0275 | @cli.command()
0276 | def examples():
0277 |     """Show usage examples and help"""
0278 |     click.echo("""
0279 | 🎓 Security Analysis Platform v3.0 - Usage Examples
0280 | 
0281 | 📝 BASIC USAGE:
0282 |    security-analyzer analyze vulnerabilities.json
0283 | 
0284 | 🎯 ADVANCED OPTIONS:
0285 |    # Custom output file
0286 |    security-analyzer analyze scan.json -o my_report.html
0287 | 
0288 |    # Specify programming language
0289 |    security-analyzer analyze abap_scan.json -l abap
0290 | 
0291 |    # Verbose output for debugging
0292 |    security-analyzer analyze results.json --verbose
0293 | 
0294 |    # Basic mode (no LLM analysis)
0295 |    security-analyzer analyze scan.json --basic-mode
0296 | 
0297 |    # Force or disable chunking
0298 |    security-analyzer analyze large_scan.json --force-chunking
0299 |    security-analyzer analyze small_scan.json --disable-chunking
0300 | 
0301 |    # Open in browser after generation
0302 |    security-analyzer analyze results.json --open-browser
0303 | 
0304 | 🔧 SYSTEM COMMANDS:
0305 |    security-analyzer setup              # Test configuration
0306 |    security-analyzer validate file.json # Validate input format
0307 | 
0308 | 📁 EXPECTED INPUT FORMAT:
0309 |    {
0310 |      "findings": [
0311 |        {
0312 |          "rule_id": "abap-sql-injection-001",
0313 |          "title": "SQL Injection Vulnerability",
0314 |          "message": "User input directly concatenated into SQL query",
0315 |          "severity": "HIGH",
0316 |          "location": {
0317 |            "file": "src/login.abap",
0318 |            "line": 42,
0319 |            "context": ["SELECT * FROM users", "WHERE name = '" + input + "'"]
0320 |          },
0321 |          "cwe": "CWE-89"
0322 |        }
0323 |      ]
0324 |    }
0325 | 
0326 | 🔑 ENVIRONMENT VARIABLES:
0327 |    OPENAI_API_KEY                 # OpenAI GPT API key
0328 |    RESEARCH_API_KEY              # IBM WatsonX API key
0329 |    LOG_LEVEL                     # Logging level (DEBUG, INFO, WARNING, ERROR)
0330 |    CHUNKING_MAX_VULNS           # Max vulnerabilities per chunk (default: 15)
0331 |    CACHE_ENABLED                # Enable result caching (default: true)
0332 | 
0333 | 💡 TIPS:
0334 |    • Use --verbose for detailed logs and debugging
0335 |    • The system auto-detects input format and language
0336 |    • LLM analysis significantly improves accuracy
0337 |    • Reports are interactive and include search functionality
0338 |    • Cache speeds up repeated analysis of same files
0339 | 
0340 | 📚 For more information: https://github.com/your-org/security-analyzer
0341 | """)
0342 | 
0343 | @cli.command()
0344 | def metrics():
0345 |     """Display performance metrics from last session"""
0346 |     click.echo("📊 Performance Metrics")
0347 |     click.echo("=" * 50)
0348 |     
0349 |     # This would load from a metrics file in a real implementation
0350 |     click.echo("Feature not yet implemented - metrics will be shown during analysis")
0351 |     click.echo("Use --verbose flag during analysis to see detailed metrics")
0352 | 
0353 | if __name__ == '__main__':
0354 |     cli()
```

---

### application\factory.py

**Ruta:** `application\factory.py`

```py
0001 | # application/factory.py - ACTUALIZADO CON CONTROL DE DEBUG
0002 | import logging
0003 | from typing import Optional
0004 | 
0005 | from core.services.scanner import ScannerService
0006 | from core.services.triage import TriageService
0007 | from core.services.remediation import RemediationService
0008 | from core.services.reporter import ReporterService
0009 | from infrastructure.llm.client import LLMClient
0010 | from infrastructure.cache import AnalysisCache
0011 | from infrastructure.config import settings
0012 | from adapters.processing.chunker import OptimizedChunker
0013 | from shared.metrics import MetricsCollector
0014 | from shared.logger import setup_logging
0015 | 
0016 | logger = logging.getLogger(__name__)
0017 | 
0018 | class ServiceFactory:
0019 |     """Factory optimizado con control de debug automático"""
0020 |     
0021 |     def __init__(self, enable_cache: bool = True, log_level: str = "INFO"):
0022 |         # Setup logging
0023 |         setup_logging(log_level)
0024 |         
0025 |         # Initialize shared components
0026 |         self.settings = settings
0027 |         self.metrics = MetricsCollector() if settings.metrics_enabled else None
0028 |         self.cache = AnalysisCache(settings.cache_directory, settings.cache_ttl_hours) if enable_cache else None
0029 |         
0030 |         # Control de debug
0031 |         self.debug_mode = False
0032 |         
0033 |         # Validate configuration
0034 |         self._validate_configuration()
0035 |         
0036 |         logger.info(f"ServiceFactory initialized with {settings.get_available_llm_provider()}")
0037 |     
0038 |     def enable_debug_mode(self):
0039 |         """Habilitar modo debug - será llamado desde el debugger"""
0040 |         self.debug_mode = True
0041 |         logger.info("🔍 Debug mode enabled in ServiceFactory")
0042 |     
0043 |     def disable_debug_mode(self):
0044 |         """Deshabilitar modo debug"""
0045 |         self.debug_mode = False
0046 |         logger.info("🔍 Debug mode disabled in ServiceFactory")
0047 |     
0048 |     def _validate_configuration(self) -> None:
0049 |         """Validate system configuration"""
0050 |         if not self.settings.has_llm_provider:
0051 |             logger.warning("No LLM providers configured - system will run in basic mode")
0052 |         else:
0053 |             logger.info(f"LLM provider available: {self.settings.get_available_llm_provider()}")
0054 |     
0055 |     def create_scanner_service(self) -> ScannerService:
0056 |         """Create configured scanner service"""
0057 |         return ScannerService(cache=self.cache)
0058 |     
0059 |     def create_llm_client(self) -> Optional[LLMClient]:
0060 |         """Create LLM client with debug control"""
0061 |         if not self.settings.has_llm_provider:
0062 |             return None
0063 |         
0064 |         try:
0065 |             provider = self.settings.get_available_llm_provider()
0066 |             # Pasar el estado de debug al cliente
0067 |             client = LLMClient(primary_provider=provider, enable_debug=self.debug_mode)
0068 |             
0069 |             # Si el debug está habilitado, registrar el cliente automáticamente
0070 |             if self.debug_mode:
0071 |                 try:
0072 |                     from debug.llm_debugger import register_llm_client_for_debug
0073 |                     register_llm_client_for_debug(client)
0074 |                 except ImportError:
0075 |                     logger.warning("Debug module not available")
0076 |             
0077 |             return client
0078 |         except Exception as e:
0079 |             logger.error(f"Failed to create LLM client: {e}")
0080 |             return None
0081 |     
0082 |     def create_triage_service(self) -> Optional[TriageService]:
0083 |         """Create triage service with LLM client"""
0084 |         llm_client = self.create_llm_client()
0085 |         if not llm_client:
0086 |             return None
0087 |         
0088 |         return TriageService(llm_client=llm_client, metrics=self.metrics)
0089 |     
0090 |     def create_remediation_service(self) -> Optional[RemediationService]:
0091 |         """Create remediation service with LLM client"""
0092 |         llm_client = self.create_llm_client()
0093 |         if not llm_client:
0094 |             return None
0095 |         
0096 |         return RemediationService(llm_client=llm_client, metrics=self.metrics)
0097 |     
0098 |     def create_reporter_service(self) -> ReporterService:
0099 |         """Create reporter service"""
0100 |         return ReporterService(metrics=self.metrics)
0101 |     
0102 |     def create_chunker(self) -> OptimizedChunker:
0103 |         """Create optimized chunker"""
0104 |         return OptimizedChunker(self.settings.chunking_config)
0105 |     
0106 |     def get_metrics(self) -> Optional[MetricsCollector]:
0107 |         """Get metrics collector"""
0108 |         return self.metrics
0109 | 
0110 | # Convenience function
0111 | def create_factory() -> ServiceFactory:
0112 |     """Create factory with default configuration"""
0113 |     return ServiceFactory(
0114 |         enable_cache=settings.cache_enabled,
0115 |         log_level=settings.log_level
0116 |     )
0117 | 
0118 | # Factory con debug habilitado - para uso desde debugger
0119 | def create_debug_factory() -> ServiceFactory:
0120 |     """Create factory with debug enabled"""
0121 |     factory = create_factory()
0122 |     factory.enable_debug_mode()
0123 |     return factory
```

---

### application\use_cases.py

**Ruta:** `application\use_cases.py`

```py
0001 | # application/use_cases.py
0002 | import asyncio
0003 | import logging
0004 | from pathlib import Path
0005 | from typing import Optional, List
0006 | from datetime import datetime
0007 | 
0008 | from core.models import AnalysisReport, ScanResult, Vulnerability
0009 | from core.services.scanner import ScannerService
0010 | from core.services.triage import TriageService
0011 | from core.services.remediation import RemediationService
0012 | from core.services.reporter import ReporterService
0013 | from adapters.processing.chunker import OptimizedChunker
0014 | from shared.metrics import MetricsCollector
0015 | 
0016 | logger = logging.getLogger(__name__)
0017 | 
0018 | class AnalysisUseCase:
0019 |     """Caso de uso principal consolidado - sin duplicación"""
0020 |     
0021 |     def __init__(self,
0022 |                  scanner_service: ScannerService,
0023 |                  triage_service: Optional[TriageService] = None,
0024 |                  remediation_service: Optional[RemediationService] = None,
0025 |                  reporter_service: Optional[ReporterService] = None,
0026 |                  chunker: Optional[OptimizedChunker] = None,
0027 |                  metrics: Optional[MetricsCollector] = None):
0028 |         
0029 |         self.scanner_service = scanner_service
0030 |         self.triage_service = triage_service
0031 |         self.remediation_service = remediation_service
0032 |         self.reporter_service = reporter_service
0033 |         self.chunker = chunker
0034 |         self.metrics = metrics
0035 |     
0036 |     async def execute_full_analysis(self,
0037 |                                   file_path: str,
0038 |                                   output_file: Optional[str] = None,
0039 |                                   language: Optional[str] = None,
0040 |                                   tool_hint: Optional[str] = None,
0041 |                                   force_chunking: bool = False,
0042 |                                   disable_chunking: bool = False) -> AnalysisReport:
0043 |         """Execute complete security analysis pipeline"""
0044 |         
0045 |         start_time = asyncio.get_event_loop().time()
0046 |         
0047 |         try:
0048 |             logger.info(f"Starting complete analysis: {file_path}")
0049 |             
0050 |             # Phase 1: Scan and normalize vulnerabilities
0051 |             scan_result = await self.scanner_service.scan_file(
0052 |                 file_path=file_path,
0053 |                 language=language,
0054 |                 tool_hint=tool_hint
0055 |             )
0056 |             
0057 |             if not scan_result.vulnerabilities:
0058 |                 logger.info("No vulnerabilities found")
0059 |                 return self._create_clean_report(scan_result, start_time)
0060 |             
0061 |             # Phase 2: LLM Triage (if available)
0062 |             triage_result = None
0063 |             if self.triage_service:
0064 |                 triage_result = await self._perform_triage_analysis(
0065 |                     scan_result, language, force_chunking, disable_chunking
0066 |                 )
0067 |             
0068 |             # Phase 3: Generate remediation plans (if available)
0069 |             remediation_plans = []
0070 |             if self.remediation_service and triage_result:
0071 |                 confirmed_vulns = self._extract_confirmed_vulnerabilities(
0072 |                     scan_result.vulnerabilities, triage_result
0073 |                 )
0074 |                 if confirmed_vulns:
0075 |                     remediation_plans = await self.remediation_service.generate_remediation_plans(
0076 |                         confirmed_vulns, language
0077 |                     )
0078 |             
0079 |             # Phase 4: Create analysis report
0080 |             total_time = asyncio.get_event_loop().time() - start_time
0081 |             analysis_report = self._create_analysis_report(
0082 |                 scan_result, triage_result, remediation_plans, total_time,
0083 |                 force_chunking, disable_chunking, language, tool_hint
0084 |             )
0085 |             
0086 |             # Phase 5: Generate HTML report (if requested)
0087 |             if output_file and self.reporter_service:
0088 |                 await self.reporter_service.generate_html_report(analysis_report, output_file)
0089 |             
0090 |             # Record metrics
0091 |             if self.metrics:
0092 |                 self.metrics.record_complete_analysis(
0093 |                     file_path=file_path,
0094 |                     vulnerability_count=len(scan_result.vulnerabilities),
0095 |                     confirmed_count=len(remediation_plans),
0096 |                     total_time=total_time,
0097 |                     chunking_used=self._was_chunking_used(scan_result, force_chunking, disable_chunking),
0098 |                     language=language,
0099 |                     success=True
0100 |                 )
0101 |             
0102 |             logger.info(f"Analysis completed successfully in {total_time:.2f}s")
0103 |             return analysis_report
0104 |             
0105 |         except Exception as e:
0106 |             total_time = asyncio.get_event_loop().time() - start_time
0107 |             if self.metrics:
0108 |                 self.metrics.record_complete_analysis(
0109 |                     file_path=file_path,
0110 |                     total_time=total_time,
0111 |                     success=False,
0112 |                     error=str(e)
0113 |                 )
0114 |             logger.error(f"Analysis failed: {e}")
0115 |             raise
0116 |     
0117 |     async def execute_basic_analysis(self, file_path: str, output_file: Optional[str] = None,
0118 |                                    tool_hint: Optional[str] = None) -> AnalysisReport:
0119 |         """Execute basic analysis without LLM services"""
0120 |         
0121 |         start_time = asyncio.get_event_loop().time()
0122 |         
0123 |         logger.info(f"Starting basic analysis: {file_path}")
0124 |         
0125 |         # Only scan and normalize
0126 |         scan_result = await self.scanner_service.scan_file(
0127 |             file_path=file_path,
0128 |             tool_hint=tool_hint
0129 |         )
0130 |         
0131 |         total_time = asyncio.get_event_loop().time() - start_time
0132 |         
0133 |         # Create basic report
0134 |         analysis_report = AnalysisReport(
0135 |             scan_result=scan_result,
0136 |             triage_result=None,
0137 |             remediation_plans=[],
0138 |             analysis_config={"mode": "basic", "tool_hint": tool_hint},
0139 |             total_processing_time_seconds=total_time,
0140 |             chunking_enabled=False
0141 |         )
0142 |         
0143 |         # Generate HTML if requested
0144 |         if output_file and self.reporter_service:
0145 |             await self.reporter_service.generate_html_report(analysis_report, output_file)
0146 |         
0147 |         logger.info(f"Basic analysis completed in {total_time:.2f}s")
0148 |         return analysis_report
0149 |     
0150 |     async def _perform_triage_analysis(self, scan_result: ScanResult, language: Optional[str],
0151 |                                      force_chunking: bool, disable_chunking: bool):
0152 |         """Perform triage analysis with optional chunking"""
0153 |         
0154 |         should_chunk = (
0155 |             (self.chunker and self.chunker.should_chunk(scan_result) and not disable_chunking) 
0156 |             or force_chunking
0157 |         )
0158 |         
0159 |         if should_chunk and self.chunker:
0160 |             logger.info("Using chunked triage analysis")
0161 |             return await self._analyze_with_chunking(scan_result, language)
0162 |         else:
0163 |             logger.info("Using direct triage analysis")
0164 |             return await self.triage_service.analyze_vulnerabilities(
0165 |                 scan_result.vulnerabilities, language
0166 |             )
0167 |     
0168 |     async def _analyze_with_chunking(self, scan_result: ScanResult, language: Optional[str]):
0169 |         """Perform chunked analysis and consolidate results"""
0170 |         
0171 |         chunks = self.chunker.create_chunks(scan_result)
0172 |         logger.info(f"Processing {len(chunks)} chunks")
0173 |         
0174 |         # Process chunks with concurrency limit
0175 |         semaphore = asyncio.Semaphore(2)
0176 |         
0177 |         async def process_chunk(chunk):
0178 |             async with semaphore:
0179 |                 return await self.triage_service.analyze_vulnerabilities(
0180 |                     chunk.vulnerabilities, language, chunk.id
0181 |                 )
0182 |         
0183 |         # Execute chunk analysis
0184 |         chunk_results = await asyncio.gather(
0185 |             *[process_chunk(chunk) for chunk in chunks],
0186 |             return_exceptions=True
0187 |         )
0188 |         
0189 |         # Filter successful results
0190 |         successful_results = [r for r in chunk_results if not isinstance(r, Exception)]
0191 |         
0192 |         if not successful_results:
0193 |             raise Exception("All chunk analyses failed")
0194 |         
0195 |         # Consolidate results
0196 |         return self._consolidate_chunk_results(successful_results)
0197 |     
0198 |     def _consolidate_chunk_results(self, chunk_results):
0199 |         """Consolidate multiple chunk results into unified result"""
0200 |         
0201 |         all_decisions = []
0202 |         seen_ids = set()
0203 |         
0204 |         # Merge decisions avoiding duplicates from overlap
0205 |         for result in chunk_results:
0206 |             for decision in result.decisions:
0207 |                 if decision.vulnerability_id not in seen_ids:
0208 |                     all_decisions.append(decision)
0209 |                     seen_ids.add(decision.vulnerability_id)
0210 |         
0211 |         # Create consolidated summary
0212 |         summary = f"Consolidated analysis from {len(chunk_results)} chunks. "
0213 |         summary += f"Total decisions: {len(all_decisions)}. "
0214 |         
0215 |         from collections import Counter
0216 |         decision_counts = Counter(d.decision.value for d in all_decisions)
0217 |         summary += f"Distribution: {dict(decision_counts)}"
0218 |         
0219 |         from core.models import TriageResult
0220 |         return TriageResult(
0221 |             decisions=all_decisions,
0222 |             analysis_summary=summary,
0223 |             llm_analysis_time_seconds=sum(r.llm_analysis_time_seconds for r in chunk_results)
0224 |         )
0225 |     
0226 |     def _extract_confirmed_vulnerabilities(self, vulnerabilities: List[Vulnerability], 
0227 |                                          triage_result) -> List[Vulnerability]:
0228 |         """Extract confirmed vulnerabilities from triage result"""
0229 |         
0230 |         from core.models import AnalysisStatus
0231 |         confirmed_ids = {
0232 |             d.vulnerability_id for d in triage_result.decisions 
0233 |             if d.decision == AnalysisStatus.CONFIRMED
0234 |         }
0235 |         
0236 |         return [v for v in vulnerabilities if v.id in confirmed_ids]
0237 |     
0238 |     def _create_analysis_report(self, scan_result: ScanResult, triage_result, 
0239 |                               remediation_plans: List, total_time: float,
0240 |                               force_chunking: bool, disable_chunking: bool,
0241 |                               language: Optional[str], tool_hint: Optional[str]) -> AnalysisReport:
0242 |         """Create comprehensive analysis report"""
0243 |         
0244 |         chunking_used = self._was_chunking_used(scan_result, force_chunking, disable_chunking)
0245 |         
0246 |         return AnalysisReport(
0247 |             scan_result=scan_result,
0248 |             triage_result=triage_result,
0249 |             remediation_plans=remediation_plans,
0250 |             analysis_config={
0251 |                 "language": language,
0252 |                 "tool_hint": tool_hint,
0253 |                 "force_chunking": force_chunking,
0254 |                 "disable_chunking": disable_chunking,
0255 |                 "chunking_used": chunking_used,
0256 |                 "chunks_processed": len(self.chunker.create_chunks(scan_result)) if chunking_used else 0
0257 |             },
0258 |             total_processing_time_seconds=total_time,
0259 |             chunking_enabled=chunking_used
0260 |         )
0261 |     
0262 |     def _create_clean_report(self, scan_result: ScanResult, start_time: float) -> AnalysisReport:
0263 |         """Create report for files with no vulnerabilities"""
0264 |         
0265 |         total_time = asyncio.get_event_loop().time() - start_time
0266 |         
0267 |         return AnalysisReport(
0268 |             scan_result=scan_result,
0269 |             triage_result=None,
0270 |             remediation_plans=[],
0271 |             analysis_config={"no_vulnerabilities_found": True},
0272 |             total_processing_time_seconds=total_time,
0273 |             chunking_enabled=False
0274 |         )
0275 |     
0276 |     def _was_chunking_used(self, scan_result: ScanResult, force_chunking: bool, 
0277 |                           disable_chunking: bool) -> bool:
0278 |         """Determine if chunking was actually used"""
0279 |         
0280 |         if disable_chunking:
0281 |             return False
0282 |         if force_chunking:
0283 |             return True
0284 |         
0285 |         return (
0286 |             self.chunker and 
0287 |             self.chunker.should_chunk(scan_result) and 
0288 |             len(scan_result.vulnerabilities) > 0
0289 |         )
0290 | 
0291 | class CLIUseCase:
0292 |     """Caso de uso específico para CLI con manejo de errores robusto"""
0293 |     
0294 |     def __init__(self, analysis_use_case: AnalysisUseCase):
0295 |         self.analysis_use_case = analysis_use_case
0296 |     
0297 |     async def execute_cli_analysis(self,
0298 |                                  input_file: str,
0299 |                                  output_file: str = "security_report.html",
0300 |                                  language: Optional[str] = None,
0301 |                                  verbose: bool = False,
0302 |                                  disable_llm: bool = False,
0303 |                                  force_chunking: bool = False) -> bool:
0304 |         """Execute analysis from CLI with comprehensive error handling"""
0305 |         
0306 |         try:
0307 |             # Validate input file
0308 |             input_path = Path(input_file)
0309 |             if not input_path.exists():
0310 |                 print(f"❌ Error: Input file not found: {input_file}")
0311 |                 return False
0312 |             
0313 |             print(f"🔍 Analyzing: {input_path.name}")
0314 |             
0315 |             # Execute appropriate analysis
0316 |             if disable_llm:
0317 |                 result = await self.analysis_use_case.execute_basic_analysis(
0318 |                     input_file, output_file
0319 |                 )
0320 |                 print("✅ Basic analysis completed")
0321 |             else:
0322 |                 result = await self.analysis_use_case.execute_full_analysis(
0323 |                     input_file, output_file, language, force_chunking=force_chunking
0324 |                 )
0325 |                 print("✅ Full analysis completed")
0326 |             
0327 |             # Display results
0328 |             self._display_results(result, output_file)
0329 |             return True
0330 |             
0331 |         except KeyboardInterrupt:
0332 |             print("\n🛑 Analysis interrupted by user")
0333 |             return False
0334 |         except Exception as e:
0335 |             print(f"\n❌ Analysis failed: {e}")
0336 |             if verbose:
0337 |                 import traceback
0338 |                 traceback.print_exc()
0339 |             return False
0340 |     
0341 |     def _display_results(self, result: AnalysisReport, output_file: str) -> None:
0342 |         """Display analysis results in CLI format"""
0343 |         
0344 |         print("\n" + "="*50)
0345 |         print("📊 ANALYSIS RESULTS")
0346 |         print("="*50)
0347 |         
0348 |         # Basic statistics
0349 |         scan_result = result.scan_result
0350 |         print(f"📁 File: {scan_result.file_info['filename']}")
0351 |         print(f"🔢 Total vulnerabilities: {len(scan_result.vulnerabilities)}")
0352 |         
0353 |         if scan_result.vulnerabilities:
0354 |             severity_dist = scan_result.severity_distribution
0355 |             for severity, count in severity_dist.items():
0356 |                 if count > 0:
0357 |                     icon = {"CRÍTICA": "🔥", "ALTA": "⚡", "MEDIA": "⚠️", "BAJA": "📝", "INFO": "ℹ️"}
0358 |                     print(f"  {icon.get(severity, '•')} {severity}: {count}")
0359 |         
0360 |         # Triage results
0361 |         if result.triage_result:
0362 |             triage = result.triage_result
0363 |             print(f"\n🤖 LLM Analysis:")
0364 |             print(f"  ✅ Confirmed: {triage.confirmed_count}")
0365 |             print(f"  ❌ False positives: {triage.false_positive_count}")
0366 |             print(f"  🔍 Need review: {triage.needs_review_count}")
0367 |         
0368 |         # Remediation plans
0369 |         if result.remediation_plans:
0370 |             print(f"\n🛠️ Remediation plans: {len(result.remediation_plans)}")
0371 |             priority_counts = {}
0372 |             for plan in result.remediation_plans:
0373 |                 priority_counts[plan.priority_level] = priority_counts.get(plan.priority_level, 0) + 1
0374 |             
0375 |             for priority in ["immediate", "high", "medium", "low"]:
0376 |                 count = priority_counts.get(priority, 0)
0377 |                 if count > 0:
0378 |                     icons = {"immediate": "🚨", "high": "⚡", "medium": "⚠️", "low": "📝"}
0379 |                     print(f"  {icons[priority]} {priority.title()}: {count}")
0380 |         
0381 |         # Performance metrics
0382 |         print(f"\n⏱️ Processing time: {result.total_processing_time_seconds:.2f}s")
0383 |         if result.chunking_enabled:
0384 |             print("🧩 Chunking: Enabled")
0385 |         
0386 |         # Output file
0387 |         if Path(output_file).exists():
0388 |             size_kb = Path(output_file).stat().st_size / 1024
0389 |             print(f"\n📄 Report generated: {output_file} ({size_kb:.1f} KB)")
0390 |         
0391 |         print("\n💡 Open the HTML file in your browser to view the detailed report")
```

---

### core\exceptions.py

**Ruta:** `core\exceptions.py`

```py
0001 | # core/exceptions.py
0002 | """Excepciones específicas del dominio"""
0003 | class SecurityAnalysisError(Exception):
0004 |     """Excepción base del sistema"""
0005 |     def __init__(self, message: str, details: dict = None):
0006 |         self.message = message
0007 |         self.details = details or {}
0008 |         super().__init__(self.message)
0009 | class ValidationError(SecurityAnalysisError):
0010 |     """Error de validación de datos"""
0011 |     pass
0012 | class ParsingError(SecurityAnalysisError):
0013 |     """Error de parsing de vulnerabilidades"""
0014 |     pass
0015 | class LLMError(SecurityAnalysisError):
0016 |     """Error del proveedor LLM"""
0017 |     pass
0018 | class ChunkingError(SecurityAnalysisError):
0019 |     """Error en el proceso de chunking"""
0020 |     pass```

---

### core\models.py

**Ruta:** `core\models.py`

```py
0001 | # core/models.py
0002 | from pydantic import BaseModel, Field, field_validator, computed_field
0003 | from typing import List, Optional, Dict, Any, Union
0004 | from datetime import datetime
0005 | from enum import Enum
0006 | 
0007 | # === ENUMS CONSOLIDADOS ===
0008 | class SeverityLevel(str, Enum):
0009 |     CRITICAL = "CRÍTICA"
0010 |     HIGH = "ALTA"
0011 |     MEDIUM = "MEDIA"
0012 |     LOW = "BAJA"
0013 |     INFO = "INFO"
0014 |     
0015 | class VulnerabilityType(str, Enum):
0016 |     SQL_INJECTION = "SQL Injection"
0017 |     XSS = "Cross-Site Scripting"
0018 |     PATH_TRAVERSAL = "Directory Traversal"
0019 |     CODE_INJECTION = "Code Injection"
0020 |     AUTH_BYPASS = "Authentication Bypass"
0021 |     BROKEN_ACCESS_CONTROL = "Broken Access Control"
0022 |     INSECURE_CRYPTO = "Insecure Cryptography"
0023 |     SENSITIVE_DATA_EXPOSURE = "Sensitive Data Exposure"
0024 |     SECURITY_MISCONFIGURATION = "Security Misconfiguration"
0025 |     OTHER = "Other Security Issue"
0026 | 
0027 | class AnalysisStatus(str, Enum):
0028 |     CONFIRMED = "confirmed"
0029 |     FALSE_POSITIVE = "false_positive"
0030 |     NEEDS_MANUAL_REVIEW = "needs_manual_review"
0031 | 
0032 | class LLMProvider(str, Enum):
0033 |     OPENAI = "openai"
0034 |     WATSONX = "watsonx"
0035 | 
0036 | class ChunkingStrategy(str, Enum):
0037 |     NO_CHUNKING = "no_chunking"
0038 |     BY_COUNT = "by_vulnerability_count"
0039 |     BY_SIZE = "by_size"
0040 |     ADAPTIVE = "adaptive"
0041 | 
0042 | class Vulnerability(BaseModel):
0043 |     """Modelo central optimizado de vulnerabilidad"""
0044 |     id: str = Field(..., description="ID único de la vulnerabilidad")
0045 |     type: VulnerabilityType
0046 |     severity: SeverityLevel
0047 |     title: str = Field(..., min_length=1)
0048 |     description: str = Field(..., min_length=10)
0049 |     
0050 |     # Ubicación
0051 |     file_path: str = Field(..., min_length=1)
0052 |     line_number: int = Field(ge=0, default=0)
0053 |     code_snippet: Optional[str] = None
0054 |     
0055 |     # Metadatos de seguridad
0056 |     cwe_id: Optional[str] = Field(None, pattern=r"^CWE-\d+$")
0057 |     confidence_level: Optional[float] = Field(None, ge=0.0, le=1.0)
0058 |     
0059 |     # Origen
0060 |     source_tool: Optional[str] = None
0061 |     rule_id: Optional[str] = None
0062 |     
0063 |     # Contexto adicional
0064 |     impact_description: Optional[str] = None
0065 |     remediation_advice: Optional[str] = None
0066 |     
0067 |     # Metadatos
0068 |     created_at: datetime = Field(default_factory=datetime.now)
0069 |     meta: Dict[str, Any] = Field(default_factory=dict)
0070 |     
0071 |     @field_validator('severity', mode='before')
0072 |     @classmethod
0073 |     def normalize_severity(cls, v):
0074 |         """Normalización inteligente de severidad"""
0075 |         if isinstance(v, str):
0076 |             mapping = {
0077 |                 'CRITICAL': SeverityLevel.CRITICAL, 'HIGH': SeverityLevel.HIGH,
0078 |                 'MEDIUM': SeverityLevel.MEDIUM, 'LOW': SeverityLevel.LOW,
0079 |                 'INFO': SeverityLevel.INFO, 'BLOCKER': SeverityLevel.CRITICAL,
0080 |                 'MAJOR': SeverityLevel.HIGH, 'MINOR': SeverityLevel.MEDIUM,
0081 |                 'CRÍTICA': SeverityLevel.CRITICAL, 'ALTA': SeverityLevel.HIGH,
0082 |                 'MEDIA': SeverityLevel.MEDIUM, 'BAJA': SeverityLevel.LOW
0083 |             }
0084 |             return mapping.get(v.upper(), SeverityLevel.MEDIUM)
0085 |         return v
0086 |     
0087 |     @computed_field
0088 |     @property
0089 |     def priority_score(self) -> int:
0090 |         """Score para ordenamiento por prioridad"""
0091 |         base_score = {
0092 |             SeverityLevel.CRITICAL: 100, SeverityLevel.HIGH: 80,
0093 |             SeverityLevel.MEDIUM: 60, SeverityLevel.LOW: 40, SeverityLevel.INFO: 20
0094 |         }[self.severity]
0095 |         
0096 |         # Ajustar por confianza
0097 |         if self.confidence_level:
0098 |             base_score = int(base_score * self.confidence_level)
0099 |         
0100 |         return base_score
0101 |     
0102 |     @computed_field
0103 |     @property
0104 |     def is_high_priority(self) -> bool:
0105 |         """Determinar si es alta prioridad"""
0106 |         return self.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
0107 | 
0108 | class TriageDecision(BaseModel):
0109 |     """Decisión de triaje optimizada"""
0110 |     vulnerability_id: str
0111 |     decision: AnalysisStatus
0112 |     confidence_score: float = Field(ge=0.0, le=1.0)
0113 |     reasoning: str = Field(..., min_length=10)
0114 |     llm_model_used: str
0115 |     analyzed_at: datetime = Field(default_factory=datetime.now)
0116 | 
0117 | class TriageResult(BaseModel):
0118 |     """Resultado de triaje con validación automática"""
0119 |     decisions: List[TriageDecision] = Field(default_factory=list)
0120 |     analysis_summary: str
0121 |     llm_analysis_time_seconds: float = Field(ge=0.0)
0122 |     
0123 |     @computed_field
0124 |     @property
0125 |     def total_analyzed(self) -> int:
0126 |         return len(self.decisions)
0127 |     
0128 |     @computed_field
0129 |     @property
0130 |     def confirmed_count(self) -> int:
0131 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.CONFIRMED)
0132 |     
0133 |     @computed_field
0134 |     @property
0135 |     def false_positive_count(self) -> int:
0136 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.FALSE_POSITIVE)
0137 |     
0138 |     @computed_field
0139 |     @property
0140 |     def needs_review_count(self) -> int:
0141 |         return sum(1 for d in self.decisions if d.decision == AnalysisStatus.NEEDS_MANUAL_REVIEW)
0142 | 
0143 | class RemediationStep(BaseModel):
0144 |     """Paso de remediación optimizado"""
0145 |     step_number: int = Field(ge=1)
0146 |     title: str = Field(..., min_length=1)
0147 |     description: str = Field(..., min_length=10)
0148 |     code_example: Optional[str] = None
0149 |     estimated_minutes: Optional[int] = Field(None, ge=1)
0150 |     difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
0151 |     tools_required: List[str] = Field(default_factory=list)
0152 | 
0153 | class RemediationPlan(BaseModel):
0154 |     """Plan de remediación consolidado"""
0155 |     vulnerability_id: str
0156 |     vulnerability_type: VulnerabilityType
0157 |     priority_level: str = Field(..., pattern=r"^(immediate|high|medium|low)$")
0158 |     steps: List[RemediationStep] = Field(..., min_length=1)
0159 |     risk_if_not_fixed: str
0160 |     references: List[str] = Field(default_factory=list)
0161 |     total_estimated_hours: Optional[float] = Field(None, ge=0.1)
0162 |     complexity_score: float = Field(ge=0.0, le=10.0, default=5.0)
0163 |     llm_model_used: str
0164 |     created_at: datetime = Field(default_factory=datetime.now)
0165 | 
0166 | class ScanResult(BaseModel):
0167 |     """Resultado de escaneo optimizado"""
0168 |     file_info: Dict[str, Any]
0169 |     vulnerabilities: List[Vulnerability] = Field(default_factory=list)
0170 |     scan_timestamp: datetime = Field(default_factory=datetime.now)
0171 |     scan_duration_seconds: float = Field(ge=0.0, default=0.0)
0172 |     language_detected: Optional[str] = None
0173 |     
0174 |     @computed_field
0175 |     @property
0176 |     def vulnerability_count(self) -> int:
0177 |         return len(self.vulnerabilities)
0178 |     
0179 |     @computed_field
0180 |     @property
0181 |     def severity_distribution(self) -> Dict[str, int]:
0182 |         from collections import Counter
0183 |         return dict(Counter(v.severity.value for v in self.vulnerabilities))
0184 |     
0185 |     @computed_field
0186 |     @property
0187 |     def high_priority_count(self) -> int:
0188 |         return sum(1 for v in self.vulnerabilities if v.is_high_priority)
0189 | 
0190 | class AnalysisReport(BaseModel):
0191 |     """Reporte de análisis completo"""
0192 |     report_id: str = Field(default_factory=lambda: f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
0193 |     generated_at: datetime = Field(default_factory=datetime.now)
0194 |     scan_result: ScanResult
0195 |     triage_result: Optional[TriageResult] = None
0196 |     remediation_plans: List[RemediationPlan] = Field(default_factory=list)
0197 |     analysis_config: Dict[str, Any] = Field(default_factory=dict)
0198 |     total_processing_time_seconds: float = Field(ge=0.0)
0199 |     chunking_enabled: bool = False
0200 |     
0201 |     @computed_field
0202 |     @property
0203 |     def executive_summary(self) -> Dict[str, Any]:
0204 |         """Resumen ejecutivo automático"""
0205 |         return {
0206 |             "total_vulnerabilities": self.scan_result.vulnerability_count,
0207 |             "high_priority_count": self.scan_result.high_priority_count,
0208 |             "severity_distribution": self.scan_result.severity_distribution,
0209 |             "processing_time": f"{self.total_processing_time_seconds:.2f}s",
0210 |             "confirmed_vulnerabilities": self.triage_result.confirmed_count if self.triage_result else 0,
0211 |             "remediation_plans_generated": len(self.remediation_plans)
0212 |         }
```

---

### core\services\remediation.py

**Ruta:** `core\services\remediation.py`

```py
0001 | # core/services/remediation.py
0002 | import logging
0003 | import asyncio
0004 | from typing import List, Optional, Dict
0005 | from collections import defaultdict
0006 | 
0007 | from ..models import Vulnerability, RemediationPlan, RemediationStep, VulnerabilityType
0008 | from ..exceptions import LLMError
0009 | from infrastructure.llm.client import LLMClient
0010 | from shared.metrics import MetricsCollector
0011 | 
0012 | logger = logging.getLogger(__name__)
0013 | 
0014 | class RemediationService:
0015 |     """Servicio de remediación optimizado sin duplicación"""
0016 |     
0017 |     def __init__(self, llm_client: LLMClient, metrics: Optional[MetricsCollector] = None):
0018 |         self.llm_client = llm_client
0019 |         self.metrics = metrics
0020 |     
0021 |     async def generate_remediation_plans(self, 
0022 |                                        confirmed_vulnerabilities: List[Vulnerability],
0023 |                                        language: Optional[str] = None) -> List[RemediationPlan]:
0024 |         """Generate remediation plans for confirmed vulnerabilities"""
0025 |         
0026 |         if not confirmed_vulnerabilities:
0027 |             logger.info("No confirmed vulnerabilities - no plans needed")
0028 |             return []
0029 |         
0030 |         logger.info(f"Generating remediation plans for {len(confirmed_vulnerabilities)} vulnerabilities")
0031 |         
0032 |         # Group by type for efficient batch processing
0033 |         grouped_vulns = self._group_by_type(confirmed_vulnerabilities)
0034 |         
0035 |         all_plans = []
0036 |         for vuln_type, vulns in grouped_vulns.items():
0037 |             try:
0038 |                 plans = await self._generate_plans_for_type(vuln_type, vulns, language)
0039 |                 all_plans.extend(plans)
0040 |             except Exception as e:
0041 |                 logger.error(f"Failed to generate plans for {vuln_type}: {e}")
0042 |                 # Add fallback plans
0043 |                 fallback_plans = self._create_fallback_plans(vulns)
0044 |                 all_plans.extend(fallback_plans)
0045 |         
0046 |         # Sort by priority
0047 |         prioritized_plans = self._prioritize_plans(all_plans)
0048 |         
0049 |         logger.info(f"Generated {len(prioritized_plans)} remediation plans")
0050 |         return prioritized_plans
0051 |     
0052 |     def _group_by_type(self, vulnerabilities: List[Vulnerability]) -> Dict[VulnerabilityType, List[Vulnerability]]:
0053 |         """Group vulnerabilities by type for batch processing"""
0054 |         groups = defaultdict(list)
0055 |         for vuln in vulnerabilities:
0056 |             groups[vuln.type].append(vuln)
0057 |         return dict(groups)
0058 |     
0059 |     async def _generate_plans_for_type(self, vuln_type: VulnerabilityType, 
0060 |                                      vulnerabilities: List[Vulnerability],
0061 |                                      language: Optional[str]) -> List[RemediationPlan]:
0062 |         """Generate plans for specific vulnerability type"""
0063 |         
0064 |         start_time = asyncio.get_event_loop().time()
0065 |         
0066 |         try:
0067 |             # Prepare remediation request
0068 |             request = self._prepare_remediation_request(vuln_type, vulnerabilities, language)
0069 |             
0070 |             # Get LLM response
0071 |             response = await self.llm_client.generate_remediation_plan(request)
0072 |             
0073 |             # Create individual plans from response
0074 |             plans = self._create_individual_plans(response, vulnerabilities)
0075 |             
0076 |             # Record metrics
0077 |             if self.metrics:
0078 |                 generation_time = asyncio.get_event_loop().time() - start_time
0079 |                 self.metrics.record_remediation_generation(
0080 |                     vuln_type.value, len(vulnerabilities), generation_time, True
0081 |                 )
0082 |             
0083 |             return plans
0084 |         
0085 |         except Exception as e:
0086 |             if self.metrics:
0087 |                 generation_time = asyncio.get_event_loop().time() - start_time
0088 |                 self.metrics.record_remediation_generation(
0089 |                     vuln_type.value, len(vulnerabilities), generation_time, False, str(e)
0090 |                 )
0091 |             raise
0092 |     
0093 |     def _prepare_remediation_request(self, vuln_type: VulnerabilityType, 
0094 |                                    vulnerabilities: List[Vulnerability],
0095 |                                    language: Optional[str]) -> str:
0096 |         """Prepare structured remediation request"""
0097 |         
0098 |         header = f"# REMEDIATION PLAN REQUEST\n"
0099 |         header += f"Vulnerability Type: {vuln_type.value}\n"
0100 |         header += f"Language: {language or 'Unknown'}\n"
0101 |         header += f"Count: {len(vulnerabilities)}\n\n"
0102 |         
0103 |         vuln_details = []
0104 |         for i, vuln in enumerate(vulnerabilities, 1):
0105 |             detail = f"""## VULNERABILITY {i} - {vuln.id}
0106 | - Severity: {vuln.severity.value}
0107 | - File: {vuln.file_path}:{vuln.line_number}
0108 | - Title: {vuln.title}
0109 | - Description: {vuln.description}"""
0110 |             
0111 |             if vuln.code_snippet:
0112 |                 detail += f"\n- Code Context:\n{vuln.code_snippet[:500]}"
0113 |             
0114 |             vuln_details.append(detail)
0115 |         
0116 |         return header + "\n\n".join(vuln_details)
0117 |     
0118 |     def _create_individual_plans(self, template_plan: RemediationPlan, 
0119 |                                vulnerabilities: List[Vulnerability]) -> List[RemediationPlan]:
0120 |         """Create individual plans from template"""
0121 |         
0122 |         individual_plans = []
0123 |         for vuln in vulnerabilities:
0124 |             # Customize plan for specific vulnerability
0125 |             customized_plan = RemediationPlan(
0126 |                 vulnerability_id=vuln.id,
0127 |                 vulnerability_type=vuln.type,
0128 |                 priority_level=self._calculate_priority(vuln),
0129 |                 steps=self._customize_steps(template_plan.steps, vuln),
0130 |                 risk_if_not_fixed=template_plan.risk_if_not_fixed,
0131 |                 references=template_plan.references,
0132 |                 total_estimated_hours=template_plan.total_estimated_hours,
0133 |                 complexity_score=self._adjust_complexity(template_plan.complexity_score, vuln),
0134 |                 llm_model_used=template_plan.llm_model_used
0135 |             )
0136 |             individual_plans.append(customized_plan)
0137 |         
0138 |         return individual_plans
0139 |     
0140 |     def _calculate_priority(self, vulnerability: Vulnerability) -> str:
0141 |         """Calculate priority level based on vulnerability characteristics"""
0142 |         priority_map = {
0143 |             "CRÍTICA": "immediate",
0144 |             "ALTA": "high", 
0145 |             "MEDIA": "medium",
0146 |             "BAJA": "low",
0147 |             "INFO": "low"
0148 |         }
0149 |         return priority_map.get(vulnerability.severity.value, "medium")
0150 |     
0151 |     def _customize_steps(self, template_steps: List[RemediationStep], 
0152 |                         vulnerability: Vulnerability) -> List[RemediationStep]:
0153 |         """Customize remediation steps for specific vulnerability"""
0154 |         
0155 |         customized_steps = []
0156 |         for step in template_steps:
0157 |             # Format step content with vulnerability specifics
0158 |             customized_step = RemediationStep(
0159 |                 step_number=step.step_number,
0160 |                 title=step.title.format(
0161 |                     file=vulnerability.file_path,
0162 |                     line=vulnerability.line_number,
0163 |                     vuln_type=vulnerability.type.value
0164 |                 ),
0165 |                 description=step.description.format(
0166 |                     vulnerability_id=vulnerability.id,
0167 |                     file_path=vulnerability.file_path,
0168 |                     severity=vulnerability.severity.value
0169 |                 ),
0170 |                 code_example=step.code_example,
0171 |                 estimated_minutes=step.estimated_minutes,
0172 |                 difficulty=step.difficulty,
0173 |                 tools_required=step.tools_required
0174 |             )
0175 |             customized_steps.append(customized_step)
0176 |         
0177 |         return customized_steps
0178 |     
0179 |     def _adjust_complexity(self, base_complexity: float, vulnerability: Vulnerability) -> float:
0180 |         """Adjust complexity based on vulnerability characteristics"""
0181 |         
0182 |         # Adjust based on severity
0183 |         severity_multipliers = {
0184 |             "CRÍTICA": 1.2,
0185 |             "ALTA": 1.1,
0186 |             "MEDIA": 1.0,
0187 |             "BAJA": 0.9,
0188 |             "INFO": 0.8
0189 |         }
0190 |         
0191 |         multiplier = severity_multipliers.get(vulnerability.severity.value, 1.0)
0192 |         adjusted = base_complexity * multiplier
0193 |         
0194 |         return min(max(adjusted, 1.0), 10.0)  # Clamp to 1-10 range
0195 |     
0196 |     def _create_fallback_plans(self, vulnerabilities: List[Vulnerability]) -> List[RemediationPlan]:
0197 |         """Create basic fallback plans when LLM fails"""
0198 |         
0199 |         logger.warning("Creating fallback remediation plans")
0200 |         
0201 |         fallback_plans = []
0202 |         for vuln in vulnerabilities:
0203 |             basic_steps = [
0204 |                 RemediationStep(
0205 |                     step_number=1,
0206 |                     title="Manual Security Review",
0207 |                     description=f"Manually review {vuln.type.value} vulnerability in {vuln.file_path}",
0208 |                     estimated_minutes=30,
0209 |                     difficulty="medium"
0210 |                 ),
0211 |                 RemediationStep(
0212 |                     step_number=2,
0213 |                     title="Research Best Practices", 
0214 |                     description=f"Research security best practices for {vuln.type.value}",
0215 |                     estimated_minutes=15,
0216 |                     difficulty="easy"
0217 |                 ),
0218 |                 RemediationStep(
0219 |                     step_number=3,
0220 |                     title="Implement Fix",
0221 |                     description="Apply appropriate security fix based on research",
0222 |                     estimated_minutes=120,
0223 |                     difficulty="hard"
0224 |                 ),
0225 |                 RemediationStep(
0226 |                     step_number=4,
0227 |                     title="Validate Fix",
0228 |                     description="Test that vulnerability has been properly addressed",
0229 |                     estimated_minutes=30,
0230 |                     difficulty="medium"
0231 |                 )
0232 |             ]
0233 |             
0234 |             plan = RemediationPlan(
0235 |                 vulnerability_id=vuln.id,
0236 |                 vulnerability_type=vuln.type,
0237 |                 priority_level=self._calculate_priority(vuln),
0238 |                 steps=basic_steps,
0239 |                 risk_if_not_fixed=f"Security risk associated with {vuln.type.value}",
0240 |                 total_estimated_hours=3.25,
0241 |                 complexity_score=5.0,
0242 |                 llm_model_used="fallback"
0243 |             )
0244 |             
0245 |             fallback_plans.append(plan)
0246 |         
0247 |         return fallback_plans
0248 |     
0249 |     def _prioritize_plans(self, plans: List[RemediationPlan]) -> List[RemediationPlan]:
0250 |         """Sort plans by priority and complexity"""
0251 |         
0252 |         priority_weights = {"immediate": 4, "high": 3, "medium": 2, "low": 1}
0253 |         
0254 |         return sorted(plans, key=lambda p: (
0255 |             priority_weights.get(p.priority_level, 0),
0256 |             -p.complexity_score  # Lower complexity = higher priority
0257 |         ), reverse=True)
```

---

### core\services\reporter.py

**Ruta:** `core\services\reporter.py`

```py
0001 | # core/services/reporter.py
0002 | import logging
0003 | from pathlib import Path
0004 | from typing import Optional
0005 | 
0006 | from ..models import AnalysisReport
0007 | from adapters.output.html_generator import OptimizedHTMLGenerator
0008 | from shared.metrics import MetricsCollector
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | class ReporterService:
0013 |     """Servicio de reportes simplificado y optimizado"""
0014 |     
0015 |     def __init__(self, 
0016 |                  html_generator: Optional[OptimizedHTMLGenerator] = None,
0017 |                  metrics: Optional[MetricsCollector] = None):
0018 |         self.html_generator = html_generator or OptimizedHTMLGenerator()
0019 |         self.metrics = metrics
0020 |     
0021 |     async def generate_html_report(self, 
0022 |                                  analysis_report: AnalysisReport,
0023 |                                  output_file: str) -> bool:
0024 |         """Generate HTML report with metrics tracking"""
0025 |         
0026 |         try:
0027 |             logger.info(f"Generating HTML report: {output_file}")
0028 |             
0029 |             success = self.html_generator.generate_report(analysis_report, output_file)
0030 |             
0031 |             if success:
0032 |                 file_size = Path(output_file).stat().st_size
0033 |                 if self.metrics:
0034 |                     self.metrics.record_report_generation(
0035 |                         "html", file_size, len(analysis_report.scan_result.vulnerabilities), True
0036 |                     )
0037 |                 logger.info(f"Report generated successfully: {output_file} ({file_size:,} bytes)")
0038 |             else:
0039 |                 if self.metrics:
0040 |                     self.metrics.record_report_generation("html", success=False)
0041 |                 logger.error(f"Failed to generate report: {output_file}")
0042 |             
0043 |             return success
0044 |             
0045 |         except Exception as e:
0046 |             if self.metrics:
0047 |                 self.metrics.record_report_generation("html", success=False, error=str(e))
0048 |             logger.error(f"Report generation failed: {e}")
0049 |             return False
```

---

### core\services\scanner.py

**Ruta:** `core\services\scanner.py`

```py
0001 | # core/services/scanner.py
0002 | import json
0003 | import logging
0004 | from pathlib import Path
0005 | from typing import Optional, Dict, Any, List
0006 | from datetime import datetime
0007 | 
0008 | from ..models import ScanResult, Vulnerability, VulnerabilityType, SeverityLevel
0009 | from ..exceptions import ValidationError, ParsingError
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class UnifiedVulnerabilityParser:
0014 |     """Parser unificado que maneja múltiples formatos - CORREGIDO"""
0015 |     
0016 |     def parse(self, data: Dict[str, Any], tool_hint: Optional[str] = None) -> List[Vulnerability]:
0017 |         """Parse vulnerabilities from any supported format"""
0018 |         
0019 |         # Extract findings from different structures
0020 |         findings = self._extract_findings(data)
0021 |         if not findings:
0022 |             logger.warning("No findings found in data")
0023 |             return []
0024 |         
0025 |         # Determine parser strategy
0026 |         parser_strategy = self._detect_format(findings[0], tool_hint)
0027 |         logger.info(f"Using parser strategy: {parser_strategy}")
0028 |         
0029 |         vulnerabilities = []
0030 |         for i, finding in enumerate(findings):
0031 |             try:
0032 |                 vuln = self._parse_finding(finding, i + 1, parser_strategy)
0033 |                 if vuln:
0034 |                     vulnerabilities.append(vuln)
0035 |             except Exception as e:
0036 |                 logger.warning(f"Failed to parse finding {i+1}: {e}")
0037 |         
0038 |         logger.info(f"Parsed {len(vulnerabilities)} vulnerabilities")
0039 |         return vulnerabilities
0040 |     
0041 |     def _extract_findings(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
0042 |         """Extract findings from various container structures"""
0043 |         
0044 |         # Direct list
0045 |         if isinstance(data, list):
0046 |             return data
0047 |         
0048 |         # Single object
0049 |         if isinstance(data, dict) and 'rule_id' in data:
0050 |             return [data]
0051 |         
0052 |         # Nested containers
0053 |         if isinstance(data, dict):
0054 |             for key in ['findings', 'vulnerabilities', 'issues', 'results', 'scan_results']:
0055 |                 if key in data and isinstance(data[key], list):
0056 |                     return data[key]
0057 |         
0058 |         return []
0059 |     
0060 |     def _detect_format(self, sample_finding: Dict[str, Any], tool_hint: Optional[str]) -> str:
0061 |         """Detect the format of findings"""
0062 |         
0063 |         if tool_hint:
0064 |             if 'abap' in tool_hint.lower():
0065 |                 return 'abap'
0066 |         
0067 |         # Auto-detection based on structure
0068 |         if 'rule_id' in sample_finding and str(sample_finding.get('rule_id', '')).startswith('abap-'):
0069 |             return 'abap'
0070 |         
0071 |         if 'check_id' in sample_finding:
0072 |             return 'semgrep'
0073 |         
0074 |         if 'ruleId' in sample_finding:
0075 |             return 'sonarqube'
0076 |         
0077 |         return 'generic'
0078 |     
0079 |     def _parse_finding(self, finding: Dict[str, Any], index: int, strategy: str) -> Optional[Vulnerability]:
0080 |         """Parse individual finding based on strategy"""
0081 |         
0082 |         try:
0083 |             if strategy == 'abap':
0084 |                 return self._parse_abap_finding(finding, index)
0085 |             else:
0086 |                 return self._parse_generic_finding(finding, index)
0087 |         
0088 |         except Exception as e:
0089 |             logger.error(f"Failed to parse finding {index}: {e}")
0090 |             return None
0091 |     
0092 |     def _parse_abap_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0093 |         """Parse ABAP-specific finding"""
0094 |         
0095 |         location = finding.get('location', {})
0096 |         
0097 |         return Vulnerability(
0098 |             id=finding.get('rule_id', f'ABAP-{index}'),
0099 |             type=self._normalize_vulnerability_type(finding.get('title', 'Unknown')),
0100 |             severity=self._normalize_severity(finding.get('severity', 'MEDIUM')),
0101 |             title=str(finding.get('title', 'ABAP Security Issue')).replace(' Vulnerability', '').strip(),
0102 |             description=finding.get('message', 'No description provided'),
0103 |             file_path=location.get('file', 'Unknown file'),
0104 |             line_number=int(location.get('line', 0)) if location.get('line') else 0,
0105 |             code_snippet=self._extract_code_context(location),
0106 |             cwe_id=self._normalize_cwe(finding.get('cwe')),
0107 |             source_tool='ABAP Security Scanner',
0108 |             rule_id=finding.get('rule_id'),
0109 |             confidence_level=self._extract_confidence(finding),
0110 |             remediation_advice=finding.get('remediation'),
0111 |             meta={
0112 |                 'original_finding': finding,
0113 |                 'parser_strategy': 'abap',
0114 |                 'parser_version': '3.0'
0115 |             }
0116 |         )
0117 |     
0118 |     def _parse_generic_finding(self, finding: Dict[str, Any], index: int) -> Vulnerability:
0119 |         """Parse generic finding format"""
0120 |         
0121 |         return Vulnerability(
0122 |             id=finding.get('id', f'GENERIC-{index}'),
0123 |             type=VulnerabilityType.OTHER,
0124 |             severity=SeverityLevel.MEDIUM,
0125 |             title=str(finding.get('title', finding.get('message', 'Security Issue')))[:100],
0126 |             description=finding.get('description', finding.get('message', 'No description')),
0127 |             file_path=finding.get('file', finding.get('path', 'Unknown')),
0128 |             line_number=finding.get('line', 0),
0129 |             source_tool=finding.get('tool', 'Generic Scanner'),
0130 |             meta={'original_finding': finding, 'parser_strategy': 'generic'}
0131 |         )
0132 |     
0133 |     def _normalize_vulnerability_type(self, title: str) -> VulnerabilityType:
0134 |         """Smart vulnerability type mapping"""
0135 |         if not title:
0136 |             return VulnerabilityType.OTHER
0137 |             
0138 |         title_lower = str(title).lower()
0139 |         
0140 |         mappings = {
0141 |             'sql injection': VulnerabilityType.SQL_INJECTION,
0142 |             'directory traversal': VulnerabilityType.PATH_TRAVERSAL,
0143 |             'path traversal': VulnerabilityType.PATH_TRAVERSAL,
0144 |             'code injection': VulnerabilityType.CODE_INJECTION,
0145 |             'cross-site scripting': VulnerabilityType.XSS,
0146 |             'xss': VulnerabilityType.XSS,
0147 |             'authentication': VulnerabilityType.AUTH_BYPASS,
0148 |             'authorization': VulnerabilityType.BROKEN_ACCESS_CONTROL,
0149 |             'crypto': VulnerabilityType.INSECURE_CRYPTO,
0150 |         }
0151 |         
0152 |         for pattern, vuln_type in mappings.items():
0153 |             if pattern in title_lower:
0154 |                 return vuln_type
0155 |         
0156 |         return VulnerabilityType.OTHER
0157 |     
0158 |     def _normalize_severity(self, severity: str) -> SeverityLevel:
0159 |         """Normalize severity levels"""
0160 |         if not severity:
0161 |             return SeverityLevel.MEDIUM
0162 |         
0163 |         severity_upper = str(severity).upper().strip()
0164 |         mappings = {
0165 |             'CRITICAL': SeverityLevel.CRITICAL,
0166 |             'HIGH': SeverityLevel.HIGH,
0167 |             'MEDIUM': SeverityLevel.MEDIUM,
0168 |             'LOW': SeverityLevel.LOW,
0169 |             'INFO': SeverityLevel.INFO,
0170 |             'CRÍTICA': SeverityLevel.CRITICAL,
0171 |             'ALTA': SeverityLevel.HIGH,
0172 |             'MEDIA': SeverityLevel.MEDIUM,
0173 |             'BAJA': SeverityLevel.LOW,
0174 |         }
0175 |         
0176 |         return mappings.get(severity_upper, SeverityLevel.MEDIUM)
0177 |     
0178 |     def _extract_code_context(self, location: Dict[str, Any]) -> Optional[str]:
0179 |         """Extract and format code context"""
0180 |         context = location.get('context', [])
0181 |         line_content = location.get('line_content', '')
0182 |         
0183 |         if isinstance(context, list) and context:
0184 |             return '\n'.join(f"{i+1:3d} | {line}" for i, line in enumerate(context) if line)
0185 |         elif line_content:
0186 |             return f">>> {str(line_content).strip()}"
0187 |         
0188 |         return None
0189 |     
0190 |     def _normalize_cwe(self, cwe: Optional[str]) -> Optional[str]:
0191 |         """Normalize CWE ID format"""
0192 |         if not cwe:
0193 |             return None
0194 |         
0195 |         cwe_str = str(cwe).strip()
0196 |         if cwe_str.isdigit():
0197 |             return f"CWE-{cwe_str}"
0198 |         elif cwe_str.startswith('CWE-'):
0199 |             return cwe_str
0200 |         
0201 |         return None
0202 |     
0203 |     def _extract_confidence(self, finding: Dict[str, Any]) -> Optional[float]:
0204 |         """Extract confidence level"""
0205 |         confidence = finding.get('confidence')
0206 |         if confidence:
0207 |             try:
0208 |                 if isinstance(confidence, str) and '%' in confidence:
0209 |                     return float(confidence.replace('%', '')) / 100.0
0210 |                 return float(confidence)
0211 |             except (ValueError, TypeError):
0212 |                 pass
0213 |         return None
0214 | 
0215 | class ScannerService:
0216 |     """Servicio de escaneo optimizado y consolidado - CORREGIDO"""
0217 |     
0218 |     def __init__(self, cache=None):  # Tipo Optional removido para evitar import circular
0219 |         self.parser = UnifiedVulnerabilityParser()
0220 |         self.cache = cache
0221 |     
0222 |     async def scan_file(self, 
0223 |                        file_path: str,
0224 |                        language: Optional[str] = None,
0225 |                        tool_hint: Optional[str] = None) -> ScanResult:
0226 |         """Scan and normalize vulnerability file"""
0227 |         
0228 |         logger.info(f"Scanning file: {file_path}")
0229 |         start_time = datetime.now()
0230 |         
0231 |         # Validate file
0232 |         self._validate_file(file_path)
0233 |         
0234 |         # Check cache
0235 |         if self.cache:
0236 |             cached_result = await self._check_cache(file_path, language, tool_hint)
0237 |             if cached_result:
0238 |                 logger.info("Using cached scan result")
0239 |                 return cached_result
0240 |         
0241 |         # Load and parse
0242 |         raw_data = self._load_file(file_path)
0243 |         vulnerabilities = self.parser.parse(raw_data, tool_hint)
0244 |         
0245 |         # Create result
0246 |         file_info = {
0247 |             'filename': Path(file_path).name,
0248 |             'full_path': str(Path(file_path).absolute()),
0249 |             'size_bytes': Path(file_path).stat().st_size,
0250 |             'language': language,
0251 |             'tool_hint': tool_hint
0252 |         }
0253 |         
0254 |         scan_duration = (datetime.now() - start_time).total_seconds()
0255 |         
0256 |         scan_result = ScanResult(
0257 |             file_info=file_info,
0258 |             vulnerabilities=vulnerabilities,
0259 |             scan_duration_seconds=scan_duration,
0260 |             language_detected=language
0261 |         )
0262 |         
0263 |         # Cache result
0264 |         if self.cache:
0265 |             await self._save_to_cache(file_path, scan_result, language, tool_hint)
0266 |         
0267 |         logger.info(f"Scan completed: {len(vulnerabilities)} vulnerabilities in {scan_duration:.2f}s")
0268 |         return scan_result
0269 |     
0270 |     def _validate_file(self, file_path: str) -> None:
0271 |         """Validate input file"""
0272 |         path = Path(file_path)
0273 |         
0274 |         if not path.exists():
0275 |             raise ValidationError(f"File not found: {file_path}")
0276 |         
0277 |         if path.suffix.lower() not in ['.json']:
0278 |             raise ValidationError(f"Unsupported file type: {path.suffix}")
0279 |         
0280 |         if path.stat().st_size > 100 * 1024 * 1024:  # 100MB
0281 |             raise ValidationError(f"File too large: {path.stat().st_size / 1024 / 1024:.1f}MB")
0282 |     
0283 |     def _load_file(self, file_path: str) -> Dict[str, Any]:
0284 |         """Load and parse JSON file"""
0285 |         try:
0286 |             with open(file_path, 'r', encoding='utf-8') as f:
0287 |                 return json.load(f)
0288 |         except json.JSONDecodeError as e:
0289 |             raise ParsingError(f"Invalid JSON in {file_path}: {e}")
0290 |         except Exception as e:
0291 |             raise ParsingError(f"Error reading {file_path}: {e}")
0292 |     
0293 |     async def _check_cache(self, file_path: str, language: Optional[str], tool_hint: Optional[str]):
0294 |         """Check cache for existing result"""
0295 |         if not self.cache:
0296 |             return None
0297 |         
0298 |         try:
0299 |             with open(file_path, 'r', encoding='utf-8') as f:
0300 |                 content = f.read()
0301 |             
0302 |             cached_data = self.cache.get(content, language, tool_hint)
0303 |             if cached_data:
0304 |                 return ScanResult(**cached_data)
0305 |         except Exception as e:
0306 |             logger.warning(f"Cache check failed: {e}")
0307 |         
0308 |         return None
0309 |     
0310 |     async def _save_to_cache(self, file_path: str, scan_result: ScanResult, 
0311 |                            language: Optional[str], tool_hint: Optional[str]) -> None:
0312 |         """Save result to cache"""
0313 |         if not self.cache:
0314 |             return
0315 |         
0316 |         try:
0317 |             with open(file_path, 'r', encoding='utf-8') as f:
0318 |                 content = f.read()
0319 |             
0320 |             # Usar model_dump en lugar de dict()
0321 |             self.cache.put(content, scan_result.model_dump(), language, tool_hint)
0322 |             logger.debug("Scan result cached")
0323 |         except Exception as e:
0324 |             logger.warning(f"Cache save failed: {e}")
```

---

### core\services\triage.py

**Ruta:** `core\services\triage.py`

```py
0001 | # core/services/triage.py
0002 | import logging
0003 | import asyncio
0004 | from typing import List, Optional
0005 | 
0006 | from ..models import Vulnerability, TriageResult, TriageDecision, AnalysisStatus
0007 | from ..exceptions import LLMError
0008 | from infrastructure.llm.client import LLMClient
0009 | from shared.metrics import MetricsCollector
0010 | 
0011 | logger = logging.getLogger(__name__)
0012 | 
0013 | class TriageService:
0014 |     """Servicio de triaje optimizado con fallbacks inteligentes"""
0015 |     
0016 |     def __init__(self, llm_client: LLMClient, metrics: Optional[MetricsCollector] = None):
0017 |         self.llm_client = llm_client
0018 |         self.metrics = metrics
0019 |     
0020 |     async def analyze_vulnerabilities(self, 
0021 |                                     vulnerabilities: List[Vulnerability],
0022 |                                     language: Optional[str] = None,
0023 |                                     chunk_id: Optional[int] = None) -> TriageResult:
0024 |         """Analyze vulnerabilities with intelligent triage"""
0025 |         
0026 |         if not vulnerabilities:
0027 |             return self._create_empty_result()
0028 |         
0029 |         start_time = asyncio.get_event_loop().time()
0030 |         
0031 |         try:
0032 |             logger.info(f"Starting triage analysis for {len(vulnerabilities)} vulnerabilities")
0033 |             
0034 |             # Prepare analysis request
0035 |             analysis_request = self._prepare_analysis_request(vulnerabilities, language, chunk_id)
0036 |             
0037 |             # Get LLM analysis
0038 |             llm_response = await self.llm_client.analyze_vulnerabilities(analysis_request)
0039 |             
0040 |             # Validate and enrich result
0041 |             validated_result = self._validate_and_complete_result(llm_response, vulnerabilities)
0042 |             
0043 |             # Record metrics
0044 |             analysis_time = asyncio.get_event_loop().time() - start_time
0045 |             if self.metrics:
0046 |                 self.metrics.record_triage_analysis(
0047 |                     len(vulnerabilities), analysis_time, True, chunk_id
0048 |                 )
0049 |             
0050 |             logger.info(f"Triage completed: {validated_result.confirmed_count} confirmed, "
0051 |                        f"{validated_result.false_positive_count} false positives")
0052 |             
0053 |             return validated_result
0054 |         
0055 |         except Exception as e:
0056 |             analysis_time = asyncio.get_event_loop().time() - start_time
0057 |             if self.metrics:
0058 |                 self.metrics.record_triage_analysis(
0059 |                     len(vulnerabilities), analysis_time, False, chunk_id, str(e)
0060 |                 )
0061 |             
0062 |             logger.error(f"Triage analysis failed: {e}")
0063 |             return self._create_fallback_result(vulnerabilities, str(e))
0064 |     
0065 |     def _prepare_analysis_request(self, vulnerabilities: List[Vulnerability], 
0066 |                                 language: Optional[str], chunk_id: Optional[int]) -> str:
0067 |         """Prepare structured analysis request for LLM"""
0068 |         
0069 |         header = f"# VULNERABILITY TRIAGE REQUEST\n"
0070 |         if chunk_id:
0071 |             header += f"Chunk ID: {chunk_id}\n"
0072 |         header += f"Language: {language or 'Unknown'}\n"
0073 |         header += f"Total Vulnerabilities: {len(vulnerabilities)}\n\n"
0074 |         
0075 |         vuln_blocks = []
0076 |         for i, vuln in enumerate(vulnerabilities, 1):
0077 |             block = f"""## VULNERABILITY {i}
0078 | - ID: {vuln.id}
0079 | - TYPE: {vuln.type.value}
0080 | - SEVERITY: {vuln.severity.value}
0081 | - FILE: {vuln.file_path}:{vuln.line_number}
0082 | - TITLE: {vuln.title}
0083 | - DESCRIPTION: {vuln.description}"""
0084 |             
0085 |             if vuln.code_snippet:
0086 |                 # Truncate code snippet for LLM context
0087 |                 snippet = vuln.code_snippet[:300] + "..." if len(vuln.code_snippet) > 300 else vuln.code_snippet
0088 |                 block += f"\n- CODE: {snippet}"
0089 |             
0090 |             if vuln.cwe_id:
0091 |                 block += f"\n- CWE: {vuln.cwe_id}"
0092 |             
0093 |             vuln_blocks.append(block)
0094 |         
0095 |         return header + "\n\n".join(vuln_blocks)
0096 |     
0097 |     def _validate_and_complete_result(self, llm_result: TriageResult, 
0098 |                                     original_vulnerabilities: List[Vulnerability]) -> TriageResult:
0099 |         """Validate LLM result and complete missing decisions"""
0100 |         
0101 |         original_ids = {v.id for v in original_vulnerabilities}
0102 |         analyzed_ids = {d.vulnerability_id for d in llm_result.decisions}
0103 |         
0104 |         # Add conservative decisions for missing vulnerabilities
0105 |         missing_ids = original_ids - analyzed_ids
0106 |         if missing_ids:
0107 |             logger.warning(f"LLM missed {len(missing_ids)} vulnerabilities, adding conservative decisions")
0108 |             
0109 |             for missing_id in missing_ids:
0110 |                 missing_vuln = next(v for v in original_vulnerabilities if v.id == missing_id)
0111 |                 conservative_decision = self._create_conservative_decision(missing_vuln)
0112 |                 llm_result.decisions.append(conservative_decision)
0113 |         
0114 |         return llm_result
0115 |     
0116 |     def _create_conservative_decision(self, vulnerability: Vulnerability) -> TriageDecision:
0117 |         """Create conservative decision for unanalyzed vulnerability"""
0118 |         
0119 |         # High severity = confirmed, others = manual review
0120 |         if vulnerability.severity in ["CRÍTICA", "ALTA"]:
0121 |             decision = AnalysisStatus.CONFIRMED
0122 |             confidence = 0.7
0123 |             reasoning = f"Conservative classification - {vulnerability.severity.value} severity assumed confirmed"
0124 |         else:
0125 |             decision = AnalysisStatus.NEEDS_MANUAL_REVIEW
0126 |             confidence = 0.5
0127 |             reasoning = f"Conservative classification - requires manual review"
0128 |         
0129 |         return TriageDecision(
0130 |             vulnerability_id=vulnerability.id,
0131 |             decision=decision,
0132 |             confidence_score=confidence,
0133 |             reasoning=reasoning,
0134 |             llm_model_used="conservative_fallback"
0135 |         )
0136 |     
0137 |     def _create_fallback_result(self, vulnerabilities: List[Vulnerability], error: str) -> TriageResult:
0138 |         """Create fallback result when LLM analysis fails"""
0139 |         
0140 |         logger.warning("Creating conservative fallback triage result")
0141 |         
0142 |         decisions = [self._create_conservative_decision(vuln) for vuln in vulnerabilities]
0143 |         
0144 |         return TriageResult(
0145 |             decisions=decisions,
0146 |             analysis_summary=f"Conservative fallback analysis due to LLM error: {error}",
0147 |             llm_analysis_time_seconds=0.0
0148 |         )
0149 |     
0150 |     def _create_empty_result(self) -> TriageResult:
0151 |         """Create empty result for no vulnerabilities"""
0152 |         return TriageResult(
0153 |             decisions=[],
0154 |             analysis_summary="No vulnerabilities to analyze",
0155 |             llm_analysis_time_seconds=0.0
0156 |         )
```

---

### debug\llm_debugger.py

**Ruta:** `debug\llm_debugger.py`

```py
0001 | # debug/llm_debugger.py - VERSIÓN ACTUALIZADA CON CONTROL DE DEBUG EN CLIENT
0002 | import json
0003 | import logging
0004 | import os
0005 | import time
0006 | from datetime import datetime
0007 | from pathlib import Path
0008 | from typing import Any, Dict, Optional
0009 | import functools
0010 | import traceback
0011 | 
0012 | class LLMDebugger:
0013 |     """Debugger que controla automáticamente el debug en LLMClient"""
0014 |     
0015 |     def __init__(self, log_file: str = None, full_content: bool = True, max_content_length: int = 100000):
0016 |         # Crear directorio debug si no existe
0017 |         debug_dir = Path("debug")
0018 |         debug_dir.mkdir(exist_ok=True)
0019 |         
0020 |         # Archivo de log con timestamp
0021 |         if not log_file:
0022 |             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
0023 |             log_file = f"debug/llm_calls_{timestamp}.log"
0024 |         
0025 |         self.log_file = log_file
0026 |         self.full_content = full_content
0027 |         self.max_content_length = max_content_length
0028 |         
0029 |         # Lista de clientes LLM activos para controlar debug
0030 |         self.llm_clients = []
0031 |         
0032 |         # Configurar logger específico para LLM
0033 |         self.logger = logging.getLogger("LLM_DEBUG")
0034 |         self.logger.setLevel(logging.DEBUG)
0035 |         
0036 |         # Remover handlers existentes
0037 |         for handler in self.logger.handlers[:]:
0038 |             self.logger.removeHandler(handler)
0039 |         
0040 |         # Handler para archivo de debug con encoding UTF-8
0041 |         file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
0042 |         file_handler.setLevel(logging.DEBUG)
0043 |         
0044 |         # Formatter detallado sin límites de longitud
0045 |         formatter = logging.Formatter(
0046 |             '%(asctime)s | %(levelname)8s | %(message)s',
0047 |             datefmt='%Y-%m-%d %H:%M:%S'
0048 |         )
0049 |         file_handler.setFormatter(formatter)
0050 |         self.logger.addHandler(file_handler)
0051 |         
0052 |         # Handler para consola (con contenido limitado)
0053 |         console_handler = logging.StreamHandler()
0054 |         console_handler.setLevel(logging.INFO)
0055 |         console_formatter = logging.Formatter('🔍 DEBUG: %(message)s')
0056 |         console_handler.setFormatter(console_formatter)
0057 |         self.logger.addHandler(console_handler)
0058 |         
0059 |         # Estadísticas
0060 |         self.call_count = 0
0061 |         self.total_time = 0
0062 |         self.errors = []
0063 |         
0064 |         self.logger.info("="*100)
0065 |         self.logger.info("🔍 LLM DEBUGGER INICIADO - ACTIVANDO DEBUG EN CLIENTES")
0066 |         self.logger.info(f"📄 Log file: {log_file}")
0067 |         self.logger.info(f"📝 Full content mode: {self.full_content}")
0068 |         self.logger.info(f"📏 Max content length: {self.max_content_length if not self.full_content else 'UNLIMITED'}")
0069 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0070 |         self.logger.info("="*100)
0071 |         
0072 |         print(f"🔍 LLM Debug logging to: {log_file} (Full Content: {self.full_content})")
0073 |         
0074 |         # Activar debug en todos los clientes LLM existentes
0075 |         self._activate_debug_in_existing_clients()
0076 |     
0077 |     def _activate_debug_in_existing_clients(self):
0078 |         """Activar debug en clientes LLM ya existentes"""
0079 |         try:
0080 |             # Buscar clientes LLM en el sistema usando introspección
0081 |             import gc
0082 |             
0083 |             for obj in gc.get_objects():
0084 |                 if hasattr(obj, '__class__') and obj.__class__.__name__ == 'LLMClient':
0085 |                     self.register_llm_client(obj)
0086 |                     
0087 |         except Exception as e:
0088 |             self.logger.warning(f"Could not auto-activate debug in existing clients: {e}")
0089 |     
0090 |     def register_llm_client(self, llm_client):
0091 |         """Registrar y activar debug en un cliente LLM"""
0092 |         if llm_client not in self.llm_clients:
0093 |             self.llm_clients.append(llm_client)
0094 |             llm_client.enable_debug_mode()
0095 |             self.logger.info(f"✅ Debug enabled for LLM Client: {id(llm_client)}")
0096 |     
0097 |     def unregister_llm_client(self, llm_client):
0098 |         """Desregistrar cliente LLM"""
0099 |         if llm_client in self.llm_clients:
0100 |             self.llm_clients.remove(llm_client)
0101 |             llm_client.disable_debug_mode()
0102 |             self.logger.info(f"❌ Debug disabled for LLM Client: {id(llm_client)}")
0103 |     
0104 |     def log_api_call(self, 
0105 |                      call_type: str,
0106 |                      provider: str,
0107 |                      payload: Dict[str, Any],
0108 |                      response: Any = None,
0109 |                      error: Exception = None,
0110 |                      duration: float = None,
0111 |                      metadata: Dict[str, Any] = None):
0112 |         """Log detallado de llamada API con contenido completo"""
0113 |         
0114 |         self.call_count += 1
0115 |         call_id = f"CALL_{self.call_count:03d}"
0116 |         
0117 |         # === HEADER ===
0118 |         self.logger.info(f"\n{'='*100}")
0119 |         self.logger.info(f"🚀 {call_id} - {call_type.upper()} | Provider: {provider}")
0120 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0121 |         self.logger.info(f"{'='*100}")
0122 |         
0123 |         # === PAYLOAD DETAILS (CONTENIDO COMPLETO) ===
0124 |         self.logger.info("📤 PAYLOAD ENVIADO (REQUEST):")
0125 |         self._log_content_section(payload, "REQUEST", is_json=True)
0126 |         
0127 |         # === RESPONSE DETAILS (CONTENIDO COMPLETO) ===
0128 |         if response is not None:
0129 |             self.logger.info("\n📥 RESPUESTA RECIBIDA (RESPONSE):")
0130 |             self._log_content_section(response, "RESPONSE", is_json=None)
0131 |         
0132 |         # === ERROR DETAILS (COMPLETO) ===
0133 |         if error:
0134 |             self.logger.error(f"\n❌ ERROR OCURRIDO:")
0135 |             self.logger.error(f"   🔧 Type: {type(error).__name__}")
0136 |             self.logger.error(f"   💬 Message: {str(error)}")
0137 |             self.logger.error(f"   📍 Traceback completo:")
0138 |             
0139 |             # Traceback completo
0140 |             tb_lines = traceback.format_exception(type(error), error, error.__traceback__)
0141 |             for line in tb_lines:
0142 |                 self.logger.error(f"     {line.rstrip()}")
0143 |             
0144 |             self.errors.append({
0145 |                 'call_id': call_id,
0146 |                 'error_type': type(error).__name__,
0147 |                 'error_message': str(error),
0148 |                 'traceback': ''.join(tb_lines),
0149 |                 'timestamp': datetime.now().isoformat()
0150 |             })
0151 |         
0152 |         # === PERFORMANCE METRICS ===
0153 |         if duration:
0154 |             self.total_time += duration
0155 |             self.logger.info(f"\n⏱️  MÉTRICAS DE RENDIMIENTO:")
0156 |             self.logger.info(f"   🕐 Duración de llamada: {duration:.3f}s")
0157 |             self.logger.info(f"   📊 Tiempo total acumulado: {self.total_time:.3f}s")
0158 |             self.logger.info(f"   📈 Promedio por llamada: {self.total_time/self.call_count:.3f}s")
0159 |             
0160 |             # Throughput si hay datos de vulnerabilidades
0161 |             if metadata and 'vulnerabilities_count' in metadata:
0162 |                 vuln_count = metadata['vulnerabilities_count']
0163 |                 throughput = vuln_count / duration if duration > 0 else 0
0164 |                 self.logger.info(f"   🚀 Throughput: {throughput:.2f} vulnerabilidades/segundo")
0165 |         
0166 |         # === METADATA ===
0167 |         if metadata:
0168 |             self.logger.info(f"\n📊 METADATOS:")
0169 |             for key, value in metadata.items():
0170 |                 self.logger.info(f"   📋 {key}: {value}")
0171 |         
0172 |         # === FOOTER ===
0173 |         self.logger.info(f"{'='*100}")
0174 |         self.logger.info(f"✅ {call_id} COMPLETADO")
0175 |         self.logger.info(f"{'='*100}\n")
0176 |     
0177 |     def _log_content_section(self, content: Any, section_name: str, is_json: bool = None):
0178 |         """Log una sección de contenido completo con análisis automático"""
0179 |         
0180 |         # Determinar el tipo de contenido y convertir a string
0181 |         if isinstance(content, dict):
0182 |             content_str = json.dumps(content, indent=2, ensure_ascii=False)
0183 |             is_json = True
0184 |         elif isinstance(content, str):
0185 |             content_str = content
0186 |             # Intentar detectar si es JSON
0187 |             if is_json is None:
0188 |                 try:
0189 |                     json.loads(content)
0190 |                     is_json = True
0191 |                 except:
0192 |                     is_json = False
0193 |         else:
0194 |             content_str = str(content)
0195 |             is_json = False
0196 |         
0197 |         # Calcular métricas
0198 |         content_size = len(content_str.encode('utf-8'))
0199 |         line_count = content_str.count('\n') + 1
0200 |         
0201 |         self.logger.info(f"   📏 Size: {content_size:,} bytes")
0202 |         self.logger.info(f"   📄 Lines: {line_count:,}")
0203 |         self.logger.info(f"   🔧 Type: {type(content).__name__}")
0204 |         self.logger.info(f"   📋 Format: {'JSON' if is_json else 'Text'}")
0205 |         
0206 |         # Si es un dict, mostrar estructura
0207 |         if isinstance(content, dict):
0208 |             self.logger.info(f"   🔑 Keys: {list(content.keys())}")
0209 |         
0210 |         # Log del contenido completo
0211 |         if self.full_content or content_size <= self.max_content_length:
0212 |             self.logger.info(f"   📋 CONTENIDO COMPLETO DE {section_name}:")
0213 |             self.logger.info("   " + "─" * 80)
0214 |             
0215 |             # Formatear con numeración de líneas
0216 |             formatted_content = self._format_with_line_numbers(content_str)
0217 |             self.logger.info(formatted_content)
0218 |             
0219 |             self.logger.info("   " + "─" * 80)
0220 |         else:
0221 |             # Modo truncado
0222 |             self.logger.info(f"   📋 CONTENIDO DE {section_name} (TRUNCADO):")
0223 |             self.logger.info("   " + "─" * 80)
0224 |             
0225 |             # Mostrar inicio y final
0226 |             preview_length = min(2000, self.max_content_length // 2)
0227 |             
0228 |             self.logger.info("   📝 INICIO:")
0229 |             start_content = content_str[:preview_length]
0230 |             self.logger.info(self._format_with_line_numbers(start_content))
0231 |             
0232 |             if len(content_str) > preview_length * 2:
0233 |                 self.logger.info(f"\n   ⚠️  ... CONTENIDO MEDIO OMITIDO ({len(content_str) - preview_length * 2:,} chars) ...\n")
0234 |             
0235 |             self.logger.info("   📝 FINAL:")
0236 |             end_content = content_str[-preview_length:]
0237 |             # Calcular número de línea inicial para el final
0238 |             start_line = content_str[:len(content_str) - preview_length].count('\n') + 1
0239 |             self.logger.info(self._format_with_line_numbers(end_content, start_line))
0240 |             
0241 |             self.logger.info("   " + "─" * 80)
0242 |             self.logger.info(f"   ⚠️  NOTA: Contenido truncado - longitud original: {content_size:,} bytes")
0243 |     
0244 |     def _format_with_line_numbers(self, text: str, start_line: int = 1) -> str:
0245 |         """Formatear texto con numeración de líneas"""
0246 |         lines = text.split('\n')
0247 |         formatted_lines = []
0248 |         
0249 |         for i, line in enumerate(lines):
0250 |             line_num = start_line + i
0251 |             formatted_lines.append(f"   [{line_num:5d}] {line}")
0252 |         
0253 |         return '\n'.join(formatted_lines)
0254 |     
0255 |     def log_triage_analysis(self, vulnerabilities_data: str, system_prompt: str, response: Any, duration: float = None):
0256 |         """Log específico para análisis de triage con contenido completo"""
0257 |         
0258 |         vuln_count = vulnerabilities_data.count("## VULNERABILITY")
0259 |         
0260 |         metadata = {
0261 |             'analysis_type': 'vulnerability_triage',
0262 |             'vulnerabilities_count': vuln_count,
0263 |             'system_prompt_length': len(system_prompt),
0264 |             'vulnerabilities_data_length': len(vulnerabilities_data),
0265 |             'total_input_size': len(system_prompt) + len(vulnerabilities_data)
0266 |         }
0267 |         
0268 |         # Payload completo para triage - CONTENIDO REAL
0269 |         full_message = f"{system_prompt}\n\nDATA TO ANALYZE:\n{vulnerabilities_data}"
0270 |         payload = {
0271 |             'message': {
0272 |                 'role': 'user',
0273 |                 'content': full_message
0274 |             },
0275 |             'temperature': 0.1,
0276 |             'model': 'meta-llama/llama-3-3-70b-instruct',
0277 |             'analysis_metadata': metadata
0278 |         }
0279 |         
0280 |         self.log_api_call(
0281 |             call_type="triage_analysis",
0282 |             provider="research_api",
0283 |             payload=payload,
0284 |             response=response,
0285 |             duration=duration,
0286 |             metadata=metadata
0287 |         )
0288 |     
0289 |     def log_remediation_generation(self, vulnerability_data: str, system_prompt: str, response: Any, duration: float = None):
0290 |         """Log específico para generación de remediación con contenido completo"""
0291 |         
0292 |         metadata = {
0293 |             'analysis_type': 'remediation_generation',
0294 |             'system_prompt_length': len(system_prompt),
0295 |             'vulnerability_data_length': len(vulnerability_data),
0296 |             'total_input_size': len(system_prompt) + len(vulnerability_data)
0297 |         }
0298 |         
0299 |         # Payload completo para remediación - CONTENIDO REAL
0300 |         full_message = f"{system_prompt}\n\nVULNERABILITY DATA:\n{vulnerability_data}"
0301 |         payload = {
0302 |             'message': {
0303 |                 'role': 'user',
0304 |                 'content': full_message
0305 |             },
0306 |             'temperature': 0.2,
0307 |             'model': 'meta-llama/llama-3-3-70b-instruct',
0308 |             'remediation_metadata': metadata
0309 |         }
0310 |         
0311 |         self.log_api_call(
0312 |             call_type="remediation_generation",
0313 |             provider="research_api",
0314 |             payload=payload,
0315 |             response=response,
0316 |             duration=duration,
0317 |             metadata=metadata
0318 |         )
0319 |     
0320 |     def log_raw_http_call(self, url: str, method: str, headers: Dict, request_body: Any, 
0321 |                          response_status: int, response_headers: Dict, response_body: Any, 
0322 |                          duration: float = None):
0323 |         """Log de llamada HTTP cruda con todos los detalles"""
0324 |         
0325 |         self.call_count += 1
0326 |         call_id = f"HTTP_{self.call_count:03d}"
0327 |         
0328 |         self.logger.info(f"\n{'='*100}")
0329 |         self.logger.info(f"🌐 {call_id} - HTTP {method.upper()} | URL: {url}")
0330 |         self.logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
0331 |         self.logger.info(f"{'='*100}")
0332 |         
0333 |         # REQUEST DETAILS
0334 |         self.logger.info("📤 HTTP REQUEST:")
0335 |         self.logger.info(f"   🔗 URL: {url}")
0336 |         self.logger.info(f"   🔧 Method: {method}")
0337 |         self.logger.info(f"   📋 Headers:")
0338 |         for header, value in headers.items():
0339 |             # Ocultar parcialmente API keys por seguridad
0340 |             if 'api' in header.lower() or 'key' in header.lower() or 'auth' in header.lower():
0341 |                 masked_value = value[:8] + "***" + value[-4:] if len(value) > 12 else "***"
0342 |                 self.logger.info(f"      {header}: {masked_value}")
0343 |             else:
0344 |                 self.logger.info(f"      {header}: {value}")
0345 |         
0346 |         # REQUEST BODY
0347 |         if request_body:
0348 |             self.logger.info(f"\n   📤 REQUEST BODY:")
0349 |             self._log_content_section(request_body, "REQUEST_BODY")
0350 |         
0351 |         # RESPONSE DETAILS
0352 |         self.logger.info(f"\n📥 HTTP RESPONSE:")
0353 |         self.logger.info(f"   📊 Status: {response_status}")
0354 |         self.logger.info(f"   📋 Headers:")
0355 |         for header, value in response_headers.items():
0356 |             self.logger.info(f"      {header}: {value}")
0357 |         
0358 |         # RESPONSE BODY
0359 |         if response_body:
0360 |             self.logger.info(f"\n   📥 RESPONSE BODY:")
0361 |             self._log_content_section(response_body, "RESPONSE_BODY")
0362 |         
0363 |         # PERFORMANCE
0364 |         if duration:
0365 |             self.total_time += duration
0366 |             self.logger.info(f"\n⏱️  HTTP PERFORMANCE:")
0367 |             self.logger.info(f"   🕐 Duration: {duration:.3f}s")
0368 |             self.logger.info(f"   📊 Status: {'✅ Success' if 200 <= response_status < 300 else '❌ Error'}")
0369 |         
0370 |         self.logger.info(f"{'='*100}\n")
0371 |     
0372 |     def get_summary_stats(self) -> Dict[str, Any]:
0373 |         """Obtener estadísticas resumidas"""
0374 |         return {
0375 |             'total_calls': self.call_count,
0376 |             'total_time_seconds': self.total_time,
0377 |             'average_time_per_call': self.total_time / self.call_count if self.call_count > 0 else 0,
0378 |             'error_count': len(self.errors),
0379 |             'success_rate': (self.call_count - len(self.errors)) / self.call_count if self.call_count > 0 else 0,
0380 |             'errors': self.errors,
0381 |             'log_file': self.log_file,
0382 |             'full_content_mode': self.full_content,
0383 |             'active_llm_clients': len(self.llm_clients)
0384 |         }
0385 |     
0386 |     def finalize_log(self):
0387 |         """Finalizar el log con estadísticas completas y desactivar debug en clientes"""
0388 |         
0389 |         # Desactivar debug en todos los clientes registrados
0390 |         for client in self.llm_clients[:]:  # Copia la lista para evitar modificaciones concurrentes
0391 |             self.unregister_llm_client(client)
0392 |         
0393 |         stats = self.get_summary_stats()
0394 |         
0395 |         self.logger.info("\n" + "="*100)
0396 |         self.logger.info("📊 RESUMEN FINAL - LLM DEBUG SESSION")
0397 |         self.logger.info("="*100)
0398 |         self.logger.info(f"🔢 Total de llamadas: {stats['total_calls']}")
0399 |         self.logger.info(f"⏱️  Tiempo total: {stats['total_time_seconds']:.2f}s")
0400 |         self.logger.info(f"📊 Tiempo promedio: {stats['average_time_per_call']:.2f}s por llamada")
0401 |         self.logger.info(f"❌ Errores: {stats['error_count']}")
0402 |         self.logger.info(f"✅ Tasa de éxito: {stats['success_rate']:.1%}")
0403 |         self.logger.info(f"📄 Archivo de log: {stats['log_file']}")
0404 |         self.logger.info(f"📝 Modo contenido completo: {stats['full_content_mode']}")
0405 |         self.logger.info(f"🔧 Clientes LLM controlados: {stats['active_llm_clients']}")
0406 |         
0407 |         if self.errors:
0408 |             self.logger.info("\n🚨 ERRORES DETECTADOS:")
0409 |             for error in self.errors:
0410 |                 self.logger.info(f"   {error['call_id']}: {error['error_type']} - {error['error_message']}")
0411 |         
0412 |         # Estadísticas de contenido
0413 |         log_size = Path(self.log_file).stat().st_size if Path(self.log_file).exists() else 0
0414 |         self.logger.info(f"\n📏 ESTADÍSTICAS DEL LOG:")
0415 |         self.logger.info(f"   📄 Tamaño del archivo: {log_size:,} bytes ({log_size/1024/1024:.2f} MB)")
0416 |         self.logger.info(f"   📝 Modo: {'Contenido completo' if self.full_content else 'Contenido limitado'}")
0417 |         
0418 |         self.logger.info("="*100)
0419 |         print(f"📄 Debug completo guardado en: {self.log_file} ({log_size/1024/1024:.2f} MB)")
0420 | 
0421 | 
0422 | # Instancia global del debugger
0423 | _debugger = None
0424 | 
0425 | def get_debugger(full_content: bool = True) -> LLMDebugger:
0426 |     """Obtener instancia singleton del debugger"""
0427 |     global _debugger
0428 |     if _debugger is None:
0429 |         _debugger = LLMDebugger(full_content=full_content)
0430 |     return _debugger
0431 | 
0432 | def debug_llm_call(func):
0433 |     """Decorador para debuggear automáticamente llamadas LLM"""
0434 |     
0435 |     @functools.wraps(func)
0436 |     async def wrapper(*args, **kwargs):
0437 |         debugger = get_debugger()
0438 |         start_time = time.time()
0439 |         
0440 |         try:
0441 |             result = await func(*args, **kwargs)
0442 |             duration = time.time() - start_time
0443 |             
0444 |             debugger.log_api_call(
0445 |                 call_type=func.__name__,
0446 |                 provider="auto_detected",
0447 |                 payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
0448 |                 response=str(result)[:1000] if len(str(result)) <= 1000 else result,
0449 |                 duration=duration
0450 |             )
0451 |             
0452 |             return result
0453 |             
0454 |         except Exception as e:
0455 |             duration = time.time() - start_time
0456 |             
0457 |             debugger.log_api_call(
0458 |                 call_type=func.__name__,
0459 |                 provider="auto_detected", 
0460 |                 payload={'args': str(args)[:500], 'kwargs': str(kwargs)[:500]},
0461 |                 error=e,
0462 |                 duration=duration
0463 |             )
0464 |             
0465 |             raise
0466 |     
0467 |     return wrapper
0468 | 
0469 | # === FUNCIONES DE UTILIDAD ===
0470 | 
0471 | def start_debug_session(full_content: bool = True):
0472 |     """Iniciar nueva sesión de debug y activar debug automáticamente en clientes LLM"""
0473 |     global _debugger
0474 |     _debugger = LLMDebugger(full_content=full_content)
0475 |     print(f"🔍 Debug session started: {_debugger.log_file}")
0476 |     print(f"📡 Auto-activating debug in LLM clients...")
0477 | 
0478 | def end_debug_session():
0479 |     """Finalizar sesión de debug y desactivar debug en clientes"""
0480 |     global _debugger
0481 |     if _debugger:
0482 |         _debugger.finalize_log()
0483 |         _debugger = None
0484 | 
0485 | def log_research_api_call(url: str, payload: Dict[str, Any], response: Any, 
0486 |                          duration: float = None, error: Exception = None):
0487 |     """Log específico para Research API con contenido completo"""
0488 |     debugger = get_debugger()
0489 |     debugger.log_api_call(
0490 |         call_type="research_api_call",
0491 |         provider="research_api",
0492 |         payload=payload,
0493 |         response=response,
0494 |         duration=duration,
0495 |         error=error,
0496 |         metadata={
0497 |             'url': url,
0498 |             'payload_size': len(json.dumps(payload, ensure_ascii=False)) if isinstance(payload, dict) else len(str(payload)),
0499 |             'response_size': len(str(response)) if response else 0
0500 |         }
0501 |     )
0502 | 
0503 | def log_http_details(url: str, method: str, headers: Dict, request_body: Any,
0504 |                     response_status: int, response_headers: Dict, response_body: Any,
0505 |                     duration: float = None):
0506 |     """Log detallado de llamada HTTP"""
0507 |     debugger = get_debugger()
0508 |     debugger.log_raw_http_call(
0509 |         url=url,
0510 |         method=method,
0511 |         headers=headers,
0512 |         request_body=request_body,
0513 |         response_status=response_status,
0514 |         response_headers=response_headers,
0515 |         response_body=response_body,
0516 |         duration=duration
0517 |     )
0518 | 
0519 | def register_llm_client_for_debug(llm_client):
0520 |     """Registrar manualmente un cliente LLM para debug"""
0521 |     try:
0522 |         debugger = get_debugger()
0523 |         debugger.register_llm_client(llm_client)
0524 |     except:
0525 |         pass  # Si no hay sesión de debug activa, no hacer nada
```

---

### debug\run_with_debug.py

**Ruta:** `debug\run_with_debug.py`

```py
0001 | # debug/run_with_full_debug.py - VERSIÓN MEJORADA
0002 | #!/usr/bin/env python3
0003 | """
0004 | Script para ejecutar análisis con debug completo y automático
0005 | """
0006 | 
0007 | import sys
0008 | import asyncio
0009 | import os
0010 | from pathlib import Path
0011 | 
0012 | # Agregar directorio raíz al path
0013 | project_root = Path(__file__).parent.parent
0014 | sys.path.insert(0, str(project_root))
0015 | 
0016 | def setup_debug_environment():
0017 |     """Configurar entorno para debug completo"""
0018 |     
0019 |     # Importar y configurar debugger
0020 |     from debug.llm_debugger import start_debug_session, get_debugger
0021 |     from application.factory import create_debug_factory
0022 |     
0023 |     print("🔍 Starting FULL CONTENT LLM Debug Session...")
0024 |     print("📝 This will log complete requests and responses to debug file")
0025 |     
0026 |     # Verificar si hay API key
0027 |     api_key = os.getenv("RESEARCH_API_KEY")
0028 |     if api_key:
0029 |         print(f"🔑 API Key detected: {api_key[:8]}***{api_key[-4:]}")
0030 |     else:
0031 |         print("⚠️  No API key - will use mock responses")
0032 |     
0033 |     # Iniciar debug session con contenido completo
0034 |     start_debug_session(full_content=True)
0035 |     
0036 |     debugger = get_debugger()
0037 |     print(f"📄 Debug file: {debugger.log_file}")
0038 |     
0039 |     return debugger
0040 | 
0041 | def patch_factory_for_debug():
0042 |     """Patchear el factory por defecto para usar debug"""
0043 |     
0044 |     import application.factory as factory_module
0045 |     
0046 |     # Guardar la función original
0047 |     original_create_factory = factory_module.create_factory
0048 |     
0049 |     # Crear función de reemplazo que habilita debug
0050 |     def create_debug_enabled_factory():
0051 |         factory = original_create_factory()
0052 |         factory.enable_debug_mode()
0053 |         return factory
0054 |     
0055 |     # Reemplazar la función
0056 |     factory_module.create_factory = create_debug_enabled_factory
0057 |     
0058 |     print("🔧 Factory patched to enable debug mode")
0059 | 
0060 | def main():
0061 |     """Ejecutar CLI con debug completo habilitado automáticamente"""
0062 |     
0063 |     debugger = None
0064 |     
0065 |     try:
0066 |         # Configurar debug
0067 |         debugger = setup_debug_environment()
0068 |         
0069 |         # Patchear factory para habilitar debug automáticamente
0070 |         patch_factory_for_debug()
0071 |         
0072 |         # Importar CLI después del patch
0073 |         from application.cli import cli
0074 |         
0075 |         print("\n🚀 Starting analysis with full debug logging...")
0076 |         print("📡 All LLM clients will be automatically configured for debug")
0077 |         
0078 |         # Ejecutar CLI normal - ahora con debug automático
0079 |         cli()
0080 |         
0081 |     except SystemExit as e:
0082 |         # SystemExit es normal para CLI
0083 |         if e.code != 0:
0084 |             print(f"⚠️  CLI exited with code: {e.code}")
0085 |     except KeyboardInterrupt:
0086 |         print("\n⚠️  Analysis interrupted by user")
0087 |     except Exception as e:
0088 |         print(f"❌ Unexpected error: {e}")
0089 |         import traceback
0090 |         traceback.print_exc()
0091 |     finally:
0092 |         # Finalizar debug session
0093 |         if debugger:
0094 |             print("\n📊 Finalizing debug session...")
0095 |             from debug.llm_debugger import end_debug_session
0096 |             end_debug_session()
0097 |             
0098 |             # Mostrar estadísticas finales
0099 |             stats = debugger.get_summary_stats()
0100 |             print(f"\n✅ Debug session completed!")
0101 |             print(f"   📞 Total calls: {stats['total_calls']}")
0102 |             print(f"   ⏱️  Total time: {stats['total_time_seconds']:.2f}s")
0103 |             print(f"   🔧 LLM clients controlled: {stats['active_llm_clients']}")
0104 |             
0105 |             if Path(debugger.log_file).exists():
0106 |                 log_size = Path(debugger.log_file).stat().st_size / 1024 / 1024
0107 |                 print(f"   📄 Log file size: {log_size:.2f} MB")
0108 |                 print(f"   📂 Log location: {debugger.log_file}")
0109 | 
0110 | if __name__ == '__main__':
0111 |     main()
```

---

### infrastructure\cache.py

**Ruta:** `infrastructure\cache.py`

```py
0001 | # infrastructure/cache.py
0002 | import hashlib
0003 | import json
0004 | import pickle
0005 | from pathlib import Path
0006 | from typing import Dict, Any, Optional
0007 | from datetime import datetime, timedelta
0008 | import logging
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | class AnalysisCache:
0013 |     """Cache optimizado para resultados de análisis"""
0014 |     
0015 |     def __init__(self, cache_dir: str = ".security_cache", ttl_hours: int = 24):
0016 |         self.cache_dir = Path(cache_dir)
0017 |         self.ttl_hours = ttl_hours
0018 |         self.cache_dir.mkdir(exist_ok=True)
0019 |         self._cleanup_expired()
0020 |     
0021 |     def _get_cache_key(self, content: str, language: Optional[str], tool_hint: Optional[str]) -> str:
0022 |         """Generate cache key from content hash"""
0023 |         key_data = f"{content}|{language or ''}|{tool_hint or ''}"
0024 |         return hashlib.sha256(key_data.encode()).hexdigest()[:16]
0025 |     
0026 |     def get(self, content: str, language: Optional[str] = None, 
0027 |             tool_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
0028 |         """Get from cache with TTL check"""
0029 |         try:
0030 |             cache_key = self._get_cache_key(content, language, tool_hint)
0031 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0032 |             
0033 |             if not cache_file.exists():
0034 |                 return None
0035 |             
0036 |             # Check TTL
0037 |             file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
0038 |             if file_age > timedelta(hours=self.ttl_hours):
0039 |                 cache_file.unlink()
0040 |                 return None
0041 |             
0042 |             with open(cache_file, 'rb') as f:
0043 |                 return pickle.load(f)
0044 |                 
0045 |         except Exception as e:
0046 |             logger.warning(f"Cache read failed: {e}")
0047 |             return None
0048 |     
0049 |     def put(self, content: str, data: Dict[str, Any], 
0050 |             language: Optional[str] = None, tool_hint: Optional[str] = None) -> None:
0051 |         """Store in cache"""
0052 |         try:
0053 |             cache_key = self._get_cache_key(content, language, tool_hint)
0054 |             cache_file = self.cache_dir / f"{cache_key}.cache"
0055 |             
0056 |             with open(cache_file, 'wb') as f:
0057 |                 pickle.dump(data, f)
0058 |                 
0059 |             logger.debug(f"Cached result: {cache_key}")
0060 |             
0061 |         except Exception as e:
0062 |             logger.warning(f"Cache write failed: {e}")
0063 |     
0064 |     def _cleanup_expired(self) -> None:
0065 |         """Clean up expired cache files"""
0066 |         try:
0067 |             cutoff_time = datetime.now() - timedelta(hours=self.ttl_hours)
0068 |             
0069 |             for cache_file in self.cache_dir.glob("*.cache"):
0070 |                 file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
0071 |                 if file_time < cutoff_time:
0072 |                     cache_file.unlink()
0073 |                     
0074 |         except Exception as e:
0075 |             logger.warning(f"Cache cleanup failed: {e}")
```

---

### infrastructure\config.py

**Ruta:** `infrastructure\config.py`

```py
0001 | # infrastructure/config.py - VERSIÓN SIMPLIFICADA TEMPORAL
0002 | import os
0003 | from typing import Optional, Dict, Any
0004 | 
0005 | class UnifiedSettings:
0006 |     """Configuración simplificada sin Pydantic Settings"""
0007 |     
0008 |     def __init__(self):
0009 |         # 🔑 API Keys
0010 |         self.openai_api_key = os.getenv("OPENAI_API_KEY")
0011 |         self.watsonx_api_key = os.getenv("RESEARCH_API_KEY")
0012 |         
0013 |         # 🤖 LLM Configuration
0014 |         self.llm_primary_provider = os.getenv("LLM_PRIMARY_PROVIDER", "openai")
0015 |         self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))
0016 |         self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1024"))
0017 |         self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT", "180"))
0018 |         
0019 |         # 🧩 Chunking Configuration
0020 |         self.chunking_max_vulnerabilities = int(os.getenv("CHUNKING_MAX_VULNS", "5"))
0021 |         self.chunking_max_size_bytes = int(os.getenv("CHUNKING_MAX_SIZE", "8000"))
0022 |         self.chunking_overlap = int(os.getenv("CHUNKING_OVERLAP", "1"))
0023 |         self.chunking_min_size = int(os.getenv("CHUNKING_MIN_SIZE", "3"))
0024 |         
0025 |         # 💾 Cache Configuration
0026 |         self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
0027 |         self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "24"))
0028 |         self.cache_directory = os.getenv("CACHE_DIR", ".security_cache")
0029 |         
0030 |         # 🔒 Security Configuration
0031 |         self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
0032 |         self.input_validation_enabled = os.getenv("INPUT_VALIDATION", "true").lower() == "true"
0033 |         
0034 |         # 📊 Reporting Configuration
0035 |         self.report_max_code_length = int(os.getenv("REPORT_MAX_CODE_LENGTH", "1000"))
0036 |         
0037 |         # 📈 Observability
0038 |         self.log_level = os.getenv("LOG_LEVEL", "INFO")
0039 |         self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
0040 |     
0041 |     @property
0042 |     def has_llm_provider(self) -> bool:
0043 |         """Check if at least one LLM provider is configured"""
0044 |         return bool(self.openai_api_key or self.watsonx_api_key)
0045 |     
0046 |     @property
0047 |     def chunking_config(self) -> Dict[str, Any]:
0048 |         """Get chunking configuration as dict"""
0049 |         return {
0050 |             "max_vulnerabilities_per_chunk": self.chunking_max_vulnerabilities,
0051 |             "max_size_bytes": self.chunking_max_size_bytes,
0052 |             "overlap_vulnerabilities": self.chunking_overlap,
0053 |             "min_chunk_size": self.chunking_min_size
0054 |         }
0055 |     
0056 |     def get_available_llm_provider(self) -> str:
0057 |         """Get the first available LLM provider"""
0058 |         if self.llm_primary_provider == "openai" and self.openai_api_key:
0059 |             return "openai"
0060 |         elif self.llm_primary_provider == "watsonx" and self.watsonx_api_key:
0061 |             return "watsonx"
0062 |         elif self.openai_api_key:
0063 |             return "openai"
0064 |         elif self.watsonx_api_key:
0065 |             return "watsonx"
0066 |         else:
0067 |             raise ValueError("No LLM provider configured")
0068 | 
0069 | # Global settings instance
0070 | settings = UnifiedSettings()
```

---

### infrastructure\llm\client.py

**Ruta:** `infrastructure\llm\client.py`

```py
0001 | # infrastructure/llm/client.py
0002 | import requests
0003 | import json
0004 | import logging
0005 | import time
0006 | import os
0007 | import uuid
0008 | from typing import Dict, Any, Optional
0009 | 
0010 | from core.models import TriageResult, RemediationPlan, TriageDecision, AnalysisStatus, RemediationStep, VulnerabilityType
0011 | from core.exceptions import LLMError
0012 | 
0013 | logger = logging.getLogger(__name__)
0014 | 
0015 | class LLMClient:
0016 |     """Cliente LLM sin debug por defecto - debug solo cuando se active explícitamente"""
0017 |     
0018 |     def __init__(self, primary_provider: str = "watsonx", enable_debug: bool = False):
0019 |         self.api_key = os.getenv("RESEARCH_API_KEY", "")
0020 |         self.primary_provider = primary_provider
0021 |         self.base_url = "https://ia-research-dev.codingbuddy-4282826dce7d155229a320302e775459-0000.eu-de.containers.appdomain.cloud"
0022 |         self.timeout = 300  # 5 minutos
0023 |         self.user_email = "franciscojavier.suarez_css@research.com"
0024 |         
0025 |         # Debug solo si se habilita explícitamente
0026 |         self.debug_enabled = enable_debug
0027 |         self.debugger = None
0028 |         
0029 |         # Configurar sesión HTTP
0030 |         self.session = requests.Session()
0031 |         self.session.headers.update({
0032 |             "Content-Type": "application/json",
0033 |             "x-api-key": self.api_key
0034 |         })
0035 |         
0036 |         self.endpoints = {
0037 |             "watsonx": "/research/llm/wx/clients",
0038 |             "openai": "/research/llm/openai/clients"
0039 |         }
0040 |         
0041 |         logger.info(f"LLM Client initialized with {self.primary_provider} (Research API)")
0042 |         
0043 |         if not self.api_key:
0044 |             logger.warning("⚠️ RESEARCH_API_KEY no configurada - usando modo mock")
0045 |     
0046 |     def enable_debug_mode(self):
0047 |         """Habilitar modo debug - solo se llama desde el debugger"""
0048 |         self.debug_enabled = True
0049 |         try:
0050 |             from debug.llm_debugger import get_debugger
0051 |             self.debugger = get_debugger()
0052 |             logger.info("🔍 Debug mode enabled for LLM Client")
0053 |         except ImportError:
0054 |             logger.warning("Debug module not available")
0055 |             self.debug_enabled = False
0056 |     
0057 |     def disable_debug_mode(self):
0058 |         """Deshabilitar modo debug"""
0059 |         self.debug_enabled = False
0060 |         self.debugger = None
0061 |         logger.info("🔍 Debug mode disabled for LLM Client")
0062 |     
0063 |     async def analyze_vulnerabilities(self, vulnerabilities_data: str,
0064 |                                     language: Optional[str] = None) -> TriageResult:
0065 |         """Analyze vulnerabilities using Research API"""
0066 |         
0067 |         if not self.api_key:
0068 |             logger.warning("Using MOCK analysis - no API key configured")
0069 |             return self._create_mock_triage_result(vulnerabilities_data)
0070 |         
0071 |         try:
0072 |             # Preparar prompt de sistema para triage
0073 |             system_prompt = self._get_triage_system_prompt(language)
0074 |             
0075 |             # Llamar a Research API
0076 |             start_time = time.time()
0077 |             response = await self._call_research_api(
0078 |                 message=f"{system_prompt}\n\nDATA TO ANALYZE:\n{vulnerabilities_data}",
0079 |                 temperature=0.1
0080 |             )
0081 |             duration = time.time() - start_time
0082 |             
0083 |             # Log solo si debug está habilitado
0084 |             if self.debug_enabled and self.debugger:
0085 |                 self.debugger.log_triage_analysis(
0086 |                     vulnerabilities_data=vulnerabilities_data,
0087 |                     system_prompt=system_prompt,
0088 |                     response=response,
0089 |                     duration=duration
0090 |                 )
0091 |             
0092 |             # Parsear respuesta
0093 |             result = self._parse_triage_response(response, vulnerabilities_data)
0094 |             
0095 |             return result
0096 |             
0097 |         except Exception as e:
0098 |             logger.error(f"LLM triage analysis failed: {e}")
0099 |             return self._create_mock_triage_result(vulnerabilities_data)
0100 | 
0101 |     async def generate_remediation_plan(self, vulnerability_data: str,
0102 |                                       vuln_type: str = None, language: Optional[str] = None) -> RemediationPlan:
0103 |         """Generate remediation plan using Research API"""
0104 |         
0105 |         if not self.api_key:
0106 |             logger.warning("Using MOCK remediation - no API key configured")
0107 |             return self._create_mock_remediation_plan()
0108 |         
0109 |         try:
0110 |             # Preparar prompt de sistema para remediación
0111 |             system_prompt = self._get_remediation_system_prompt(vuln_type, language)
0112 |             
0113 |             # Llamar a Research API
0114 |             start_time = time.time()
0115 |             response = await self._call_research_api(
0116 |                 message=f"{system_prompt}\n\nVULNERABILITY DATA:\n{vulnerability_data}",
0117 |                 temperature=0.2
0118 |             )
0119 |             duration = time.time() - start_time
0120 |             
0121 |             # Log solo si debug está habilitado
0122 |             if self.debug_enabled and self.debugger:
0123 |                 self.debugger.log_remediation_generation(
0124 |                     vulnerability_data=vulnerability_data,
0125 |                     system_prompt=system_prompt,
0126 |                     response=response,
0127 |                     duration=duration
0128 |                 )
0129 |             
0130 |             # Parsear respuesta
0131 |             result = self._parse_remediation_response(response)
0132 |             
0133 |             return result
0134 |             
0135 |         except Exception as e:
0136 |             logger.error(f"LLM remediation generation failed: {e}")
0137 |             return self._create_mock_remediation_plan()
0138 | 
0139 |     async def _call_research_api(self, message: str, temperature: float = 0.1) -> str:
0140 |         """Call Research API - versión LIMPIA sin debug por defecto"""
0141 |         
0142 |         url = f"{self.base_url}{self.endpoints[self.primary_provider]}"
0143 |         session_uuid = str(uuid.uuid4())
0144 |         
0145 |         # Payload completo
0146 |         payload = {
0147 |             "message": {
0148 |                 "role": "user",
0149 |                 "content": message
0150 |             },
0151 |             "temperature": temperature,
0152 |             "model": "meta-llama/llama-3-3-70b-instruct" if self.primary_provider == "watsonx" else "gpt-4",
0153 |             "prompt": None,
0154 |             "uuid": session_uuid,
0155 |             "language": "es",
0156 |             "user": self.user_email
0157 |         }
0158 |         
0159 |         start_time = time.time()
0160 |         
0161 |         try:
0162 |             logger.info(f"Calling Research API: {self.primary_provider}")
0163 |             
0164 |             # Hacer la llamada HTTP
0165 |             response = self.session.post(url, json=payload, timeout=self.timeout)
0166 |             duration = time.time() - start_time
0167 |             
0168 |             # Log HTTP solo si debug está habilitado
0169 |             if self.debug_enabled and self.debugger:
0170 |                 try:
0171 |                     from debug.llm_debugger import log_http_details, log_research_api_call
0172 |                     
0173 |                     log_http_details(
0174 |                         url=url,
0175 |                         method="POST",
0176 |                         headers=dict(self.session.headers),
0177 |                         request_body=payload,
0178 |                         response_status=response.status_code,
0179 |                         response_headers=dict(response.headers),
0180 |                         response_body=response.text,
0181 |                         duration=duration
0182 |                     )
0183 |                 except ImportError:
0184 |                     pass  # Debug module no disponible
0185 |             
0186 |             if response.status_code != 200:
0187 |                 error_msg = f"HTTP {response.status_code}: {response.text}"
0188 |                 logger.error(f"Research API error: {error_msg}")
0189 |                 raise LLMError(f"Research API failed: {error_msg}")
0190 |             
0191 |             response_text = response.text
0192 |             
0193 |             # Intentar parsear como JSON
0194 |             try:
0195 |                 result = response.json()
0196 |             except json.JSONDecodeError:
0197 |                 result = response_text
0198 |             
0199 |             # Extraer contenido de la respuesta
0200 |             if isinstance(result, dict):
0201 |                 content = (result.get('content') or 
0202 |                           result.get('response') or 
0203 |                           result.get('message') or 
0204 |                           result.get('text') or 
0205 |                           result.get('output') or
0206 |                           str(result))
0207 |             else:
0208 |                 content = str(result)
0209 |             
0210 |             # Log de Research API solo si debug está habilitado
0211 |             if self.debug_enabled and self.debugger:
0212 |                 try:
0213 |                     from debug.llm_debugger import log_research_api_call
0214 |                     log_research_api_call(
0215 |                         url=url,
0216 |                         payload=payload,
0217 |                         response=content,
0218 |                         duration=duration
0219 |                     )
0220 |                 except ImportError:
0221 |                     pass
0222 |             
0223 |             logger.info(f"Research API call successful - {duration:.2f}s")
0224 |             return content
0225 |             
0226 |         except requests.exceptions.Timeout:
0227 |             duration = time.time() - start_time
0228 |             error_msg = f"Research API timeout after {self.timeout} seconds"
0229 |             
0230 |             # Log del error solo si debug está habilitado
0231 |             if self.debug_enabled and self.debugger:
0232 |                 try:
0233 |                     from debug.llm_debugger import log_http_details
0234 |                     log_http_details(
0235 |                         url=url,
0236 |                         method="POST", 
0237 |                         headers=dict(self.session.headers),
0238 |                         request_body=payload,
0239 |                         response_status=408,  # Timeout
0240 |                         response_headers={},
0241 |                         response_body=f"TIMEOUT: {error_msg}",
0242 |                         duration=duration
0243 |                     )
0244 |                 except ImportError:
0245 |                     pass
0246 |             
0247 |             raise LLMError(error_msg)
0248 |             
0249 |         except requests.exceptions.ConnectionError as e:
0250 |             duration = time.time() - start_time
0251 |             error_msg = f"Research API connection error: {e}"
0252 |             
0253 |             if self.debug_enabled and self.debugger:
0254 |                 try:
0255 |                     from debug.llm_debugger import log_http_details
0256 |                     log_http_details(
0257 |                         url=url,
0258 |                         method="POST",
0259 |                         headers=dict(self.session.headers),
0260 |                         request_body=payload,
0261 |                         response_status=0,  # Connection error
0262 |                         response_headers={},
0263 |                         response_body=f"CONNECTION ERROR: {error_msg}",
0264 |                         duration=duration
0265 |                     )
0266 |                 except ImportError:
0267 |                     pass
0268 |             
0269 |             raise LLMError(error_msg)
0270 |             
0271 |         except Exception as e:
0272 |             duration = time.time() - start_time
0273 |             error_msg = f"Research API unexpected error: {e}"
0274 |             
0275 |             if self.debug_enabled and self.debugger:
0276 |                 try:
0277 |                     from debug.llm_debugger import log_http_details
0278 |                     log_http_details(
0279 |                         url=url,
0280 |                         method="POST",
0281 |                         headers=dict(self.session.headers),
0282 |                         request_body=payload,
0283 |                         response_status=-1,  # Unknown error
0284 |                         response_headers={},
0285 |                         response_body=f"UNEXPECTED ERROR: {error_msg}",
0286 |                         duration=duration
0287 |                     )
0288 |                 except ImportError:
0289 |                     pass
0290 |             
0291 |             raise LLMError(error_msg)
0292 | 
0293 |     def _get_triage_system_prompt(self, language: Optional[str]) -> str:
0294 |         """System prompt for vulnerability triage"""
0295 |         return f"""You are a cybersecurity expert analyzing vulnerabilities from SAST tools.
0296 | 
0297 | TASK: Analyze each vulnerability and classify as:
0298 | - "confirmed": Real security issue needing fixes  
0299 | - "false_positive": Scanner false alarm
0300 | - "needs_manual_review": Uncertain case requiring human review
0301 | 
0302 | OUTPUT: Return ONLY valid JSON in this exact format:
0303 | {{
0304 |   "decisions": [
0305 |     {{
0306 |       "vulnerability_id": "vuln_id_here",
0307 |       "decision": "confirmed",
0308 |       "confidence_score": 0.8,
0309 |       "reasoning": "Brief technical explanation",
0310 |       "llm_model_used": "research_api"
0311 |     }}
0312 |   ],
0313 |   "analysis_summary": "Overall analysis summary",
0314 |   "llm_analysis_time_seconds": 1.5
0315 | }}
0316 | 
0317 | Language: {language or 'Spanish'}
0318 | Be conservative: when uncertain, choose "needs_manual_review"."""
0319 | 
0320 |     def _get_remediation_system_prompt(self, vuln_type: str, language: Optional[str]) -> str:
0321 |         """System prompt for remediation planning"""
0322 |         return f"""You are a senior security engineer creating remediation plans.
0323 | 
0324 | TASK: Create step-by-step remediation plan for {vuln_type or 'security'} vulnerabilities.
0325 | 
0326 | OUTPUT: Return ONLY valid JSON in this exact format:
0327 | {{
0328 |   "vulnerability_id": "vuln_id",
0329 |   "vulnerability_type": "{vuln_type or 'Other Security Issue'}",
0330 |   "priority_level": "high",
0331 |   "steps": [
0332 |     {{
0333 |       "step_number": 1,
0334 |       "title": "Step title",
0335 |       "description": "Detailed description",
0336 |       "code_example": null,
0337 |       "estimated_minutes": 30,
0338 |       "difficulty": "medium",
0339 |       "tools_required": []
0340 |     }}
0341 |   ],
0342 |   "risk_if_not_fixed": "Risk description",
0343 |   "references": [],
0344 |   "total_estimated_hours": 2.0,
0345 |   "complexity_score": 5.0,
0346 |   "llm_model_used": "research_api"
0347 | }}
0348 | 
0349 | Language: {language or 'Spanish'}"""
0350 | 
0351 |     def _parse_triage_response(self, llm_response: str, original_data: str) -> TriageResult:
0352 |         """Parse LLM response to TriageResult"""
0353 |         try:
0354 |             if isinstance(llm_response, str):
0355 |                 response_data = json.loads(llm_response)
0356 |             else:
0357 |                 response_data = llm_response
0358 |             
0359 |             return TriageResult(**response_data)
0360 |             
0361 |         except (json.JSONDecodeError, ValueError) as e:
0362 |             logger.warning(f"Failed to parse LLM triage response: {e}")
0363 |             return self._create_mock_triage_result(original_data)
0364 | 
0365 |     def _parse_remediation_response(self, llm_response: str) -> RemediationPlan:
0366 |         """Parse LLM response to RemediationPlan"""
0367 |         try:
0368 |             if isinstance(llm_response, str):
0369 |                 response_data = json.loads(llm_response)
0370 |             else:
0371 |                 response_data = llm_response
0372 |             
0373 |             return RemediationPlan(**response_data)
0374 |             
0375 |         except (json.JSONDecodeError, ValueError) as e:
0376 |             logger.warning(f"Failed to parse LLM remediation response: {e}")
0377 |             return self._create_mock_remediation_plan()
0378 | 
0379 |     def _create_mock_triage_result(self, vulnerabilities_data: str) -> TriageResult:
0380 |         """Create mock triage result for testing"""
0381 |         
0382 |         # Extraer IDs de vulnerabilidades
0383 |         import re
0384 |         vuln_ids = re.findall(r'ID:\s*([^\s\n]+)', vulnerabilities_data)
0385 |         
0386 |         decisions = []
0387 |         for i, vuln_id in enumerate(vuln_ids[:5]):  # Limitar a 5 para testing
0388 |             decision_types = [AnalysisStatus.CONFIRMED, AnalysisStatus.FALSE_POSITIVE, AnalysisStatus.NEEDS_MANUAL_REVIEW]
0389 |             decision = decision_types[i % len(decision_types)]
0390 |             
0391 |             decisions.append(TriageDecision(
0392 |                 vulnerability_id=vuln_id,
0393 |                 decision=decision,
0394 |                 confidence_score=0.7,
0395 |                 reasoning=f"Mock analysis for {vuln_id} - classified as {decision.value}",
0396 |                 llm_model_used="mock_research_api"
0397 |             ))
0398 |         
0399 |         return TriageResult(
0400 |             decisions=decisions,
0401 |             analysis_summary=f"Mock Research API triage of {len(decisions)} vulnerabilities",
0402 |             llm_analysis_time_seconds=1.2
0403 |         )
0404 | 
0405 |     def _create_mock_remediation_plan(self) -> RemediationPlan:
0406 |         """Create mock remediation plan"""
0407 |         
0408 |         mock_steps = [
0409 |             RemediationStep(
0410 |                 step_number=1,
0411 |                 title="Identify and validate the security issue",
0412 |                 description="Review the vulnerability details and confirm the security impact",
0413 |                 estimated_minutes=30,
0414 |                 difficulty="medium"
0415 |             ),
0416 |             RemediationStep(
0417 |                 step_number=2,
0418 |                 title="Implement security fix",
0419 |                 description="Apply the appropriate security control or code change",
0420 |                 estimated_minutes=120,
0421 |                 difficulty="hard"
0422 |             ),
0423 |             RemediationStep(
0424 |                 step_number=3,
0425 |                 title="Test and validate fix",
0426 |                 description="Verify the vulnerability has been properly addressed",
0427 |                 estimated_minutes=30,
0428 |                 difficulty="medium"
0429 |             )
0430 |         ]
0431 |         
0432 |         return RemediationPlan(
0433 |             vulnerability_id="mock_vuln",
0434 |             vulnerability_type=VulnerabilityType.OTHER,
0435 |             priority_level="medium",
0436 |             steps=mock_steps,
0437 |             risk_if_not_fixed="Security risk if not addressed - mock assessment",
0438 |             total_estimated_hours=3.0,
0439 |             complexity_score=5.0,
0440 |             llm_model_used="mock_research_api"
0441 |         )
```

---

### infrastructure\llm\prompts.py

**Ruta:** `infrastructure\llm\prompts.py`

```py
0001 | # infrastructure/llm/prompts.py
0002 | from typing import Optional
0003 | 
0004 | class PromptManager:
0005 |     """Gestión centralizada y optimizada de prompts"""
0006 |     
0007 |     def get_triage_system_prompt(self, language: Optional[str] = None) -> str:
0008 |         """System prompt optimizado para triaje"""
0009 |         return f"""You are a cybersecurity expert specializing in vulnerability analysis.
0010 | 
0011 | TASK: Analyze the provided vulnerabilities and classify each one as:
0012 | - "confirmed": Real security vulnerability that needs fixing
0013 | - "false_positive": Scanner false alarm, not a real issue  
0014 | - "needs_manual_review": Uncertain case requiring human expert review
0015 | 
0016 | CONTEXT: Language/Technology: {language or 'Unknown'}
0017 | 
0018 | OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
0019 | {{
0020 |   "decisions": [
0021 |     {{
0022 |       "vulnerability_id": "vuln_id_here",
0023 |       "decision": "confirmed|false_positive|needs_manual_review",
0024 |       "confidence_score": 0.0-1.0,
0025 |       "reasoning": "Brief technical explanation of your decision",
0026 |       "llm_model_used": "{self._get_model_name()}"
0027 |     }}
0028 |   ],
0029 |   "analysis_summary": "Overall analysis summary",
0030 |   "llm_analysis_time_seconds": 1.5
0031 | }}
0032 | 
0033 | GUIDELINES:
0034 | - Be conservative: when uncertain, choose "needs_manual_review"
0035 | - Consider code context, severity, and vulnerability type
0036 | - Provide clear, technical reasoning
0037 | - Focus on actual exploitability, not theoretical risks"""
0038 | 
0039 |     def get_remediation_system_prompt(self, vuln_type: str, language: Optional[str] = None) -> str:
0040 |         """System prompt optimizado para remediación"""
0041 |         return f"""You are a senior security engineer creating actionable remediation plans.
0042 | 
0043 | TASK: Create a detailed, step-by-step remediation plan for {vuln_type} vulnerabilities.
0044 | 
0045 | CONTEXT: 
0046 | - Vulnerability Type: {vuln_type}
0047 | - Language/Technology: {language or 'Unknown'}
0048 | 
0049 | OUTPUT FORMAT: Return ONLY valid JSON in this exact structure:
0050 | {{
0051 |   "vulnerability_id": "vuln_id",
0052 |   "vulnerability_type": "{vuln_type}",
0053 |   "priority_level": "immediate|high|medium|low",
0054 |   "steps": [
0055 |     {{
0056 |       "step_number": 1,
0057 |       "title": "Descriptive step title",
0058 |       "description": "Clear, actionable description of what to do",
0059 |       "code_example": "Concrete code example if applicable",
0060 |       "estimated_minutes": 30,
0061 |       "difficulty": "easy|medium|hard",
0062 |       "tools_required": ["tool1", "tool2"]
0063 |     }}
0064 |   ],
0065 |   "risk_if_not_fixed": "Clear explanation of the security risk",
0066 |   "references": ["https://owasp.org/relevant-reference"],
0067 |   "total_estimated_hours": 2.0,
0068 |   "complexity_score": 1.0-10.0,
0069 |   "llm_model_used": "{self._get_model_name()}"
0070 | }}
0071 | 
0072 | REQUIREMENTS:
0073 | - Provide 3-5 specific, actionable steps
0074 | - Include code examples when relevant
0075 | - Focus on practical implementation
0076 | - Consider the specific technology stack
0077 | - Prioritize based on severity and impact"""
0078 | 
0079 |     def _get_model_name(self) -> str:
0080 |         """Get current model name for tracking"""
0081 |         return "gpt-4"  # This could be dynamic based on actual provider
```

---

### shared\logger.py

**Ruta:** `shared\logger.py`

```py
0001 | # shared/logger.py
0002 | import logging
0003 | import logging.handlers
0004 | import sys
0005 | from pathlib import Path
0006 | from datetime import datetime
0007 | from typing import Optional
0008 | import json
0009 | 
0010 | class JSONFormatter(logging.Formatter):
0011 |     """Formatter JSON optimizado para logs estructurados"""
0012 |     
0013 |     def format(self, record):
0014 |         log_data = {
0015 |             "timestamp": datetime.fromtimestamp(record.created).isoformat(),
0016 |             "level": record.levelname,
0017 |             "logger": record.name,
0018 |             "message": record.getMessage(),
0019 |             "module": record.module,
0020 |             "function": record.funcName,
0021 |             "line": record.lineno
0022 |         }
0023 |         
0024 |         if hasattr(record, 'extra'):
0025 |             log_data["extra"] = record.extra
0026 |         
0027 |         if record.exc_info:
0028 |             log_data["exception"] = self.formatException(record.exc_info)
0029 |         
0030 |         return json.dumps(log_data, ensure_ascii=False)
0031 | 
0032 | class ColoredFormatter(logging.Formatter):
0033 |     """Formatter con colores para consola"""
0034 |     
0035 |     COLORS = {
0036 |         'DEBUG': '\033[36m',    # Cyan
0037 |         'INFO': '\033[32m',     # Green
0038 |         'WARNING': '\033[33m',  # Yellow
0039 |         'ERROR': '\033[31m',    # Red
0040 |         'CRITICAL': '\033[35m', # Magenta
0041 |         'RESET': '\033[0m'      # Reset
0042 |     }
0043 |     
0044 |     def format(self, record):
0045 |         color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
0046 |         reset = self.COLORS['RESET']
0047 |         
0048 |         return (
0049 |             f"{color}[{datetime.fromtimestamp(record.created).strftime('%H:%M:%S')}] "
0050 |             f"{record.levelname:<8}{reset} - "
0051 |             f"{record.module}.{record.funcName}:{record.lineno} - "
0052 |             f"{record.getMessage()}"
0053 |         )
0054 | 
0055 | def setup_logging(log_level: str = "INFO", 
0056 |                  log_file: Optional[str] = None,
0057 |                  structured: bool = False) -> None:
0058 |     """Configurar logging optimizado y simplificado"""
0059 |     
0060 |     level = getattr(logging, log_level.upper(), logging.INFO)
0061 |     
0062 |     # Clear existing handlers
0063 |     root_logger = logging.getLogger()
0064 |     root_logger.handlers.clear()
0065 |     root_logger.setLevel(level)
0066 |     
0067 |     # Console handler
0068 |     console_handler = logging.StreamHandler(sys.stdout)
0069 |     console_handler.setLevel(level)
0070 |     
0071 |     if structured:
0072 |         console_formatter = JSONFormatter()
0073 |     else:
0074 |         console_formatter = ColoredFormatter()
0075 |     
0076 |     console_handler.setFormatter(console_formatter)
0077 |     root_logger.addHandler(console_handler)
0078 |     
0079 |     # File handler (optional)
0080 |     if log_file:
0081 |         log_path = Path(log_file)
0082 |         log_path.parent.mkdir(parents=True, exist_ok=True)
0083 |         
0084 |         file_handler = logging.handlers.RotatingFileHandler(
0085 |             log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
0086 |         )
0087 |         file_handler.setLevel(logging.DEBUG)
0088 |         file_handler.setFormatter(JSONFormatter())
0089 |         root_logger.addHandler(file_handler)
0090 |     
0091 |     # Suppress noisy loggers
0092 |     for noisy_logger in ['urllib3', 'requests', 'openai']:
0093 |         logging.getLogger(noisy_logger).setLevel(logging.WARNING)
0094 |     
0095 |     logger = logging.getLogger(__name__)
0096 |     logger.info(f"Logging configured - Level: {log_level}")
```

---

### shared\metrics.py

**Ruta:** `shared\metrics.py`

```py
0001 | # shared/metrics.py
0002 | import time
0003 | import logging
0004 | from typing import Dict, Any, Optional, List
0005 | from dataclasses import dataclass, field
0006 | from datetime import datetime
0007 | from collections import defaultdict, Counter
0008 | import json
0009 | 
0010 | logger = logging.getLogger(__name__)
0011 | 
0012 | @dataclass
0013 | class PerformanceMetrics:
0014 |     """Métricas de rendimiento simplificadas"""
0015 |     operation: str
0016 |     start_time: float
0017 |     end_time: Optional[float] = None
0018 |     success: bool = True
0019 |     error: Optional[str] = None
0020 |     metadata: Dict[str, Any] = field(default_factory=dict)
0021 |     
0022 |     @property
0023 |     def duration_seconds(self) -> float:
0024 |         if self.end_time:
0025 |             return self.end_time - self.start_time
0026 |         return 0.0
0027 | 
0028 | class MetricsCollector:
0029 |     """Colector de métricas optimizado y simplificado"""
0030 |     
0031 |     def __init__(self):
0032 |         self.metrics: List[PerformanceMetrics] = []
0033 |         self.counters: Dict[str, int] = defaultdict(int)
0034 |         self.start_time = time.time()
0035 |     
0036 |     def record_complete_analysis(self, file_path: str, vulnerability_count: int = 0,
0037 |                                confirmed_count: int = 0, total_time: float = 0.0,
0038 |                                chunking_used: bool = False, language: Optional[str] = None,
0039 |                                success: bool = True, error: Optional[str] = None):
0040 |         """Record complete analysis metrics"""
0041 |         
0042 |         metric = PerformanceMetrics(
0043 |             operation="complete_analysis",
0044 |             start_time=time.time() - total_time,
0045 |             end_time=time.time(),
0046 |             success=success,
0047 |             error=error,
0048 |             metadata={
0049 |                 "file_path": file_path,
0050 |                 "vulnerability_count": vulnerability_count,
0051 |                 "confirmed_count": confirmed_count,
0052 |                 "chunking_used": chunking_used,
0053 |                 "language": language
0054 |             }
0055 |         )
0056 |         
0057 |         self.metrics.append(metric)
0058 |         self.counters["analyses_total"] += 1
0059 |         if success:
0060 |             self.counters["analyses_successful"] += 1
0061 |         
0062 |         logger.info(f"Analysis metrics recorded: {vulnerability_count} vulns, {total_time:.2f}s")
0063 |     
0064 |     def record_triage_analysis(self, vulnerability_count: int, analysis_time: float,
0065 |                              success: bool, chunk_id: Optional[int] = None,
0066 |                              error: Optional[str] = None):
0067 |         """Record triage analysis metrics"""
0068 |         
0069 |         metric = PerformanceMetrics(
0070 |             operation="triage_analysis",
0071 |             start_time=time.time() - analysis_time,
0072 |             end_time=time.time(),
0073 |             success=success,
0074 |             error=error,
0075 |             metadata={
0076 |                 "vulnerability_count": vulnerability_count,
0077 |                 "chunk_id": chunk_id,
0078 |                 "throughput": vulnerability_count / analysis_time if analysis_time > 0 else 0
0079 |             }
0080 |         )
0081 |         
0082 |         self.metrics.append(metric)
0083 |         self.counters["triage_calls"] += 1
0084 |     
0085 |     def record_remediation_generation(self, vulnerability_type: str, count: int,
0086 |                                     generation_time: float, success: bool,
0087 |                                     error: Optional[str] = None):
0088 |         """Record remediation generation metrics"""
0089 |         
0090 |         metric = PerformanceMetrics(
0091 |             operation="remediation_generation",
0092 |             start_time=time.time() - generation_time,
0093 |             end_time=time.time(),
0094 |             success=success,
0095 |             error=error,
0096 |             metadata={
0097 |                 "vulnerability_type": vulnerability_type,
0098 |                 "count": count
0099 |             }
0100 |         )
0101 |         
0102 |         self.metrics.append(metric)
0103 |         self.counters["remediation_calls"] += 1
0104 |     
0105 |     def record_report_generation(self, report_type: str, file_size: int = 0,
0106 |                                vulnerability_count: int = 0, success: bool = True,
0107 |                                error: Optional[str] = None):
0108 |         """Record report generation metrics"""
0109 |         
0110 |         metric = PerformanceMetrics(
0111 |             operation="report_generation",
0112 |             start_time=time.time(),
0113 |             end_time=time.time(),
0114 |             success=success,
0115 |             error=error,
0116 |             metadata={
0117 |                 "report_type": report_type,
0118 |                 "file_size": file_size,
0119 |                 "vulnerability_count": vulnerability_count
0120 |             }
0121 |         )
0122 |         
0123 |         self.metrics.append(metric)
0124 |         self.counters["reports_generated"] += 1
0125 |     
0126 |     def get_summary(self) -> Dict[str, Any]:
0127 |         """Get performance summary"""
0128 |         
0129 |         total_analyses = self.counters.get("analyses_total", 0)
0130 |         successful_analyses = self.counters.get("analyses_successful", 0)
0131 |         
0132 |         if total_analyses == 0:
0133 |             return {"message": "No metrics recorded"}
0134 |         
0135 |         # Calculate averages
0136 |         analysis_metrics = [m for m in self.metrics if m.operation == "complete_analysis"]
0137 |         avg_analysis_time = sum(m.duration_seconds for m in analysis_metrics) / len(analysis_metrics) if analysis_metrics else 0
0138 |         
0139 |         session_duration = time.time() - self.start_time
0140 |         
0141 |         return {
0142 |             "session_duration_seconds": session_duration,
0143 |             "total_analyses": total_analyses,
0144 |             "successful_analyses": successful_analyses,
0145 |             "success_rate": successful_analyses / total_analyses if total_analyses > 0 else 0,
0146 |             "average_analysis_time": avg_analysis_time,
0147 |             "triage_calls": self.counters.get("triage_calls", 0),
0148 |             "remediation_calls": self.counters.get("remediation_calls", 0),
0149 |             "reports_generated": self.counters.get("reports_generated", 0)
0150 |         }
0151 |     
0152 |     def export_metrics(self, output_file: Optional[str] = None) -> str:
0153 |         """Export all metrics to JSON"""
0154 |         
0155 |         export_data = {
0156 |             "export_timestamp": datetime.now().isoformat(),
0157 |             "session_start": datetime.fromtimestamp(self.start_time).isoformat(),
0158 |             "summary": self.get_summary(),
0159 |             "detailed_metrics": [
0160 |                 {
0161 |                     "operation": m.operation,
0162 |                     "duration_seconds": m.duration_seconds,
0163 |                     "success": m.success,
0164 |                     "error": m.error,
0165 |                     "metadata": m.metadata
0166 |                 } for m in self.metrics
0167 |             ],
0168 |             "counters": dict(self.counters)
0169 |         }
0170 |         
0171 |         json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
0172 |         
0173 |         if output_file:
0174 |             with open(output_file, 'w', encoding='utf-8') as f:
0175 |                 f.write(json_data)
0176 |             logger.info(f"Metrics exported to {output_file}")
0177 |         
0178 |         return json_data
```

---

## Resumen del Análisis

- **Total de archivos en el proyecto:** 52
- **Archivos procesados:** 24
- **Archivos excluidos:** 28
- **Total de líneas de código:** 5,281
