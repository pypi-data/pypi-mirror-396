# Trampoline Client

Python client for [Trampoline](https://github.com/rlange/trampoline) dynamic reverse proxy.

## Installation

```bash
pip install trampoline-client
```

## Usage

```python
from trampoline_client import TrampolineClient
import time

client = TrampolineClient(
    host="https://proxy.example.com",
    name="my-service",
    secret="your-secret",
    target="http://localhost:3000"
)

client.start()
time.sleep(1)

if client.connected:
    print(f"Service available at: {client.remote_address}")
    # https://proxy.example.com/my-service

client.stop()
```

## Load Balancing

```python
for i in range(3):
    client = TrampolineClient(
        host="https://proxy.example.com",
        name="my-service",
        existing_ok=True,  # Join existing pool
        target="http://localhost:3000"
    )
    client.start()
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `host` | Server URL | (required) |
| `name` | Tunnel name (cannot be `_`) | (required) |
| `secret` | Auth secret | `None` |
| `target` | Local server to forward to | `http://localhost:80` |
| `existing_ok` | Join existing pool | `False` |
| `daemon` | Daemon thread | `True` |

## Properties

| Property | Description |
|----------|-------------|
| `connected` | Connection active |
| `remote_address` | Public URL (e.g., `https://example.com/myapp`) |
| `pool_size` | Workers in pool |

## License

MIT
