# Dockerfile for Claude Code harness
# Build with: docker build -f dockerfiles/claude-code.Dockerfile -t vibelab/claude-code:latest .

FROM node:20-slim

# Install git for patch generation
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Set working directory
WORKDIR /workspace

# Default command (container will be kept alive with sleep infinity)
CMD ["sleep", "infinity"]

