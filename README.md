# SciTeX SSH (<code>scitex-ssh</code>)

<p align="center">
  <a href="https://scitex.ai">
    <img src="docs/scitex-logo-blue-cropped.png" alt="SciTeX" width="400">
  </a>
</p>

<p align="center"><b>Persistent SSH reverse tunnel for NAT traversal</b></p>

<p align="center">
  <a href="https://scitex-ssh.readthedocs.io/">Full Documentation</a> · <code>pip install scitex-ssh</code>
</p>

<!-- scitex-badges:start -->
[![PyPI](https://img.shields.io/pypi/v/scitex-ssh.svg)](https://pypi.org/project/scitex-ssh/)
[![Python](https://img.shields.io/pypi/pyversions/scitex-ssh.svg)](https://pypi.org/project/scitex-ssh/)
[![Tests](https://github.com/ywatanabe1989/scitex-ssh/actions/workflows/test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-ssh/actions/workflows/test.yml)
[![Install Test](https://github.com/ywatanabe1989/scitex-ssh/actions/workflows/install-test.yml/badge.svg)](https://github.com/ywatanabe1989/scitex-ssh/actions/workflows/install-test.yml)
[![Coverage](https://codecov.io/gh/ywatanabe1989/scitex-ssh/graph/badge.svg)](https://codecov.io/gh/ywatanabe1989/scitex-ssh)
[![Docs](https://readthedocs.org/projects/scitex-ssh/badge/?version=latest)](https://scitex-ssh.readthedocs.io/en/latest/)
[![License: AGPL v3](https://img.shields.io/badge/license-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
<!-- scitex-badges:end -->

---

## Problem and Solution

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Lab machines are behind NAT** -- collaborator can't `ssh lab-box` from the conference | **Persistent reverse tunnel** -- `scitex-ssh setup --port 8888 --bastion gw.example.com` installs an autossh systemd service; survives reboots + flaky networks |
| 2 | **Manual `autossh` + systemd unit authoring is tedious** -- half the team never bothers | **One-line lifecycle** -- `setup` / `status` / `remove` commands handle the unit file, env vars, restart policy |

## Architecture

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
pip install scitex-ssh
```

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
  https://raw.githubusercontent.com/ywatanabe1989/scitex-ssh/main/src/scitex_ssh/scripts/setup-autossh-service.sh
curl -o ~/.local/bin/remove-autossh-service.sh \
  https://raw.githubusercontent.com/ywatanabe1989/scitex-ssh/main/src/scitex_ssh/scripts/remove-autossh-service.sh
chmod +x ~/.local/bin/setup-autossh-service.sh ~/.local/bin/remove-autossh-service.sh

# Usage (requires sudo)
setup-autossh-service.sh -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa
remove-autossh-service.sh -p 2222
```

</details>

## Quick Start

```bash
# Set up a persistent reverse tunnel
scitex-ssh setup -p 2222 -b user@bastion.example.com -s ~/.ssh/id_rsa

# Check tunnel status
scitex-ssh status

# Remove a tunnel
scitex-ssh remove -p 2222
```

## Four Interfaces

<details>
<summary><strong>Python API ⭐</strong></summary>

<br>

```python
import scitex_ssh

# Set up tunnel
result = scitex_ssh.setup(2222, "user@bastion.example.com", "~/.ssh/id_rsa")

# Check status
result = scitex_ssh.status()
result = scitex_ssh.status(port=2222)

# Remove tunnel
result = scitex_ssh.remove(2222)
```

> **[Full API reference](https://scitex-ssh.readthedocs.io/en/latest/api/scitex_ssh.html)**

</details>

<details>
<summary><strong>CLI Commands ⭐⭐⭐</strong></summary>

<br>

```bash
scitex-ssh --help-recursive                # Show all commands
scitex-ssh setup -p 2222 -b user@host -s ~/.ssh/id_rsa
scitex-ssh status                          # All tunnels
scitex-ssh status -p 2222                  # Specific port
scitex-ssh remove -p 2222                  # Remove tunnel
scitex-ssh list-python-apis                # List Python APIs
scitex-ssh mcp list-tools                  # List MCP (Model Context Protocol) tools
```

> **[Full CLI reference](https://scitex-ssh.readthedocs.io/en/latest/quickstart.html)** · run `scitex-ssh --help-recursive` for the live tree.

</details>

<details>
<summary><strong>MCP Server ⭐⭐</strong></summary>

<br>

AI agents can manage tunnels autonomously.

| Tool | Description |
|------|-------------|
| `tunnel_setup` | Set up a persistent SSH reverse tunnel |
| `tunnel_status` | Check status of SSH reverse tunnels |
| `tunnel_remove` | Remove a persistent SSH reverse tunnel |

<sub><b>Table 2.</b> Three MCP tools. All tools accept JSON (JavaScript Object Notation) parameters and return JSON results.</sub>

```bash
scitex-ssh mcp start
```

> **[Full MCP specification](https://scitex-ssh.readthedocs.io/en/latest/api/scitex_ssh._mcp.html)** · run `scitex-ssh mcp list-tools` for the live registry.

</details>

<details>
<summary><strong>Skills ⭐⭐</strong></summary>

<br>

Bundled `_skills/scitex-ssh/` for AI-agent discovery (loaded by Claude
Code, MCP-aware tools, or `newb`):

| File | Purpose |
|------|---------|
| `SKILL.md` | Index — what this package does + tag map |
| `01_quick-start.md` | 30-second tour |
| `02_python-api.md` | Python API surface |
| `10_cli-commands.md` | CLI reference |
| `11_mcp-tools-for-ai-agents.md` | MCP tool catalog |
| `20_environment-variables.md` | `SCITEX_SSH_*` env vars |

```bash
scitex-ssh skills list
scitex-ssh skills get quick-start
```

> **[Full skills directory](https://github.com/ywatanabe1989/scitex-ssh/tree/develop/src/scitex_ssh/_skills/scitex-ssh)**

</details>

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SCITEX_SSH_BASTION_SERVER` | Default bastion server | `user@bastion.example.com` |
| `SCITEX_SSH_SECRET_KEY_PATH` | Default SSH (Secure Shell) private key path | `~/.ssh/id_rsa` |
| `SCITEX_SSH_DEBUG_MODE` | Enable verbose output (`1`) | `0` |

<p align="center"><sub><b>Table 3.</b> Environment variables. CLI flags take precedence when provided.</sub></p>

Set these in `.env` or your shell profile to avoid repeating `-b` and `-s` flags:

```bash
export SCITEX_SSH_BASTION_SERVER=user@bastion.example.com
export SCITEX_SSH_SECRET_KEY_PATH=~/.ssh/id_rsa

# Now just specify the port
scitex-ssh setup -p 2222
```

## Part of SciTeX

`scitex-ssh` is part of [**SciTeX**](https://scitex.ai). Install via
the umbrella with `pip install scitex[ssh]` to use as
`scitex.ssh` (Python) or `scitex ssh ...` (CLI).

SciTeX follows the Four Freedoms for Research below, inspired by
[the Free Software Definition](https://www.gnu.org/philosophy/free-sw.en.html):

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
