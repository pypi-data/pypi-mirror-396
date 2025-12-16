#!/usr/bin/env python3
"""
Setup script for honest-chain package.
"""
from setuptools import setup, find_packages

setup(
    name="honest-chain",
    version="2.10.0",
    description="HONEST CHAIN SDK - Make AI Honest to God",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stellanium Ltd",
    author_email="admin@stellanium.io",
    url="https://github.com/Stellanium/aoai-genesis",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
