# Copyright (c) 2023-2024 Steve Castellotti
# This file is part of Urcuchillay and is released under the MIT License.
# See LICENSE file in the project root for full license information.

# Base
FROM python:3.11.6
WORKDIR /app

# Dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir fastapi httpx uvicorn llama_index transformers torch chromadb \
    pypdf Pillow docx2txt nbconvert EbookLib html2text \
    pydub git+https://github.com/openai/whisper.git

# Package
COPY gateway.py client.py config.py utils.py ./
COPY schemas ./schemas

# Make API port 8080 available
EXPOSE 8080

# Mount points
VOLUME ["/app/data", "/app/storage", "/app/config.json"]

# Run gateway.py with optional argumenets when the container launches
ENTRYPOINT ["python3", "./gateway.py"]
