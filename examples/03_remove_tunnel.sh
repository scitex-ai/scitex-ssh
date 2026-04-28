#!/usr/bin/env bash
# Example: Remove a persistent SSH reverse tunnel
# Requires: sudo
#
# Usage:
#   ./03_remove_tunnel.sh -p PORT

set -euo pipefail

usage() {
    echo "Usage: $0 -p PORT"
    echo ""
    echo "  -p PORT   Port of tunnel to remove"
    echo "  -h        Show this help"
    exit 1
}

while getopts "p:h" opt; do
    case $opt in
    p) PORT=$OPTARG ;;
    h) usage ;;
    *) usage ;;
    esac
done

if [ -z "${PORT:-}" ]; then
    usage
fi

echo "=== Removing tunnel on port $PORT ==="
scitex-ssh remove -p "$PORT"

echo ""
echo "=== Verifying ==="
scitex-ssh status || echo "No active tunnels."

# EOF
