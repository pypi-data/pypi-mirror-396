"""
EnvSender - A Python package for loading and sending environment variables to APIs.

This package provides functionality to:
- Load environment variables from .env files
- Read system environment variables
- Filter sensitive keys automatically
- Send environment variables to API endpoints
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .env_sender import EnvSender, send_env_to_api

__all__ = ["EnvSender", "send_env_to_api"]

