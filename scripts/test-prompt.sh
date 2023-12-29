#!/bin/sh

HOST=127.0.0.1
PORT=8000

if [ -n "$1" ]; then
    PORT=$1
fi

curl "http://$HOST:$PORT/v1/completions" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxxxxxx" \
  -d '{
        "model": "text-davinci-003",
        "prompt": "What is Urcuchillay AI?",
        "max_tokens": 256,
        "temperature": 1.0
      }'
