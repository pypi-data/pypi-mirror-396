# -*- coding: utf-8 -*-
"""
Seigr Toolset Crypto (STC) - Setup Configuration
Post-classical cryptographic engine with entropy-regenerative architecture
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="seigr-toolset-crypto",
    version="0.4.3",
    author="Sergi Saldaña-Massó - Seigr Lab",
    author_email="sergism@gmail.com",
    description="Post-classical cryptographic engine with automated security profiles and high-performance streaming",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Seigr-lab/SeigrToolsetCrypto",
    project_urls={
        "Homepage": "https://github.com/Seigr-lab/SeigrToolsetCrypto",
        "Documentation": "https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/USAGE.md",
        "Source": "https://github.com/Seigr-lab/SeigrToolsetCrypto",
        "Sponsor": "https://github.com/sponsors/Seigr-lab",
        "Changelog": "https://github.com/Seigr-lab/SeigrToolsetCrypto/blob/main/docs/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "docs", "docs.*", "interfaces.ui", "interfaces.ui.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Information Technology",
        "Topic :: Security :: Cryptography",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="cryptography seigr entropy security profiles adaptive streaming post-classical lattice-based",
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage[toml]>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stc-cli=interfaces.cli.stc_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
