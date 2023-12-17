# utils.py
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import typing

import config


def parse_arguments_common(parser):
    parser.add_argument('--debug', type=str2bool, nargs='?', const=True, default=config.Config.DEBUG,
                        help='Enable debug mode (default: %(default)s)')
    parser.add_argument('--host', '--api_host', type=str, default=config.APIConfig.API_HOST,
                        help=f'Hostname or IP address of API service (default: %(default)s)')
    parser.add_argument('--port', '--api_port', type=str, default=config.APIConfig.API_PORT,
                        help=f'Port for API service (default: %(default)s)')
    parser.add_argument('--cpu', action='store_const', const=0, default=config.Config.ENABLE_GPU,
                        help='Use the CPU only instead of GPU acceleration')
    parser.add_argument('--temperature', type=float, default=config.Config.TEMPERATURE,
                        help='The temperature value for the model (default: %(default)s)')
    parser.add_argument('--max_new_tokens', type=float, default=config.Config.MAX_NEW_TOKENS,
                        help='The max new tokens value for the model (default: %(default)s)')
    parser.add_argument('--context', '--context_window', type=float, default=config.Config.CONTEXT_WINDOW,
                        help='The context window value for the model (default: %(default)s)')
    parser.add_argument('--save', type=str2bool, nargs='?', const=True, default=False,
                        help='Save indexed vector store locally (default: %(default)s)')
    parser.add_argument('--load', type=str2bool, nargs='?', const=True, default=False,
                        help='Load indexed vector store (default: %(default)s)')
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
    parser.add_argument('--embed_model_name', type=str, default=config.Config.EMBED_MODEL_NAME,
                        help='The name of the embedding model to use (default: %(default)s)')
    parser.add_argument('--embed_model_provider', type=str, default=None,
                        help='The provider of the embedding model to use (default: %(default)s)')
    parser.add_argument('--pretrained_model_name', type=str, default=None,
                        help='The name of the pretrained model to use (default: %(default)s)')
    parser.add_argument('--pretrained_model_provider', type=str, default=None,
                        help='The provider of the pretrained model to use (default: %(default)s)')
    return parser


def update_arguments_common(args):
    if str.lower(args.model) in config.Models.MODEL_ALIASES.keys():
        args.model = config.Models.MODEL_ALIASES[args.model]

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
    for action in parser._actions:
        if f'--{argument_name}' in action.option_strings:
            return True
    return False