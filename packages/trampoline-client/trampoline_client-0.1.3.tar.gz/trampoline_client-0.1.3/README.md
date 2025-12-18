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

# Create client that forwards requests to your local server
client = TrampolineClient(
    host="wss://proxy.example.com",
    name="my-service",
    secret="your-secret",
    target="http://localhost:3000"  # Your local server
)

# Start the tunnel
client.start()

# Wait for connection
time.sleep(1)

# Check connection status
if client.connected:
    print(f"Tunnel is active at: {client.remote_address}")
    # e.g., "https://my-service.proxy.example.com"

# Stop the client when done
client.stop()
```

## Load Balancing

Multiple workers can connect with the same tunnel name for automatic load balancing:

```python
# Start multiple workers for the same tunnel
for i in range(3):
    client = TrampolineClient(
        host="wss://proxy.example.com",
        name="my-service",
        existing_ok=True,  # Allow joining existing pool
        target="http://localhost:3000"
    )
    client.start()

# Requests to my-service.proxy.example.com are distributed
# across all workers using round-robin
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `host` | Trampoline server WebSocket URL | (required) |
| `name` | Tunnel name to register | (required) |
| `secret` | Authentication secret | `None` |
| `target` | Local server to forward requests to | `http://localhost:80` |
| `existing_ok` | Allow joining existing tunnel pool for load balancing | `False` |
| `daemon` | Run as daemon thread | `True` |

## Properties

| Property | Description |
|----------|-------------|
| `connected` | `True` if WebSocket connection is active |
| `remote_address` | Public URL for external clients (e.g., `https://myapp.example.com`) |
| `pool_size` | Number of workers in this tunnel's pool |

## License

MIT
