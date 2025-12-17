# Universal Sandbox Python SDK

Python SDK for Universal Sandbox API.

📖 **[API Documentation](https://api.sandbox.ai-infra.org/docs)**

## Installation

```bash
pip install universal-sandbox
```

## Usage

For more detailed usage, please refer to [example.py](./example.py)

```python
from universal_sandbox import Sandbox

# Initialize client
# Get Sandbox API Token from https://ai-infra.org/
sandbox = Sandbox(token="sandbox-api-token")

# Check API health
health = sandbox.check_health()
print(health.status)

# Create a code interpreter sandbox
sb = sandbox.code_interpreter.create()
print(f"Sandbox ID: {sb.id}")
print(f"Provider: {sb.provider}")

# Execute code
result = sandbox.sandboxes.execute(sb.id, command="print('Hello, World!')")
print(result.stdout)

# Get sandbox info
info = sandbox.sandboxes.get(sb.id)
print(f"Status: {info.status}")

# List all sandboxes
sandbox_list = sandbox.sandboxes.list()
print(f"Total: {sandbox_list.total}")

# Delete sandbox
sandbox.sandboxes.delete(sb.id)
```

## API to SDK Mapping

| API Endpoint                       | SDK Interface                        |
|------------------------------------|--------------------------------------|
| `GET /health`                      | `sandbox.check_health()`             |
| `GET /regions`                     | `sandbox.list_regions()`             |
| `GET /limits`                      | `sandbox.get_limits()`               |
| `POST /sandboxes/code-interpreter` | `sandbox.code_interpreter.create()`  |
| `POST /sandboxes/browser`          | `sandbox.browser.create()`           |
| `POST /sandboxes/aio`              | `sandbox.aio.create()`               |
| `GET /sandboxes`                   | `sandbox.sandboxes.list()` |
| `GET /sandboxes/{id}`              | `sandbox.sandboxes.get()`    |
| `DELETE /sandboxes/{id}`           | `sandbox.sandboxes.delete()` |
| `POST /sandboxes/{id}/execute`     | `sandbox.sandboxes.execute()`        |
| `POST /admin/tokens`               | `sandbox.tokens.issue()`             |
| `POST /admin/tokens/{prefix}/revoke` | `sandbox.tokens.revoke()`          |
| `GET /admin/users/{user_id}/token` | `sandbox.tokens.get()`               |

## API Reference

### Sandbox Client

```python
from universal_sandbox import Sandbox

sandbox = Sandbox(
    token="your-token",           # API token (optional if auth disabled)
    base_url="https://...",       # Optional, defaults to production
)
```

### Root Methods

- `sandbox.check_health()` - Check API health status
- `sandbox.list_regions()` - List available regions for all providers
- `sandbox.get_limits()` - Get resource limits and current usage

### Sandbox Creation

- `sandbox.code_interpreter.create(provider, timeout_minutes, region, metadata)` - Create code interpreter
- `sandbox.browser.create(provider, timeout_minutes, region, metadata)` - Create browser sandbox
- `sandbox.aio.create(provider, timeout_minutes, region, metadata)` - Create all-in-one sandbox (only supports `provider="volcengine"`)

### Sandbox Management

- `sandbox.sandboxes.list()` - List all sandboxes
- `sandbox.sandboxes.get(sandbox_id)` - Get sandbox by ID
- `sandbox.sandboxes.delete(sandbox_id)` - Delete a sandbox
- `sandbox.sandboxes.execute(sandbox_id, command, timeout)` - Execute command

### Token Management (Admin)

- `sandbox.tokens.issue(...)` - Create a personal access token
- `sandbox.tokens.revoke(prefix)` - Revoke a token
- `sandbox.tokens.get(user_id)` - Get user's token
