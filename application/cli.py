# application/cli.py
"""
CLI Interface - Simplified Version
==================================
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click

from application.factory import create_factory
from application.use_cases import AnalysisUseCase, CLIUseCase
from infrastructure.config import settings

@click.group()
@click.version_option("3.0.0", prog_name="Security Analysis Platform")
def cli():
    """🛡️  Security Analysis Platform v3.0 - LLM-Powered Vulnerability Analysis"""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default='security_report.html', help='Output HTML file')
@click.option('-l', '--language', type=str, help='Programming language (python, java, abap)')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')

# LLM Provider
@click.option(
    '--llm-provider',
    type=click.Choice(['openai', 'watsonx'], case_sensitive=False),
    help='LLM provider (overrides env config)'
)
@click.option('--llm-model', type=str, help='Specific model (e.g., gpt-4o)')

# Chunking
@click.option('--force-chunking', is_flag=True, help='Force chunking for large datasets')
@click.option('--disable-chunking', is_flag=True, help='Disable chunking completely')

# 🎯 FILTERING OPTIONS (SIMPLIFIED)
@click.option(
    '--min-severity',
    type=click.Choice(['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'], case_sensitive=False),
    help='⚡ Filter by minimum severity. Example: --min-severity HIGH'
)
@click.option(
    '--max-vulns',
    type=int,
    help='📊 Limit maximum vulnerabilities. Example: --max-vulns 20'
)
@click.option(
    '--group-similar',
    is_flag=True,
    default=True,
    help='🔗 Group similar vulnerabilities (default: enabled)'
)
def analyze(
    input_file, output, language, verbose,
    llm_provider, llm_model,
    force_chunking, disable_chunking,
    min_severity, max_vulns, group_similar
):
    """
    Analyze security vulnerabilities with filtering
    
    📚 EXAMPLES:
    
    # Basic analysis
    llm-triage analyze scan.json
    
    # Filter by severity (only HIGH and CRITICAL)
    llm-triage analyze scan.json --min-severity HIGH
    
    # Limit to top 10 most critical
    llm-triage analyze scan.json --min-severity HIGH --max-vulns 10
    
    # Group similar vulnerabilities
    llm-triage analyze scan.json --group-similar
    
    # Complete example with LLM provider
    llm-triage analyze scan.json --min-severity HIGH --max-vulns 15 --llm-provider openai
    """
    
    # Display header
    click.echo("="*60)
    click.echo("🛡️  Security Analysis Platform v3.0")
    click.echo("="*60)
    
    # Display configuration
    click.echo(f"\n📁 Input:  {Path(input_file).name}")
    click.echo(f"📄 Output: {output}")
    
    if language:
        click.echo(f"💻 Language: {language}")
    
    # Display filters
    if min_severity:
        click.echo(f"⚡ Severity Filter: >= {min_severity.upper()}")
    
    if max_vulns:
        click.echo(f"📊 Max Vulnerabilities: {max_vulns}")
    
    if group_similar:
        click.echo("🔗 Grouping: Similar vulnerabilities enabled")
    
    # LLM Configuration
    if llm_provider:
        click.echo(f"🤖 LLM Provider: {llm_provider.upper()}")
    if llm_model:
        click.echo(f"📦 LLM Model: {llm_model}")
    
    click.echo("")
    
    try:
        # Run analysis
        success = asyncio.run(_run_analysis(
            input_file=input_file,
            output=output,
            language=language,
            verbose=verbose,
            llm_provider=llm_provider,
            llm_model=llm_model,
            force_chunking=force_chunking,
            disable_chunking=disable_chunking,
            min_severity=min_severity,
            max_vulns=max_vulns,
            group_similar=group_similar
        ))
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n\n🛑 Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Fatal error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


async def _run_analysis(
    input_file: str,
    output: str,
    language: Optional[str],
    verbose: bool,
    llm_provider: Optional[str],
    llm_model: Optional[str],
    force_chunking: bool,
    disable_chunking: bool,
    min_severity: Optional[str],
    max_vulns: Optional[int],
    group_similar: bool
) -> bool:
    """Execute analysis workflow with filtering"""
    
    try:
        # Create factory
        factory = create_factory(
            llm_provider_override=llm_provider,
            llm_model_override=llm_model
        )
        
        # Check LLM
        if not settings.has_llm_provider and not llm_provider:
            click.echo("⚠️  No LLM configured - analysis may be limited")
            click.echo("Set OPENAI_API_KEY or RESEARCH_API_KEY for full analysis\n")
        else:
            active_provider = factory._get_effective_provider()
            click.echo(f"✅ Using LLM: {active_provider.upper()}\n")
        
        # Create services
        analysis_use_case = AnalysisUseCase(
            scanner_service=factory.create_scanner_service(),
            triage_service=factory.create_triage_service(),
            remediation_service=factory.create_remediation_service(),
            reporter_service=factory.create_reporter_service(),
            chunker=factory.create_chunker(),
            metrics=factory.get_metrics()
        )
        
        # Create CLI use case
        cli_use_case = CLIUseCase(analysis_use_case)
        
        # Execute with filtering
        return await cli_use_case.execute_cli_analysis(
            input_file=input_file,
            output_file=output,
            language=language,
            verbose=verbose,
            force_chunking=force_chunking,
            disable_chunking=disable_chunking,
            min_severity=min_severity,
            max_vulns=max_vulns,
            group_similar=group_similar
        )
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


# ════════════════════════════════════════════════════════════════
# VALIDATE COMMAND
# ════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """Validate input file format and structure"""
    click.echo("="*60)
    click.echo("🔍 Validating Input File")
    click.echo("="*60)
    click.echo(f"\nFile: {input_file}\n")
    
    try:
        from core.services.scanner import ScannerService
        
        scanner = ScannerService()
        
        # Validate file
        scanner._validate_file(input_file)
        click.echo("✅ File validation: PASSED")
        
        # Load JSON
        raw_data = scanner._load_file(input_file)
        click.echo("✅ JSON format: VALID")
        
        # Structure analysis
        if isinstance(raw_data, list):
            click.echo(f"📊 Format: List with {len(raw_data)} items")
        elif isinstance(raw_data, dict):
            keys = list(raw_data.keys())[:5]
            click.echo(f"📊 Format: Object with keys: {keys}")
            
            # Look for findings
            for key in ['findings', 'vulnerabilities', 'issues', 'results']:
                if key in raw_data and isinstance(raw_data[key], list):
                    count = len(raw_data[key])
                    click.echo(f"🎯 Found {count} items in '{key}'")
                    break
        
        # Parse test
        vulns = scanner.parser.parse(raw_data)
        click.echo(f"\n✅ Parsing test: Found {len(vulns)} vulnerabilities")
        
        if vulns:
            # Severity distribution
            from collections import Counter
            severity_dist = Counter(v.severity.value for v in vulns)
            
            click.echo("\n📈 Severity Distribution:")
            for severity, count in severity_dist.items():
                click.echo(f"   {severity}: {count}")
        
        click.echo("\n" + "="*60)
        click.echo("✅ Validation Complete")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"\n❌ Validation failed: {e}")
        sys.exit(1)


# ════════════════════════════════════════════════════════════════
# EXAMPLES COMMAND
# ════════════════════════════════════════════════════════════════

@cli.command()
def examples():
    """Show usage examples"""
    click.echo("""
