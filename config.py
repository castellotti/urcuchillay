#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import json
import os
import sys

try:
    import llama_cpp.server.app
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)


class Models:
    MODELS = {
        'llama-2-7b-chat.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF',
            'url': 'https://huggingface.co/TheBloke/Llama-2-7B-chat-GGUF/' +
                   'resolve/main/llama-2-7b-chat.Q4_K_M.gguf',
            'prompt_template': '{prompt}',
            'model_creator': 'Meta',
            'model_provider': 'TheBloke',  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        },
        'llama-2-13b-chat.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF',
            'url': 'https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/' +
                   'resolve/main/llama-2-13b-chat.Q4_K_M.gguf',
            'prompt_template': '{prompt}',
            'model_creator': 'Meta',
            'model_provider': 'TheBloke',  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        },
        'llama-2-70b-chat.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF',
            'url': 'https://huggingface.co/TheBloke/Llama-2-70B-chat-GGUF/' +
                   'resolve/main/llama-2-70b-chat.Q4_K_M.gguf',
            'prompt_template': '{prompt}',
            'model_creator': 'Meta',
            'model_provider': 'TheBloke',  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        },
        'mistral-7b-v0.1.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF',
            'url': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf',
            'prompt_template': '[INST] {prompt} [/INST]',
            'model_creator': 'Mistral AI',
            'model_provider': 'TheBloke',  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        },
        'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF',
            'url': 'https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/' +
                   'resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
            'prompt_template': '[INST] {prompt} [/INST]',
            'model_creator': 'Mistral AI',
            'model_provider': 'TheBloke',  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        },
    }

    MODEL_ALIASES = {
        '7': 'llama-2-7b-chat.Q4_K_M.gguf',
        '7b': 'llama-2-7b-chat.Q4_K_M.gguf',
        'llama-2-7b': 'llama-2-7b-chat.Q4_K_M.gguf',
        '13': 'llama-2-13b-chat.Q4_K_M.gguf',
        '13b': 'llama-2-13b-chat.Q4_K_M.gguf',
        'llama-2-13b': 'llama-2-13b-chat.Q4_K_M.gguf',
        '70': 'llama-2-70b-chat.Q4_K_M.gguf',
        '70b': 'llama-2-70b-chat.Q4_K_M.gguf',
        'llama-2-70b': 'llama-2-70b-chat.Q4_K_M.gguf',
        'small': 'llama-2-7b-chat.Q4_K_M.gguf',
        'medium': 'llama-2-13b-chat.Q4_K_M.gguf',
        'large': 'llama-2-70b-chat.Q4_K_M.gguf',
        'mistral': 'mistral-7b-v0.1.Q4_K_M.gguf',
        'mistral-7b': 'mistral-7b-v0.1.Q4_K_M.gguf',
        'mixtral': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-8x7b': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-8x7b-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
    }


class Config:
    DEBUG = False

    CONFIG_FILE = 'config.json'

    ENABLE_GPU = 1
    TEMPERATURE = 0.1
    MAX_NEW_TOKENS = 256
    CONTEXT_WINDOW = 4096

    DATA_PATH = os.path.join(os.getcwd(), 'data')
    MODEL_PATH = os.path.join(os.getcwd(), 'models')
    STORAGE_PATH = os.path.join(os.getcwd(), 'storage')

    MODEL_DEFAULT = Models.MODEL_ALIASES['mistral-7b']
    MODEL_URL_DEFAULT = Models.MODELS[MODEL_DEFAULT]['url']
    EMBED_MODEL_NAME = 'local'


class APIConfig:
    API_HOST = 'localhost'  # llama_cpp.server.app.Settings.host
    API_PORT = 8000  # llama_cpp.server.app.Settings.port

    @staticmethod
    def get_docker_openai_api_host():
        return f'http://host.docker.internal:{APIConfig.API_PORT}'

    @staticmethod
    def get_openai_api_host():
        return f'http://{APIConfig.API_HOST}:{APIConfig.API_PORT}'

    OPENAI_API_KEY = 'xxxxxxxx'


def load_config():
    try:
        with open(Config.CONFIG_FILE, 'r') as f:
            config_data = json.load(f)

        for key, value in config_data.get('Config', {}).items():
            setattr(Config, key, value)
        for key, value in config_data.get('APIConfig', {}).items():
            setattr(APIConfig, key, value)
        for key, value in config_data.get('Models', {}).items():
            setattr(Models, key, value)

    except FileNotFoundError:
        print('Config file not found, using default settings.')
    except json.JSONDecodeError:
        print('Error decoding JSON, using default settings.')


load_config()