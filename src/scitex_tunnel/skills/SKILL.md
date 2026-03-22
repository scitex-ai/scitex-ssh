---
name: scitex-tunnel
description: Persistent SSH reverse tunnel for NAT traversal - auto-reconnecting tunnels for accessing machines behind firewalls. Use when setting up remote access to lab machines or HPC nodes.
allowed-tools: mcp__scitex__tunnel_*
---

# SSH Tunnels with scitex-tunnel

## Quick Start

```bash
# Setup a tunnel (port 22 exposed via bastion)
scitex-tunnel setup --port 22 --bastion jump.example.com --secret-key ~/.ssh/id_rsa

# Check status
scitex-tunnel status

# Check specific port
scitex-tunnel status --port 22

# Remove tunnel
scitex-tunnel remove --port 22
```

```python
from scitex_tunnel import setup, status, remove

# Create tunnel
result = setup(port=22, bastion_server="jump.example.com", secret_key_path="~/.ssh/id_rsa")
# Returns: {"success": True, "stdout": "...", "stderr": "..."}

# Check all tunnels
result = status()

# Check specific port
result = status(port=22)

# Remove tunnel
result = remove(port=22)

# Check availability
from scitex_tunnel import AVAILABLE, get_version
print(AVAILABLE)       # True/False
print(get_version())   # "0.x.y"
```

## Python API

| Function | Signature | Purpose |
|----------|-----------|---------|
| `setup()` | `setup(port, bastion_server=None, secret_key_path=None) -> dict` | Create persistent SSH tunnel |
| `status()` | `status(port=None) -> dict` | Check tunnel status (all or specific port) |
| `remove()` | `remove(port) -> dict` | Remove tunnel by port |
| `get_version()` | `get_version() -> str` | Get package version |
| `AVAILABLE` | `bool` | Whether tunnel dependencies are available |

## CLI Commands

```bash
# Core
scitex-tunnel setup --port <port> --bastion <host> --secret-key <path>
scitex-tunnel status [--port <port>]
scitex-tunnel remove --port <port>

# MCP server
scitex-tunnel mcp start [--transport <str>] [--host <host>] [--port <port>]
scitex-tunnel mcp doctor
scitex-tunnel mcp list-tools
scitex-tunnel mcp installation

# Introspection
scitex-tunnel list-python-apis [-v]
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SCITEX_TUNNEL_BASTION_SERVER` | Default bastion server (if --bastion not provided) |
| `SCITEX_TUNNEL_SECRET_KEY_PATH` | Default SSH key path (if --secret-key not provided) |

## MCP Tools (for AI agents)

| Tool | Parameters | Purpose |
|------|-----------|---------|
| `tunnel_setup` | `port`, `bastion_server`, `secret_key_path` | Create persistent SSH tunnel |
| `tunnel_status` | `port` (optional) | Check tunnel status |
| `tunnel_remove` | `port` | Remove tunnel |
