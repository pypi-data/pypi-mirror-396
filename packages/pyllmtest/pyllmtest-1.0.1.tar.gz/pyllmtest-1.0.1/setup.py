"""
LLMTest Setup Configuration
============================
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="pyllmtest",
    version="1.0.1",
    author="Rahul Malik",
    author_email="rm324556@gmail.com",
    description="The most comprehensive LLM testing framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RahulMK22/llmtest",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
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
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0", "tiktoken>=0.5.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "all": [
            "openai>=1.0.0",
            "tiktoken>=0.5.0",
            "anthropic>=0.18.0",
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.990",
            "pytest-cov>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llmtest=llmtest.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "llm",
        "testing",
        "ai",
        "openai",
        "anthropic",
        "gpt",
        "claude",
        "pytest",
        "test-automation",
        "quality-assurance",
        "rag",
        "prompt-engineering",
    ],
    project_urls={
        "Bug Reports": "https://github.com/RahulMK22/llmtest/issues",
        "Source": "https://github.com/RahulMK22/llmtest",
        "Documentation": "https://llmtest.readthedocs.io",
    },
)
