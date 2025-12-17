#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for mijia-mcp-server Python components
仅用于开发环境安装，不用于独立发布
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from __init__.py
version = {}
with open("__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="mijia-mcp-server",
    version=version.get("__version__", "2.0.0"),
    description="米家智能家居 MCP 服务器 - Python 适配器组件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MijiaAPI-MCP Contributors",
    license="GPL-3.0",
    url="https://github.com/yourusername/mijia-mcp-server",
    packages=find_packages(include=["adapter", "utils"]),
    install_requires=[
        "mijiaAPI>=3.0.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="mijia xiaomi smart-home iot mcp model-context-protocol",
)
