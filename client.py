#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import os
import sys

import config

try:
    import llama_index
    import transformers
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)


class Client:
    def __init__(self, args):

        self.debug = args.debug

        llama_debug = llama_index.callbacks.LlamaDebugHandler(print_trace_on_end=self.debug)
        self.callback_manager = llama_index.callbacks.CallbackManager([llama_debug])

        # Fallback settings for api_base, api_key, and api_version
        os.environ['OPENAI_API_BASE'] = config.APIConfig.get_openai_api_base()
        os.environ['OPENAI_API_KEY'] = config.APIConfig.OPENAI_API_KEY
        os.environ['OPENAI_API_VERSION'] = config.APIConfig.OPENAI_API_VERSION

        self.llm = None
        self.service_context = None
        self.index = None

    def set_llm(self, args):
        self.llm = llama_index.llms.OpenAI(
            model="text-davinci-002",
            temperature=args.temperature,
            max_tokens=args.max_new_tokens,
            callback_manager=self.callback_manager,
            api_base=config.APIConfig.get_openai_api_base(),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
        )

        self.service_context = llama_index.ServiceContext.from_defaults(
            llm=self.llm,
            context_window=args.context,
            num_output=args.max_new_tokens,
        )

    def set_index(self, args):
        if args.load and config.storage_verify(args.storage):
            # load vector index from storage
            storage_context = llama_index.StorageContext.from_defaults(persist_dir=args.storage)
            self.index = llama_index.load_index_from_storage(storage_context, service_context=self.service_context)
        else:
            # load documents
            documents = llama_index.SimpleDirectoryReader(args.data).load_data()
            # create vector store index
            self.index = llama_index.VectorStoreIndex.from_documents(
                documents, service_context=self.service_context
            )
