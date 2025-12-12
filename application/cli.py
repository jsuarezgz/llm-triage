# application/cli.py
#!/usr/bin/env python3
"""
🛡️ Security Analysis Platform v3.0 - Unified CLI
Análisis completo con arquitectura optimizada
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional
import click

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.factory import create_factory
from application.use_cases import AnalysisUseCase, CLIUseCase
from infrastructure.config import settings

@click.group()
@click.version_option("3.0", prog_name="Security Analysis Platform")
def cli():
    """🛡️ Security Analysis Platform v3.0 - Advanced Security Analysis"""
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True, readable=True))
@click.option('--output', '-o', default='security_report.html',
              help='Output HTML file')
@click.option('--language', '-l', 
              help='Programming language hint (abap, java, python, etc.)')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
@click.option('--basic-mode', is_flag=True,
              help='Run in basic mode without LLM analysis')
@click.option('--force-chunking', is_flag=True,
              help='Force chunking even for small files')
@click.option('--disable-chunking', is_flag=True,
              help='Disable chunking completely')
@click.option('--tool-hint',
              help='Scanner tool hint (abap_custom, semgrep, etc.)')
@click.option('--open-browser', is_flag=True,
              help='Open report in browser after generation')
def analyze(input_file, output, language, verbose, basic_mode, force_chunking, 
           disable_chunking, tool_hint, open_browser):
    """Analyze security vulnerabilities from SAST tool outputs"""
    
    # Display banner
    click.echo("""
╔══════════════════════════════════════════════════════════════╗
║    🛡️  SECURITY ANALYSIS PLATFORM v3.0                      ║
║                                                              ║
║    🤖 AI-Powered Triage • 🧩 Smart Chunking • 📊 Rich Reports ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Normalize output file
    if not output.lower().endswith('.html'):
        output = f"{output}.html"
    
    # Show configuration
    click.echo(f"📁 Input: {Path(input_file).name}")
    click.echo(f"📄 Output: {output}")
    if language:
        click.echo(f"🔤 Language: {language}")
    if tool_hint:
        click.echo(f"🔧 Tool: {tool_hint}")
    
    mode_desc = "Basic (No LLM)" if basic_mode else "Full AI Analysis"
    click.echo(f"⚙️  Mode: {mode_desc}")
    
    if verbose:
        click.echo("📝 Verbose logging enabled")
    
    click.echo()
    
    # Execute analysis
    try:
        success = asyncio.run(_run_analysis(
            input_file, output, language, verbose, basic_mode,
            force_chunking, disable_chunking, tool_hint
        ))
        
        if success and open_browser:
            _open_in_browser(output)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

async def _run_analysis(input_file: str, output: str, language: Optional[str],
                       verbose: bool, basic_mode: bool, force_chunking: bool,
                       disable_chunking: bool, tool_hint: Optional[str]) -> bool:
    """Execute analysis with proper error handling"""
    
    try:
        # Create factory and services
        factory = create_factory()
        
        if basic_mode or not settings.has_llm_provider:
            if not basic_mode:
                click.echo("⚠️  No LLM provider configured - running in basic mode")
            
            # Basic analysis
            analysis_use_case = AnalysisUseCase(
                scanner_service=factory.create_scanner_service(),
                reporter_service=factory.create_reporter_service(),
                metrics=factory.get_metrics()
            )
            
            cli_use_case = CLIUseCase(analysis_use_case)
            return await cli_use_case.execute_cli_analysis(
                input_file, output, language, verbose, disable_llm=True
            )
        
        else:
            # Full analysis with LLM
            analysis_use_case = AnalysisUseCase(
                scanner_service=factory.create_scanner_service(),
                triage_service=factory.create_triage_service(),
                remediation_service=factory.create_remediation_service(),
                reporter_service=factory.create_reporter_service(),
                chunker=factory.create_chunker(),
                metrics=factory.get_metrics()
            )
            
            cli_use_case = CLIUseCase(analysis_use_case)
            return await cli_use_case.execute_cli_analysis(
                input_file, output, language, verbose, disable_llm=False, 
                force_chunking=force_chunking
            )
    
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def _open_in_browser(output_file: str):
    """Open report in default browser"""
    try:
        import webbrowser
        file_url = f"file://{Path(output_file).absolute()}"
        webbrowser.open(file_url)
        click.echo(f"🌐 Opening report in browser: {file_url}")
    except Exception as e:
        click.echo(f"⚠️  Could not open browser: {e}")

