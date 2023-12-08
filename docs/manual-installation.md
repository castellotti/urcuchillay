# Manual Installation

*Note*: Automated installation via ```setup.sh``` is recommended.

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
pip install llama_cpp_python llama_index transformers torch
```

#### Alternative: Install known-working versions
```
pip install --no-cache-dir -r requirements.txt
```
