#!/usr/bin/env python3
# Copyright (c) 2023-2024 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import json
import logging
import sys
import time

import client
import config
import schemas.openai

try:
    import fastapi
    import httpx
    import utils
    import uvicorn
except ModuleNotFoundError as e:
    print('\nError importing Python module(s)')
    print('If installed using setup.sh it may be necessary to run:\n')
    print('pyenv activate urcuchillay-env\n')
    sys.exit(1)


class Gateway(client.Client):
    def __init__(self, args):
        super().__init__(args)

        self.debug = args.debug

        self.args = args
        self.host = args.host
        self.port = args.port

        level = logging.DEBUG if self.debug else args.level
        logging.basicConfig(stream=sys.stdout, level=level)
        logging.getLogger().name = __name__

        self.llm = self.get_llm(args)

        if config.Config.STORAGE_TYPE == 'chromadb':
            args.embed_model_provider = 'BAAI'
            args.embed_model_name = 'bge-base-en-v1.5'

        self.service_context = self.get_service_context(self.llm, args)
        self.index = self.get_index(self.service_context, args)
        self.engine = None

        self.chat_mode = config.Config.CHAT_MODE


arguments = utils.parse_arguments()
gateway = Gateway(arguments)
app = fastapi.FastAPI()


@app.get('/v0/gateway/load')
async def load_index():
    """When the vector store is updated this service needs to reload it into memory"""
    args = gateway.args
    args.load = True
    gateway.get_index(gateway.service_context, args)
    return {'message': 'Index loaded successfully'}


@app.get('/v0/gateway/reset')
async def reset_index():
    """Resets the database. This will delete all collections and entries."""
    gateway.reset_index(gateway.args)
    return {'message': 'Index reset successfully'}


@app.api_route('/v1/completions', methods=['POST'])
async def completions_endpoint(request_data: schemas.openai.CompletionsRequest, request: fastapi.Request):
    # Check if the content type is application/json
    if request.headers.get('Content-Type') != 'application/json':
        raise fastapi.HTTPException(status_code=400, detail='Invalid Content-Type. Expected application/json.')

    # Log the request data for debugging
    logging.debug('Request Data:', request_data)

    created = int(time.time())

    if not request_data.stream:
        gateway.engine = gateway.index.as_query_engine()
        result = gateway.engine.query(request_data.prompt)

        response = {
            'id': utils.generate_message_id(),
            'object': 'text_completion',
            'created': created,
            'model': request_data.model,
            'choices': [
                {
                    'text': f'{result}',
                    'index': 0,
                    'finish_reason': 'length',
                },
            ],
        }
        return response

    else:
        gateway.engine = gateway.index.as_query_engine(streaming=True)
        message_id = utils.generate_message_id()

        # Use generator to handle streaming response
        def generate_responses():
            streaming_response = gateway.engine.query(request_data.prompt)
            tokens = list(streaming_response.response_gen)  # Convert generator to list

            for i, token in enumerate(tokens):
                finish_reason = None if i < len(tokens) - 1 else 'stop'

                choice = {
                    'text': f'{token}',
                    'index': 0,
                    'finish_reason': finish_reason,
                }

                # Format the chunk as in the OpenAI API response
                chunk_data = {
                    'id': message_id,
                    'object': 'text_completion',
                    'created': created,
                    'model': request_data.model,
                    'choices': [choice],
                }
                chunk = f'data: {json.dumps(chunk_data)}\n\n'
                yield chunk

        return fastapi.responses.StreamingResponse(generate_responses(), media_type='text/event-stream')


