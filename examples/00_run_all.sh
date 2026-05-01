#!/usr/bin/env bash
# Run all scitex-ssh examples
# Note: These examples require a bastion server and sudo privileges

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/00_run_all.sh.log"

GREEN=$'\033[0;32m'
RED=$'\033[0;31m'
RESET=$'\033[0m'

# Tee everything to a log file from here on.
exec > >(tee "$LOG_FILE") 2>&1

declare -a RESULTS=()

run_example() {
    local label="$1"
    local cmd="$2"
    echo ""
    echo "=== $label ==="
    if eval "$cmd"; then
        RESULTS+=("PASS $label")
    else
        RESULTS+=("FAIL $label")
    fi
}

echo "=== scitex-ssh examples ==="

run_example "01_check_status.sh" "bash '$SCRIPT_DIR/01_check_status.sh'"

echo ""
echo "=== Examples 02-03 require a bastion server ==="
echo "See individual scripts for usage."

echo ""
echo "=== Summary ==="
exit_code=0
for r in "${RESULTS[@]}"; do
    if [[ "$r" == PASS* ]]; then
        echo "${GREEN}${r}${RESET}"
    else
        echo "${RED}${r}${RESET}"
        exit_code=1
    fi
done

exit "$exit_code"

# EOF
