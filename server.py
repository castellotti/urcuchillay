#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import os
import sys

import config
import utils

try:
    import llama_cpp.server.app
    import llama_index
    import transformers
    import uvicorn
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)


class Server:
    def __init__(self, args):

        if not args.model:
            args.model = os.path.join(os.getcwd(), 'models', config.Config.MODEL_DEFAULT)
        else:
            if not os.path.exists(args.model):
                args.model = os.path.join(os.getcwd(), 'models', args.model)

        # Collect and filter valid field names for llama_cpp.server
        valid_field_names = set(llama_cpp.server.app.Settings.model_fields.keys())
        filtered_args = {k: v for k, v in vars(args).items() if k in valid_field_names and v is not None}
        settings = llama_cpp.server.app.Settings(**filtered_args)

        self.host = args.host
        self.port = args.port
        self.app = llama_cpp.server.app.create_app(settings=settings)

    def run(self):
        uvicorn.run(
            self.app, host=os.getenv("HOST", self.host), port=int(os.getenv("PORT", self.port))
        )


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')

    parser = utils.parse_arguments_common(parser)

    for name, field in llama_cpp.server.app.Settings.model_fields.items():
        # Skip common arguments already included
        if utils.is_argument_defined(parser, name):
            continue

        description = field.description or ''
        if field.default is not None:
            description += f" (default: {field.default})"

        arg_params = {
            'dest': name,
            'help': description,
        }

        base_type = utils.get_base_type(field.annotation) if field.annotation is not None else str

        if base_type is bool:
            arg_params['type'] = utils.str2bool
        else:
            arg_params['type'] = base_type
            if utils.contains_list_type(field.annotation):
                arg_params['nargs'] = '*'

        parser.add_argument(f"--{name}", **arg_params)

    args = parser.parse_args()

    args = utils.update_arguments_common(args)

    return args


def main():
    args = parse_arguments()
    server = Server(args=args)
    server.run()


if __name__ == "__main__":
    main()
