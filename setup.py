# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="security-analysis-platform",
    version="3.0.0",
    description="Advanced Security Vulnerability Analysis with AI-Powered Triage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Security Team",
    author_email="security@yourcompany.com",
    url="https://github.com/your-org/security-analyzer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.0.0",
        "click>=8.0.0", 
        "jinja2>=3.0.0",
        "openai>=1.0.0",
        "asyncio-compat>=0.1.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "watsonx": [
            "ibm-watson-machine-learning>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "security-analyzer=application.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    package_data={
        "adapters.output": ["templates/*.html"],
    },
)