╔══════════════════════════════════════════════════════════════╗
║  🎓 Security Analysis Platform - Usage Examples             ║
╚══════════════════════════════════════════════════════════════╝

📝 BASIC USAGE:
   llm-triage analyze vulnerabilities.json

⚡ FILTER BY SEVERITY:
   # Only HIGH and CRITICAL
   llm-triage analyze scan.json --min-severity ALTA
   
   # Only CRITICAL
   llm-triage analyze scan.json --min-severity CRÍTICA

📊 LIMIT RESULTS (For quick analysis):
   # Analyze top 10 most critical
   llm-triage analyze scan.json --min-severity ALTA --max-vulns 10
   
   # Analyze top 20 high severity
   llm-triage analyze scan.json --min-severity ALTA --max-vulns 20

🔗 GROUP SIMILAR VULNERABILITIES:
   # Automatic grouping (enabled by default)
   llm-triage analyze scan.json --group-similar

🎯 WITH LLM PROVIDER:
   # Use OpenAI
   llm-triage analyze scan.json --llm-provider openai
   
   # Use WatsonX
   llm-triage analyze scan.json --llm-provider watsonx
   
   # Specify model
   llm-triage analyze scan.json --llm-provider openai --llm-model gpt-4o

🎯 COMPLETE EXAMPLES:

   # Example 1: Focus on critical issues only
   llm-triage analyze large_scan.json \\
       --min-severity CRÍTICA \\
       --max-vulns 5 \\
       --group-similar

   # Example 2: Production scan with OpenAI
   llm-triage analyze production_scan.json \\
       --min-severity ALTA \\
       --llm-provider openai \\
       --llm-model gpt-4o \\
       --group-similar \\
       -o critical_report.html

   # Example 3: Quick triage of top issues
   llm-triage analyze scan.json \\
       --min-severity ALTA \\
       --max-vulns 15 \\
       -o quick_report.html

