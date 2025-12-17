# Dockerfile for OpenAI Codex harness
# Build with: docker build -f dockerfiles/openai-codex.Dockerfile -t vibelab/openai-codex:latest .

FROM node:20-slim

# Install git for patch generation
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install OpenAI Codex CLI
RUN npm install -g @openai/codex

# Set working directory
WORKDIR /workspace

# Default command (container will be kept alive with sleep infinity)
CMD ["sleep", "infinity"]

