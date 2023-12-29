# [Urcuchillay](http://urcuchillay.ai)

"Ur-koo-CHEE-lye"

A lightweight [OpenAI API](https://platform.openai.com/docs/api-reference)-compatible service bundling a local [LLM](https://en.wikipedia.org/wiki/Large_language_model) with [RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation#Retrieval-augmented_generation) and hardware acceleration for Apple and NVIDIA GPUs.

![Urcuchillay](docs/images/urcuchillay-header.png)

In the Incan religion, Urcuchillay was depicted as a multicolored male llama, worshipped by Incan herders for his role in protecting and increasing the size of their herds.

## Features

- [OpenAI API](https://platform.openai.com/docs/api-reference)
- Local large language models ([LLMs](https://en.wikipedia.org/wiki/Large_language_model))
- Retrieval-augmented generation ([RAG](https://en.wikipedia.org/wiki/Retrieval-augmented_generation#Retrieval-augmented_generation))
- GPU acceleration
  - Apple Metal
  - NVIDIA CUDA
- Open Source
  - [MIT license](LICENSE)
- Python modules
  - [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
  - [LlamaIndex](https://www.llamaindex.ai)

# Table of Contents
- [Urcuchillay](#urcuchillay)
  - [Features](#features)
- [Table of Contents](#table-of-contents)
  - [Software](#software)
  - [Prerequisites](#prerequisites)
    - [macOS](#macos)
    - [Linux](#linux)
  - [Installation](#installation)
    - [Manual Installation](#manual-installation)
  - [Models](#models)
  - [Data](#data)
  - [Storage](#storage)
  - [Usage](#usage)
    - [Server](#server)
    - [Index](#index)
    - [Gateway](#gateway)
  - [Endpoint Tests](#endpoint-tests)
    - [Models](#models-1)
      - [Server](#server-1)
      - [Gateway](#gateway-1)
    - [Text Completion](#text-completion)
      - [Server](#server-2)
      - [Gateway](#gateway-2)
    - [Chat](#chat)
      - [Server](#server-3)
      - [Gateway](#gateway-3)
    - [Chat Streaming](#chat-streaming)
      - [Server](#server-4)
      - [Gateway](#gateway-4)


## Software

- [gateway.py](gateway.py): The core API service, merging a local LLM with RAG functionality via [LlamaIndex](https://www.llamaindex.ai) while conforming to OpenAI API [chat](https://platform.openai.com/docs/api-reference/chat) and [text-completion](https://platform.openai.com/docs/api-reference/completions) endpoints. All other endpoints are proxied through without modification to the local LLM server.
- [server.py](server.py): An embedded [Llama.cpp](https://github.com/ggerganov/llama.cpp/) service with [Python bindings](https://github.com/abetlen/llama-cpp-python) providing [OpenAI API](https://platform.openai.com/docs/api-reference)-compatible access to your local LLM.
- [index.py](index.py): A command-line tool to create and manage the vector store for retrieval-augmented generation (RAG).
- [prompt.py](prompt.py): A command-line tool for simple single queries to test the LLM and RAG storage.
- [config.json](config.json): This file overrides [default configuration settings](config.py) in a simple JSON format.

## Prerequisites

### macOS

- [Homebrew](https://brew.sh) is used to install software dependencies.

### Linux

- For NVIDIA GPU acceleration, please [install CUDA drivers](https://developer.nvidia.com/cuda-downloads?target_os=Linux).

## Installation

The setup script creates a virtual Python environment ([pyenv](https://github.com/pyenv/pyenv)) with all dependency modules prepared for use.
This script is suitable for both macOS and Linux (tested with [Ubuntu 22.04 LTS](http://releases.ubuntu.com/22.04/) and [Fedora 39](https://fedoraproject.org/workstation/download/)).
```shell
sh setup.sh
```

Alternatively, Urcuchillay can be installed directly via curl:
- Open the *Terminal* application and paste the following:
```shell
curl -L setup.urcuchillay.ai | sh
```

### Manual Installation
*Note*: Automated installation via ```setup.sh``` is recommended.

For manual installation instructions, see the [Manual Installation Guide](docs/manual-installation.md).

## Models
Models are automatically downloaded and cached locally if not already present.

A folder called ```models``` will be created in the current directory if it does not already exist.

By default, Urcuchillay supports alias names for the following models (by using the ```--model``` argument):
- mistral: (7B) [TheBloke/Mistral-7B-v0.1-GGUF](https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF)
- mixtral: (8x7B) [TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF](https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF)
- small: (7B) [TheBloke/Llama-2-7B-Chat-GGUF](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF)*
- medium: (13B) [TheBloke/Llama-2-13B-Chat-GGUF](https://huggingface.co/TheBloke/Llama-2-13B-Chat-GGUF)*
- large: (70B) [TheBloke/Llama-2-70B-Chat-GGUF](https://huggingface.co/TheBloke/Llama-2-70B-Chat-GGUF)*

Alternative models can be specified using the ```--model_url``` argument.

***Note**: Use of indicated models are governed by the Meta license. Please [visit the website and accept the license](https://ai.meta.com/resources/models-and-libraries/llama-downloads/) before using these models with Urcuchillay.

## Data
Urcuchillay uses [LlamaIndex](https://www.llamaindex.ai) for data ingesting and indexing.

[Supported file types](https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader.html#supported-file-types):
- .csv - comma-separated values
- .docx - Microsoft Word
- .epub - EPUB ebook format
- .hwp - Hangul Word Processor
- .ipynb - Jupyter Notebook
- .jpeg, .jpg - JPEG image
- .mbox - MBOX email archive
- .md - Markdown
- .mp3, .mp4 - audio and video
- .pdf - Portable Document Format
- .png - Portable Network Graphics
- .ppt, .pptm, .pptx - Microsoft PowerPoint

## Storage
The result of data files which have been indexed into a vector store can be saved to a local directory.

Files will be stored in a directory called ```storage``` by default.

The ```storage``` directory will be created if it does not already exist.

## Usage

***Note***: Typically after install via ```setup.sh``` it is necessary to activate the pyenv virtual environment for urcuchillay in a new terminal before use:
```shell
pyenv activate urcuchillay-env
```

### Server
- First the ```server.py``` service should be started:
```shell
./server.py
```
- If a model file is not found a download for the default model will automatically begin:
```shell
WARNING:server:Model not found. Downloading from URL.
Downloading url https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf to path models/mistral-7b-instruct-v0.1.Q4_K_M.gguf
total size (MB): 4368.44
  4%|█▋                                      | 181/4166 [00:04<01:43, 38.47it/s]
```

- Once initialized the service will begin accepting requests (on **localhost** port **8000** by default):
```shell
INFO:     Started server process [#]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
- A custom host and port can be specified via ```--api_host``` and ```--api_port``` arguments respectively.
- For additional options please check usage:
```shell
./server.py --help
```

### Index
- To generate and save a local vector store for RAG support, the ```index.py``` command-line tool is available.
- By default files in the ```data``` directory will be processed and the local vector store will be placed in a directory called ```storage```. These locations can be set using the ```--data``` and ```--storage``` arguments respectively.
- The following command will delete any existing local vector store and create a new one from files found in the ```data``` directory:
```shell
./index --reset
```
- For additional options please check usage:
```shell
./index.py --help
```

### Gateway
- The ```gateway.py``` service operates similarly to the ```server.py``` process but will include RAG support via LlamaIndex for any calls to the [chat](https://platform.openai.com/docs/api-reference/chat) or [text-completion](https://platform.openai.com/docs/api-reference/completions) endpoints.
- The service will scan files in the ```data``` directory at startup and create a vector store for RAG support.
- By default ```gateway.py``` will listen on **localhost** port **8080** and will communicate with ```server.py``` on port **8000**.
- The default host and port for the ```gateway.py``` service can be set using the ```--gateway_host``` and ```--gateway_port``` arguments.
```shell
./gateway.py
INFO:     Started server process [#]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```
- To save startup time, the ```index.py``` command can be used to create and save the vector store locally, and ```gateway.py``` can access this local cache using the ```--load``` argument:
```shell
./gateway --load
```
- For additional options please check usage:
```shell
./gateway.py --help
```

## Endpoint Tests
- Test scripts and other utilities can be found in the ```scripts``` directory.
- In the following examples the ```server.py``` and ```gateway.py``` services are running on their default ports:
  - ```server.py```: **8000**
  - ```gateway.py```: **8080**
- Results for ```server.py``` will only include the information on which the original model has been trained by the provider.
- Results for ```gateway.py``` will include RAG results from the vector store generated automatically at startup or previously created and saved by ```index.py```.

### Models
#### Server
```shell
./scripts/test-models.sh 8000
```
```json
{
  "object": "list",
  "data": [
    {
      "id": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
      "object": "model",
      "owned_by": "me",
      "permissions": []
    }
  ]
}%
```
#### Gateway
```shell
./scripts/test-models.sh 8080
```
```json
{
  "object": "list",
  "data": [
    {
      "id": "mistral-7b-instruct-v0.1.Q4_K_M.gguf",
      "object": "model",
      "owned_by": "me",
      "permissions": []
    }
  ]
}%
```

### Text Completion
#### Server
```shell
./scripts/test-prompt.sh 8000
```
```json
{
  "id": "cmpl-5237496e-00dd-445d-93b8-8b4574315464",
  "object": "text_completion",
  "created": 1703827990,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": "\nAnswer: I am not aware of any specific entity called \"Urcuchillay AI\". Could you please provide more context or details about this topic?",
      "index": 0,
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 33,
    "total_tokens": 43
  }
}%
```
#### Gateway
```shell
./scripts/test-prompt.sh 8080
```
```json
{
  "id": "cmpl-54a90e1a-5b03-406f-8cf4-a1367f6f08d1",
  "object": "text_completion",
  "created": 1703828070,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": "\nUrcuchillay AI is a local large language model (LLM) that utilizes retrieval-augmented generation (RAG) to provide responses. It can be accelerated using Apple and NVIDIA GPUs for better performance.",
      "index": 0,
      "finish_reason": "length"
    }
  ]
}%
```

### Chat
#### Server
```shell
./scripts/test-prompt-chat.sh 8000
```
```json
{
  "id": "chatcmpl-94442f30-d0a9-4091-af65-b0e02981b8f6",
  "object": "chat.completion",
  "created": 1703828618,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "content": "I'm not aware of a specific AI system or model named \"Urcuchillay AI.\" It is possible that you may be referring to a custom-built AI or an internal project with that name, which I wouldn't have information about. However, Urcuchillay is a deity in Andean mythology, often depicted as a rainbow-colored llama or alpaca, known for its ability to change its color and shape. If you can provide more context or clarify what you're looking for, I would be happy to try and help with your question!",
        "role": "assistant"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 33,
    "completion_tokens": 124,
    "total_tokens": 157
  }
}%
```
#### Gateway
```shell
./scripts/test-prompt-chat.sh 8080
```
```json
{
  "id": "cmpl-572964a9-4457-4da8-8530-d3f51676b9af",
  "object": "chat.completion",
  "created": 1703830758,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "\nUrcuchillay AI is a lightweight OpenAI API service bundling a local large language model (LLM) with retrieval-augmented generation (RAG) and hardware acceleration for Apple and NVIDIA GPUs."
      },
      "finish_reason": "stop"
    }
  ]
}%
```

### Chat Streaming
#### Server
```shell
./scripts/test-prompt-chat-stream.sh 8000
```
```
data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " I"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " couldn"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": "'"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": "t"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " find"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " any"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " specific"}, "finish_reason": null}]}

data: {"id": "chatcmpl-fb249baa-83bf-4cef-bfc1-47723d6a202b", "model": "gpt-3.5-turbo", "created": 1703830918, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {"content": " information"}, "finish_reason": null}]}
...
etc.
...
data: [DONE]
```
#### Gateway
```shell
./scripts/test-prompt-chat-stream.sh 8080
```
```
data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "\n"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "U"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "rc"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "uch"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "ill"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "ay"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " AI"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " is"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " an"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " advanced"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " language"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " model"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " that"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": " comb"}, "index": 0, "finish_reason": null}]}

data: {"id": "cmpl-41fdc520-b946-49ef-b49d-8930cc0a0dc5", "model": "gpt-3.5-turbo", "created": 1703829030, "object": "chat.completion.chunk", "choices": [{"delta": {"content": "ines"}, "index": 0, "finish_reason": null}]}
...
etc.
...
data: [DONE]
```
