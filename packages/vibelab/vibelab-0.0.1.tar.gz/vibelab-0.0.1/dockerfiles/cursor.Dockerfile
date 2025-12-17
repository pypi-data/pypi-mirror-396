# Dockerfile for Cursor harness
# Build with: docker build -f dockerfiles/cursor.Dockerfile -t vibelab/cursor:latest .

FROM node:20-slim

# Install git for patch generation
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install Cursor CLI (using curl method)
# Note: This is a placeholder - actual installation may vary
RUN curl https://cursor.com/install -fsS | bash || true

# Set working directory
WORKDIR /workspace

# Default command (container will be kept alive with sleep infinity)
CMD ["sleep", "infinity"]

