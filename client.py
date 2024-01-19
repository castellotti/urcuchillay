#!/usr/bin/env python3
# Copyright (c) 2023-2024 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.
import logging
import os
import sys

import config

try:
    import chromadb
    import llama_index
    import llama_index.vector_stores
    import transformers
    import utils
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
        os.environ['OPENAI_API_BASE'] = config.APIConfig.get_openai_api_base(host=args.api_host, port=args.api_port)
        os.environ['OPENAI_API_KEY'] = config.APIConfig.OPENAI_API_KEY
        os.environ['OPENAI_API_VERSION'] = config.APIConfig.OPENAI_API_VERSION

        # Set Parallel Iterator
        os.environ['TOKENIZERS_PARALLELISM'] = 'true' if config.Config.TOKENIZERS_PARALLELISM else 'false'

        # ChromaDB Settings
        self.db = None
        self.chromadb_settings = chromadb.config.Settings(
            anonymized_telemetry=config.Config.ANONYMIZED_TELEMETRY,
            allow_reset=config.Config.ALLOW_RESET,
        )

        self.llm = None
        self.service_context = None
        self.index = None

    def get_llm(self, args):
        return llama_index.llms.OpenAI(
            model='text-davinci-003',
            temperature=args.temperature,
            max_tokens=args.context,
            api_base=config.APIConfig.get_openai_api_base(host=args.api_host, port=args.api_port),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
            max_retries=args.max_retries,
            timeout=args.timeout,
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

    def get_index(self, service_context, args, storage_type=config.Config.STORAGE_TYPE):
        if storage_type == 'json' and self.index:
            return self.get_index(service_context, args)
        elif storage_type == 'chromadb':
            return self.get_index_chroma(service_context, args)
        else:
            return None

    def save_index(self, args, storage_type=config.Config.STORAGE_TYPE):
        if storage_type == 'json' and self.index:
            self.index.storage_context.persist(persist_dir=args.storage)
        elif storage_type == 'chromadb':
            # For ChromaDB, storage is already written to disk
            # as part of the loading data process
            pass

    def reset_index(self, args):
        logging.warning('resetting index')
        if config.Config.STORAGE_TYPE == 'json':
            utils.storage_reset(storage_path=args.storage)
        elif config.Config.STORAGE_TYPE == 'chromadb':
            if not self.db:
                self.db = chromadb.PersistentClient(
                    settings=self.chromadb_settings,
                    path=args.storage
                )
            self.db.reset()
            self.reset_chroma_collection()
            self.service_context = self.get_service_context(self.llm, args)
            self.index = self.get_index(self.service_context, args)

    @staticmethod
    def get_index_json(service_context, args):
        if args.load and all(os.path.exists(os.path.join(args.storage, filename))
                             for filename in config.Config.STORAGE_FILES):
            # load vector index from storage
            storage_context = llama_index.StorageContext.from_defaults(persist_dir=args.storage)
            return llama_index.load_index_from_storage(storage_context, service_context=service_context)
        else:
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

    def get_index_chroma(self, service_context, args):

        if not self.db:
            self.db = chromadb.PersistentClient(
                settings=self.chromadb_settings,
                path=args.storage
            )

        chroma_collection = self.db.get_or_create_collection('quickstart')

        # set up ChromaVectorStore and load in data
        vector_store = llama_index.vector_stores.ChromaVectorStore(chroma_collection=chroma_collection)

        if args.load:
            # noinspection PyTypeChecker
            index = llama_index.VectorStoreIndex.from_vector_store(
                vector_store,
                service_context=service_context,
            )
        else:
            storage_context = llama_index.storage.storage_context.StorageContext.from_defaults(
                vector_store=vector_store)

            documents = llama_index.SimpleDirectoryReader(args.data).load_data()
            index = llama_index.VectorStoreIndex.from_documents(
                documents, storage_context=storage_context, service_context=service_context
            )

        return index

    @staticmethod
    def reset_chroma_collection():
        chroma_client = chromadb.EphemeralClient()
        for collection in chroma_client.list_collections():
            chroma_client.delete_collection(name=collection.name)
