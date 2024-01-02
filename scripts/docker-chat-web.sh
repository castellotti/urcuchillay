#!/bin/sh
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

# Check if the script is running in the 'urcuchillay-env' virtual environment
if [ "$(pyenv version-name)" != "urcuchillay-env" ]; then
    echo "This script must be run in the 'urcuchillay-env' virtual environment."
    echo "If installed using setup.sh it may be necessary to run:"
    echo
    echo "pyenv activate urcuchillay-env"
    exit 1
fi

# Function to parse JSON using Python
parse_json() {
    echo "$1" | python -c "import sys, json; print(json.load(sys.stdin)$2)"
}

# Function to find config.json in current or parent directory (if current directory is named "scripts")
find_config_file() {
    if [ -f "./config.json" ]; then
        echo "./config.json"
    elif [ "$(basename $(pwd))" = "scripts" ] && [ -f "../config.json" ]; then
        echo "../config.json"
    else
        echo ""
    fi
}

# Find the config file
CONFIG_FILE=$(find_config_file)

# Default values
GATEWAY_PORT=8080
OPENAI_API_KEY="xxxxxxxx"
UI_PORT=3000

# If config file is found, load JSON content into variables
if [ -n "$CONFIG_FILE" ]; then
    CONFIG_JSON=$(cat "$CONFIG_FILE")
    GATEWAY_PORT=$(parse_json "$CONFIG_JSON" '["Config"]["GATEWAY_PORT"]')
    UI_PORT=$(parse_json "$CONFIG_JSON" '["Config"]["UI_PORT"]')
    OPENAI_API_KEY=$(parse_json "$CONFIG_JSON" '["APIConfig"]["OPENAI_API_KEY"]')
fi

# Docker run command with dynamic environment variables
docker run \
    --add-host=host.docker.internal:host-gateway \
    -e OPENAI_API_HOST="http://host.docker.internal:$GATEWAY_PORT" \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  	-v ./config.json:/usr/src/app/config.json \
    -p "$UI_PORT":"$UI_PORT" \
    ghcr.io/mckaywrigley/chatbot-ui:main
