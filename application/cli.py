# application/cli.py
"""
CLI Interface - Clean & User-Friendly
=====================================

Responsibilities:
- Parse command-line arguments
- Display user-friendly messages
- Handle errors gracefully
- Orchestrate analysis workflow
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click

from application.factory import create_factory
from application.use_cases import AnalysisUseCase, CLIUseCase
from infrastructure.config import settings

# ════════════════════════════════════════════════════════════════════
# CLI GROUP
# ════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option("3.0.0", prog_name="Security Analysis Platform")
def cli():
    """🛡️  Security Analysis Platform v3.0 - LLM-Powered Vulnerability Analysis"""
    pass


# ════════════════════════════════════════════════════════════════════
# ANALYZE COMMAND
# ════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default='security_report.html', help='Output HTML file')
@click.option('-l', '--language', type=str, help='Programming language (python, java, abap)')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('--basic-mode', is_flag=True, help='Run without LLM analysis')
# LLM Provider Options
@click.option(
    '--llm-provider',
    type=click.Choice(['openai', 'watsonx'], case_sensitive=False),
    help='LLM provider (overrides env config)'
)
@click.option('--llm-model', type=str, help='Specific model (e.g., gpt-4o, gpt-4-turbo)')
# Feature Flags
@click.option('--no-dedup', is_flag=True, help='Disable duplicate removal')
@click.option(
    '--dedup-strategy',
    type=click.Choice(['strict', 'moderate', 'loose'], case_sensitive=False),
    default='moderate',
    help='Deduplication strategy'
)
@click.option('--force-chunking', is_flag=True, help='Force chunking for large datasets')
@click.option('--disable-chunking', is_flag=True, help='Disable chunking completely')
def analyze(
    input_file, output, language, verbose, basic_mode,
    llm_provider, llm_model,
    no_dedup, dedup_strategy,
    force_chunking, disable_chunking
):
    """
    Analyze security vulnerabilities from SAST tool output
    
    Example:
        security-analyzer analyze vulnerabilities.json
        security-analyzer analyze scan.json --llm-provider openai -o report.html
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
    
    # LLM Configuration
    if llm_provider:
        click.echo(f"🤖 LLM Provider: {llm_provider.upper()}")
    if llm_model:
        click.echo(f"📦 LLM Model: {llm_model}")
    
    # Feature flags
    if no_dedup:
        click.echo("🔄 Deduplication: DISABLED")
    else:
        click.echo(f"🔄 Deduplication: {dedup_strategy.upper()}")
    
    if basic_mode:
        click.echo("⚡ Mode: BASIC (no LLM)")
    
    click.echo("")
    
    try:
        # Run analysis
        success = asyncio.run(_run_analysis(
            input_file=input_file,
            output=output,
            language=language,
            verbose=verbose,
            basic_mode=basic_mode,
            llm_provider=llm_provider,
            llm_model=llm_model,
            enable_dedup=not no_dedup,
            dedup_strategy=dedup_strategy,
            force_chunking=force_chunking,
            disable_chunking=disable_chunking
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
    basic_mode: bool,
    llm_provider: Optional[str],
    llm_model: Optional[str],
    enable_dedup: bool,
    dedup_strategy: str,
    force_chunking: bool,
    disable_chunking: bool
) -> bool:
    """Execute analysis workflow"""
    
    try:
        # Create factory with overrides
        factory = create_factory(
            llm_provider_override=llm_provider,
            llm_model_override=llm_model
        )
        
        # Configure deduplication
        factory.enable_dedup = enable_dedup
        factory.dedup_strategy = dedup_strategy
        
        # Check LLM availability
        if not basic_mode and not settings.has_llm_provider and not llm_provider:
            click.echo("⚠️  No LLM configured - switching to basic mode")
            basic_mode = True
        
        # Display active provider
        if not basic_mode:
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
        
        # Execute
        return await cli_use_case.execute_cli_analysis(
            input_file=input_file,
            output_file=output,
            language=language,
            verbose=verbose,
            disable_llm=basic_mode,
            force_chunking=force_chunking,
            disable_chunking=disable_chunking
        )
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


# ════════════════════════════════════════════════════════════════════
# VALIDATE COMMAND
# ════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """
    Validate input file format and structure
    
    Example:
        security-analyzer validate vulnerabilities.json
    """
    click.echo("="*60)
    click.echo("🔍 Validating Input File")
    click.echo("="*60)
    click.echo(f"\nFile: {input_file}\n")
    
    try:
        from core.services.scanner import ScannerService
        
        scanner = ScannerService()
        
        # Basic validation
        scanner._validate_file(input_file)
        click.echo("✅ File validation: PASSED")
        
        # Load and analyze
        raw_data = scanner._load_file(input_file)
        click.echo("✅ JSON format: VALID")
        
        # Structure analysis
        if isinstance(raw_data, list):
            click.echo(f"📊 Format: List with {len(raw_data)} items")
        elif isinstance(raw_data, dict):
            keys = list(raw_data.keys())[:5]
            click.echo(f"📊 Format: Object with keys: {keys}")
            
            # Look for vulnerabilities
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
            
            # CVSS check
            cvss_scores = [
                v.meta.get('cvss_score') for v in vulns
                if v.meta.get('cvss_score') is not None
            ]
            
            if cvss_scores:
                click.echo(f"\n📊 CVSS Scores:")
                click.echo(f"   Count: {len(cvss_scores)}")
                click.echo(f"   Min: {min(cvss_scores):.1f}")
                click.echo(f"   Max: {max(cvss_scores):.1f}")
                click.echo(f"   Avg: {sum(cvss_scores)/len(cvss_scores):.1f}")
            else:
                click.echo("\n⚠️  No CVSS scores found")
        
        click.echo("\n" + "="*60)
        click.echo("✅ Validation Complete")
        click.echo("="*60)
        
    except Exception as e:
        click.echo(f"\n❌ Validation failed: {e}")
        sys.exit(1)


# ════════════════════════════════════════════════════════════════════
# EXAMPLES COMMAND
# ════════════════════════════════════════════════════════════════════

@cli.command()
def examples():
    """Show usage examples"""
    click.echo("""
╔════════════════════════════════════════════════════════════════╗
║  🎓 Security Analysis Platform - Usage Examples               ║
╚════════════════════════════════════════════════════════════════╝

📝 BASIC USAGE:
   security-analyzer analyze vulnerabilities.json

🎯 WITH LLM PROVIDER:
   # Use OpenAI
   security-analyzer analyze scan.json --llm-provider openai
   
   # Use WatsonX
   security-analyzer analyze scan.json --llm-provider watsonx
   
   # Specify model
   security-analyzer analyze scan.json \\
       --llm-provider openai \\
       --llm-model gpt-4-turbo

💻 LANGUAGE-SPECIFIC:
   security-analyzer analyze abap_scan.json --language abap
   security-analyzer analyze py_scan.json --language python

🔧 CUSTOM OUTPUT:
   security-analyzer analyze scan.json -o my_report.html

🔄 DEDUPLICATION:
   # Strict (keep most findings)
   security-analyzer analyze scan.json --dedup-strategy strict
   
   # Moderate (balanced - default)
   security-analyzer analyze scan.json --dedup-strategy moderate
   
   # Loose (aggressive dedup)
   security-analyzer analyze scan.json --dedup-strategy loose
   
   # Disable deduplication
   security-analyzer analyze scan.json --no-dedup

⚡ MODES:
   # Basic mode (no LLM)
   security-analyzer analyze scan.json --basic-mode
   
   # Verbose output
   security-analyzer analyze scan.json --verbose

🧩 CHUNKING:
   # Force chunking (for large files)
   security-analyzer analyze large_scan.json --force-chunking
   
   # Disable chunking
   security-analyzer analyze scan.json --disable-chunking

🔍 VALIDATION:
   security-analyzer validate vulnerabilities.json

📚 COMPLETE EXAMPLE:
   security-analyzer analyze production_scan.json \\
       --llm-provider openai \\
       --llm-model gpt-4o \\
       --language java \\
       --dedup-strategy moderate \\
       -o prod_report.html \\
       --verbose

🔑 ENVIRONMENT VARIABLES:
   OPENAI_API_KEY=sk-proj-xxxxx           # OpenAI key
   RESEARCH_API_KEY=your_key              # WatsonX key
   LLM_PRIMARY_PROVIDER=openai            # Default provider
   LOG_LEVEL=INFO                         # Logging level
   CACHE_ENABLED=true                     # Enable caching
   DEDUP_STRATEGY=moderate                # Default dedup

💡 TIPS:
   • Use --verbose for detailed logs
   • Validate files before analysis
   • OpenAI is faster, WatsonX is cost-effective
   • Deduplication reduces noise significantly
   • Cache speeds up repeated analysis

📖 Documentation: https://github.com/your-org/security-analyzer
""")


# ════════════════════════════════════════════════════════════════════
# CONFIG COMMAND
# ════════════════════════════════════════════════════════════════════

@cli.command()
def config():
    """Display current configuration"""
    from infrastructure.config import settings
    
    click.echo("="*60)
    click.echo("⚙️  Current Configuration")
    click.echo("="*60)
    
    # LLM Configuration
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
    
    # Features
    click.echo("\n🔧 Features:")
    click.echo(f"   Cache: {'✅ Enabled' if settings.cache_enabled else '❌ Disabled'}")
    click.echo(f"   Deduplication: {'✅ Enabled' if settings.dedup_enabled else '❌ Disabled'}")
    click.echo(f"   Metrics: {'✅ Enabled' if settings.metrics_enabled else '❌ Disabled'}")
    
    # Cache
    if settings.cache_enabled:
        click.echo(f"\n💾 Cache:")
        click.echo(f"   Directory: {settings.cache_directory}")
        click.echo(f"   TTL: {settings.cache_ttl_hours} hours")
    
    # Chunking
    click.echo(f"\n🧩 Chunking:")
    click.echo(f"   Max vulns/chunk: {settings.chunking_max_vulnerabilities}")
    
    # Logging
    click.echo(f"\n📝 Logging:")
    click.echo(f"   Level: {settings.log_level}")
    
    click.echo("\n" + "="*60)


# ════════════════════════════════════════════════════════════════════
# TEST COMMAND
# ════════════════════════════════════════════════════════════════════

@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'watsonx']), help='Test specific provider')
def test(provider):
    """Test LLM connection"""
    from infrastructure.llm.client import LLMClient
    
    click.echo("="*60)
    click.echo("🧪 Testing LLM Connection")
    click.echo("="*60)
    
    # Determine provider
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
        # Create client
        client = LLMClient(llm_provider=test_provider)
        click.echo(f"✅ Client created")
        click.echo(f"   Model: {client.model_name}")
        
        # Test message
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


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    cli()
