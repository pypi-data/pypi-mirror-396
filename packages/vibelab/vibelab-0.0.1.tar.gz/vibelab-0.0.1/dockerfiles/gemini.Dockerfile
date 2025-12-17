# Dockerfile for Gemini harness
# Build with: docker build -f dockerfiles/gemini.Dockerfile -t vibelab/gemini:latest .

FROM python:3.11-slim

# Install git for patch generation
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Google Generative AI SDK
RUN pip install --no-cache-dir google-generativeai

# Set working directory
WORKDIR /workspace

# Default command (container will be kept alive with sleep infinity)
CMD ["sleep", "infinity"]

