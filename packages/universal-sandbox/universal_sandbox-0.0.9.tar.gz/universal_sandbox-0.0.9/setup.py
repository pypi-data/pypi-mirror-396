"""Setup script for Universal Sandbox Python SDK."""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="universal-sandbox",
    version="0.0.9",
    description="Python SDK for Universal Sandbox API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Universal Sandbox",
    author_email="support@ai-infra.org",
    url="https://github.com/universal-sandbox/sdk-python",
    project_urls={
        "Documentation": "https://api.sandbox.ai-infra.org/docs",
        "Source": "https://github.com/universal-sandbox/sdk-python",
        "Bug Reports": "https://github.com/universal-sandbox/sdk-python/issues",
    },
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.32.3",
        "pydantic>=2.12.0",
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
