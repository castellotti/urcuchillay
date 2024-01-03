#!/bin/sh
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

# Default values for Docker Compose
API_PORT_ARG=""
CONFIG_PATH_ARG=""
DATA_PATH_ARG=""
GATEWAY_ARGS=""
GPU_LAYERS_ARGS=""
MODELS_PATH_ARG=""
STORAGE_PATH_ARG=""
UI_PORT_ARG=""

# Function to add argument to GATEWAY_ARGS in Docker Compose
# Function to add argument to GATEWAY_ARGS
add_to_gateway_args() {
  if [ -n "$2" ] && [ "${2#-}" = "$2" ]; then
    # If $2 does not start with '-', treat $1 and $2 as a pair
    GATEWAY_ARGS="${GATEWAY_ARGS} $1 $2"
    return 2
  else
    # Otherwise, treat $1 as a standalone argument
    GATEWAY_ARGS="${GATEWAY_ARGS} $1"
    return 1
  fi
}

# Parse arguments
while [ $# -gt 0 ]; do
  case "$1" in
    --api_port)
      API_PORT_ARG="$2"
      shift 2
      ;;
    --config)
      CONFIG_PATH_ARG="$2"
      # Check if the path exists and is a directory
      if [ -f "CONFIG_PATH_ARG" ]; then
        # If the path does not start with "/" or "./", prepend "./"
        case $CONFIG_PATH_ARG in
          (/*) ;;
          (./*) ;;
          (*) CONFIG_PATH_ARG="./CONFIG_PATH_ARG" ;;
        esac
      fi
      shift 2
      ;;
    --data)
      DATA_PATH_ARG="$2"
      # Check if the path exists and is a directory
      if [ -d "DATA_PATH_ARG" ]; then
        # If the path does not start with "/" or "./", prepend "./"
        case $DATA_PATH_ARG in
          (/*) ;;
          (./*) ;;
          (*) DATA_PATH_ARG="./DATA_PATH_ARG" ;;
        esac
      fi
      shift 2
      ;;
    --models)
      MODELS_PATH_ARG="$2"
      # Check if the path exists and is a directory
      if [ -d "MODELS_PATH_ARG" ]; then
        # If the path does not start with "/" or "./", prepend "./"
        case $MODELS_PATH_ARG in
          (/*) ;;
          (./*) ;;
          (*) MODELS_PATH_ARG="./MODELS_PATH_ARG" ;;
        esac
      fi
      shift 2
      ;;
    --n-gpu-layers)
      GPU_LAYERS_ARGS="$1 $2"
      shift 2
      ;;
    --storage)
      STORAGE_PATH_ARG="$2"
      # Check if the path exists and is a directory
      if [ -d "$STORAGE_PATH_ARG" ]; then
        # If the path does not start with "/" or "./", prepend "./"
        case $STORAGE_PATH_ARG in
          (/*) ;;
          (./*) ;;
          (*) STORAGE_PATH_ARG="./$STORAGE_PATH_ARG" ;;
        esac
      fi
      shift 2
      ;;
    --ui_port)
      UI_PORT_ARG="$2"
      shift 2
      ;;
    --*) # Any other -- argument
      add_to_gateway_args "$1" "$2"
      shift_count=$?
      shift $shift_count
      ;;
    *)
      # Unknown option
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set environment variables for Docker Compose
if [ -n "$API_PORT_ARG" ]; then
  export API_PORT=$API_PORT_ARG
fi

if [ -n "$CONFIG_PATH_ARG" ]; then
  export CONFIG_PATH=$CONFIG_PATH_ARG
fi

if [ -n "$DATA_PATH_ARG" ]; then
  export DATA_PATH=$DATA_PATH_ARG
fi

if [ -n "$GATEWAY_ARGS" ]; then
  export GATEWAY_ARGS
fi

if [ -n "$GPU_LAYERS_ARGS" ]; then
  export GPU_LAYERS_ARGS
fi

if [ -n "$MODELS_PATH_ARG" ]; then
  export STORAGE_PATH=$STORAGE_PATH_ARG
fi

if [ -n "$STORAGE_PATH_ARG" ]; then
  export STORAGE_PATH=$STORAGE_PATH_ARG
fi

if [ -n "$UI_PORT_ARG" ]; then
  export UI_PORT=$UI_PORT_ARG
fi

# Test for NVIDIA CUDA version of Docker Compose
USE_LLAMA_CPP_SERVER_CUDA=false
export USE_LLAMA_CPP_SERVER_CUDA

# If running on Linux, and NVIDIA CUDA and NVIDIA Container Toolkit are available use all-in-one Docker Compose
if [ "$(uname -s)" = "Linux" ]; then
    CUDA_STATUS="not available"
    NCT_STATUS="not available"

    # Check for nvidia-smi to determine if CUDA is available
    if command -v nvidia-smi>/dev/null 2>&1; then
        CUDA_STATUS="available"
    fi

    # Check for nvidia-container-toolkit to determine if it's installed
    if command -v nvidia-container-toolkit>/dev/null 2>&1; then
        NCT_STATUS="available"
    fi

    MESSAGE="Running on Linux with CUDA ($CUDA_STATUS) and NVIDIA Container Toolkit ($NCT_STATUS)."
    echo "$MESSAGE"

    USE_LLAMA_CPP_SERVER_CUDA=$([ "$CUDA_STATUS" = "available" ] && [ "$NCT_STATUS" = "available" ] && echo true || echo false)
fi

# Verify correct directory
if [ ! -f docker-compose.yml ]; then
  # shellcheck disable=SC2046
  if [ "$(basename $(pwd))" = "scripts" ] && \
    [ "$(basename $(dirname $(pwd)))" = "urcuchillay" ] && \
    [ -f ../docker-compose.yml ]; then
      cd ..
  else
      echo "docker-compose.yml not found." >&2
      exit 1
  fi
fi

# Execute appropriate version of Docker Compose
if [ "$USE_LLAMA_CPP_SERVER_CUDA" = true ]; then
    docker-compose -f docker-compose.cuda.yml up
else
    docker-compose -f docker-compose.yml up
fi
