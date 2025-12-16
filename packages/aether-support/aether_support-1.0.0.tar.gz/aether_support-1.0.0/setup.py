"""
Aether Support Python SDK
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aether-support",
    version="1.0.0",
    author="Aether Support",
    author_email="developers@aether-support.com",
    description="Official Python SDK for Aether Support - AI-powered customer support platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aether-support/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/aether-support/python-sdk/issues",
        "Documentation": "https://docs.aether-support.com/sdk/python",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "async": ["aiohttp>=3.8.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-httpx>=0.22.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
)
