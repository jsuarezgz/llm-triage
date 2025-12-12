#!/usr/bin/env python3
"""
🛡️ Security Analysis Platform v3.0
Advanced Security Vulnerability Analysis with AI-Powered Triage

Entry point for the security analysis platform.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run CLI
from application.cli import cli

if __name__ == '__main__':
    cli()
