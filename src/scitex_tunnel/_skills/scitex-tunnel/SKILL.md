---
description: Persistent SSH reverse tunnel for NAT traversal - auto-reconnecting tunnels for accessing machines behind firewalls. Use when setting up remote access to lab machines or HPC nodes.
allowed-tools: mcp__scitex__tunnel_*
---


# SSH Tunnels with scitex-tunnel

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-tunnel
import scitex_tunnel
scitex_tunnel.setup(...)

# Umbrella — pip install scitex
import scitex.tunnel
scitex.tunnel.setup(...)
```

`pip install scitex-tunnel` alone does NOT expose the `scitex` namespace;
`import scitex.tunnel` raises `ModuleNotFoundError`. To use the
`scitex.tunnel` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

## Sub-skills

### Core
- [01_quick-start.md](01_quick-start.md) — Quick start
- [02_python-api.md](02_python-api.md) — Python API

### Workflows
- [10_cli-commands.md](10_cli-commands.md) — CLI commands
- [11_mcp-tools-for-ai-agents.md](11_mcp-tools-for-ai-agents.md) — MCP tools for AI agents

### Standards
- [20_environment-variables.md](20_environment-variables.md) — Environment variables
