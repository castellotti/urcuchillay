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

LLM_MODELS = {
    'small': 7,
    'medium': 13,
    'large': 70
}
MODEL_SIZE_DEFAULT = 'small'
MODEL_URL_TEMPLATE = "https://huggingface.co/TheBloke/Llama-2-{MODEL_SIZE}B-chat-GGUF/" + \
                     "resolve/main/llama-2-{MODEL_SIZE}b-chat.Q4_K_M.gguf"

EMBED_MODEL_NAME = "local"

DATA_PATH = os.path.join(os.getcwd(), "data")
MODEL_PATH = os.getcwd()
STORAGE_PATH = os.path.join(os.getcwd(), "storage")

DEFAULT_PROMPT = "What is Urcuchillay?"


class Query:
    def __init__(self, args,
                 data_path=DATA_PATH,
                 model_path=MODEL_PATH,
                 storage_path=STORAGE_PATH):

        debug = args.debug

        load = args.load
        save = args.save
        enable_gpu = args.cpu
        temperature = args.temperature

        model_url = args.model_url
        model_name = args.model_name
        embed_model_name = args.embed_model_name
        embed_model_provider = args.embed_model_provider
        pretrained_model_name = args.pretrained_model_name
        pretrained_model_provider = args.pretrained_model_provider

        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(stream=sys.stdout, level=level)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

        llama_debug = llama_index.callbacks.LlamaDebugHandler(print_trace_on_end=debug)
        self.callback_manager = llama_index.callbacks.CallbackManager([llama_debug])

        if model_path is not None:
            path = os.path.join(model_path, model_name)
            if os.path.exists(path):
                model_url = "file://" + path

        os.environ["LLAMA_INDEX_CACHE_DIR"] = model_path

        if pretrained_model_name is not None:
            llama_index.set_global_tokenizer(
                transformers.AutoTokenizer.from_pretrained(
                    pretrained_model_provider + "/" + pretrained_model_name
                ).encode
            )

        self.llm = llama_index.llms.LlamaCPP(
            model_url=model_url,
            model_path=None,  # Setting a custom model path causes a fault
            temperature=temperature,
            max_new_tokens=256,
            context_window=3900,  # Llama 2 has a context window of 4096 tokens, set below for safety
            generate_kwargs={},  # kwargs to pass to __call__()
            model_kwargs={"n_gpu_layers": enable_gpu},  # kwargs to pass to __init__()
            # transform inputs into Llama 2 format
            messages_to_prompt=llama_index.llms.llama_utils.messages_to_prompt,
            completion_to_prompt=llama_index.llms.llama_utils.completion_to_prompt,
            verbose=debug,
        )

        if args.embed_model_name == "local":
            embed_model = args.embed_model_name
        else:
            # use Huggingface embeddings
            embed_model = llama_index.embeddings.HuggingFaceEmbedding(
                model_name=embed_model_provider + "/" + embed_model_name)

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
        print("Query: %s\n" % query)
        response = self.query_engine.query(query)
        print("Response: %s\n" % str(response).strip())


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
    parser.add_argument('--save', type=str2bool, nargs='?', const=True, default=False,
                        help='Save indexed vector store locally (default: %(default)s)')
    parser.add_argument('--load', type=str2bool, nargs='?', const=True, default=False,
                        help='Load indexed vector store (default: %(default)s)')
    parser.add_argument('--data_path', type=str, default=DATA_PATH,
                        help='The path to data files to be indexed (default: %(default)s)')
    parser.add_argument('--model_path', type=str, default=MODEL_PATH,
                        help='The path to store the "models" directory (default: %(default)s)')
    parser.add_argument('--storage_path', type=str, default=STORAGE_PATH,
                        help='The path to save and load the vector store (default: %(default)s)')
    parser.add_argument('--model_size', '--size', choices=LLM_MODELS.keys(), default=MODEL_SIZE_DEFAULT,
                        help='Select the model size (default: %(default)s)')
    parser.add_argument('--model_url', help='Custom model URL, overrides model size selection')
    parser.add_argument('--model_name', type=str, default=None,
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

    if not args.model_url:
        args.model_url = MODEL_URL_TEMPLATE.replace("{MODEL_SIZE}", str(LLM_MODELS[args.model_size]))
    if not args.model_name:
        args.model_name = args.model_url.split('/')[-1]

    return args


def main():
    args = parse_arguments()
    llm_query = Query(args=args)
    llm_query.display_exchange(args.prompt)


if __name__ == "__main__":
    main()