@cli.command()
def setup():
    """Setup and validate system configuration"""
    click.echo("🔧 Setting up Security Analysis Platform v3.0...")
    
    # Check dependencies
    missing_deps = []
    required_packages = ['pydantic', 'click', 'jinja2']
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_deps.append(package)
    
    if missing_deps:
        click.echo(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        click.echo("Install with: pip install " + ' '.join(missing_deps))
        return
    
    click.echo("✅ Dependencies: OK")
    
    # Check API keys
    click.echo("\n🔑 API Key Status:")
    click.echo(f"  OpenAI: {'✅ Configured' if settings.openai_api_key else '❌ Missing'}")
    click.echo(f"  WatsonX: {'✅ Configured' if settings.watsonx_api_key else '❌ Missing'}")
    
    if not settings.has_llm_provider:
        click.echo("\n⚠️  No API keys configured!")
        click.echo("Set at least one API key:")
        click.echo("  export OPENAI_API_KEY='sk-your-key-here'")
        click.echo("  export RESEARCH_API_KEY='your-watsonx-key'")
        click.echo("\n💡 You can still run basic analysis without API keys")
    else:
        click.echo(f"\n✅ LLM Provider: {settings.get_available_llm_provider()}")
    
    # Test basic functionality
    click.echo("\n🧪 Testing system...")
    try:
        factory = create_factory()
        scanner = factory.create_scanner_service()
        click.echo("✅ Scanner service: OK")
        
        if settings.has_llm_provider:
            triage = factory.create_triage_service()
            remediation = factory.create_remediation_service()
            if triage and remediation:
                click.echo("✅ LLM services: OK")
        
        click.echo("\n🎉 Setup completed successfully!")
        click.echo("\nNext steps:")
        click.echo("1. Run analysis: security-analyzer analyze your_file.json")
        click.echo("2. View help: security-analyzer --help")
        
    except Exception as e:
        click.echo(f"❌ Setup test failed: {e}")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """Validate input file format and structure"""
    click.echo(f"🔍 Validating: {input_file}")
    
    try:
        from core.services.scanner import ScannerService
        
        scanner = ScannerService()
        
        # Basic validation
        scanner._validate_file(input_file)
        click.echo("✅ File validation: PASSED")
        
        # Load and analyze structure
        raw_data = scanner._load_file(input_file)
        click.echo("✅ JSON format: VALID")
        
        # Analyze structure
        if isinstance(raw_data, list):
            click.echo(f"📊 Format: List with {len(raw_data)} items")
        elif isinstance(raw_data, dict):
            keys = list(raw_data.keys())[:5]
            click.echo(f"📊 Format: Object with keys: {keys}")
            
            # Look for vulnerability containers
            for container_key in ['findings', 'vulnerabilities', 'issues', 'results']:
                if container_key in raw_data and isinstance(raw_data[container_key], list):
                    count = len(raw_data[container_key])
                    click.echo(f"🎯 Found {count} items in '{container_key}'")
                    
                    # Sample first item
                    if count > 0:
                        sample = raw_data[container_key][0]
                        if isinstance(sample, dict):
                            sample_keys = list(sample.keys())[:3]
                            click.echo(f"📋 Sample item keys: {sample_keys}")
                    break
        
        # Test parsing
        parser = scanner.parser
        vulnerabilities = parser.parse(raw_data)
        click.echo(f"✅ Parsing test: Found {len(vulnerabilities)} vulnerabilities")
        
        if vulnerabilities:
            severity_dist = {}
            for vuln in vulnerabilities:
                sev = vuln.severity.value
                severity_dist[sev] = severity_dist.get(sev, 0) + 1
            
            click.echo("📈 Severity distribution:")
            for severity, count in severity_dist.items():
                click.echo(f"  • {severity}: {count}")
    
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")

@cli.command()
def examples():
    """Show usage examples and help"""
    click.echo("""
🎓 Security Analysis Platform v3.0 - Usage Examples

📝 BASIC USAGE:
   security-analyzer analyze vulnerabilities.json

🎯 ADVANCED OPTIONS:
   # Custom output file
   security-analyzer analyze scan.json -o my_report.html

   # Specify programming language
   security-analyzer analyze abap_scan.json -l abap

   # Verbose output for debugging
   security-analyzer analyze results.json --verbose

   # Basic mode (no LLM analysis)
   security-analyzer analyze scan.json --basic-mode

   # Force or disable chunking
   security-analyzer analyze large_scan.json --force-chunking
   security-analyzer analyze small_scan.json --disable-chunking

   # Open in browser after generation
   security-analyzer analyze results.json --open-browser

🔧 SYSTEM COMMANDS:
   security-analyzer setup              # Test configuration
   security-analyzer validate file.json # Validate input format

📁 EXPECTED INPUT FORMAT:
   {
     "findings": [
       {
         "rule_id": "abap-sql-injection-001",
         "title": "SQL Injection Vulnerability",
         "message": "User input directly concatenated into SQL query",
         "severity": "HIGH",
         "location": {
           "file": "src/login.abap",
           "line": 42,
           "context": ["SELECT * FROM users", "WHERE name = '" + input + "'"]
         },
         "cwe": "CWE-89"
       }
     ]
   }

🔑 ENVIRONMENT VARIABLES:
   OPENAI_API_KEY                 # OpenAI GPT API key
   RESEARCH_API_KEY              # IBM WatsonX API key
   LOG_LEVEL                     # Logging level (DEBUG, INFO, WARNING, ERROR)
   CHUNKING_MAX_VULNS           # Max vulnerabilities per chunk (default: 15)
   CACHE_ENABLED                # Enable result caching (default: true)

💡 TIPS:
   • Use --verbose for detailed logs and debugging
   • The system auto-detects input format and language
   • LLM analysis significantly improves accuracy
   • Reports are interactive and include search functionality
   • Cache speeds up repeated analysis of same files

📚 For more information: https://github.com/your-org/security-analyzer
""")

@cli.command()
def metrics():
    """Display performance metrics from last session"""
    click.echo("📊 Performance Metrics")
    click.echo("=" * 50)
    
    # This would load from a metrics file in a real implementation
    click.echo("Feature not yet implemented - metrics will be shown during analysis")
    click.echo("Use --verbose flag during analysis to see detailed metrics")

if __name__ == '__main__':
    cli()
