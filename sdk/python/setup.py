"""
Setup script for OmniSync Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="omnisync",
    version="0.1.0",
    author="OmniSync Team",
    description="OmniSync Protocol SDK for Python - Interoperability layer for AI agent frameworks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/omnisync/omnisync",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "websockets>=11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "langchain": ["langchain>=0.1.0"],
        "autogen": ["pyautogen>=0.2.0"],
        "crewai": ["crewai>=0.1.0"],
        "llamaindex": ["llama-index>=0.9.0"],
    },
)

