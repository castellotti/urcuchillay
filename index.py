#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import sys

import client
import utils

try:
    import llama_index
    import transformers
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)


class Index(client.Client):
    def __init__(self, args):

        super().__init__(args)

        utils.set_index_cache(args)

        if args.pretrained_model_name is not None:
            llama_index.set_global_tokenizer(
                transformers.AutoTokenizer.from_pretrained(
                    args.pretrained_model_provider + '/' + args.pretrained_model_name
                ).encode
            )

        self.set_llm(args)
        self.set_index(args)

        if args.save:
            # persist the index to disk
            self.index.storage_context.persist(persist_dir=args.storage)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')
    parser = utils.parse_arguments_common(parser)
    args = parser.parse_args()
    args = utils.update_arguments_common(args)
    return args


def main():
    args = parse_arguments()
    Index(args=args)


if __name__ == '__main__':
    main()