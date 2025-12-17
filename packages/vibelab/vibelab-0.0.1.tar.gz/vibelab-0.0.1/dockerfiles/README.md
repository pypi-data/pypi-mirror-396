# VibeLab Container Images

This directory contains Dockerfiles for building container images for each harness.

## Building Images

To build an image for a specific harness:

```bash
docker build -f dockerfiles/claude-code.Dockerfile -t vibelab/claude-code:latest .
docker build -f dockerfiles/openai-codex.Dockerfile -t vibelab/openai-codex:latest .
docker build -f dockerfiles/cursor.Dockerfile -t vibelab/cursor:latest .
docker build -f dockerfiles/gemini.Dockerfile -t vibelab/gemini:latest .
```

## Pushing to Registry

To push images to a registry (e.g., Docker Hub or GHCR):

```bash
docker tag vibelab/claude-code:latest your-registry/vibelab/claude-code:latest
docker push your-registry/vibelab/claude-code:latest
```

Then set the environment variable to use your registry:

```bash
export VIBELAB_CLAUDE_CODE_IMAGE=your-registry/vibelab/claude-code:latest
```

## Image Requirements

All harness images must:
1. Include git for patch generation
2. Install the harness CLI tool
3. Set `/workspace` as the working directory
4. Keep the container alive (use `sleep infinity` as CMD)

## Environment Variables

Containers will receive API keys via environment variables:
- `ANTHROPIC_API_KEY` (for Claude Code)
- `OPENAI_API_KEY` (for OpenAI Codex)
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` (for Gemini)
- `CURSOR_API_KEY` (for Cursor)

These are passed automatically by the Docker driver.

