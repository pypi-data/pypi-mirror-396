# Universal Sandbox Python SDK

Python SDK for Universal Sandbox API.

## Installation

```bash
pip install universal-sandbox
```

## Usage

```python
from universal_sandbox import Sandbox

# Initialize client (base_url defaults to https://api.sandbox.ai-infra.org)
sandbox = Sandbox(token="your-token")

# Check API health
health = sandbox.check_health()
print(health.status)

# Create a code interpreter sandbox
sb = sandbox.code_interpreter.create(provider="e2b", timeout_minutes=5)
print(f"Sandbox ID: {sb.id}")

# Execute code
result = sandbox.sandboxes.execute(sb.id, command="print('Hello, World!')")
print(result.stdout)

# Get sandbox info
info = sandbox.sandboxes.get_sandbox(sb.id)
print(f"Status: {info.status}")

# List all sandboxes
sandbox_list = sandbox.sandboxes.list_sandboxes()
print(f"Total: {sandbox_list.total}")

# Delete sandbox
sandbox.sandboxes.delete_sandbox(sb.id)
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
| `GET /sandboxes`                   | `sandbox.sandboxes.list_sandboxes()` |
| `GET /sandboxes/{id}`              | `sandbox.sandboxes.get_sandbox()`    |
| `DELETE /sandboxes/{id}`           | `sandbox.sandboxes.delete_sandbox()` |
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
- `sandbox.aio.create(provider, timeout_minutes, region, metadata)` - Create all-in-one sandbox

### Sandbox Management

- `sandbox.sandboxes.list_sandboxes()` - List all sandboxes
- `sandbox.sandboxes.get_sandbox(sandbox_id)` - Get sandbox by ID
- `sandbox.sandboxes.delete_sandbox(sandbox_id)` - Delete a sandbox
- `sandbox.sandboxes.execute(sandbox_id, command, timeout)` - Execute command

### Token Management (Admin)

- `sandbox.tokens.issue(...)` - Create a personal access token
- `sandbox.tokens.revoke(prefix)` - Revoke a token
- `sandbox.tokens.get(user_id)` - Get user's token
