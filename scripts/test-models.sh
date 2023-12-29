#!/bin/sh

HOST=127.0.0.1
PORT=8000

if [ -n "$1" ]; then
    PORT=$1
fi

curl "http://$HOST:$PORT/v1/models" \
  -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer xxxxxxxx"
