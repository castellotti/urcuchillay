# openai.py
# Copyright (c) 2023 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

import uuid
import fastapi
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union


# header
class CustomStreamingResponse(fastapi.responses.StreamingResponse):
    def __init__(self, content, *args, **kwargs):
        super().__init__(content, *args, **kwargs)
        # Set custom headers
        self.headers["Cache-Control"] = "no-cache"
        self.headers["Connection"] = "keep-alive"
        self.headers["X-Accel-Buffering"] = "no"
        self.headers["Content-Type"] = "text/event-stream; charset=utf-8"
        self.headers["OpenAI-Processing-ms"] = "658"  # This should ideally be dynamic
        self.headers["X-Request-ID"] = str(uuid.uuid4()).replace('-', '')  # Generate a unique ID for each request
        self.headers["Transfer-Encoding"] = "chunked"


# /v1/completions
class CompletionsRequest(BaseModel):
    model: str  # Required
    prompt: Union[str, List[str]]  # Required, can be either a string or a list of strings
    max_tokens: Optional[int] = None  # Optional
    temperature: Optional[float] = None  # Optional
    top_p: Optional[float] = None  # Optional
    n: Optional[int] = None  # Optional
    stream: Optional[bool] = None  # Optional
    logprobs: Optional[int] = None  # Optional
    echo: Optional[bool] = None  # Optional
    stop: Optional[Union[str, List[str]]] = None  # Optional, can be either a string or a list of strings
    presence_penalty: Optional[float] = None  # Optional
    frequency_penalty: Optional[float] = None  # Optional
    best_of: Optional[int] = None  # Optional
    user: Optional[str] = None  # Optional


# /v1/chat/completions
class MessageRole(Enum):
    USER = 'user'
    SYSTEM = 'system'
    ASSISTANT = 'assistant'


class ChatMessage(BaseModel):
    role: MessageRole = MessageRole.USER
    content: Optional[Any] = ""  # The message content
    id: Optional[str] = None  # Optional unique identifier for the message
    additional_kwargs: dict = Field(default_factory=dict)


class ChatCompletionsRequest(BaseModel):
    model: str  # Required, specifies the language model to be used
    messages: List[ChatMessage]  # Required, list of message objects
    max_tokens: Optional[int] = None  # Optional, maximum number of tokens to generate
    temperature: Optional[float] = None  # Optional, controls randomness
    top_p: Optional[float] = None  # Optional, controls diversity via nucleus sampling
    n: Optional[int] = None  # Optional, number of completions to generate for each prompt
    logprobs: Optional[int] = None  # Optional, number of log probabilities to return
    echo: Optional[bool] = None  # Optional, if True, includes the prompt in the output
    stop: Optional[Union[str, List[str]]] = None  # Optional, token(s) that signal the end of generation
    presence_penalty: Optional[float] = None  # Optional, adjusts for repetition
    frequency_penalty: Optional[float] = None  # Optional, adjusts for repetitiveness
    user: Optional[str] = None  # Optional, a string representing the user making the request
