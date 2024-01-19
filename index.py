#!/usr/bin/env python3
# Copyright (c) 2023-2024 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import logging
import sys

import client
import config
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

        logging.getLogger().name = __name__

        utils.set_index_cache(args)

        if args.pretrained_model_name is not None:
            llama_index.set_global_tokenizer(
                transformers.AutoTokenizer.from_pretrained(
                    args.pretrained_model_provider + '/' + args.pretrained_model_name
                ).encode
            )

        llm = self.get_llm(args)
        service_context = self.get_service_context(llm, args)

        if args.reset:
            self.reset_index(args)
            logging.warning('vector store was reset')
            if config.Config.STORAGE_TYPE == 'json':
                args.load = False  # Do not attempt to load from the deleted storage, generate a new vector store
        else:
            index = self.get_index(service_context, args)

            if args.save:
                self.save_index(args)
                # persist the index to disk
                if config.Config.STORAGE_TYPE == 'json':
                    index.storage_context.persist(persist_dir=args.storage)
                else:
                    # For ChromaDB, storage is written to disk as part
                    # of the loading data process
                    pass

        if args.reload:
            # Request gateway to reload indexed vector store
            utils.request_gateway_load(args.host, args.port)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')
    parser = utils.parse_arguments_common(parser)

    parser.add_argument('--pretrained_model_name', type=str, default=None,
                        help='The name of the pretrained model to use (default: %(default)s)')
    parser.add_argument('--pretrained_model_provider', type=str, default=None,
                        help='The provider of the pretrained model to use (default: %(default)s)')

    args = parser.parse_args()
    args = utils.update_arguments_common(args)
    return args


def main():
    args = parse_arguments()
    Index(args=args)


if __name__ == '__main__':
    main()
