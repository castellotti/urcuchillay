#!/bin/sh

# Exit on any error
set -e

# Detect the operating system
OS="$(uname -s)"

case "$OS" in
    Darwin)
        PYENV_VERSION=3.11.6
        echo "Running on macOS. Installing using Homebrew..."
        brew install pyenv pyenv-virtualenv
        echo
        echo "Checking if auto-activation of virtualenvs is enabled..."
        # Check and update .zshrc for pyenv and pyenv-virtualenv initialization
        ZSHRC="$HOME/.zshrc"
        # shellcheck disable=SC2016
        PYENV_PATH='export PATH="$HOME/.pyenv/bin:$PATH"'
        PYENV_INIT="eval \"\$(pyenv init --path)\""
        PYENV_VIRTUALENV_INIT="eval \"\$(pyenv virtualenv-init -)\""


        for line in "$PYENV_PATH" "$PYENV_INIT" "$PYENV_VIRTUALENV_INIT"; do
            if ! grep -Fxq "$line" "$ZSHRC"; then
                printf "Add '%s' to %s? (y/N) " "$line" "$ZSHRC"
                read -r REPLY
                echo  # Move to a new line
                if [ "$REPLY" = "Y" ] || [ "$REPLY" = "y" ]; then
                    echo "Adding '$line' to $ZSHRC"
                    echo "$line" >> "$ZSHRC"
                else
                    echo "Skipping '$line'"
                fi
            else
                echo "'$line' already exists in $ZSHRC"
            fi
        done
        ;;

    Linux)
        PYENV_VERSION=3.11.3
        echo "Running on Linux. Installing using APT..."
        # Update packages and install prerequisites
        sudo apt update
        sudo apt install -y make build-essential libssl-dev zlib1g-dev \
                            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
                            libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
                            libffi-dev liblzma-dev
        echo
        echo "Checking for pyenv..."
        # Check if pyenv is already installed
        if command -v pyenv >/dev/null 2>&1; then
            echo "pyenv is already installed."
        else
            echo "Installing pyenv..."
            curl https://pyenv.run | bash
        fi
        echo
        echo "Checking for pyenv-virtualenv..."
        # Check if pyenv-virtualenv is installed
        if ! command -v pyenv-virtualenv >/dev/null 2>&1; then
	            PYENV_VIRTUALENV_DIR="$(pyenv root)/plugins/pyenv-virtualenv"
            if [ -d "$PYENV_VIRTUALENV_DIR" ]; then
                echo "pyenv-virtualenv directory already exists."
            else
                echo "Installing pyenv-virtualenv..."
                # Install pyenv-virtualenv
                git clone https://github.com/pyenv/pyenv-virtualenv.git "$PYENV_VIRTUALENV_DIR"
            fi
        else
            echo "pyenv-virtualenv is already installed."
        fi
        echo
        echo "Checking if auto-activation of virtualenvs is enabled..."
        # Check and update .bashrc for pyenv and pyenv-virtualenv initialization
        BASHRC="$HOME/.bashrc"
        # shellcheck disable=SC2016
        PYENV_PATH='export PATH="$HOME/.pyenv/bin:$PATH"'
        PYENV_INIT="eval \"\$(pyenv init --path)\""
        PYENV_VIRTUALENV_INIT="eval \"\$(pyenv virtualenv-init -)\""

        for line in "$PYENV_PATH" "$PYENV_INIT" "$PYENV_VIRTUALENV_INIT"; do
            if ! grep -Fxq "$line" "$BASHRC"; then
                printf "Add '%s' to %s? (y/N) " "$line" "$BASHRC"
                read -r REPLY
                echo  # Move to a new line
                if [ "$REPLY" = "Y" ] || [ "$REPLY" = "y" ]; then
                    echo "Adding '$line' to $BASHRC"
                    echo "$line" >> "$BASHRC"
                else
                    echo "Skipping '$line'"
                fi
            else
                echo "'$line' already exists in $BASHRC"
            fi
        done
        ;;

    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

# Activate virtual PyEnv for current shell script
if [ -n "$ZSH_VERSION" ]; then
    # For Zsh
    # shellcheck disable=SC1090
    [ -f ~/.zshrc ] && . ~/.zshrc
elif [ -n "$BASH_VERSION" ]; then
    # For Bash
    # shellcheck disable=SC1090
    [ -f ~/.bashrc ] && . ~/.bashrc
fi

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

pip install llama_cpp_python llama_index transformers torch \
  pypdf Pillow

printf "Verifying llama_cpp_python version: "
python -c "import llama_cpp; print(llama_cpp.__version__)"

printf "Verifying llama_index version: "
python -c "import llama_index; print(llama_index.__version__)"
