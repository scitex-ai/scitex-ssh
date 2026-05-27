---
description: |
  [TOPIC] Core
  [DETAILS] Core — see file body for details..
tags: [scitex-ssh-cli-commands]
version: 1.0.0
exported_via: installed
---

## CLI Commands

```bash
# Core
scitex-ssh setup --port <port> --bastion <host> --secret-key <path>
scitex-ssh status [--port <port>]
scitex-ssh remove --port <port>

# MCP server
scitex-ssh mcp start [--transport <str>] [--host <host>] [--port <port>]
scitex-ssh mcp doctor
scitex-ssh mcp list-tools
scitex-ssh mcp installation

# Introspection
scitex-ssh list-python-apis [-v]
```
