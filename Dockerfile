# Optimized Dockerfile for Hugging Face Spaces
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama for Linux x86_64 (Standard HF Spaces CPU)
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && chmod +x /usr/bin/ollama

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0
ENV PORT=7860
ENV HOME=/tmp

# Create working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a more robust start script
RUN echo '#!/bin/bash\n\
export OLLAMA_MODELS=/app/ollama_models\n\
mkdir -p $OLLAMA_MODELS\n\
ollama serve &\n\
echo "Waiting for Ollama to start..."\n\
until curl -s http://localhost:11434/api/tags > /dev/null; do sleep 2; done\n\
echo "Ollama started. Pulling models..."\n\
ollama pull mistral\n\
ollama pull nomic-embed-text\n\
echo "Models ready. Starting FastAPI..."\n\
python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the port
EXPOSE 7860

# Entry point
CMD ["/app/start.sh"]
