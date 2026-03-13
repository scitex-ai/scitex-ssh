# SciTeX Tunnel (<code>scitex-tunnel</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Persistent SSH reverse tunnel for NAT traversal</b></p>

<p align="center">
  <a href="https://badge.fury.io/py/scitex-tunnel"><img src="https://badge.fury.io/py/scitex-tunnel.svg" alt="PyPI version"></a>
  <a href="https://scitex-tunnel.readthedocs.io/"><img src="https://readthedocs.org/projects/scitex-tunnel/badge/?version=latest" alt="Documentation"></a>
  <a href="https://github.com/ywatanabe1989/scitex-tunnel/actions/workflows/ci.yml"><img src="https://github.com/ywatanabe1989/scitex-tunnel/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
</p>

<p align="center">
  <a href="https://scitex-tunnel.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-tunnel</code>
</p>

---

## Problem

Machines behind NAT or institutional firewalls cannot receive incoming SSH connections. Researchers running long experiments on lab workstations, HPC nodes, or edge devices need reliable remote access without manual port forwarding or VPN setup. Existing solutions (ngrok, cloudflared) often require external accounts or lack systemd integration for persistent, auto-recovering connections.

## Solution

SciTeX Tunnel creates **persistent reverse SSH tunnels** using autossh and systemd. Each tunnel runs as a managed service that auto-restarts on failure, survives reboots, and requires only a bastion server with SSH access.

```
Host (behind NAT) --[reverse tunnel]--> Bastion Server <--[SSH]--> Client
```

| Operation | What it does |
|-----------|-------------|
| **setup** | Creates a systemd service that maintains a reverse SSH tunnel via autossh |
| **status** | Queries systemd for tunnel service state |
| **remove** | Stops, disables, and deletes the systemd service |

<p align="center"><sub><b>Table 1.</b> Three operations. Each maps to a CLI command, Python function, and MCP tool.</sub></p>

## Installation

Requires `autossh` on the host machine (`sudo apt install autossh`).

```bash
pip install scitex-tunnel
```

> **SciTeX users**: `pip install scitex` already includes tunnel support.

## Quick Start

```bash
# Set up a persistent reverse tunnel
scitex-tunnel setup -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa

# Check tunnel status
scitex-tunnel status

# Remove a tunnel
scitex-tunnel remove -p 2222
```

## Three Interfaces

<details>
<summary><strong>Python API</strong></summary>

<br>

```python
import scitex_tunnel

# Set up tunnel
result = scitex_tunnel.setup(2222, "user@bastion.example.com", "~/.ssh/id_rsa")

# Check status
result = scitex_tunnel.status()
result = scitex_tunnel.status(port=2222)

# Remove tunnel
result = scitex_tunnel.remove(2222)
```

> **[Full API reference](https://scitex-tunnel.readthedocs.io/)**

</details>

<details>
<summary><strong>CLI Commands</strong></summary>

<br>

```bash
scitex-tunnel --help-recursive                # Show all commands
scitex-tunnel setup -p 2222 -b user@host -s ~/.ssh/id_rsa
scitex-tunnel status                          # All tunnels
scitex-tunnel status -p 2222                  # Specific port
scitex-tunnel remove -p 2222                  # Remove tunnel
scitex-tunnel list-python-apis                # List Python API
scitex-tunnel mcp list-tools                  # List MCP tools
```

> **[Full CLI reference](https://scitex-tunnel.readthedocs.io/)**

</details>

<details>
<summary><strong>MCP Server — for AI Agents</strong></summary>

<br>

AI agents can manage tunnels autonomously.

| Tool | Description |
|------|-------------|
| `tunnel_setup` | Set up a persistent SSH reverse tunnel |
| `tunnel_status` | Check status of SSH reverse tunnels |
| `tunnel_remove` | Remove a persistent SSH reverse tunnel |

<sub><b>Table 2.</b> Three MCP tools. All tools accept JSON parameters and return JSON results.</sub>

```bash
scitex-tunnel mcp start
```

> **[Full MCP specification](https://scitex-tunnel.readthedocs.io/)**

</details>

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCITEX_TUNNEL_BASTION_SERVER` | Default bastion server | `user@bastion.example.com` |
| `SCITEX_TUNNEL_SECRET_KEY_PATH` | Default SSH private key path | `~/.ssh/id_rsa` |
| `SCITEX_TUNNEL_DEBUG_MODE` | Enable verbose output (`1`) | `0` |

<p align="center"><sub><b>Table 3.</b> Environment variables. CLI flags take precedence when provided.</sub></p>

Set these in `.env` or your shell profile to avoid repeating `-b` and `-s` flags:

```bash
export SCITEX_TUNNEL_BASTION_SERVER=user@bastion.example.com
export SCITEX_TUNNEL_SECRET_KEY_PATH=~/.ssh/id_rsa

# Now just specify the port
scitex-tunnel setup -p 2222
```

## Part of SciTeX

Tunnel is part of [**SciTeX**](https://scitex.ai). When used inside the SciTeX framework, tunnel management integrates with the orchestrator:

```python
import scitex

# Manage tunnels through the unified interface
result = scitex.tunnel.setup(2222, "user@bastion.example.com", "~/.ssh/id_rsa")
scitex.tunnel.status()
```

The SciTeX ecosystem follows the Four Freedoms for researchers:

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->
