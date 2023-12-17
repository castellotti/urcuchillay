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


DEFAULT_PROMPT = 'What is Urcuchillay?'


class Query:
    def __init__(self, args):

        self.debug = args.debug

        data_path = args.data
        model_path = args.path
        storage_path = args.storage

        load = args.load
        save = args.save
        enable_gpu = args.cpu
        temperature = args.temperature
        max_new_tokens = args.max_new_tokens
        context_window = args.context

        self.model_name = args.model
        model_url = args.model_url
        embed_model_name = args.embed_model_name
        embed_model_provider = args.embed_model_provider
        pretrained_model_name = args.pretrained_model_name
        pretrained_model_provider = args.pretrained_model_provider

        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(stream=sys.stdout, level=level)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        llama_debug = llama_index.callbacks.LlamaDebugHandler(print_trace_on_end=self.debug)
        self.callback_manager = llama_index.callbacks.CallbackManager([llama_debug])

        # llama_index will automatically assume models are cached in a subdirectory of the current path named
        # "models" so we need to handle if a user explicitly included "models" at the end of --model_path
        cache_directory = model_path
        if os.path.basename(model_path) == 'models':
            path = os.path.join(model_path, self.model_name)
            cache_directory = os.path.dirname(model_path)
        else:
            path = os.path.join(model_path, 'models', self.model_name)
        if os.path.exists(path):
            model_url = 'file://' + str(path)

        os.environ['LLAMA_INDEX_CACHE_DIR'] = cache_directory

        if pretrained_model_name is not None:
            llama_index.set_global_tokenizer(
                transformers.AutoTokenizer.from_pretrained(
                    pretrained_model_provider + '/' + pretrained_model_name
                ).encode
            )

        self.llm = llama_index.llms.LlamaCPP(
            model_url=model_url,
            model_path=None,  # Note: setting a custom model_path here causes a fault
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            context_window=context_window,
            generate_kwargs={},  # kwargs to pass to __call__()
            model_kwargs={'n_gpu_layers': enable_gpu},  # kwargs to pass to __init__()
            # transform inputs into Llama 2 format
            messages_to_prompt=llama_index.llms.llama_utils.messages_to_prompt,
            completion_to_prompt=llama_index.llms.llama_utils.completion_to_prompt,
            verbose=self.debug,
        )

        if args.embed_model_name == 'local':
            embed_model = args.embed_model_name
        else:
            # use Huggingface embeddings
            embed_model = llama_index.embeddings.HuggingFaceEmbedding(
                model_name=embed_model_provider + '/' + embed_model_name)

        # create a service context
        service_context = llama_index.ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=embed_model,
            callback_manager=self.callback_manager
        )

        if load:
            # load vector index from storage
            storage_context = llama_index.StorageContext.from_defaults(persist_dir=storage_path)
            index = llama_index.load_index_from_storage(storage_context, service_context=service_context)
        else:
            # load documents
            documents = llama_index.SimpleDirectoryReader(data_path).load_data()
            # create vector store index
            index = llama_index.VectorStoreIndex.from_documents(
                documents, service_context=service_context
            )

        # persist the index to disk
        if save:
            index.storage_context.persist(persist_dir=storage_path)

        # set up query engine
        self.query_engine = index.as_query_engine()

    def display_exchange(self, query):
        print('Query: %s\n' % query)

        if self.model_name in config.Models.MODELS.keys():
            query = config.Models.MODELS[self.model_name]['prompt_template'].replace('{prompt}', query)
            if self.debug:
                print('Query (prompt): %s\n' % query)

        response = self.query_engine.query(query)
        print('Response: %s\n' % str(response).strip())


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')

    parser.add_argument('-p', '--prompt', type=str, default=DEFAULT_PROMPT,
                        help='The prompt to process (default: %(default)s)')

    parser = utils.parse_arguments_common(parser)

    args = parser.parse_args()

    args = utils.update_arguments_common(args)

    return args


def main():
    args = parse_arguments()
    llm_query = Query(args=args)
    llm_query.display_exchange(args.prompt)


if __name__ == '__main__':
    main()
