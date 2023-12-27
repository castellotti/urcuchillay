# utils.py
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import logging
import os
import tempfile
import typing
import uuid

import config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')
    parser = parse_arguments_common(parser)
    args = parser.parse_args()
    args = update_arguments_common(args)
    return args


def parse_arguments_common(parser):
    parser.add_argument('--debug', type=str2bool, nargs='?', const=True, default=config.Config.DEBUG,
                        help='Enable debug mode (default: %(default)s)')
    parser.add_argument('--level', '--log_level', type=str, default=logging.getLevelName(config.Config.LOG_LEVEL),
                        help=f'Logging level (default: %(default)s)')
    parser.add_argument('--host', '--gateway_host', type=str, default=config.Config.GATEWAY_HOST,
                        help=f'Hostname or IP address of gateway service (default: %(default)s)')
    parser.add_argument('--port', '--gateway_port', type=str, default=config.Config.GATEWAY_PORT,
                        help=f'Port for gateway service (default: %(default)s)')
    parser.add_argument('--api_host', '--openai_host', type=str, default=config.APIConfig.API_HOST,
                        help=f'Hostname or IP address of API service (default: %(default)s)')
    parser.add_argument('--api_port', '--openai_port', type=str, default=config.APIConfig.API_PORT,
                        help=f'Port for API service (default: %(default)s)')
    parser.add_argument('--cpu', action='store_const', const=0,
                        help='Use the CPU only instead of GPU acceleration')
    parser.add_argument('--gpus', '--enable_gpus', '--n_gpu_layers', action='store_const',
                        default=config.Config.ENABLE_GPUS,
                        help='One or more GPU layers will enable hardware acceleration (default: %(default)s)')
    parser.add_argument('--temperature', type=float, default=config.Config.TEMPERATURE,
                        help='The temperature value for the model (default: %(default)s)')
    parser.add_argument('--max_new_tokens', type=float, default=config.Config.MAX_NEW_TOKENS,
                        help='The max new tokens value for the model (default: %(default)s)')
    parser.add_argument('--context', '--context_window', type=float, default=config.Config.CONTEXT_WINDOW,
                        help='The context window value for the model (default: %(default)s)')
    parser.add_argument('--save', type=str2bool, nargs='?', const=True, default=True,
                        help='Save indexed vector store locally (default: %(default)s)')
    parser.add_argument('--load', type=str2bool, nargs='?', const=True, default=False,
                        help='Load indexed vector store (default: %(default)s)')
    parser.add_argument('--reset', '--clear', type=str2bool, nargs='?', const=True, default=False,
                        help='Reset indexed vector store (default: %(default)s)')
    parser.add_argument('--data', '--data_path', type=str, default=config.Config.DATA_PATH,
                        help='The path to data files to be indexed (default: %(default)s)')
    parser.add_argument('--path', '--model_path', type=str, default=config.Config.MODEL_PATH,
                        help='The path to the directory for cached models (default: %(default)s)')
    parser.add_argument('--storage', '--storage_path', type=str, default=config.Config.STORAGE_PATH,
                        help='The path to save and load the vector store (default: %(default)s)')
    parser.add_argument('--model_url', type=str, default=config.Config.MODEL_URL_DEFAULT,
                        help='Custom URL for model (defaults to the mistral-7b model)')
    parser.add_argument('--model', '--model_name', type=str, default=config.Config.MODEL_DEFAULT,
                        help='The name of the model to use (default: extracted from model url)')
    return parser


def update_arguments_common(args):
    if str.lower(args.model) in config.Models.MODEL_ALIASES.keys():
        args.model = config.Models.MODEL_ALIASES[args.model]

    if not hasattr(args, 'level') or args.level not in config.Config.LOG_LEVELS:
        args.level = logging.getLevelName(config.Config.LOG_LEVEL) if not args.debug else logging.DEBUG

    # Set number of GPU layers to one or more to enable hardware acceleration
    if not hasattr(args, 'n_gpu_layers'):
        args.n_gpu_layers = args.gpus

    if args.cpu is None:
        # Set CPU based on enabled GPUs
        args.cpu = 0 if args.gpus > 0 else 1

    if not hasattr(args, 'n_ctx') or not args.n_ctx:
        args.n_ctx = args.context

    return args


def str2bool(arg):
    """Parse boolean arguments."""
    if isinstance(arg, bool):
        return arg
    if arg.lower() in ('yes', 'true', 'on', 't', 'y', '1'):
        return True
    elif arg.lower() in ('no', 'false', 'off', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def get_base_type(annotation):
    """Determine the type of the argument."""
    if getattr(annotation, '__origin__', None) is typing.Literal:
        return type(annotation.__args__[0])
    elif getattr(annotation, '__origin__', None) is typing.Union:
        non_optional_args = [arg for arg in annotation.__args__ if arg is not type(None)]
        if non_optional_args:
            return get_base_type(non_optional_args[0])
    elif getattr(annotation, '__origin__', None) is list or getattr(annotation, '__origin__', None) is typing.List:
        return get_base_type(annotation.__args__[0])
    else:
        return annotation


def contains_list_type(annotation) -> bool:
    origin = getattr(annotation, '__origin__', None)

    if origin is list or origin is typing.List:
        return True
    elif origin in (typing.Literal, typing.Union):
        return any(contains_list_type(arg) for arg in annotation.__args__)
    else:
        return False


def is_argument_defined(parser, argument_name):
    """Skip arguments already included in parse_arguments_common."""
    # TODO Access to a protected member _actions of a class
    for action in parser._actions:
        if f'--{argument_name}' in action.option_strings:
            return True
    return False


def set_index_cache(args):
    cache_directory = args.path
    # llama_index will automatically assume models are cached in a subdirectory of the current path named
    # "models" so we need to handle if a user explicitly included "models" at the end of --model_path
    if os.path.basename(args.path) == 'models':
        cache_directory = os.path.dirname(args.path)

    os.environ['LLAMA_INDEX_CACHE_DIR'] = cache_directory


def generate_message_id():
    # Generate a random UUID (UUIDv4)
    random_uuid = uuid.uuid4()
    # Return the formatted message ID
    return f"cmpl-{random_uuid}"


def create_temporary_empty_file():
    # Create a temporary empty file and return its path
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    return temp_file_path
