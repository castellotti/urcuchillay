#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
import logging
import os
import sys

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


class Index:
    def __init__(self, args):

        self.debug = args.debug

        logging.basicConfig(stream=sys.stdout, level=args.level)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        llama_debug = llama_index.callbacks.LlamaDebugHandler(print_trace_on_end=self.debug)
        self.callback_manager = llama_index.callbacks.CallbackManager([llama_debug])

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

        # Fallback settings for api_base, api_key, and api_version
        os.environ['OPENAI_API_BASE'] = config.APIConfig.get_openai_api_base()
        os.environ['OPENAI_API_KEY'] = config.APIConfig.OPENAI_API_KEY
        os.environ['OPENAI_API_VERSION'] = config.APIConfig.OPENAI_API_VERSION

        # define LLM
        llm = llama_index.llms.OpenAI(
            api_base=config.APIConfig.get_openai_api_base(),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
            embed_model=embed_model,
            callback_manager=self.callback_manager,
            temperature=args.temperature,
            model="text-davinci-002",
        )

        service_context = llama_index.ServiceContext.from_defaults(
            llm=llm,
            num_output=args.max_new_tokens,
        )

        if args.load:
            # load vector index from storage
            storage_context = llama_index.StorageContext.from_defaults(persist_dir=args.storage)
            index = llama_index.load_index_from_storage(storage_context, service_context=service_context)
        else:
            # load documents
            documents = llama_index.SimpleDirectoryReader(args.data).load_data()
            # create vector store index
            index = llama_index.VectorStoreIndex.from_documents(
                documents, service_context=service_context
            )

        # persist the index to disk
        if args.save:
            index.storage_context.persist(persist_dir=args.storage)


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
