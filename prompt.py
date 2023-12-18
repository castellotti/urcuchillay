#!/usr/bin/env python3
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import argparse
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


DEFAULT_PROMPT = 'What is Urcuchillay?'


class Prompt(client.Client):
    def __init__(self, args):

        super().__init__(args)

        self.llm = llama_index.llms.OpenAI(
            api_base=config.APIConfig.get_openai_api_base(),
            api_key=config.APIConfig.OPENAI_API_KEY,
            api_version=config.APIConfig.OPENAI_API_VERSION,
            callback_manager=self.callback_manager,
            temperature=args.temperature,
            model="text-davinci-002",
            max_tokens=config.Config.MAX_NEW_TOKENS,
        )

        # create a service context
        self.service_context = llama_index.ServiceContext.from_defaults(
            llm=self.llm,
            callback_manager=self.callback_manager,
            context_window=args.context,
            num_output=args.max_new_tokens,
        )

        self.get_index(args)

        # set up query engine
        self.query_engine = self.index.as_query_engine()

    def display_exchange(self, query):
        print('Query: %s\n' % query)

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
    prompt = Prompt(args=args)
    prompt.display_exchange(args.prompt)


if __name__ == '__main__':
    main()
