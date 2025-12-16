#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for scoretest package.

Score Test for First-Order Autoregressive Model with Heteroscedasticity
Implementation of Tsai (1986) - Biometrika, 73(2), 455-460

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tsai-scoretest",
    version="1.0.0",
    author="Dr Merwan Roudane",
    author_email="merwanroudane920@gmail.com",
    description="Score Test for First-Order Autoregressive Model with Heteroscedasticity (Tsai 1986)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/merwanroudane/scoretest",
    project_urls={
        "Bug Tracker": "https://github.com/merwanroudane/scoretest/issues",
        "Documentation": "https://github.com/merwanroudane/scoretest#readme",
        "Source Code": "https://github.com/merwanroudane/scoretest",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "numpydoc>=1.5.0",
        ],
    },
    keywords=[
        "econometrics",
        "score test",
        "autocorrelation",
        "heteroscedasticity",
        "time series",
        "regression diagnostics",
        "AR(1)",
        "Durbin-Watson",
        "Cook-Weisberg",
        "Tsai test",
    ],
    include_package_data=True,
    zip_safe=False,
)
