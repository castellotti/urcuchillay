#!/bin/sh

HOST=127.0.0.1
PORT=8000

if [ -n "$1" ]; then
    PORT=$1
fi

curl "http://$HOST:$PORT/v1/chat/completions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxxxxxx" \
  -d '{
        "model": "gpt-3.5-turbo",
        "messages": [
          {
            "role": "system",
            "content": "You are ChatGPT, a large language model trained by OpenAI. Follow the users instructions carefully. Respond using markdown."
          },
          {
            "role": "user",
            "content": "What is Urcuchillay AI?"
          }
        ],
        "max_tokens": 3900,
        "temperature": 1.0,
        "stream": true
      }'
