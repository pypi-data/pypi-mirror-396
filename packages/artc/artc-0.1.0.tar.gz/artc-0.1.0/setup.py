"""
ARTC - Adaptive Regression Tensor Compression
"""

from setuptools import setup, find_packages
import re

# Read version from __init__.py
def get_version():
    with open("artc/__init__.py", "r") as f:
        content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    raise RuntimeError("Version not found")

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="artc",
    version=get_version(),
    author="169B",
    author_email="your.email@example.com",
    description="ARTC-LITE: Lightweight IoT Tensor Encoding for sensor data compression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/169B/ARTC",
    project_urls={
        "Bug Tracker": "https://github.com/169B/ARTC/issues",
        "Documentation": "https://github.com/169B/ARTC#readme",
        "Source Code": "https://github.com/169B/ARTC",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Archiving :: Compression",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    keywords="compression, iot, sensors, tensor, lora, embedded, arduino, esp32",
)
