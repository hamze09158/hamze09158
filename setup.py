#!/usr/bin/env python3
"""
Setup script for Multi-Chain Wallet Recovery Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wallet-recovery-tool",
    version="1.0.0",
    author="Wallet Recovery Team",
    author_email="support@walletrecovery.com",
    description="Multi-chain cryptocurrency wallet recovery tool for partial seed phrases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wallet-recovery-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    entry_points={
        "console_scripts": [
            "wallet-recovery=wallet_recovery:main",
            "wallet-recovery-gui=gui_wallet_recovery:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.txt", "*.md"],
    },
    keywords="cryptocurrency wallet recovery bitcoin ethereum blockchain seed phrase",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wallet-recovery-tool/issues",
        "Source": "https://github.com/yourusername/wallet-recovery-tool",
        "Documentation": "https://github.com/yourusername/wallet-recovery-tool#readme",
    },
)