# application/cli.py
"""
🛡️ Security Analysis Platform CLI - Simplified & Optimized
===========================================================

Professional CLI for vulnerability analysis with LLM.
Version: 3.0.0
"""

import asyncio
import sys
import click
from pathlib import Path
from typing import Optional

from application.factory import create_factory
from application.use_cases import AnalysisUseCase, CLIUseCase
from infrastructure.config import settings
from shared.logger import setup_logging

__version__ = "3.0.0"


# ═══════════════════════════════════════════════════════════════════════════
# CLI GROUP
# ═══════════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(__version__, prog_name="Security Analysis Platform")
def cli():
    """
    🛡️ Security Analysis Platform v3.0
    
    LLM-powered vulnerability triage and remediation.
    
    Quick start:  llm-triage analyze scan.json --format semgrep
    """
    pass


# ═══════════════════════════════════════════════════════════════════════════
# ANALYZE COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default='security_report.html', help='Output HTML file')
@click.option('-l', '--language', type=click.Choice(
    ['python', 'java', 'javascript', 'abap', 'ruby', 'go', 'php'], case_sensitive=False
))
@click.option('-f', '--format', 'input_format', 
    type=click.Choice(['auto', 'semgrep', 'abap', 'sonarqube', 'generic'], case_sensitive=False),
    default='auto', show_default=True, help='Input JSON format'
)
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--llm-provider', type=click.Choice(['openai', 'watsonx'], case_sensitive=False))
@click.option('--llm-model', type=str, help='LLM model name')
@click.option('--min-severity', type=click.Choice(
    ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], case_sensitive=False
))
@click.option('--max-vulns', type=int, help='Maximum vulnerabilities to analyze')
@click.option('--group-similar/--no-group-similar', default=True)
@click.option('--force-chunking', is_flag=True)
@click.option('--disable-chunking', is_flag=True)
def analyze(input_file, output, language, input_format, verbose, llm_provider, 
            llm_model, min_severity, max_vulns, group_similar, 
            force_chunking, disable_chunking):
    """
    🔍 Analyze vulnerabilities with LLM triage
    
    \b
    Examples:
      llm-triage analyze scan.json
      llm-triage analyze scan.json --format semgrep --min-severity HIGH
      llm-triage analyze scan.json --format abap --language abap
      llm-triage analyze scan.json --min-severity HIGH --max-vulns 10
    """
    
    # Setup
    setup_logging('INFO' if verbose else 'WARNING')
    _print_header(input_file, output, input_format, min_severity, max_vulns)
    
    # Validate
    if force_chunking and disable_chunking:
        click.secho("❌ Cannot use both --force-chunking and --disable-chunking", fg='red', err=True)
        sys.exit(1)
    
    # Run
    tool_hint = None if input_format == 'auto' else input_format.lower()
    
    try:
        success = asyncio.run(_execute_analysis(
            input_file, output, language, tool_hint, llm_provider, llm_model,
            min_severity, max_vulns, group_similar, force_chunking, 
            disable_chunking, verbose
        ))
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        click.secho("\n🛑 Interrupted", fg='yellow', err=True)
        sys.exit(130)
    except Exception as e:
        click.secho(f"\n❌ Error: {e}", fg='red', err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


async def _execute_analysis(input_file, output, language, tool_hint, llm_provider,
                            llm_model, min_severity, max_vulns, group_similar,
                            force_chunking, disable_chunking, verbose):
    """Execute analysis pipeline"""
    
    factory = create_factory(llm_provider, llm_model)
    
    # Check LLM
    if not settings.has_llm_provider:
        click.secho("⚠️  No LLM configured (limited analysis)", fg='yellow')
    else:
        click.echo(f"✅ LLM: {factory._get_effective_provider().upper()}")
    
    # Create use case
    use_case = AnalysisUseCase(
        scanner_service=factory.create_scanner_service(),
        triage_service=factory.create_triage_service(),
        remediation_service=factory.create_remediation_service(),
        reporter_service=factory.create_reporter_service(),
        chunker=factory.create_chunker(),
        metrics=factory.get_metrics()
    )
    
    cli_use_case = CLIUseCase(use_case)
    
    # Execute
    return await cli_use_case.execute_cli_analysis(
        input_file=input_file,
        output_file=output,
        language=language,
        tool_hint=tool_hint,
        verbose=verbose,
        force_chunking=force_chunking,
        disable_chunking=disable_chunking,
        min_severity=min_severity,
        max_vulns=max_vulns,
        group_similar=group_similar
    )


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATE COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', 'expected_format')
@click.option('--show-sample', is_flag=True)
def validate(input_file, expected_format, show_sample):
    """
    🔍 Validate JSON file format
    
    \b
    Examples:
      llm-triage validate scan.json
      llm-triage validate scan.json --format semgrep
      llm-triage validate scan.json --show-sample
    """
    
    from core.services.scanner import ScannerService
    from adapters.parsers.parser_factory import ParserFactory
    from collections import Counter
    
    click.echo("="*70)
    click.echo("🔍 FILE VALIDATION")
    click.echo("="*70)
    click.echo(f"\nFile: {input_file}\n")
    
    try:
        scanner = ScannerService()
        parser_factory = ParserFactory()
        
        # Step 1: File validation
        click.echo("1️⃣  File validation...")
        scanner._validate_file(input_file)
        size = Path(input_file).stat().st_size
        click.secho(f"   ✅ Valid ({size:,} bytes)\n", fg='green')
        
        # Step 2: JSON structure
        click.echo("2️⃣  JSON parsing...")
        raw_data = scanner._load_file(input_file)
        click.secho("   ✅ Valid JSON\n", fg='green')
        
        # Step 3: Format detection
        click.echo("3️⃣  Format detection...")
        detected = parser_factory.detect_format(raw_data)
        
        if detected:
            click.secho(f"   ✅ Detected: {detected}", fg='green')
            if expected_format:
                if detected.lower() == expected_format.lower():
                    click.secho(f"   ✅ Matches expected: {expected_format}", fg='green')
                else:
                    click.secho(f"   ⚠️  Expected {expected_format}, got {detected}", fg='yellow')
        else:
            click.secho("   ⚠️  Could not detect format", fg='yellow')
        
        click.echo()
        
        # Step 4: Parse vulnerabilities
        click.echo("4️⃣  Parsing vulnerabilities...")
        vulns = parser_factory.parse(raw_data, tool_hint=expected_format)
        click.secho(f"   ✅ Parsed {len(vulns)} vulnerabilities\n", fg='green')
        
        if vulns:
            # Statistics
            severity_dist = Counter(v.severity.value for v in vulns)
            
            click.echo("📊 Severity Distribution:")
            for sev in ['CRÍTICA', 'ALTA', 'MEDIA', 'BAJA', 'INFO']:
                count = severity_dist.get(sev, 0)
                if count > 0:
                    bar = '█' * min(count, 40)
                    click.echo(f"   {sev:8s}: {count:4d} {bar}")
            
            # Sample
            if show_sample:
                click.echo("\n📄 Sample:")
                v = vulns[0]
                click.echo(f"   ID:       {v.id}")
                click.echo(f"   Title:    {v.title}")
                click.echo(f"   Severity: {v.severity.value}")
                click.echo(f"   File:     {v.file_path}:{v.line_number}")
        
        # Success
        click.echo("\n" + "="*70)
        click.secho("✅ VALIDATION SUCCESSFUL", fg='green', bold=True)
        click.echo("="*70)
        
        # Suggest command
        if detected and vulns:
            fmt = f"--format {detected.lower()}" if detected.lower() != 'auto' else ""
            click.echo(f"\n💡 Run: llm-triage analyze {input_file} {fmt}".strip())
        
    except Exception as e:
        click.secho(f"\n❌ Validation failed: {e}", fg='red', err=True)
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# CONFIG COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
def config():
    """⚙️  Show configuration"""
    
    click.echo("="*70)
    click.echo("⚙️  CONFIGURATION")
    click.echo("="*70)
    
    # LLM
    click.echo("\n🤖 LLM Providers:")
    click.echo(f"   OpenAI:  {'✅' if settings.openai_api_key else '❌'}")
    click.echo(f"   WatsonX: {'✅' if settings.watsonx_api_key else '❌'}")
    
    if settings.has_llm_provider:
        provider = settings.get_available_llm_provider()
        config = settings.get_llm_config(provider)
        click.echo(f"\n   Active: {provider.upper()}")
        click.echo(f"   Model:  {config['model']}")
        click.echo(f"   Temp:   {config['temperature']}")
    
    # Features
    click.echo("\n🔧 Features:")
    click.echo(f"   Cache:  {'✅' if settings.cache_enabled else '❌'}")
    click.echo(f"   Dedup:  {'✅' if settings.dedup_enabled else '❌'} ({settings.dedup_strategy})")
    click.echo(f"   Metrics: {'✅' if settings.metrics_enabled else '❌'}")
    
    # Parsers
    click.echo("\n📋 Parsers:")
    from adapters.parsers.parser_factory import ParserFactory
    for fmt in ParserFactory().get_supported_formats():
        click.echo(f"   • {fmt}")
    
    click.echo("\n" + "="*70)


# ═══════════════════════════════════════════════════════════════════════════
# FORMATS COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
def formats():
    """📋 List supported formats"""
    
    formats = [
        ("semgrep", "Semgrep static analysis", "semgrep --json --config auto"),
        ("abap", "ABAP Security Scanner", "abap-scanner --output scan.json"),
        ("sonarqube", "SonarQube issues export", "sonar-scanner"),
        ("generic", "Generic vulnerability JSON", "Any basic JSON format"),
    ]
    
    click.echo("\n📋 SUPPORTED FORMATS\n")
    
    for key, desc, example in formats:
        click.echo(f"  {key:12s} - {desc}")
        click.echo(f"               Example: {example}\n")
    
    click.echo("Usage: llm-triage analyze scan.json --format <key>\n")


# ═══════════════════════════════════════════════════════════════════════════
# TEST COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'watsonx'], case_sensitive=False))
def test(provider):
    """🧪 Test LLM connection"""
    
    if provider:
        test_provider = provider.lower()
    elif settings.has_llm_provider:
        test_provider = settings.get_available_llm_provider()
    else:
        click.secho("❌ No LLM provider configured", fg='red', err=True)
        sys.exit(1)
    
    click.echo(f"🧪 Testing {test_provider.upper()}...\n")
    
    try:
        from infrastructure.llm.client import LLMClient
        
        client = LLMClient(llm_provider=test_provider)
        click.echo(f"✅ Client created (model: {client.model_name})")
        
        async def run_test():
            response = await client._call_api(
                '{"status": "test"}', 
                temperature=0.0
            )
            click.echo(f"✅ Response received ({len(response)} chars)")
            return True
        
        asyncio.run(run_test())
        
        click.secho(f"\n✅ {test_provider.upper()} is working correctly", fg='green', bold=True)
        
    except Exception as e:
        click.secho(f"\n❌ Test failed: {e}", fg='red', err=True, bold=True)
        
        click.echo("\n💡 Troubleshooting:")
        if test_provider == 'openai':
            click.echo("   • Set OPENAI_API_KEY environment variable")
            click.echo("   • Verify key at platform.openai.com")
        elif test_provider == 'watsonx':
            click.echo("   • Set RESEARCH_API_KEY environment variable")
            click.echo("   • Check RESEARCH_API_URL if custom")
        
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLES COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@cli.command()
def examples():
    """📚 Show usage examples"""
    
    click.echo("""
╔══════════════════════════════════════════════════════════════════════╗
║  📚 USAGE EXAMPLES                                                   ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 BASIC
   llm-triage analyze scan.json
   llm-triage analyze scan.json -o report.html

📋 WITH FORMAT
   llm-triage analyze scan.json --format semgrep
   llm-triage analyze scan.json --format abap --language abap
   llm-triage analyze scan.json --format sonarqube

🔍 FILTERING
   llm-triage analyze scan.json --min-severity HIGH
   llm-triage analyze scan.json --min-severity HIGH --max-vulns 10
   llm-triage analyze scan.json --no-group-similar

🤖 LLM OPTIONS
   llm-triage analyze scan.json --llm-provider openai
   llm-triage analyze scan.json --llm-provider watsonx
   llm-triage analyze scan.json --llm-model gpt-4o

🎯 COMPLETE EXAMPLE
   llm-triage analyze production-scan.json \\
       --format semgrep \\
       --language python \\
       --min-severity HIGH \\
       --max-vulns 20 \\
       --llm-provider openai \\
       --output critical-report.html \\
       --verbose

⚡ PERFORMANCE
   llm-triage analyze large.json --force-chunking
   llm-triage analyze small.json --disable-chunking

🔧 UTILITIES
   llm-triage validate scan.json
   llm-triage validate scan.json --format semgrep --show-sample
   llm-triage config
   llm-triage test --provider openai
   llm-triage formats

╚══════════════════════════════════════════════════════════════════════╝
""")


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _print_header(input_file, output, input_format, min_severity, max_vulns):
    """Print analysis header"""
    click.echo("="*70)
    click.echo("🛡️  SECURITY ANALYSIS PLATFORM v3.0")
    click.echo("="*70)
    
    click.echo(f"\n📋 Configuration:")
    click.echo(f"   Input:  {Path(input_file).name}")
    click.echo(f"   Output: {output}")
    
    # Format
    if input_format == 'auto':
        click.echo(f"   Format: AUTO-DETECT")
    else:
        click.secho(f"   Format: {input_format.upper()}", fg='cyan')
    
    # Filters
    filters = []
    if min_severity:
        filters.append(f"severity≥{min_severity}")
    if max_vulns:
        filters.append(f"max={max_vulns}")
    
    if filters:
        click.secho(f"   Filters: {', '.join(filters)}", fg='yellow')
    
    click.echo()


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    try:
        cli(prog_name='llm-triage')
    except Exception as e:
        click.secho(f"Fatal error: {e}", fg='red', err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