🔍 VALIDATION:
   llm-triage validate vulnerabilities.json

🔧 CONFIGURATION:
   llm-triage config

🧪 TEST LLM CONNECTION:
   llm-triage test --provider openai

📚 Documentation: https://github.com/jsuarezgz/llm-triage
""")


# ════════════════════════════════════════════════════════════════
# CONFIG COMMAND
# ════════════════════════════════════════════════════════════════

@cli.command()
def config():
    """Display current configuration"""
    from infrastructure.config import settings
    
    click.echo("="*60)
    click.echo("⚙️  Current Configuration")
    click.echo("="*60)
    
    click.echo("\n🤖 LLM Providers:")
    click.echo(f"   OpenAI:  {'✅ Configured' if settings.openai_api_key else '❌ Not configured'}")
    click.echo(f"   WatsonX: {'✅ Configured' if settings.watsonx_api_key else '❌ Not configured'}")
    
    if settings.has_llm_provider:
        try:
            provider = settings.get_available_llm_provider()
            click.echo(f"\n   Active Provider: {provider.upper()}")
            config = settings.get_llm_config(provider)
            click.echo(f"   Model: {config['model']}")
            click.echo(f"   Temperature: {config['temperature']}")
            click.echo(f"   Max Tokens: {config['max_tokens']}")
            click.echo(f"   Timeout: {config['timeout']}s")
        except Exception as e:
            click.echo(f"\n   ⚠️  Error: {e}")
    
    click.echo("\n🔧 Features:")
    click.echo(f"   Cache: {'✅ Enabled' if settings.cache_enabled else '❌ Disabled'}")
    click.echo(f"   Metrics: {'✅ Enabled' if settings.metrics_enabled else '❌ Disabled'}")
    
    if settings.cache_enabled:
        click.echo(f"\n💾 Cache:")
        click.echo(f"   Directory: {settings.cache_directory}")
        click.echo(f"   TTL: {settings.cache_ttl_hours} hours")
    
    click.echo(f"\n🧩 Chunking:")
    click.echo(f"   Max vulns/chunk: {settings.chunking_max_vulnerabilities}")
    
    click.echo(f"\n📝 Logging:")
    click.echo(f"   Level: {settings.log_level}")
    
    click.echo("\n" + "="*60)


# ════════════════════════════════════════════════════════════════
# TEST COMMAND
# ════════════════════════════════════════════════════════════════

@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'watsonx']), help='Test specific provider')
def test(provider):
    """Test LLM connection"""
    from infrastructure.llm.client import LLMClient
    
    click.echo("="*60)
    click.echo("🧪 Testing LLM Connection")
    click.echo("="*60)
    
    if provider:
        test_provider = provider
    else:
        if not settings.has_llm_provider:
            click.echo("\n❌ No LLM provider configured")
            click.echo("Set OPENAI_API_KEY or RESEARCH_API_KEY")
            sys.exit(1)
        test_provider = settings.get_available_llm_provider()
    
    click.echo(f"\n🤖 Testing: {test_provider.upper()}\n")
    
    try:
        client = LLMClient(llm_provider=test_provider)
        click.echo(f"✅ Client created")
        click.echo(f"   Model: {client.model_name}")
        
        async def run_test():
            test_message = "Return only this JSON: {\"status\": \"ok\", \"message\": \"test successful\"}"
            
            click.echo(f"\n📡 Sending test request...")
            response = await client._call_api(test_message, temperature=0.0)
            
            click.echo(f"✅ Response received ({len(response)} chars)")
            click.echo(f"\nPreview:\n{response[:200]}...")
        
        asyncio.run(run_test())
        
        click.echo("\n" + "="*60)
        click.echo("✅ Test Successful")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
