# setup.py
from setuptools import setup, find_packages
from pathlib import Path

readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    try:
        long_description = readme_path.read_text(encoding="utf-8")
    except Exception:
        long_description = "LLM-Powered Vulnerability Triage"

setup(
    name="llm-triage",
    version="3.0.0",
    description="LLM-Powered Vulnerability Triage with CVSS Filtering and Deduplication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Security Team",
    author_email="security@research.com",
    url="https://github.com/your-org/llm-vuln-triage",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
        ],
        "openai": ["openai>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "llm-triage=application.cli:cli",
            "vuln-triage=application.cli:cli",
        ],
    },
    python_requires=">=3.8",
    package_data={
        "adapters.output": ["templates/*.html"],
    },
)
