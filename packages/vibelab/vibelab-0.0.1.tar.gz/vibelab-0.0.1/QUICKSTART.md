# VibeLab Quick Start

## Installation

```bash
# Install Python dependencies
uv sync

# Install frontend dependencies
cd web && bun install && cd ..
```

## Running the Application

### Start the Web UI

```bash
# Start both backend and frontend dev servers
vibelab start
# Or: uv run vibelab start
```

This starts:
- Backend API server at http://localhost:8000
- Frontend dev server at http://localhost:5173 (automatically proxies API requests)

Open http://localhost:5173 in your browser to use the web UI.

### Using the CLI

### Hello World Test

Start with a simple test using GitHub's official Hello-World repo:

```bash
# Quick hello world test (uses tiny repo, fast to clone)
./scripts/hello_world.sh

# Or run directly:
uv run vibelab run run-cmd \
  --code "github:octocat/Hello-World@master" \
  --prompt "Add a comment to the README saying 'Hello from VibeLab!'" \
  --executor "claude-code:anthropic:haiku" \
  --timeout 300
```

### General Usage

```bash
# Initialize database (happens automatically on first use)
uv run vibelab scenario list

# Create a scenario
uv run vibelab scenario create --code "github:owner/repo@main" --prompt "Add input validation"

# Run a scenario against executors
uv run vibelab run \
  --code "github:owner/repo@main" \
  --prompt "Add input validation" \
  --executor "claude-code:anthropic:sonnet" \
  --executor "openai-codex:openai:gpt-4o"

# List results
uv run vibelab result list

# View a result
uv run vibelab result get <result-id>

# View diff
uv run vibelab result diff <result-id>
```

## Development

```bash
# Format code
make fmt

# Lint code
make lint

# Type check
make check

# Run tests
make test

# Run development servers (backend + frontend)
make dev
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Git
- `uv` (Python package manager)
- `bun` (JavaScript runtime)

## Environment Variables

- `VIBELAB_HOME` - Data directory (default: `~/.vibelab`)
- `VIBELAB_DRIVER` - Execution driver (default: `local`)
- `VIBELAB_TIMEOUT` - Default timeout in seconds (default: `1800`)
- `VIBELAB_LOG_LEVEL` - Logging level (default: `INFO`)

## API Keys

Configure API keys for the agents you want to use:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export CURSOR_API_KEY=your-cursor-api-key
```
