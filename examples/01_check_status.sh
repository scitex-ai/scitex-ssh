#!/usr/bin/env bash
# Example: Check status of existing SSH reverse tunnels
# This is safe to run without any setup

set -euo pipefail

echo "=== Checking tunnel status via CLI ==="
scitex-ssh status || echo "No active tunnels found."

echo ""
echo "=== Checking tunnel status via Python API ==="
python3 -c "
from scitex_ssh import status, get_version
print(f'scitex-ssh v{get_version()}')
result = status()
print(result['stdout'] or 'No active tunnels.')
"

# EOF
