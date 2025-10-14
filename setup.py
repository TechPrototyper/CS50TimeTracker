#!/usr/bin/env python3
"""
SITR Setup Script
Installs SITR as a global command-line tool
"""
from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name="sitr",
    version="1.0.0",
    author="Tim Walter",
    author_email="tim@smartlogics.net",
    description="Simple Time Tracker - A personal time-tracking OS for the command line",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/TechPrototyper/CS50TimeTracker",
    packages=find_packages(exclude=["tests", "legacy"]),
    py_modules=[
        "sitr_cli",
        "sitr_api",
        "sitr_models",
        "api_client",
        "config_manager",
        "server_manager",
        "time_management_service",
        "database_manager",
        "database_repositories",
        "enums",
        "report_generator"
    ],
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "email-validator>=2.0.0",
        "sqlmodel>=0.0.14",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sitr=sitr_cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Time Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)
