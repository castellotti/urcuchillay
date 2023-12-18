#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import os
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

        # llama_index will automatically assume models are cached in a subdirectory of the current path named
        # "models" so we need to handle if a user explicitly included "models" at the end of --model_path
        cache_directory = args.path
        if os.path.basename(args.path) == 'models':
            cache_directory = os.path.dirname(args.path)

        os.environ['LLAMA_INDEX_CACHE_DIR'] = cache_directory

        if args.pretrained_model_name is not None:
            llama_index.set_global_tokenizer(
                transformers.AutoTokenizer.from_pretrained(
                    args.pretrained_model_provider + '/' + args.pretrained_model_name
                ).encode
            )

        if args.embed_model_name == 'local':
            embed_model = args.embed_model_name
        else:
            # use Huggingface embeddings
            embed_model = llama_index.embeddings.HuggingFaceEmbedding(
                model_name=args.embed_model_provider + '/' + args.embed_model_name)

        # define LLM
        self.llm = llama_index.llms.OpenAI(
            api_base=config.APIConfig.get_openai_api_base(),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
            embed_model=embed_model,
            callback_manager=self.callback_manager,
            temperature=args.temperature,
            model="text-davinci-002",
            max_tokens=config.Config.MAX_NEW_TOKENS,
        )

        self.service_context = llama_index.ServiceContext.from_defaults(
            llm=self.llm,
            callback_manager=self.callback_manager,
            context_window=config.Config.CONTEXT_WINDOW,
            num_output=args.max_new_tokens,
        )

        self.get_index(args)

        # persist the index to disk
        if args.save:
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
