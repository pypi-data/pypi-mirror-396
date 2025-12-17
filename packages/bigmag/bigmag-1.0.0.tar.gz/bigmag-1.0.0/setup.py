#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for BIgMAG package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bigmag",
    version="1.0.0",
    author="Jeferyd Yepes García, Laurent Falquet",
    author_email="jeferyd.yepes@unibe.ch",
    description="BIgMAG: Board InteGrating Metagenome-Assembled Genomes - A dashboard for metagenome quality metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffe107/BIgMAG",
    packages=find_packages(),
    package_data={
        "bigmag": ["assets/*"],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bigmag=bigmag.cli:main",
            "bigmag-lite=bigmag.cli_lite:main",
        ],
    },
)
