#!/usr/bin/env python3
"""
Setup script for signal-fabric-client
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from package
version = {}
with open("signal_fabric/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="signal-fabric-client",
    version=version["__version__"],
    description="gRPC client library for Signal Fabric server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PhaseQuant",
    author_email="",  # Add your email
    url="https://github.com/phasequant/signal-fabric",  # Update with actual repo URL
    project_urls={
        "Bug Tracker": "https://github.com/phasequant/signal-fabric/issues",
        "Source Code": "https://github.com/phasequant/signal-fabric",
    },
    packages=find_packages(include=["signal_fabric", "signal_fabric.*", "generated", "generated.*"]),
    python_requires=">=3.8",
    install_requires=[
        "grpcio>=1.76.0",
        "protobuf>=4.0.0",
    ],
    extras_require={
        "dev": [
            "grpcio-tools>=1.76.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    keywords="signal-fabric grpc client trading signals market-data",
    license="MIT",
    zip_safe=False,
)
