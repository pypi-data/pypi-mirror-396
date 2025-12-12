# Connect Client for Python

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python library for interacting with the Trinity IoT Connect API. 
This library provides a clean interface for accessing the Connect API endpoints 
with comprehensive error handling, type hints, and good test coverage.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Using uv (recommended)

```bash
uv add trinity-connect-client
```

### Using pip

```bash
pip install trinity-connect-client
```

### From source

```bash
uv add git+https://github.com/trinity-telecomms/connect-py-client@v0.2.0
```

## Quick Start

```python
from trinity_connect_client import ConnectClient
from trinity_connect_client.exceptions import ResourceNotFoundError, UnauthorisedError

# Initialize the client
client = ConnectClient(
  api_version="v4",
  base_url="https://capi.trintel.co.za",
  token="your-service-account-token"
)

# Get a device by ID (returns dict)
try:
    device = client.devices.get(device_id=123)
    print(f"Device name: {device['name']}")
except ResourceNotFoundError:
    print("Device not found")
except UnauthorisedError:
    print("Access denied")
```

## Using Response Models

The library provides type-safe dataclass models for API responses:

```python
from trinity_connect_client import ConnectClient, Device, Company, Folder

client = ConnectClient(
    api_version="v4",
    base_url="https://capi.trintel.co.za",
    token="your-service-account-token"
)

# Get device as dict, then convert to model for type safety
device_dict = client.devices.get(device_id=123)
device = Device.from_dict(device_dict)

# Now you have full type hints and IDE autocomplete
print(f"Device: {device.name}")
print(f"UID: {device.uid}")
print(f"Status: {device.status}")

# Works with all response types
company_dict = client.orgs.get(company_id=1)
company = Company.from_dict(company_dict)

folders_list = client.orgs.get_folders(company_id=1)
folders = [Folder.from_dict(f) for f in folders_list]
```

**Available Models:**
- `Device` - Device information
- `Company` - Company/organization information
- `Folder` - Folder information
- `DeviceData` - Device telemetry data
- `DeviceEvent` - Device events
- `DeviceCommand` - Device commands

## Configuration

### Environment Variables

You can set your service account token via environment variables:

```bash
export CONNECT_API_TOKEN="your-service-account-token"
export CONNECT_API_BASE_URL="https://capi.trintel.co.za"
```

```python
import os
from trinity_connect_client import ConnectClient

client = ConnectClient(
    api_version="v4",
    base_url=os.getenv("CONNECT_API_BASE_URL"),
    token=os.getenv("CONNECT_API_TOKEN")
)
```

## Migration from v0.1.x to v0.2.0

Version 0.2.0 introduces breaking changes to authentication:

### What Changed
- Credentials-based authentication (email/password) has been removed
- Service account token authentication is now required
- Token caching logic has been removed (tokens are long-lived)
- The `auth` module and login endpoint are no longer available

### Upgrading

**Before (v0.1.x):**
```python
client = ConnectClient(
    base_url="https://capi.trintel.co.za",
    credentials={
        "email": "user@example.com",
        "password": "password"
    },
    cache=cache_instance  # Optional
)
```

**After (v0.2.0):**
```python
client = ConnectClient(
    base_url="https://capi.trintel.co.za",
    token="your-service-account-token"
)
```

**How to get a service account token:**
Contact your Trinity IoT administrator to generate a service account token for your application.

## Error Handling

The library raises specific exceptions for different error conditions:

```python
from trinity_connect_client.exceptions import (
    ResourceNotFoundError,
    UnauthorisedError,
    ConnectAPIError
)

try:
    device = client.devices.get(device_id=123)
except ResourceNotFoundError:
    print("Device not found (404)")
except UnauthorisedError:
    print("Authentication failed (401)")
except PermissionError:
    print("Access forbidden (403)")
except ConnectAPIError as e:
    print(f"API error: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/trinity-telecomms/connect-py-client.git
cd connect-py-client

# Install dependencies with uv
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=connect_client

# Run specific test file
uv run pytest tests/modules/devices/test_devices_api.py
```

### Building the Package

This project uses the `uv_build` backend for building distributions:

```bash
# Build both wheel and source distribution
uv build

# Build only wheel
uv build --wheel

# Build only source distribution
uv build --sdist

# Build to a specific directory
uv build --out-dir dist/
```

The built distributions will be available in the `dist/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`uv run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT Licence - 
see the [LICENCE](LICENSE) file for details.