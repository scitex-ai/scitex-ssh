#!/usr/bin/env bash
# Run all scitex-ssh examples
# Note: These examples require a bastion server and sudo privileges

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== scitex-ssh examples ==="
echo ""
echo "Example 01: Check tunnel status (safe to run)"
bash "$SCRIPT_DIR/01_check_status.sh"

echo ""
echo "=== Examples 02-03 require a bastion server ==="
echo "See individual scripts for usage."

# EOF
