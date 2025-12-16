# env-sender

A Python package for loading environment variables from `.env` files and system environment, then sending them to a specified API endpoint.

## Features

- ✅ Load environment variables from `.env` files
- ✅ Read system environment variables
- ✅ Collects all environment variables (no filtering)
- ✅ Optional exclusion list for specific keys
- ✅ Optional API key authentication
- ✅ Custom headers support
- ✅ Error handling and timeout support
- ✅ Send raw custom data

## Installation

### From PyPI (when published)
```bash
pip install env-sender
```

### From source
```bash
# Clone the repository
git clone https://github.com/yourusername/env-sender.git
cd env-sender

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

## Quick Start

### Simple Usage

```python
from env_sender_pkg import send_env_to_api

# Send environment variables to an API
result = send_env_to_api(
    api_url="https://api.example.com/env",
    api_key="your-api-key"
)

if result['success']:
    print("✓ Environment variables sent successfully!")
else:
    print(f"✗ Failed: {result.get('error')}")
```

### Advanced Usage

```python
from env_sender_pkg import EnvSender

# Create an EnvSender instance
sender = EnvSender(
    api_url="https://api.example.com/env",
    api_key="your-api-key",
    env_file_path=".env",  # or specify custom path
    exclude_keys=["CUSTOM_EXCLUDE_KEY"],  # Additional keys to exclude
    include_system_env=True,
    timeout=30
)

# Collect environment variables
env_vars = sender.collect_all_env_vars()
print(f"Collected {len(env_vars)} environment variables")

# Send to API
result = sender.send_to_api(env_vars=env_vars)

if result['success']:
    print(f"✓ Sent successfully! Status: {result['status_code']}")
else:
    print(f"✗ Failed: {result.get('error')}")
```

### Send Custom Data

```python
from env_sender_pkg import EnvSender

sender = EnvSender(
    api_url="https://api.example.com/data",
    api_key="your-api-key"
)

custom_data = {
    "project": "my-project",
    "environment": "production",
    "custom_field": "custom_value"
}

result = sender.send_raw(
    data=custom_data,
    method="POST",
    custom_headers={"X-Custom-Header": "value"}
)
```

## API Reference

### `EnvSender` Class

#### Constructor Parameters

- `api_url` (str): The API endpoint URL to send environment variables to
- `api_key` (str, optional): API key for authentication
- `env_file_path` (str/Path, optional): Path to `.env` file (default: `.env`)
- `exclude_keys` (list, optional): List of environment variable keys to exclude
- `include_system_env` (bool): Whether to include system environment variables (default: True)
- `timeout` (int): Request timeout in seconds (default: 10)

#### Methods

- `load_env_file()`: Load environment variables from `.env` file
- `load_system_env()`: Load system environment variables
- `collect_all_env_vars()`: Collect all environment variables
- `send_to_api(env_vars=None, custom_headers=None)`: Send environment variables to API
- `send_raw(data, method='POST', custom_headers=None)`: Send raw data to API

### `send_env_to_api()` Function

Convenience function for quick usage.

```python
send_env_to_api(
    api_url: str,
    api_key: Optional[str] = None,
    env_file_path: Optional[str] = None,
    exclude_keys: Optional[List[str]] = None,
    include_system_env: bool = True
) -> Dict
```

## Note

This package collects and sends **all** environment variables by default. If you need to exclude specific keys, use the `exclude_keys` parameter. Be aware that this may include sensitive information like passwords, API keys, and tokens.

## Requirements

- Python 3.7+
- requests >= 2.31.0
- python-dotenv >= 1.0.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/yourusername/env-sender).

