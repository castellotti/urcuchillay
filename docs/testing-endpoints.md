# Testing Endpoints
- [Test Scripts](#test-scripts)
  - [Models](#models)
    - [Server](#server)
    - [Gateway](#gateway)
  - [Text Completion](#text-completion)
    - [Server](#server-1)
    - [Gateway](#gateway-1)
  - [Chat](#chat)
    - [Server](#server-2)
    - [Gateway](#gateway-2)
  - [Chat Streaming](#chat-streaming)
    - [Server](#server-3)
    - [Gateway](#gateway-3)

## Test Scripts
Test scripts and other utilities can be found in the [scripts](../scripts) directory.
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
