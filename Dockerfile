# Dockerfile for Hugging Face Spaces
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -L https://ollama.com/download/ollama-linux-arm64 -o /usr/bin/ollama && chmod +x /usr/bin/ollama
# Note: For HF Spaces default CPU (x86_64), use this instead:
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && chmod +x /usr/bin/ollama

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0
ENV PORT=7860

# Create working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create start script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
ollama pull mistral\n\
ollama pull nomic-embed-text\n\
python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the port
EXPOSE 7860

# Entry point
CMD ["/app/start.sh"]
