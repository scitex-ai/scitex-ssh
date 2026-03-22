# SciTeX Tunnel (<code>scitex-tunnel</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Persistent SSH (Secure Shell) reverse tunnel for NAT (Network Address Translation) traversal</b></p>

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

Machines behind NAT (Network Address Translation) or institutional firewalls cannot receive incoming SSH (Secure Shell) connections. Researchers running long experiments on lab workstations, HPC (High-Performance Computing) nodes, or edge devices need reliable remote access without manual port forwarding or VPN (Virtual Private Network) setup. Existing solutions (ngrok, cloudflared) often require external accounts or lack systemd integration for persistent, auto-recovering connections.

## Solution

SciTeX Tunnel creates **persistent reverse SSH tunnels** using autossh and systemd. Each tunnel runs as a managed service that auto-restarts on failure, survives reboots, and requires only a bastion server with SSH access.

```
┌─────────────────────────────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│  Lab Workstation (behind NAT/firewall)  │     │   Bastion Server     │     │  Remote Client   │
│                                         │     │   (public IP)        │     │  (laptop, etc.)  │
│  ┌──────────────────────────────────┐   │     │                      │     │                  │
│  │ systemd service                  │   │     │                      │     │                  │
│  │ autossh-tunnel-{port}.service    │   │     │                      │     │                  │
│  │   ┌──────────────────────────┐   │   │     │  ┌────────────────┐  │     │                  │
│  │   │ autossh                  │   │   │     │  │ sshd listening │  │     │                  │
│  │   │ (auto-reconnect daemon)  │───┼───┼─────┼──│ on port {port} │──┼─────│  ssh -p {port}   │
│  │   │                          │   │   │     │  │                │  │     │  bastion-server  │
│  │   └──────────────────────────┘   │   │     │  └────────────────┘  │     │                  │
│  └──────────────────────────────────┘   │     │                      │     │                  │
│                                         │     │                      │     │                  │
│  localhost:22 (SSH server)              │     │                      │     │                  │
└─────────────────────────────────────────┘     └──────────────────────┘     └──────────────────┘
          ────── reverse tunnel ──────►               ◄─── SSH connection ───
     -R {port}:localhost:22 bastion-server         ssh -p {port} bastion-server
```

<p align="center"><sub><b>Figure 1.</b> Architecture overview. The lab workstation initiates a reverse SSH tunnel to the bastion server. The remote client connects to the bastion server, which forwards the connection back through the tunnel to the lab workstation.</sub></p>

## How It Works

1. **`setup`** (requires **sudo**) writes a systemd unit file at `/etc/systemd/system/autossh-tunnel-{port}.service` that runs autossh with the reverse tunnel flag (`-R {port}:localhost:22`). The service is enabled (starts on boot) and started immediately.
2. **autossh** monitors the SSH connection and automatically re-establishes it if the connection drops — network interruptions, server reboots, or SSH timeouts are handled transparently.
3. **systemd** ensures the service survives host reboots (`WantedBy=multi-user.target`) and restarts on process failure (`Restart=always`, `RestartSec=3`).
4. A remote client connects to the bastion server on the forwarded port, and the connection is routed back through the tunnel to the lab workstation's SSH server (port 22).

| Operation | What it does |
|-----------|-------------|
| **setup** | Creates a systemd service at `/etc/systemd/system/autossh-tunnel-{port}.service` that maintains a reverse SSH tunnel via autossh |
| **status** | Queries systemd for tunnel service state (`systemctl status`) |
| **remove** | Stops, disables, and deletes the systemd service file |

<p align="center"><sub><b>Table 1.</b> Three operations. Each maps to a CLI (Command-Line Interface) command, Python function, and MCP (Model Context Protocol) tool.</sub></p>

## Installation

Requires `autossh` on the host machine (`sudo apt install autossh`).

```bash
pip install scitex-tunnel
```

> **SciTeX users**: `pip install scitex` already includes tunnel support.

> **Note**: `setup` and `remove` require **sudo** privileges because they write systemd service files to `/etc/systemd/system/` and run `systemctl` commands. You will be prompted for your password.

> **Disclaimer**: Before setting up reverse tunnels, please check your organization's acceptable use policy and network terms of service. Reverse tunnels may bypass institutional firewalls or network policies. The authors accept no responsibility for any consequences arising from the use of this software.

<details>
<summary><strong>Alternative: No-sudo setup via ~/.bashrc (no root access needed)</strong></summary>

<br>

If you do not have sudo access (e.g., shared HPC nodes, university servers), you can run autossh directly from your shell profile. Add to `~/.bashrc`:

