#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import json
import logging
import os


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
        'mistral-7b-instruct-v0.1.Q4_K_M.gguf': {
            'model': 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF',
            'url': 'https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/' +
                   'resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf',
            'prompt_template': '<s>[INST] {prompt} [/INST]',
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
        'mistral': 'mistral-7b-instruct-v0.1.Q4_K_M.gguf',
        'mistral-7b': 'mistral-7b-instruct-v0.1.Q4_K_M.gguf',
        'mistral-7b-instruct': 'mistral-7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-8x7b': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'mixtral-8x7b-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
    }


class Config:
    DEBUG = False

    LOG_LEVELS = ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'NOTSET']
    LOG_LEVEL = logging.DEBUG if DEBUG else logging.ERROR

    CONFIG_FILE = 'config.json'

    GATEWAY_HOST = 'localhost'
    GATEWAY_PORT = 8080

    UI_HOST = 'localhost'
    UI_PORT = 3000

    ENABLE_GPUS = 1  # One or more GPU layers will enable hardware acceleration (1 is correct for Apple Silicon)
    TEMPERATURE = 0.1  # llama_index.constants.DEFAULT_TEMPERATURE
    CONTEXT_WINDOW = 3900  # llama_index.constants.DEFAULT_CONTEXT_WINDOW
    MAX_NEW_TOKENS = 256  # llama_index.constants.DEFAULT_NUM_OUTPUTS

    DATA_PATH = os.path.join(os.getcwd(), 'data')
    MODEL_PATH = os.path.join(os.getcwd(), 'models')
    STORAGE_PATH = os.path.join(os.getcwd(), 'storage')

    MODEL_DEFAULT = Models.MODEL_ALIASES['mistral-7b-instruct']
    MODEL_URL_DEFAULT = Models.MODELS[MODEL_DEFAULT]['url']
    EMBED_MODEL_NAME = 'default'

    STORAGE_FILES = ['default__vector_store.json',
                     'docstore.json',
                     'graph_store.json',
                     'image__vector_store.json',
                     'index_store.json']

    # https://docs.llamaindex.ai/en/stable/module_guides/deploying/chat_engines/usage_pattern.html#available-chat-modes

    # First generate a standalone question from conversation context and last message,
    # then query the query engine for a response.
    # CHAT_MODE = "condense_question"  # llama_index.chat_engine.types.ChatMode.CONDENSE_QUESTION

    # First retrieve text from the index using the user's message, then use the context
    # in the system prompt to generate a response.
    CHAT_MODE = "context"  # llama_index.chat_engine.types.ChatMode.CONTEXT

    # First condense a conversation and latest user message to a standalone question.
    # Then build a context for the standalone question from a retriever,
    # Then pass the context along with prompt and user message to LLM to generate a response.
    # CHAT_MODE = "condense_plus_context"  # llama_index.chat_engine.types.ChatMode.CONDENSE_PLUS_CONTEXT


class APIConfig:
    API_HOST = 'localhost'  # llama_cpp.server.app.Settings.host
    API_PORT = 8000  # llama_cpp.server.app.Settings.port
    OPENAI_API_VERSION = '1'
    OPENAI_API_KEY = 'xxxxxxxx'
    TIMEOUT = 60.0  # llama_index.llms.openai
    MAX_RETRIES = 3  # llama_index.llms.openai

    @staticmethod
    def get_docker_openai_api_host(port=API_PORT):
        return f'http://host.docker.internal:{port}'

    @staticmethod
    def get_openai_api_host(host=API_HOST, port=API_PORT):
        return f'http://{host}:{port}'

    @staticmethod
    def get_openai_api_base(host=API_HOST, port=API_PORT, version=OPENAI_API_VERSION):
        return f'http://{host}:{port}/v{version}'


def storage_verify(storage_path=Config.STORAGE_PATH):
    verified = True
    for file in Config.STORAGE_FILES:
        if not os.path.exists(os.path.join(storage_path, file)):
            verified = False
    return verified


def storage_reset(storage_path=Config.STORAGE_PATH):
    for file in Config.STORAGE_FILES:
        filepath = os.path.join(storage_path, file)
        if os.path.exists(filepath):
            os.remove(filepath)


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
    except PermissionError:
        print('Config file permission denied, using default settings.')
    except json.JSONDecodeError:
        print('Error decoding JSON, using default settings.')


load_config()
