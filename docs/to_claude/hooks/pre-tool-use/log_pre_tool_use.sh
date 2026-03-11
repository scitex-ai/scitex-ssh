#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-09 16:51:51 (ywatanabe)"
# File: ./.claude/hooks/pre-tool-use/log_pre_tool_use.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

# Description: Logs all Claude Code tool uses to a timestamped log file

# Log file location - same as post-tool-use log
LOG_DIR="$GIT_ROOT/logs/"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/claude-code.log"

echo "$0" >> "$LOG_FILE"

# # Log file location
# LOG_DIR="$HOME/.claude/logs"
# mkdir -p "$LOG_DIR"
# LOG_FILE="$LOG_DIR/tool_use.log"

# Read input from stdin
INPUT="$(cat)"

# Get timestamp and CWD
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"
CWD="$(pwd)"

# Parse and log using Python for reliable JSON handling
# Pass input via environment variable to avoid pipe/heredoc conflict
INPUT="$INPUT" python3 - "$TIMESTAMP" "$CWD" "$LOG_FILE" <<'PYTHON_SCRIPT'
import json
import sys
import os

input_data = os.environ.get("INPUT", "{}")
timestamp = sys.argv[1]
cwd = sys.argv[2]
log_file = sys.argv[3]

try:
    d = json.loads(input_data)
    tool_name = d.get("tool_name", "unknown")
    tool_input = d.get("tool_input", {}) or {}

    # Build log entry
    lines = [
        "----------------------------------------",
        f"Time: {timestamp}",
        f"Tool: {tool_name}",
        f"CWD:  {cwd}",
    ]

    # Extract fields based on tool type
    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        desc = tool_input.get("description", "")
        if cmd:
            cmd_display = cmd.replace("\n", "\\n")[:300]
            lines.append(f"Cmd:  {cmd_display}")
        if desc:
            lines.append(f"Desc: {desc[:100]}")

    elif tool_name in ("Read", "Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        if file_path:
            lines.append(f"File: {file_path}")
        if tool_name == "Edit":
            old_str = tool_input.get("old_string", "")[:80]
            new_str = tool_input.get("new_string", "")[:80]
            if old_str:
                lines.append(f"Old:  {old_str.replace(chr(10), '\\n')}")
            if new_str:
                lines.append(f"New:  {new_str.replace(chr(10), '\\n')}")

    elif tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        if pattern:
            lines.append(f"Pattern: {pattern}")
        if path:
            lines.append(f"Path: {path}")

    elif tool_name == "Grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        if pattern:
            lines.append(f"Pattern: {pattern}")
        if path:
            lines.append(f"Path: {path}")

    elif tool_name == "Task":
        desc = tool_input.get("description", "")
        prompt = tool_input.get("prompt", "")[:200]
        agent = tool_input.get("subagent_type", "")
        if desc:
            lines.append(f"Desc: {desc}")
        if agent:
            lines.append(f"Agent: {agent}")
        if prompt:
            lines.append(f"Prompt: {prompt.replace(chr(10), ' ')}")

    elif tool_name == "WebFetch":
        url = tool_input.get("url", "")
        if url:
            lines.append(f"URL: {url}")

    elif tool_name == "WebSearch":
        query = tool_input.get("query", "")
        if query:
            lines.append(f"Query: {query}")

    else:
        # Generic handling for other tools
        for key, val in list(tool_input.items())[:5]:
            if val and isinstance(val, str):
                val_display = val.replace("\n", "\\n")[:100]
                lines.append(f"{key}: {val_display}")

    # Write to log
    with open(log_file, "a") as f:
        f.write("\n".join(lines) + "\n")

except Exception as e:
    with open(log_file, "a") as f:
        f.write(f"----------------------------------------\n")
        f.write(f"Time: {timestamp}\n")
        f.write(f"Error: {e}\n")

PYTHON_SCRIPT

# Always exit 0 - logging hook should never block
exit 0

# EOF