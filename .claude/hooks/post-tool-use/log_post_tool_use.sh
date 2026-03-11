#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-06 (ywatanabe)"
# File: ./.claude/hooks/post-tool-use/log_post_tool_use.sh

# Description: Logs all Claude Code tool responses (stdout/stderr/exit_code)
# to a structured log file. Uses tempfile for reliable JSON handling.

set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"

if [[ -n "$GIT_ROOT" ]]; then
    LOG_DIR="$GIT_ROOT/logs"
else
    LOG_DIR="$HOME/.claude/logs"
fi
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/claude-code.log"

# Read entire stdin into a tempfile (avoids env var size limits and escaping issues)
TMPFILE=$(mktemp /tmp/claude-hook-XXXXXX.json)
cat > "$TMPFILE"

# Parse and log with Python, reading from the tempfile
python3 - "$TMPFILE" "$LOG_FILE" << 'PYTHON_SCRIPT'
import json
import sys
import os
from datetime import datetime

tmpfile = sys.argv[1]
log_file = sys.argv[2]

MAX_STDOUT = 3000
MAX_STDERR = 1000

try:
    with open(tmpfile, "r") as f:
        raw = f.read()

    if not raw.strip():
        sys.exit(0)

    d = json.loads(raw)
    tool_name = d.get("tool_name", "unknown")
    tool_input = d.get("tool_input", {}) or {}
    tool_response = d.get("tool_response", {})

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "=" * 72,
        f"Time: {ts}",
        f"Tool: {tool_name}",
    ]

    # --- Tool input context ---
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        desc = tool_input.get("description", "")
        if cmd:
            # Show first 200 chars of command
            cmd_short = cmd.replace("\n", "\\n")[:200]
            lines.append(f"Cmd:  {cmd_short}")
        if desc:
            lines.append(f"Desc: {desc[:100]}")

    elif tool_name in ("Write", "Edit", "Read"):
        fp = tool_input.get("file_path", "")
        if fp:
            lines.append(f"File: {fp}")
        if tool_name == "Edit":
            old = (tool_input.get("old_string", "") or "")[:80].replace("\n", "\\n")
            new = (tool_input.get("new_string", "") or "")[:80].replace("\n", "\\n")
            if old:
                lines.append(f"Old:  {old}")
            if new:
                lines.append(f"New:  {new}")

    elif tool_name in ("Glob", "Grep"):
        pat = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        if pat:
            lines.append(f"Pattern: {pat}")
        if path:
            lines.append(f"Path: {path}")

    elif tool_name == "Task":
        desc = tool_input.get("description", "")
        prompt = (tool_input.get("prompt", "") or "")[:200].replace("\n", " ")
        agent = tool_input.get("subagent_type", "")
        if desc:
            lines.append(f"Desc: {desc}")
        if agent:
            lines.append(f"Agent: {agent}")
        if prompt:
            lines.append(f"Prompt: {prompt}")

    elif tool_name in ("WebFetch", "WebSearch"):
        url = tool_input.get("url", "")
        query = tool_input.get("query", "")
        if url:
            lines.append(f"URL: {url}")
        if query:
            lines.append(f"Query: {query}")

    else:
        # Generic: show first few fields
        for k, v in list(tool_input.items())[:3]:
            if v and isinstance(v, str):
                lines.append(f"{k}: {v[:100].replace(chr(10), '\\n')}")

    # --- Tool response ---
    stdout = ""
    stderr = ""
    exit_code = None

    if isinstance(tool_response, str):
        stdout = tool_response
    elif isinstance(tool_response, dict):
        stdout = tool_response.get("stdout", tool_response.get("output", "")) or ""
        stderr = tool_response.get("stderr", "") or ""
        exit_code = tool_response.get("exit_code", tool_response.get("exitCode"))
    elif tool_response is not None:
        stdout = str(tool_response)

    stdout = str(stdout) if stdout else ""
    stderr = str(stderr) if stderr else ""

    if exit_code is not None:
        lines.append(f"Exit: {exit_code}")

    if stdout and stdout not in ("None", "", "null"):
        lines.append("--- stdout ---")
        if len(stdout) > MAX_STDOUT:
            lines.append(stdout[:MAX_STDOUT])
            lines.append(f"... [truncated, {len(stdout)} total chars]")
        else:
            lines.append(stdout)

    if stderr and stderr not in ("None", "", "null"):
        lines.append("--- stderr ---")
        if len(stderr) > MAX_STDERR:
            lines.append(stderr[:MAX_STDERR])
            lines.append(f"... [truncated, {len(stderr)} total chars]")
        else:
            lines.append(stderr)

    # Write to log
    with open(log_file, "a") as f:
        f.write("\n".join(lines) + "\n\n")

except json.JSONDecodeError as e:
    with open(log_file, "a") as f:
        f.write(f"{'=' * 72}\n")
        f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"JSON Parse Error: {e}\n")
        # Dump first 500 chars of raw input for debugging
        with open(tmpfile, "r") as tf:
            raw_preview = tf.read()[:500]
        f.write(f"Raw input (first 500 chars): {raw_preview}\n\n")

except Exception as e:
    with open(log_file, "a") as f:
        f.write(f"{'=' * 72}\n")
        f.write(f"Hook Error: {e}\n\n")

PYTHON_SCRIPT

# Clean up
rm -f "$TMPFILE"

# Never block
exit 0

# EOF
