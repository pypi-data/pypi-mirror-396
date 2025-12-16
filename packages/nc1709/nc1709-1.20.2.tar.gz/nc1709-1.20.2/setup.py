"""
Setup script for NC1709 CLI
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="nc1709",
    version="1.8.0",
    author="NC1709 Team",
    author_email="",
    description="A Local-First AI Developer Assistant with Multi-Model Orchestration and Agentic Architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nc1709",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "litellm>=1.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
        ],
        "memory": [
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
        ],
        "search": [
            "ddgs>=9.0.0",
        ],
        "notebook": [
            "nbconvert>=7.0.0",
            "nbformat>=5.0.0",
        ],
        "screenshot": [
            "playwright>=1.40.0",
        ],
        "all": [
            # Web dashboard
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
            # Memory/search
            "chromadb>=0.4.0",
            "sentence-transformers>=2.2.0",
            # Web search
            "ddgs>=9.0.0",
            # Notebook support
            "nbconvert>=7.0.0",
            "nbformat>=5.0.0",
            # Screenshots
            "playwright>=1.40.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nc1709=nc1709.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
