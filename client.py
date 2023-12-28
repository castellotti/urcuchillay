#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

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

    def get_llm(self, args):
        return llama_index.llms.OpenAI(
            model="text-davinci-002",
            temperature=args.temperature,
            max_tokens=args.max_new_tokens,
            api_base=config.APIConfig.get_openai_api_base(),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
            callback_manager=self.callback_manager,
        )

    def get_service_context(self, llm, args):
        embed_model = config.Config.EMBED_MODEL_NAME
        if hasattr(args, 'embed_model_name'):
            if args.embed_model_name == 'default' or args.embed_model_name == 'local':
                embed_model = args.embed_model_name
            else:
                if hasattr(args, 'embed_model_provider'):
                    # use Huggingface embeddings
                    embed_model = llama_index.embeddings.HuggingFaceEmbedding(
                        model_name=args.embed_model_provider + '/' + args.embed_model_name)

        return llama_index.ServiceContext.from_defaults(
            llm=llm,
            embed_model=embed_model,
            callback_manager=self.callback_manager,
            context_window=args.context,
            num_output=args.max_new_tokens,
        )

    @staticmethod
    def get_index(service_context, args):
        if not os.path.exists(args.data) or not os.listdir(args.data):
            # Create a temporary empty file for the index if a missing or empty data directory was supplied
            temp_file = utils.create_temporary_empty_file()
            documents = llama_index.SimpleDirectoryReader(input_files=[temp_file]).load_data()
            index = llama_index.VectorStoreIndex.from_documents(documents, service_context=service_context)
            os.remove(temp_file)
            return index
        else:
            documents = llama_index.SimpleDirectoryReader(args.data).load_data()
            return llama_index.VectorStoreIndex.from_documents(
                documents, service_context=service_context
            )
