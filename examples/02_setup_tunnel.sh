#!/usr/bin/env bash
# Example: Set up a persistent SSH reverse tunnel
# Requires: autossh, SSH key, bastion server access, sudo
#
# Usage:
#   ./02_setup_tunnel.sh -p PORT -b USER@BASTION -s KEY_PATH

set -euo pipefail

usage() {
    echo "Usage: $0 -p PORT -b BASTION_SERVER -s SECRET_KEY_PATH"
    echo ""
    echo "  -p PORT              Port number (e.g., 2222)"
    echo "  -b BASTION_SERVER    Bastion server (e.g., user@bastion.example.com)"
    echo "  -s SECRET_KEY_PATH   Path to SSH private key"
    echo "  -h                   Show this help"
    exit 1
}

while getopts "p:b:s:h" opt; do
    case $opt in
    p) PORT=$OPTARG ;;
    b) BASTION=$OPTARG ;;
    s) KEY_PATH=$OPTARG ;;
    h) usage ;;
    *) usage ;;
    esac
done

if [ -z "${PORT:-}" ] || [ -z "${BASTION:-}" ] || [ -z "${KEY_PATH:-}" ]; then
    usage
fi

echo "=== Setting up tunnel on port $PORT ==="
scitex-ssh setup -p "$PORT" -b "$BASTION" -s "$KEY_PATH"

echo ""
echo "=== Verifying ==="
scitex-ssh status -p "$PORT"

# EOF
