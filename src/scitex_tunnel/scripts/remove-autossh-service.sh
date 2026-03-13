#!/bin/bash
# Script created on: 2024-06-22 14:47:13
# Script path: /home/ywatanabe/setup-persistent-ssh-reverse-tunnel/remove-autossh-service.sh

# Argument Parser
while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | --help) # Display help
        echo "Usage: $0 [-h|--help] [-p|--port: Port of the service to remove]"
        exit 0
        ;;
    -p | --port)
        PORT="$2"
        shift
        ;;
    *) # Unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
    shift
done

# Parameters
LOG_PATH="/tmp/scitex-tunnel-remove-$(date +%s).log"

# Functions
main() {
    # Opening
    echo -e "$0 starts.\n"

    # Main
    SERVICE_PATH=/etc/systemd/system/autossh-tunnel-"$PORT".service
    SERVICE_NAME=$(basename "$SERVICE_PATH")

    sudo systemctl stop "$SERVICE_NAME"
    sudo systemctl disable "$SERVICE_NAME"
    sudo rm "$SERVICE_PATH"

    sudo systemctl daemon-reload
    sudo systemctl reset-failed

    # Closing
    echo -e "\n$0 ends"
}

touch "$LOG_PATH"
main | tee "$LOG_PATH"
echo -e "
Logged to: $LOG_PATH"

# EOF
