# Base
FROM python:3.11.6
WORKDIR /usr/src/app

# Dependencies
RUN pip install --no-cache-dir fastapi httpx uvicorn llama_index transformers torch pypdf Pillow

# Package
COPY gateway.py client.py config.py utils.py ./
COPY schemas ./schemas

# Make API port 8080 available
EXPOSE 8080

# Mount points
VOLUME ["/usr/src/app/data", "/usr/src/app/storage", "/usr/src/app/config.json"]

# Run gateway.py with optional argumenets when the container launches
ENTRYPOINT ["python", "./gateway.py"]
