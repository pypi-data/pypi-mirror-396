"""
Setup script for env-sender package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Read version from package
version = "1.0.0"

setup(
    name="env-sender",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python package for loading and sending environment variables to APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/env-sender",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
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
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    keywords="environment variables, env, .env, api, configuration, secrets",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/env-sender/issues",
        "Source": "https://github.com/yourusername/env-sender",
        "Documentation": "https://github.com/yourusername/env-sender#readme",
    },
    include_package_data=True,
    zip_safe=False,
)