```bash
# Persistent reverse tunnel without sudo — starts on every login
# Checks if tunnel is already running before starting
if ! pgrep -f "autossh.*-R 2222:localhost:22" > /dev/null 2>&1; then
    autossh -M 0 -f -N \
        -o "PubkeyAuthentication=yes" \
        -o "PasswordAuthentication=no" \
        -o "ServerAliveInterval=30" \
        -o "ServerAliveCountMax=3" \
        -i ~/.ssh/id_rsa \
        -R 2222:localhost:22 user@bastion.example.com
fi
```

**Trade-offs vs. systemd approach**:
- No sudo required
- Starts on user login (not on boot — requires an active login session)
- No automatic restart if autossh crashes between logins
- `-f` runs autossh in the background; `-M 0` relies on SSH keepalives

</details>

<details>
<summary><strong>Alternative: Persistent session via screen, tmux, or nohup (no root, survives logout)</strong></summary>

<br>

For long-running sessions on HPC or shared servers where you want the tunnel to survive logout:

```bash
# Option 1: screen (detaches from terminal)
screen -dmS tunnel autossh -M 0 -N \
    -o "ServerAliveInterval=30" -o "ServerAliveCountMax=3" \
    -i ~/.ssh/id_rsa -R 2222:localhost:22 user@bastion.example.com

# Reattach:  screen -r tunnel
# Kill:      screen -S tunnel -X quit

# Option 2: tmux
tmux new-session -d -s tunnel "autossh -M 0 -N \
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
    -i ~/.ssh/id_rsa -R 2222:localhost:22 user@bastion.example.com"

# Reattach:  tmux attach -t tunnel
# Kill:      tmux kill-session -t tunnel

# Option 3: nohup (simplest, no terminal multiplexer needed)
nohup autossh -M 0 -N \
    -o "ServerAliveInterval=30" -o "ServerAliveCountMax=3" \
    -i ~/.ssh/id_rsa -R 2222:localhost:22 user@bastion.example.com \
    > /dev/null 2>&1 &

# Kill:      pkill -f "autossh.*-R 2222:localhost:22"
```

**Trade-offs**: No sudo needed. Survives logout (unlike ~/.bashrc approach). Does not survive reboot — you must restart manually or add the command to a cron `@reboot` job.

</details>

<details>
<summary><strong>Alternative: Direct shell scripts (no Python required)</strong></summary>

<br>

If you have sudo access but prefer not to install Python, use the shell scripts directly:

```bash
# Download the scripts (one-time)
curl -o ~/.local/bin/setup-autossh-service.sh \
  https://raw.githubusercontent.com/ywatanabe1989/scitex-tunnel/main/src/scitex_tunnel/scripts/setup-autossh-service.sh
curl -o ~/.local/bin/remove-autossh-service.sh \
  https://raw.githubusercontent.com/ywatanabe1989/scitex-tunnel/main/src/scitex_tunnel/scripts/remove-autossh-service.sh
chmod +x ~/.local/bin/setup-autossh-service.sh ~/.local/bin/remove-autossh-service.sh

# Usage (requires sudo)
setup-autossh-service.sh -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa
remove-autossh-service.sh -p 2222
```

</details>

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
<summary><strong>Python API (Application Programming Interface)</strong></summary>

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
scitex-tunnel list-python-apis                # List Python APIs
scitex-tunnel mcp list-tools                  # List MCP (Model Context Protocol) tools
```

> **[Full CLI reference](https://scitex-tunnel.readthedocs.io/)**

</details>

<details>
<summary><strong>MCP (Model Context Protocol) Server — for AI Agents</strong></summary>

<br>

AI agents can manage tunnels autonomously.

| Tool | Description |
|------|-------------|
| `tunnel_setup` | Set up a persistent SSH reverse tunnel |
| `tunnel_status` | Check status of SSH reverse tunnels |
| `tunnel_remove` | Remove a persistent SSH reverse tunnel |

<sub><b>Table 2.</b> Three MCP tools. All tools accept JSON (JavaScript Object Notation) parameters and return JSON results.</sub>

```bash
scitex-tunnel mcp start
```

> **[Full MCP specification](https://scitex-tunnel.readthedocs.io/)**

</details>

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCITEX_TUNNEL_BASTION_SERVER` | Default bastion server | `user@bastion.example.com` |
| `SCITEX_TUNNEL_SECRET_KEY_PATH` | Default SSH (Secure Shell) private key path | `~/.ssh/id_rsa` |
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

The SciTeX system follows the Four Freedoms for Research below, inspired by [the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

>Four Freedoms for Research
>
>0. The freedom to **run** your research anywhere — your machine, your terms.
>1. The freedom to **study** how every step works — from raw data to final manuscript.
>2. The freedom to **redistribute** your workflows, not just your papers.
>3. The freedom to **modify** any module and share improvements with the community.
>
>AGPL-3.0 — because we believe research infrastructure deserves the same freedoms as the software it runs on.

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
</p>

<!-- EOF -->
