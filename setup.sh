#!/bin/sh
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

# Exit on any error
set -e

echo "Preparing to install Urcuchillay."

# Variable for storing information to output at the end of installation
output_message=""

# Function to prompt for user confirmation
confirm() {
    while true; do
        printf '%s [y/N]: ' "$1"
        read -r yn </dev/tty
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Function to check if inside a git repository by looking for .git directory
is_in_git_repo() {
    dir=$(pwd)
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ]; then
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

# Download Urcuchillay software if not already inside a git repo
if ! is_in_git_repo; then
    # Check if git is installed
    if ! command -v git > /dev/null 2>&1; then
        echo "ERROR: It appears git is not installed. Please install git to proceed."
        exit 1
    fi

    echo "Cloning Urcuchillay git repository..."
    git clone http://git.urcuchillay.ai urcuchillay || \
      { echo "Failed to clone Urcuchillay repository"; exit 1; }
    cd urcuchillay || { echo "Failed to enter directory"; exit 1; }
fi

# Detect the operating system
OS="$(uname -s)"

case "$OS" in
    Darwin)
        SHELL_RC="$HOME/.zshrc"
        PYENV_VERSION=3.11.6
        echo "Running on macOS."
        if ! command -v brew >/dev/null 2>&1; then
            echo "Homebrew not found. Please install it first."
            echo
            echo 'To install Homebrew, paste the following command into the terminal:'
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo
            echo "For details please visit https://brew.sh"
            exit 1
        fi
        echo "Installing dependencies using Homebrew..."
        (brew install pyenv pyenv-virtualenv) < /dev/null

        # Check if Docker is installed
        if ! command -v docker >/dev/null 2>&1; then
            echo # newline for better visibility
            echo "Docker is not installed."
            echo "Docker is recommended for using the web chat user interface."

            # Ask user for permission to install Docker
            if confirm "Do you want to install Docker?"; then
                echo "Installing Docker..."

                # Install Docker using Homebrew
                (brew install --cask docker) < /dev/null

                echo "Docker has been installed."
                if [ -n "$output_message" ]; then
                    output_message="${output_message}\n"
                fi
                output_message="${output_message}  Docker was installed.\n"
                output_message="${output_message}  In order to use docker it will be necessary to run Docker Desktop.\n"
                output_message="${output_message}  Docker Desktop can found in the Launchpad menu listed as \"Docker\"\n"
            else
                echo "Installation cancelled."
            fi
        else
            echo "Docker is already installed."
        fi
        ;;

    Linux)
        SHELL_RC="$HOME/.bashrc"
        PYENV_VERSION=3.11.3
        echo "Running on Linux."

        # Check for NVIDIA CUDA support
        if command -v nvidia-smi >/dev/null 2>&1; then
            echo "NVIDIA CUDA support detected."
            export CMAKE_ARGS="-DLLAMA_CUBLAS=ON"
        fi

        # Extract the ID value from /etc/os-release
        ID=$(grep '^ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"')

        # Check the ID and execute different commands based on the OS
        if [ "$ID" = "ubuntu" ] || [ "$ID" = "debian" ]; then
            echo "Ubuntu (or Debian) detected."
            # List of prerequisite packages
            packages="make build-essential libssl-dev zlib1g-dev libbz2-dev \
                      libreadline-dev libsqlite3-dev wget curl llvm \
                      libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
                      libffi-dev liblzma-dev docker.io docker-compose"

            # Collect missing prerequisites
            install_required=false
            docker_install_required=false
            is_installed() {
                dpkg -l "$1" > /dev/null 2>&1
                return $?
            }
            for pkg in $packages; do
                if ! is_installed "$pkg"; then
                    install_required=true
                    echo "$pkg is not installed."
                    if [ "$pkg" = "docker.io" ]; then
                        docker_install_required=true
                    fi
                fi
            done

            # Install missing packages
            if [ "$install_required" = true ]; then
                echo "Installing missing dependencies using APT."
                sudo apt update
                # shellcheck disable=SC2086
                sudo apt-get install -y $packages
            else
                echo "All dependencies are already installed."
            fi

            # Grant Docker permission to user if docker.io is being installed
            if [ "$docker_install_required" = true ]; then
                sudo usermod -aG docker "$(whoami)"
                echo # newline for better visibility
                echo "Docker user permissions set for $(whoami)."
                echo # newline for better visibility
                if [ -n "$output_message" ]; then
                    output_message="${output_message}\n"
                fi
                output_message="${output_message}  Docker was installed.\n"
                output_message="${output_message}  It may be necessary to run the following before using docker:\n"
                output_message="${output_message}  newgrp docker\n"
            fi

        elif [ "$ID" = "fedora" ]; then
            echo "Fedora detected."
            # List of prerequisite packages
            packages="zlib-devel bzip2 bzip2-devel readline-devel \
                      sqlite sqlite-devel openssl-devel xz xz-devel \
                      libffi-devel findutils gcc-c++ docker docker-compose"

            # Collect missing prerequisites
            to_install=""
            docker_install_required=false
            is_installed() {
                dnf list installed "$1" > /dev/null 2>&1
                return $?
            }
            for pkg in $packages; do
                if ! is_installed "$pkg"; then
                    to_install="$to_install $pkg"
                    if [ "$pkg" = "docker" ]; then
                        docker_install_required=true
                    fi
                fi
            done
            to_install=$(echo "$to_install" | sed 's/^ //')

            # Install missing packages
            if [ -n "$to_install" ]; then
                echo "The following packages are missing and will be installed via dnf: $to_install"
                # shellcheck disable=SC2086
                sudo dnf --assumeyes install $to_install
            else
                echo "All dependencies are already installed."
            fi

            # Grant Docker permission to user if docker is being installed
            if [ "$docker_install_required" = true ]; then
                sudo usermod -aG docker "$(whoami)"
                echo # newline for better visibility
                echo "Docker user permissions set for $(whoami)."
                echo # newline for better visibility
                if [ -n "$output_message" ]; then
                    output_message="${output_message}\n"
                fi
                output_message="${output_message}  Docker was installed.\n"
                output_message="${output_message}  It may be necessary to run the following before using docker:\n"
                output_message="${output_message}  sudo systemctl start docker\n"
                output_message="${output_message}  sudo systemctl enable docker\n"
                output_message="${output_message}  newgrp docker\n"
            fi

        else
            echo "Warning: Unknown distribution detected. Dependencies may be missing."
        fi

        echo "Checking for pyenv..."
        if command -v pyenv >/dev/null 2>&1; then
            echo "pyenv is already installed."
        else
            echo "Installing pyenv..."
            curl https://pyenv.run 2> /dev/null | bash 2> /dev/null
            export PYENV_ROOT="$HOME/.pyenv"
            if [ -d "$PYENV_ROOT/bin" ]; then
                export PATH="$PYENV_ROOT/bin:$PATH"
                eval "$(pyenv init -)"
            fi
        fi

        echo "Checking for pyenv-virtualenv..."
        if ! command -v pyenv-virtualenv >/dev/null 2>&1; then
	            PYENV_VIRTUALENV_DIR="$(pyenv root)/plugins/pyenv-virtualenv"
            if [ -d "$PYENV_VIRTUALENV_DIR" ]; then
                echo "pyenv-virtualenv directory already exists."
            else
                echo "Installing pyenv-virtualenv..."
                git clone https://github.com/pyenv/pyenv-virtualenv.git "$PYENV_VIRTUALENV_DIR"
            fi
        else
            echo "pyenv-virtualenv is already installed."
        fi
        ;;

    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

