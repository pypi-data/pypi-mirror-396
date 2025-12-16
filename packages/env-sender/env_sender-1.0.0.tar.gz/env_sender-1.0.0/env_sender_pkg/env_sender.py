"""
Environment Variable Sender Module

This module loads environment variables from .env files and system environment,
then sends them to a specified API endpoint.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union
from pathlib import Path
from dotenv import load_dotenv


class EnvSender:
    """Class to load and send environment variables to an API."""
    
    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        env_file_path: Optional[Union[str, Path]] = None,
        exclude_keys: Optional[List[str]] = None,
        include_system_env: bool = True,
        timeout: int = 10
    ):
        """
        Initialize the EnvSender.
        
        Args:
            api_url: The API endpoint URL to send environment variables to
            api_key: Optional API key for authentication
            env_file_path: Path to .env file (default: .env in current directory)
            exclude_keys: List of environment variable keys to exclude from sending
            include_system_env: Whether to include system environment variables
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.api_key = api_key
        self.env_file_path = env_file_path or ".env"
        self.exclude_keys = exclude_keys or []
        self.include_system_env = include_system_env
        self.timeout = timeout
    
    def load_env_file(self) -> Dict[str, str]:
        """
        Load environment variables from .env file.
        
        Returns:
            Dictionary of environment variables from .env file
        """
        env_vars = {}
        env_path = Path(self.env_file_path)
        
        if env_path.exists():
            # Load .env file using python-dotenv
            load_dotenv(env_path, override=False)
            
            # Read .env file directly to get all variables
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if not line or line.startswith('#'):
                            continue
                        
                        # Parse KEY=VALUE format
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            
                            env_vars[key] = value
            except Exception as e:
                print(f"Warning: Could not read .env file: {e}")
        
        return env_vars
    
    def load_system_env(self) -> Dict[str, str]:
        """
        Load system environment variables.
        
        Returns:
            Dictionary of system environment variables
        """
        return dict(os.environ)
    
    def collect_all_env_vars(self) -> Dict[str, str]:
        """
        Collect all environment variables from .env file and system.
        
        Returns:
            Dictionary of all environment variables
        """
        all_vars = {}
        
        # Load from .env file
        env_file_vars = self.load_env_file()
        all_vars.update(env_file_vars)
        
        # Load from system environment
        if self.include_system_env:
            system_vars = self.load_system_env()
            # System vars take precedence (don't override .env vars)
            for key, value in system_vars.items():
                if key not in all_vars:
                    all_vars[key] = value
        
        # Apply exclude_keys if specified
        if self.exclude_keys:
            all_vars = {k: v for k, v in all_vars.items() if k not in self.exclude_keys}
        
        return all_vars
    
    def send_to_api(
        self,
        env_vars: Optional[Dict[str, str]] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Send environment variables to the specified API endpoint.
        
        Args:
            env_vars: Optional dictionary of env vars (if None, collects all)
            custom_headers: Optional custom headers for the request
            
        Returns:
            Dictionary with response status and data
        """
        # Collect environment variables if not provided
        if env_vars is None:
            env_vars = self.collect_all_env_vars()
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'EnvSender/1.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
            # Or use API key header if preferred:
            # headers['X-API-Key'] = self.api_key
        
        if custom_headers:
            headers.update(custom_headers)
        
        # Prepare payload
        payload = {
            'environment_variables': env_vars,
            'count': len(env_vars),
            'timestamp': str(os.path.getmtime(Path(self.env_file_path)) if Path(self.env_file_path).exists() else None)
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.content else {},
                'message': 'Environment variables sent successfully'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to send environment variables: {e}'
            }
    
    def send_raw(
        self,
        data: Dict,
        method: str = 'POST',
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Send raw data to the API endpoint.
        
        Args:
            data: Dictionary of data to send
            method: HTTP method (POST, PUT, PATCH)
            custom_headers: Optional custom headers
            
        Returns:
            Dictionary with response status and data
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'EnvSender/1.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        if custom_headers:
            headers.update(custom_headers)
        
        try:
            if method.upper() == 'POST':
                response = requests.post(
                    self.api_url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == 'PUT':
                response = requests.put(
                    self.api_url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == 'PATCH':
                response = requests.patch(
                    self.api_url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                return {
                    'success': False,
                    'error': f'Unsupported HTTP method: {method}'
                }
            
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.content else {},
                'message': 'Data sent successfully'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to send data: {e}'
            }


def send_env_to_api(
    api_url: str,
    api_key: Optional[str] = None,
    env_file_path: Optional[str] = None,
    exclude_keys: Optional[List[str]] = None,
    include_system_env: bool = True
) -> Dict:
    """
    Convenience function to quickly send environment variables to an API.
    
    Args:
        api_url: The API endpoint URL
        api_key: Optional API key for authentication
        env_file_path: Path to .env file
        exclude_keys: List of keys to exclude (optional)
        include_system_env: Whether to include system environment variables
        
    Returns:
        Dictionary with response status and data
    """
    sender = EnvSender(
        api_url=api_url,
        api_key=api_key,
        env_file_path=env_file_path,
        exclude_keys=exclude_keys,
        include_system_env=include_system_env
    )
    
    return sender.send_to_api()

