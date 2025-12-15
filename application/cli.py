# application/cli.py
#!/usr/bin/env python3
"""
🛡️ Security Analysis Platform v3.0 - CLI
Complete command-line interface with filtering support
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


# ============================================================================
# CLI GROUP
# ============================================================================

@click.group()
@click.version_option("3.0", prog_name="LLM Vulnerability Triage")
def cli():
    """🛡️ LLM Vulnerability Triage v1.0 - Advanced Security Analysis"""
    pass


# ============================================================================
# ANALYZE COMMAND - MAIN FUNCTIONALITY
# ============================================================================

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output', default='security_report.html', help='Output file')
@click.option('-v', '--verbose', is_flag=True, help='Verbose logging')
@click.option('--no-dedup', is_flag=True, help='Disable duplicate removal')
def analyze(input_file, output, verbose, no_dedup):
    """Analyze security vulnerabilities from SAST results"""
    
    click.echo("🛡️  LLM Vulnerability Triage v3.0\n")
    click.echo(f"📁 {Path(input_file).name} → {output}")
    
    if no_dedup:
        click.echo("🔄 Deduplication: Disabled")
    
    try:
        success = asyncio.run(_run_analysis(
            input_file=input_file,
            output=output,
            verbose=verbose,
            dedup_enabled=not no_dedup
        ))
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Interrupted")
        sys.exit(1)



async def _run_analysis(input_file, output, verbose, min_cvss=0.0, 
                       dedup_enabled=True, dedup_mode='moderate'):
    """Execute analysis"""
    
    try:
        factory = create_factory()
        factory.enable_dedup = dedup_enabled
        factory.dedup_strategy = dedup_mode
        
        if not settings.has_llm_provider:
            click.echo("⚠️  No LLM - using basic mode")
        
        analysis = AnalysisUseCase(
            scanner_service=factory.create_scanner_service(),
            triage_service=factory.create_triage_service(),
            remediation_service=factory.create_remediation_service(),
            reporter_service=factory.create_reporter_service(),
            chunker=factory.create_chunker(),
            metrics=factory.get_metrics()
        )
        
        cli_case = CLIUseCase(analysis)
        return await cli_case.execute_cli_analysis(input_file, output, None, verbose)
        
    except Exception as e:
        click.echo(f"❌ {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


# ============================================================================
# VALIDATE COMMAND
# ============================================================================

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
                            
                            # Check for CVSS
                            if any(k in sample for k in ['cvss_score', 'cvss', 'score']):
                                click.echo(f"✅ CVSS scores detected")
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
            
            click.echo("\n📈 Severity distribution:")
            for severity, count in severity_dist.items():
                click.echo(f"  • {severity}: {count}")
            
            # Check CVSS scores
            cvss_scores = [v.meta.get('cvss_score') for v in vulnerabilities 
                          if v.meta.get('cvss_score') is not None]
            
            if cvss_scores:
                click.echo(f"\n📊 CVSS Statistics ({len(cvss_scores)} vulnerabilities with scores):")
                click.echo(f"  • Min: {min(cvss_scores):.1f}")
                click.echo(f"  • Max: {max(cvss_scores):.1f}")
                click.echo(f"  • Average: {sum(cvss_scores)/len(cvss_scores):.1f}")
                high_cvss = sum(1 for s in cvss_scores if s >= 7.0)
                click.echo(f"  • High severity (>= 7.0): {high_cvss}")
            else:
                click.echo(f"\n⚠️  No CVSS scores found in vulnerabilities")
    
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")


# ============================================================================
# EXAMPLES COMMAND
# ============================================================================

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

🆕 FILTERING OPTIONS:
   # Filter by minimum CVSS score (only analyze HIGH/CRITICAL)
   security-analyzer analyze scan.json --min-cvss 7.0
   
   # Disable duplicate removal (keep all duplicates)
   security-analyzer analyze scan.json --no-remove-duplicates
   
   # Change deduplication strategy
   security-analyzer analyze scan.json --dedup-strategy strict
   
   # Combined: CVSS + Deduplication
   security-analyzer analyze scan.json --min-cvss 6.5 --dedup-strategy loose

🔄 DEDUPLICATION STRATEGIES:
   • strict:   Exact match (file, line, type, description hash)
               - Safest, removes ~15-25% duplicates
   
   • moderate: Similar location (±5 lines) + same type + 80% description match
               - Recommended, removes ~25-35% duplicates [DEFAULT]
   
   • loose:    Fuzzy matching (same type, 70%+ description similarity)
               - Aggressive, removes ~35-50% duplicates

🧩 CHUNKING OPTIONS:
   # Force or disable chunking
   security-analyzer analyze large_scan.json --force-chunking
   security-analyzer analyze small_scan.json --disable-chunking

   # Open in browser after generation
   security-analyzer analyze results.json --open-browser

🔧 SYSTEM COMMANDS:
   security-analyzer setup              # Test configuration
   security-analyzer validate file.json # Validate input format
   security-analyzer examples           # Show this help
   security-analyzer metrics            # View performance metrics

📁 EXPECTED INPUT FORMAT:
   {
     "findings": [
       {
         "rule_id": "abap-sql-injection-001",
         "title": "SQL Injection Vulnerability",
         "message": "User input directly concatenated into SQL query",
         "severity": "HIGH",
         "cvss_score": 8.5,  // 🆕 Optional CVSS score (0.0-10.0)
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
   OPENAI_API_KEY          # OpenAI GPT API key
   RESEARCH_API_KEY        # IBM WatsonX API key
   LOG_LEVEL               # Logging level (DEBUG, INFO, WARNING, ERROR)
   CHUNKING_MAX_VULNS      # Max vulnerabilities per chunk (default: 5)
   CACHE_ENABLED           # Enable result caching (default: true)

💡 PRACTICAL EXAMPLES:

   # Focus on critical issues only
   security-analyzer analyze scan.json --min-cvss 9.0

   # Analyze with strict deduplication (most conservative)
   security-analyzer analyze scan.json --dedup-strategy strict

   # Quick scan without deduplication (see all findings)
   security-analyzer analyze scan.json --no-remove-duplicates --basic-mode

   # Production-ready analysis
   security-analyzer analyze production_scan.json \\
       --min-cvss 7.0 \\
       --dedup-strategy moderate \\
       -l java \\
       --open-browser

   # Debug mode with all details
   security-analyzer analyze scan.json --verbose --no-remove-duplicates

📊 CVSS SCORE RANGES:
   • 0.0-3.9:  LOW     (informational issues)
   • 4.0-6.9:  MEDIUM  (moderate risk)
   • 7.0-8.9:  HIGH    (serious vulnerabilities)
   • 9.0-10.0: CRITICAL (critical security flaws)

🔄 DEDUPLICATION IMPACT:
   Without dedup: 100% of findings (includes duplicates)
   Strict mode:   ~75-85% kept (very safe, minimal false removals)
   Moderate mode: ~65-75% kept (balanced, recommended)
   Loose mode:    ~50-65% kept (aggressive, may over-deduplicate)

📈 TYPICAL WORKFLOW:

   1. Validate your input file first:
      security-analyzer validate scan.json

   2. Run analysis with appropriate filters:
      security-analyzer analyze scan.json --min-cvss 7.0

   3. Review the HTML report in your browser

   4. Re-run with different settings if needed:
      security-analyzer analyze scan.json --dedup-strategy loose

💡 TIPS:
   • Use --verbose for detailed logs and debugging
   • The system auto-detects input format and language
   • LLM analysis significantly improves accuracy
   • Use --min-cvss to focus on critical vulnerabilities
   • Deduplication is enabled by default to reduce noise
   • Reports are interactive with search functionality
   • Cache speeds up repeated analysis of same files

📚 For more information: https://github.com/your-org/security-analyzer
""")


# ============================================================================
# METRICS COMMAND
# ============================================================================

@cli.command()
def metrics():
    """Display performance metrics from last session"""
    click.echo("📊 Performance Metrics")
    click.echo("=" * 50)
    
    # Check if metrics file exists
    metrics_file = Path(".security_cache/metrics.json")
    
    if metrics_file.exists():
        try:
            import json
            with open(metrics_file, 'r') as f:
                data = json.load(f)
            
            click.echo(f"\n📈 Session Summary:")
            click.echo(f"  • Total analyses: {data.get('total_analyses', 0)}")
            click.echo(f"  • Success rate: {data.get('success_rate', 0):.1%}")
            click.echo(f"  • Average time: {data.get('avg_time', 0):.2f}s")
            click.echo(f"  • Vulnerabilities analyzed: {data.get('total_vulns', 0)}")
            click.echo(f"  • Duplicates removed: {data.get('duplicates_removed', 0)}")
            
        except Exception as e:
            click.echo(f"❌ Could not load metrics: {e}")
    else:
        click.echo("\n⚠️  No metrics file found")
        click.echo("Metrics are collected during analysis.")
        click.echo("Run an analysis first, then check metrics again.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    cli()
