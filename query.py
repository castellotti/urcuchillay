#!/usr/bin/env python3
import argparse
import logging
import os
import sys

try:
    import llama_index
    import transformers
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)

DEBUG = False

ENABLE_GPU = 1
TEMPERATURE = 0.1
MAX_NEW_TOKENS = 256
CONTEXT_WINDOW = 3900  # Llama 2 has a context window of 4096 tokens, set below for safety

MODELS = {
    'llama-2-7b-chat.Q4_K_M.gguf': {  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        'model': 'https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF',
        'url': 'https://huggingface.co/TheBloke/Llama-2-7B-chat-GGUF/' +
               'resolve/main/llama-2-7b-chat.Q4_K_M.gguf',
        'prompt_template': '{prompt}',
        'model_creator': 'Meta',
        'model_provider': 'TheBloke',
    },
    'llama-2-13b-chat.Q4_K_M.gguf': {  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        'model': 'https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF',
        'url': 'https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/' +
               'resolve/main/llama-2-13b-chat.Q4_K_M.gguf',
        'prompt_template': '{prompt}',
        'model_creator': 'Meta',
        'model_provider': 'TheBloke',
    },
    'llama-2-70b-chat.Q4_K_M.gguf': {  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        'model': 'https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF',
        'url': 'https://huggingface.co/TheBloke/Llama-2-70B-chat-GGUF/' +
               'resolve/main/llama-2-70b-chat.Q4_K_M.gguf',
        'prompt_template': '{prompt}',
        'model_creator': 'Meta',
        'model_provider': 'TheBloke',
    },
    'mistral-7b-v0.1.Q4_K_M.gguf': {  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        'model': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF',
        'url': 'https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf',
        'prompt_template': '[INST] {prompt} [/INST]',
        'model_creator': 'Mistral AI',
        'model_provider': 'TheBloke',
    },
    'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf': {  # (Q4_K_M: 4-bit, medium, balanced quality - recommended)
        'model': 'https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF',
        'url': 'https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/' +
               'resolve/main/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
        'prompt_template': '[INST] {prompt} [/INST]',
        'model_creator': 'Mistral AI',
        'model_provider': 'TheBloke',
    },
}

MODEL_ALIASES = {
    '7': 'llama-2-7b-chat.Q4_K_M.gguf',
    '7b': 'llama-2-7b-chat.Q4_K_M.gguf',
    'llama-2-7b': 'llama-2-7b-chat.Q4_K_M.gguf',
    '13': 'llama-2-13b-chat.Q4_K_M.gguf',
    '13b': 'llama-2-13b-chat.Q4_K_M.gguf',
    'llama-2-13b': 'llama-2-13b-chat.Q4_K_M.gguf',
    '70': 'llama-2-70b-chat.Q4_K_M.gguf',
    '70b': 'llama-2-70b-chat.Q4_K_M.gguf',
    'llama-2-70b': 'llama-2-70b-chat.Q4_K_M.gguf',
    'small': 'llama-2-7b-chat.Q4_K_M.gguf',
    'medium': 'llama-2-13b-chat.Q4_K_M.gguf',
    'large': 'llama-2-70b-chat.Q4_K_M.gguf',
    'mistral': 'mistral-7b-v0.1.Q4_K_M.gguf',
    'mistral-7b': 'mistral-7b-v0.1.Q4_K_M.gguf',
    'mixtral': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
    'mixtral-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
    'mixtral-8x7b': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
    'mixtral-8x7b-instruct': 'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf',
}

MODEL_URL_DEFAULT = MODELS[MODEL_ALIASES['7']]['url']

EMBED_MODEL_NAME = 'local'

DATA_PATH = os.path.join(os.getcwd(), 'data')
MODEL_PATH = os.path.join(os.getcwd(), 'models')
STORAGE_PATH = os.path.join(os.getcwd(), 'storage')

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

        if self.model_name in MODELS.keys():
            query = MODELS[self.model_name]['prompt_template'].replace('{prompt}', query)
            if self.debug:
                print('Query (prompt): %s\n' % query)

        response = self.query_engine.query(query)
        print('Response: %s\n' % str(response).strip())


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 'on', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'off', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process command parameters')
    parser.add_argument('--debug', type=str2bool, nargs='?', const=True, default=DEBUG,
                        help='Enable debug mode (default: %(default)s)')
    parser.add_argument('-p', '--prompt', type=str, default=DEFAULT_PROMPT,
                        help='The prompt to process (default: %(default)s)')
    parser.add_argument('--cpu', action='store_const', const=0, default=ENABLE_GPU,
                        help='Use the CPU only instead of GPU acceleration')
    parser.add_argument('--temperature', type=float, default=TEMPERATURE,
                        help='The temperature value for the model (default: %(default)s)')
    parser.add_argument('--max_new_tokens', type=float, default=MAX_NEW_TOKENS,
                        help='The max new tokens value for the model (default: %(default)s)')
    parser.add_argument('--context', '--context_window', type=float, default=CONTEXT_WINDOW,
                        help='The context window value for the model (default: %(default)s)')
    parser.add_argument('--save', type=str2bool, nargs='?', const=True, default=False,
                        help='Save indexed vector store locally (default: %(default)s)')
    parser.add_argument('--load', type=str2bool, nargs='?', const=True, default=False,
                        help='Load indexed vector store (default: %(default)s)')
    parser.add_argument('--data', '--data_path', type=str, default=DATA_PATH,
                        help='The path to data files to be indexed (default: %(default)s)')
    parser.add_argument('--path', '--model_path', type=str, default=MODEL_PATH,
                        help='The path to the directory for cached models (default: %(default)s)')
    parser.add_argument('--storage', '--storage_path', type=str, default=STORAGE_PATH,
                        help='The path to save and load the vector store (default: %(default)s)')
    parser.add_argument('--model_url', type=str, default=MODEL_URL_DEFAULT,
                        help='Custom URL for model')
    parser.add_argument('--model', '--model_name', type=str, default=None,
                        help='The name of the model to use (default: extracted from model url)')
    parser.add_argument('--embed_model_name', type=str, default=EMBED_MODEL_NAME,
                        help='The name of the embedding model to use (default: %(default)s)')
    parser.add_argument('--embed_model_provider', type=str, default=None,
                        help='The provider of the embedding model to use (default: %(default)s)')
    parser.add_argument('--pretrained_model_name', type=str, default=None,
                        help='The name of the pretrained model to use (default: %(default)s)')
    parser.add_argument('--pretrained_model_provider', type=str, default=None,
                        help='The provider of the pretrained model to use (default: %(default)s)')

    args = parser.parse_args()

    if not args.model:
        args.model = args.model_url.split('/')[-1]

    if str.lower(args.model) in MODEL_ALIASES.keys():
        args.model = MODEL_ALIASES[args.model]

    return args


def main():
    args = parse_arguments()
    llm_query = Query(args=args)
    llm_query.display_exchange(args.prompt)


if __name__ == '__main__':
    main()
