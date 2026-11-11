---
description: |
  [TOPIC] scitex-ssh CLI Reference
  [DETAILS] Top-level subcommands of `scitex-ssh` — exec, copy, sync, probe, attach, tunnel (setup/check-status/remove), mcp, list-python-apis.
tags: [scitex-ssh-cli-reference]
---

# CLI Reference

`scitex-ssh` is the entry point installed by `pip install scitex-ssh`.

```text
scitex-ssh [OPTIONS] COMMAND [ARGS]...
```

## Top-level options

| Flag                 | Purpose                                              |
|----------------------|------------------------------------------------------|
| `-V / --version`     | Show version and exit                                |
| `--help-recursive`   | Show help for the root and every subcommand          |
| `--json`             | Emit structured JSON output                          |
| `-h / --help`        | Show help                                            |

Tunnel policy uses `$SCITEX_SSH_CONFIG` when set; otherwise it reads
`~/.scitex/ssh/config.yaml`. A missing policy denies tunnel setup and removal.
The CLI does not automatically read `config.yaml` from the working directory.

## SSH primitives

| Command  | Purpose                                              |
|----------|------------------------------------------------------|
| `exec`   | Run a command on HOST via ssh                        |
| `copy`   | Copy files between local and `HOST:PATH`             |
| `sync`   | Synchronize a directory with rsync over SSH          |
| `probe`  | Check reachability and required remote executables   |
| `attach` | Open an interactive `ssh -t` session to HOST         |

```bash
scitex-ssh exec user@host "uname -a"
scitex-ssh copy ./local.txt user@host:/tmp/
scitex-ssh attach user@host
```

## Tunnel management

| Command                 | Purpose                                              |
|-------------------------|------------------------------------------------------|
| `tunnel setup`          | Install autossh systemd unit (reverse tunnel)        |
| `tunnel check-status`   | Show one or all installed tunnels                    |
| `tunnel remove`         | Stop + uninstall a tunnel by port                    |

Backward-compat shortcuts at the top level (`scitex-ssh setup-tunnel /
scitex-ssh show-status / scitex-ssh remove-tunnel`) are still accepted
but deprecated.

```bash
scitex-ssh tunnel setup --port 22 --bastion jump.example.com \
    --secret-key ~/.ssh/id_rsa
scitex-ssh tunnel check-status
scitex-ssh tunnel check-status --port 22
scitex-ssh tunnel remove --port 22
```

## Integration

| Command            | Purpose                                              |
|--------------------|------------------------------------------------------|
| `mcp`              | MCP server management (start / stop / status)        |
| `list-python-apis` | Print the public Python API surface                  |

## Allowlist gating

Persistent tunnel setup and removal consult the policy file above. A host
without an explicit entry inherits `default.tunnels`; without an applicable
allow rule, these operations fail with `PolicyError`. Informational
`check-status` and the SSH primitives do not use this allowlist. The SSH
transport still uses the caller’s SSH authentication and configuration.

The owning implementations are `_allowlist.config_path`, `_allowlist.is_allowed`,
and `_cli._tunnel.tunnel_status`. Behavioral controls are in
`tests/scitex_ssh/test__allowlist.py`, `tests/scitex_ssh/_cli/test__main.py`,
and `tests/scitex_ssh/_cli/test__primitives.py`.

## Examples

```bash
scitex-ssh tunnel check-status --json         # machine-readable
scitex-ssh --help-recursive | head -60        # full surface dump
```

See `02_quick-start.md` for the typical end-to-end flow.
