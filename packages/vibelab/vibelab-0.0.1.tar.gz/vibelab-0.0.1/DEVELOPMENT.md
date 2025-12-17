# VibeLab Development Guide

This guide covers setting up a development environment and contributing to VibeLab.

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Git
- [uv](https://github.com/astral-sh/uv) - Python package manager
- [bun](https://bun.sh/) - JavaScript runtime and package manager

## Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-org/vibelab
cd vibelab

# Install all dependencies
make install

# Run the development servers (starts both backend and frontend)
make dev

# Or use the CLI command (recommended)
uv run vibelab start
```

## Project Structure

```
vibelab/
├── Makefile                 # Build orchestration
├── pyproject.toml           # Python project config
├── README.md                # User documentation
├── SPEC.md                  # Product requirements
├── PLAN.md                  # Implementation plan
├── DEVELOPMENT.md           # This file
├── AGENTS.md                # LLM agent instructions
│
├── src/vibelab/             # Python backend
│   ├── __init__.py
│   ├── models/              # Pydantic types
│   │   ├── __init__.py
│   │   ├── scenario.py
│   │   ├── result.py
│   │   ├── executor.py
│   │   └── dataset.py
│   ├── db/                  # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── migrations.py
│   │   └── queries.py
│   ├── engine/              # Core execution engine
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   ├── streaming.py     # Real-time log streaming
│   │   └── loader.py
│   ├── drivers/             # Execution environments
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── docker.py
│   │   └── modal.py
│   ├── harnesses/           # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── claude_code.py
│   │   ├── openai_codex.py
│   │   └── cursor.py
│   ├── cli/                 # CLI commands
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── run.py
│   │   ├── scenario.py
│   │   ├── result.py
│   │   ├── executor.py
│   │   └── dataset.py
│   ├── api/                 # FastAPI routes
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── scenarios.py
│   │   ├── results.py
│   │   ├── runs.py
│   │   ├── datasets.py
│   │   └── streaming.py     # SSE streaming endpoints
│   └── lib.py               # Public library interface
│
├── web/                     # React frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api.ts
│       └── components/
│           ├── Dashboard.tsx
│           ├── Scenarios.tsx
│           ├── Runs.tsx
│           ├── Executors.tsx
│           ├── Navbar.tsx
│           ├── Breadcrumbs.tsx
│           ├── RunCreate.tsx
│           ├── ScenarioDetail.tsx
│           ├── ResultDetail.tsx
│           ├── CompareResults.tsx
│           ├── Datasets.tsx
│           ├── DatasetDetail.tsx
│           ├── DatasetCreate.tsx
│           ├── DatasetAnalytics.tsx
│           ├── DiffViewer.tsx
│           ├── LogsViewer.tsx       # Chat/raw log display
│           └── StreamingLogs.tsx    # Real-time SSE log viewer
│
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_models.py
    │   ├── test_db.py
    │   └── test_harnesses.py
    ├── integration/
    │   ├── test_runner.py
    │   └── test_api.py
    └── e2e/
        └── test_workflows.py
```

## Development Commands

The Makefile provides standard commands:

```bash
make install    # Install all dependencies (Python + frontend)
make dev        # Run development servers
make fmt        # Format all code
make lint       # Lint all code
make check      # Type check all code
make build      # Build all artifacts
make test       # Run all tests
make clean      # Remove build artifacts
```

### Individual Commands

```bash
# Python
uv sync                          # Install Python dependencies
uv run pytest                    # Run tests
uv run ruff format .             # Format Python code
uv run ruff check .              # Lint Python code
uv run mypy src                  # Type check Python code

# Frontend
cd web && bun install            # Install frontend dependencies
# Or use the unified start command (recommended):
uv run vibelab start             # Starts both backend and frontend dev servers
cd web && bun run build          # Build production bundle
cd web && bun run typecheck      # Type check TypeScript
cd web && bun run lint           # Lint TypeScript code
```

## Feature Development Layering

When implementing features, follow this layered approach:

```
0. Tests        → Write tests first (TDD when practical)
1. DB           → Minimal schema changes if needed
2. Core Engine  → State management and data fetching
3. Library      → Expose as typed Python function in lib.py
4. API          → Expose as FastAPI endpoint
5. CLI          → Expose as command-line interface
6. UI           → Expose in web interface
```

This ensures well-architected, testable code with multiple access patterns.

## Backend Development

### Adding a New Harness

1. Create a new file in `src/vibelab/harnesses/`:

```python
# src/vibelab/harnesses/my_agent.py
from pathlib import Path
from vibelab.harnesses.base import Harness, HarnessOutput, ModelInfo

class MyAgentHarness(Harness):
    id = "my-agent"
    name = "My Agent"
    supported_providers = ["my-provider"]
    preferred_driver = None  # Or "docker" if needed

    def get_models(self, provider: str) -> list[ModelInfo]:
        return [
            ModelInfo(id="model-a", name="Model A"),
            ModelInfo(id="model-b", name="Model B"),
        ]

    def check_available(self) -> tuple[bool, str | None]:
        # Check if CLI is installed
        import shutil
        if shutil.which("my-agent") is None:
            return False, "my-agent CLI not found"
        return True, None

    def run(
        self,
        workdir: Path,
        prompt: str,
        provider: str,
        model: str,
        timeout_seconds: int,
    ) -> HarnessOutput:
        import subprocess
        cmd = ["my-agent", "--model", model, prompt]
        result = subprocess.run(
            cmd,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        return HarnessOutput(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
```

2. Register in `src/vibelab/harnesses/__init__.py`:

```python
from .my_agent import MyAgentHarness

HARNESSES = {
    # ... existing harnesses
    "my-agent": MyAgentHarness(),
}
```

### Adding a New Driver

1. Create a new file in `src/vibelab/drivers/`:

```python
# src/vibelab/drivers/my_driver.py
from vibelab.drivers.base import Driver, ExecutionContext, RunOutput

class MyDriver(Driver):
    id = "my-driver"

    def setup(self, ctx: ExecutionContext) -> None:
        # Prepare execution environment
        pass

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        # Run the harness
        pass

    def cleanup(self, ctx: ExecutionContext) -> None:
        # Clean up resources
        pass
```

2. Register in `src/vibelab/drivers/__init__.py`

### Database Migrations

Add migrations to `src/vibelab/db/migrations.py`:

```python
MIGRATIONS = [
    # Version 1: Initial schema
    "...",
    # Version 2: Your new migration
    """
    ALTER TABLE results ADD COLUMN new_field TEXT;
    """,
]
```

Migrations run automatically on startup.

### Streaming Infrastructure

VibeLab uses file-based streaming for real-time log output:

```
~/.vibelab/results/{result_id}/
├── combined.stream     # Real-time combined stdout+stderr
├── stdout.stream       # Real-time stdout only
├── stderr.stream       # Real-time stderr only
├── stream.status       # Current status (queued/running/completed/failed)
├── stdout.log          # Final stdout (after completion)
├── stderr.log          # Final stderr (after completion)
└── patch.diff          # Git diff of changes
```

#### Using StreamingLog in Drivers/Harnesses

```python
from vibelab.engine.streaming import StreamingLog

# Create streaming log
streaming_log = StreamingLog(result_id=result.id)
streaming_log.set_status("running")

# Append output in real-time
streaming_log.append_stdout("Starting execution...\n")
streaming_log.append_stderr("Warning: ...\n")

# Finalize when done
streaming_log.finalize(final_stdout=output, final_stderr=stderr)
# Or mark as failed
streaming_log.mark_failed()
```

#### Updating Result Status

Always update `updated_at` when changing result status:

```python
from vibelab.db import update_result_status
from vibelab.models.result import ResultStatus

# This automatically sets updated_at
update_result_status(db, result_id, ResultStatus.RUNNING, started_at=now)
```

## Frontend Development

### Tech Stack

- React 18
- TypeScript
- Vite
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- CSS Custom Properties (design tokens)

### Design System & Style Guide

VibeLab uses a design token-based system inspired by Weights & Biases. All colors, spacing, and typography are defined as CSS custom properties in `web/src/styles/tokens.css`.

#### Design Tokens

**Never use hardcoded colors.** Always use semantic token classes:

```tsx
// ❌ Bad - hardcoded colors
<div className="bg-gray-800 text-green-300 border-gray-700">

// ✅ Good - semantic tokens
<div className="bg-surface text-status-success border-border">
```

**Color tokens available:**

| Token | Usage |
|-------|-------|
| `bg-canvas` | Page background |
| `bg-surface` | Card/panel backgrounds |
| `bg-surface-2` | Elevated surfaces (headers) |
| `bg-surface-3` | Hover states |
| `border` | Primary borders |
| `border-muted` | Subtle borders |
| `text-primary` | Main text |
| `text-secondary` | Secondary text |
| `text-tertiary` | Muted/hint text |
| `text-disabled` | Disabled text |
| `accent` | Primary accent (gold) |
| `accent-hover` | Accent hover state |
| `accent-muted` | Accent backgrounds |
| `on-accent` | Text on accent backgrounds |
| `status-success` | Success states (green) |
| `status-error` | Error states (red) |
| `status-warning` | Warning states (yellow) |
| `status-info` | Info states (blue) |
| `status-*-muted` | Muted status backgrounds |

#### UI Components

Use the pre-built components from `web/src/components/ui/`:

```tsx
import { 
  Button,           // Primary, secondary, ghost, danger variants
  Card,             // Container with header/content
  Table,            // Data tables with sticky headers
  Badge,            // Status labels
  StatusBadge,      // Result status display
  Input,            // Form text input
  Select,           // Dropdown select
  Textarea,         // Multi-line input
  Checkbox,         // Checkbox with label
  Dialog,           // Modal dialogs
  ConfirmDialog,    // Confirmation modals
  PageHeader,       // Page title with breadcrumbs
  EmptyState,       // Empty content placeholder
  DropdownMenu,     // Action menus
} from './ui'
```

**Button variants:**

```tsx
<Button variant="primary">Save</Button>      // Gold accent
<Button variant="secondary">Cancel</Button>  // Subtle gray
<Button variant="ghost">Edit</Button>        // Text only
<Button variant="danger">Delete</Button>     // Red (use in menus)
```

**Card pattern:**

```tsx
<Card>
  <Card.Header>
    <Card.Title>Section Title</Card.Title>
  </Card.Header>
  <Card.Content>
    {/* Content */}
  </Card.Content>
</Card>
```

**Table pattern:**

```tsx
<Table maxHeight="500px">
  <Table.Header>
    <tr>
      <Table.Head>Column</Table.Head>
    </tr>
  </Table.Header>
  <Table.Body>
    <Table.Row>
      <Table.Cell>Value</Table.Cell>
    </Table.Row>
  </Table.Body>
</Table>
```

#### Interaction States

All interactive elements should have hover, active, and focus states:

```tsx
// Buttons have built-in states via CVA variants
<Button variant="primary">Click me</Button>

// For custom interactive elements, use these patterns:
<button className={cn(
  'px-3 py-2 rounded transition-all duration-150',
  'bg-surface-2 text-text-secondary',
  'hover:bg-surface-3 hover:text-text-primary',
  'active:scale-[0.97]',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent'
)}>
  Custom Button
</button>
```

#### Layout Guidelines

1. **Always use breadcrumbs** - Every page should have a `PageHeader` with breadcrumbs
2. **Tables over tiles** - Use table views for data lists, not card grids
3. **Consistent spacing** - Use `mb-6` between major sections
4. **Hide destructive actions** - Put delete/danger actions in `DropdownMenu`
5. **Always-visible action buttons** - Don't conditionally render action buttons; disable them instead

#### The `cn()` Utility

Use the `cn()` helper for conditional classes:

```tsx
import { cn } from '../lib/cn'

<div className={cn(
  'base-classes',
  isActive && 'active-classes',
  variant === 'large' && 'large-classes'
)}>
```

#### Theme Support

The app supports light and dark modes via `data-theme` attribute on `<html>`. Tokens automatically adapt - no need for `dark:` prefixes when using semantic tokens.

### Adding a New Page

**Design Pattern**: Prefer table views over nested detail views for better data scanning. See the Executors page (`Executors.tsx`) as an example of a single table with filtering and selection.

1. Create component in `web/src/components/`:

```tsx
// web/src/components/MyPage.tsx
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { fetchData } from '../api'
import { PageHeader, Table, Button, EmptyState } from './ui'

export default function MyPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['my-data'],
    queryFn: fetchData,
  })

  if (isLoading) {
    return (
      <div>
        <PageHeader 
          breadcrumbs={[{ label: 'My Page' }]} 
          title="My Page" 
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'My Page' }]}
        title="My Page"
        description="Description of what this page shows"
        actions={
          <Link to="/my-page/create">
            <Button>New Item</Button>
          </Link>
        }
      />

      {!data || data.length === 0 ? (
        <EmptyState
          title="No items yet"
          description="Create your first item to get started."
          action={
            <Link to="/my-page/create">
              <Button>Create Item</Button>
            </Link>
          }
        />
      ) : (
        <Table>
          <Table.Header>
            <tr>
              <Table.Head>ID</Table.Head>
              <Table.Head>Name</Table.Head>
              <Table.Head>Status</Table.Head>
              <Table.Head></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {data.map((item) => (
              <Table.Row key={item.id}>
                <Table.Cell mono className="text-text-tertiary text-xs">
                  {item.id}
                </Table.Cell>
                <Table.Cell className="text-text-primary">
                  {item.name}
                </Table.Cell>
                <Table.Cell>
                  <StatusBadge status={item.status} />
                </Table.Cell>
                <Table.Cell>
                  <Link to={`/my-page/${item.id}`}>
                    <Button variant="ghost" size="sm">View</Button>
                  </Link>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      )}
    </div>
  )
}
```

2. Add route in `web/src/App.tsx`:

```tsx
<Route path="/my-page" element={<MyPage />} />
```

### API Client

Add API functions to `web/src/api.ts`:

```typescript
export async function fetchData(): Promise<MyData> {
  const response = await fetch(`${API_BASE}/my-endpoint`)
  if (!response.ok) throw new Error('Failed to fetch')
  return response.json()
}
```

### Real-time Updates & Polling

VibeLab uses a hybrid approach for real-time updates:

1. **SSE (Server-Sent Events)** for streaming logs during execution
2. **Conditional polling** for status updates on list/detail pages

#### Adding Polling to a Component

Use TanStack Query's `refetchInterval` with a function to conditionally poll:

```typescript
const { data, isLoading } = useQuery({
  queryKey: ['my-data'],
  queryFn: fetchMyData,
  // Poll every 3 seconds if any items are "running", otherwise stop
  refetchInterval: (query) => {
    const data = query.state.data
    const hasActiveItems = data?.some(item => 
      item.status === 'running' || item.status === 'queued'
    )
    return hasActiveItems ? 3000 : false
  },
})
```

**Important:** Always use lowercase status values when comparing (`'running'`, not `'RUNNING'`). The API returns lowercase status strings.

#### Using SSE for Streaming Logs

For real-time log streaming, use the `subscribeToResultStream` helper:

```typescript
import { subscribeToResultStream } from '../api'

useEffect(() => {
  const close = subscribeToResultStream(resultId, {
    onConnect: () => setStatus('connected'),
    onStatus: (status) => setStatus(status),
    onOutput: (data) => setLogs(prev => prev + data),
    onPatch: (patch) => setPatch(patch),
    onDone: (status) => {
      setStatus(status)
      queryClient.invalidateQueries({ queryKey: ['result', resultId] })
    },
    onError: (error) => setError(error),
  })
  
  return () => close()  // Cleanup on unmount
}, [resultId])
```

#### Status Values

Result status is always lowercase:
- `queued` - Waiting to start
- `running` - Currently executing  
- `completed` - Finished successfully
- `failed` - Execution failed
- `timeout` - Exceeded timeout limit

#### Stale Results

Results include an `is_stale` boolean that's true when:
- Status is `running`
- Elapsed time exceeds the configured timeout

Display stale results with a warning indicator in the UI.

## Testing

### Running Tests

```bash
# All tests
make test

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=src/vibelab

# Specific test file
uv run pytest tests/unit/test_models.py

# Specific test
uv run pytest tests/unit/test_models.py::test_scenario_creation
```

### Writing Tests

```python
# tests/unit/test_models.py
import pytest
from vibelab.models import Scenario, CodeType

def test_scenario_creation():
    scenario = Scenario(
        id=1,
        code_type=CodeType.GITHUB,
        code_ref={"owner": "test", "repo": "repo", "commit_sha": "abc123"},
        prompt="Test prompt",
    )
    assert scenario.code_type == CodeType.GITHUB

@pytest.fixture
def sample_scenario():
    """Fixture for test scenarios."""
    return Scenario(...)
```

### E2E Testing

```bash
# Install Playwright
cd web && bun run playwright install

# Run E2E tests
cd web && bun run test:e2e
```

## Code Style

### Python

- Formatter: `ruff format`
- Linter: `ruff check`
- Type checker: `mypy`

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### TypeScript

- Linter: `oxlint`
- Type checker: `tsc`

### Commit Messages

Use conventional commits:

```
feat: Add new harness for Cursor CLI
fix: Handle timeout in local driver
docs: Update installation instructions
refactor: Simplify runner queue logic
test: Add integration tests for API
```

## Debugging

### Backend Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Detailed info")
logger.info("General info")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

Set log level via `VIBELAB_LOG_LEVEL=DEBUG`.

### Frontend Debugging

- React DevTools browser extension
- TanStack Query DevTools (included in dev build)
- Vite provides HMR and clear error overlays

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push --tags`
5. CI builds and publishes to PyPI

## Getting Help

- Check existing issues on GitHub
- Review PLAN.md for architecture decisions
- See AGENTS.md for AI agent instructions