@app.api_route('/v1/chat/completions', methods=['POST'])
async def create_chat_completions(request_data: schemas.openai.ChatCompletionsRequest, request: fastapi.Request):
    if request.headers.get('Content-Type') != 'application/json':
        raise fastapi.HTTPException(status_code=400, detail='Invalid Content-Type. Expected application/json.')

    logging.debug('Request Data:', request_data)

    gateway.engine = gateway.index.as_chat_engine(chat_mode=gateway.chat_mode)

    # Assuming request_data_messages is a list of ChatMessage objects
    chat_history = [msg for msg in request_data.messages
                    if not (msg.role == schemas.openai.MessageRole.USER and
                            msg == request_data.messages[-1])]  # Don't place last user message received in chat_history

    # Find the last user message
    last_user_message = next((msg for msg in reversed(request_data.messages) if
                              msg.role == schemas.openai.MessageRole.USER), None)

    # TODO: Access to a protected member _memory of a class
    gateway.engine._memory.reset()  # To clear existing history if needed
    for message in chat_history:
        gateway.engine._memory.put(message)

    message_id = utils.generate_message_id()
    created = int(time.time())

    if not request_data.stream:
        content = gateway.engine.chat(last_user_message.content)
        response = {
            'id': message_id,
            'object': 'chat.completion',
            'created': created,
            'model': request_data.model,
            'choices': [
                {
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': content.response,
                    },
                    'finish_reason': 'stop'
                }
            ]
        }
        return response

    else:
        # Use generator to handle streaming response
        def generate_responses():
            if last_user_message.role == schemas.openai.MessageRole.USER:
                logging.info(f'User prompt: {last_user_message.content}')
                streaming_response = gateway.engine.stream_chat(last_user_message.content)
                tokens = list(streaming_response.response_gen)  # Convert generator to list

                for i, token in enumerate(tokens):
                    finish_reason = None if i < len(tokens) - 1 else 'stop'

                    choice = {
                        'delta': {
                            'content': f'{token}',
                        },
                        'index': 0,
                        'finish_reason': finish_reason,
                    }

                    # Format the chunk as in the OpenAI API response
                    chunk_data = {
                        'id': message_id,
                        'model': request_data.model,
                        'created': created,
                        'object': 'chat.completion.chunk',
                        'choices': [choice],
                    }
                    chunk = f'data: {json.dumps(chunk_data)}\n\n'
                    yield chunk

        return schemas.openai.CustomStreamingResponse(generate_responses())


async def get_request_body(request: fastapi.Request):
    body = None
    if request.method in ['POST', 'PUT', 'PATCH'] and request.headers.get('Content-Type') == 'application/json':
        try:
            body = await request.json()
        except json.JSONDecodeError:
            pass

    if body is None:
        body = await request.body()

    return body


@app.api_route('/v1/models', methods=['GET'])
async def models_endpoint(request: fastapi.Request):
    # Forward the request to the API server
    url = f'http://{arguments.api_host}:{arguments.api_port}/v1/models'

    body = await get_request_body(request)

    async with httpx.AsyncClient() as async_client:
        # Forward the original request method, headers, and body
        response = await async_client.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None
        )

        # Process the response to modify the model id
        response_data = response.json()  # Parse JSON response
        if 'data' in response_data:
            for item in response_data['data']:
                # If the complete local path (or URL) to a model was provided
                # then only supply the filename instead
                last_slash = max(item['id'].rfind('/'), item['id'].rfind('\\'))
                if last_slash != -1:
                    item['id'] = item['id'][last_slash+1:]

        content = json.dumps(response_data)
        headers = dict(response.headers)
        headers['content-length'] = str(len(content.encode('utf-8')))

        # Return the response from the llama app
        return fastapi.Response(content=content, status_code=response.status_code, headers=headers)


@app.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'])
async def forward(request: fastapi.Request, path: str):
    # Forward the request to the API server
    url = f'http://{arguments.api_host}:{arguments.api_port}/{path}'

    body = await get_request_body(request)

    async with httpx.AsyncClient() as async_client:
        # Forward the original request method, headers, and body
        response = await async_client.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=body if isinstance(body, dict) else None,
            content=body if not isinstance(body, dict) else None
        )

        # Return the response from the llama app
        return fastapi.Response(content=response.content, status_code=response.status_code,
                                headers=dict(response.headers))


def main():
    uvicorn.run(app, host=arguments.host, port=arguments.port)


if __name__ == '__main__':
    main()