# shellcheck disable=SC2016
PYENV_PATH='export PATH="$HOME/.pyenv/bin:$PATH"'
PYENV_INIT_PATH="eval \"\$(pyenv init --path)\""
PYENV_INIT="eval \"\$(pyenv init -)\""
PYENV_VIRTUALENV_INIT="eval \"\$(pyenv virtualenv-init -)\""
PYENV_COMMENT="# pyenv and virtualenv initialization"
PYENV_COMMENT_ADDED=false
AUTO_ACCEPT=false

echo "Checking if auto-activation of virtualenvs is enabled..."
if [ ! -f "$SHELL_RC" ]; then
    echo "Creating $SHELL_RC since it does not exist."
    touch "$SHELL_RC"
    AUTO_ACCEPT=true
fi
for line in "$PYENV_PATH" "$PYENV_INIT_PATH" "$PYENV_INIT" "$PYENV_VIRTUALENV_INIT"; do
    if ! grep -Fxq "$line" "$SHELL_RC"; then
        if [ "$AUTO_ACCEPT" = false ]; then
            echo # newline for better visibility
            echo "We would like to add auto-activation commands to your environment"
            printf "Add '%s' to %s? (y/N) " "$line" "$SHELL_RC"
            # Read input directly from the terminal in case piped from curl
            if read -r REPLY </dev/tty; then
              if [ "$REPLY" = "Y" ] || [ "$REPLY" = "y" ]; then
                  AUTO_ACCEPT=true
              else
                  echo "Skipping '$line'"
                  continue
              fi
            else
                continue
            fi
        fi
        # Add a comment block for first new entry during this session
        if [ "$PYENV_COMMENT_ADDED" = false ]; then
            printf "\n%s\n" "$PYENV_COMMENT" >> "$SHELL_RC"
            PYENV_COMMENT_ADDED=true
        fi
        echo "Adding '$line' to $SHELL_RC"
        echo "$line" >> "$SHELL_RC"
    else
        echo "'$line' already exists in $SHELL_RC"
    fi
done

# Activate virtual PyEnv for current shell script
# shellcheck disable=SC1090
# shellcheck disable=SC2086
[ -f $SHELL_RC ] && . $SHELL_RC

eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

if ! pyenv versions | grep -q "$PYENV_VERSION"; then
    pyenv install $PYENV_VERSION
else
    echo "Python $PYENV_VERSION is already installed."
fi

if ! pyenv virtualenvs | grep -q "urcuchillay-env"; then
    pyenv virtualenv $PYENV_VERSION urcuchillay-env
else
    echo "Virtual environment 'urcuchillay-env' already exists."
fi

if pyenv versions | grep -q '^\* urcuchillay-env'; then
    echo "'urcuchillay-env' is already active."
else
    echo "Activating 'urcuchillay-env'..."
    pyenv activate urcuchillay-env
fi

pip install 'llama-cpp-python[server]' llama_index transformers torch \
  pypdf Pillow

printf "Verifying llama_cpp_python version: "
python -c "import llama_cpp; print(llama_cpp.__version__)"

printf "Verifying llama_index version: "
python -c "import llama_index; print(llama_index.__version__)"

if [ -n "$output_message" ]; then
    echo # newline for better visibility
    echo "Installation Notes:"
    printf "%b" "$output_message"
fi

echo # newline for better visibility
echo "To use Urcuchillay, please start a new terminal and run:"
echo "pyenv activate urcuchillay-env"
