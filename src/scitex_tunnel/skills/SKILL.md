---
name: scitex-tunnel
description: Persistent SSH reverse tunnel for NAT traversal - auto-reconnecting tunnels for accessing machines behind firewalls. Use when setting up remote access to lab machines or HPC nodes.
allowed-tools: mcp__scitex__tunnel_*
---

# SSH Tunnels with scitex-tunnel

## Quick Start

```bash
# Setup a tunnel
scitex-tunnel setup --remote-host jump.example.com --remote-port 2222 --local-port 22

# Check status
scitex-tunnel status

# Remove tunnel
scitex-tunnel remove
```

## CLI Commands

```bash
scitex-tunnel setup --remote-host <host> --remote-port <port> --local-port <port>
scitex-tunnel status
scitex-tunnel remove

# Skills
scitex-tunnel skills list
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `tunnel_setup` | Create persistent SSH tunnel |
| `tunnel_status` | Check tunnel status |
| `tunnel_remove` | Remove tunnel |
