# Manual Installation

*Note*: Automated installation via ```setup.sh``` is recommended.

- [macOS Manual Installation](#macos-manual-installation)
  - [Install brew dependencies](#install-brew-dependencies)
  - [Configure pyenv virtual environment](#configure-pyenv-virtual-environment)
  - [Install Python modules](#install-python-modules)
    - [Recommended: Install latest releases](#recommended-install-latest-releases)
    - [Alternative: Install known-working versions](#alternative-install-known-working-versions)

## macOS Manual Installation

### Install brew dependencies
```
brew install pyenv pyenv-virtualenv
```

### Configure pyenv virtual environment
```
pyenv install 3.11.6
pyenv virtualenv 3.11.6 urcuchillay-env
pyenv activate urcuchillay-env
```

### Install Python modules

#### Recommended: Install latest releases
```
pip install 'llama-cpp-python[server]' llama_index transformers torch pypdf Pillow
```

#### Alternative: Install known-working versions
```
pip install --no-cache-dir -r requirements.txt
```
