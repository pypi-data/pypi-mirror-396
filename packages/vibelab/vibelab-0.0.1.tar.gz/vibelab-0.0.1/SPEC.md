# VibeLab Product Specification

> Rigorous evaluation tool for comparing LLM coding agents.

*This specification defines a fresh implementation. See PLAN.md for implementation details.*

## Problem

Software engineers need a structured way to evaluate LLM coding agents (Claude Code, Codex, Cursor, Gemini CLI) when new tools or models are released. Current evaluation methods are ad-hoc "vibe checks" that don't provide reproducible, comparable results.

## Solution

VibeLab provides a framework for running controlled experiments across different agent configurations and comparing their outputs systematically.

## Core Concepts

### Scenario
A specific task for an LLM agent:
- **Code**: Starting repository state (GitHub URL + commit)
- **Prompt**: Task instruction for the agent
- **Tooling** (future): MCP servers, skills, rules

### Executor
Agent configuration: `harness:provider:model`
- **Harness**: Agent CLI (claude-code, openai-codex)
- **Provider**: Inference endpoint (anthropic, openai)
- **Model**: Specific model (sonnet, gpt-4o)

### Result
Output of running an executor on a scenario:
- Git patch of code changes
- Execution logs (stdout/stderr)
- Metrics: duration, lines changed, tokens, cost
- User annotations (mutable)
- Notes: Human-added context about the run (mutable)
- Quality score: Coarse-grained rating (4=Perfect, 3=Good, 2=Workable, 1=Bad) (mutable)

### LLM Judge
An automatic grader that mimics human scores using few-shot examples:
- **LLMScenarioJudge**: Applies to a single scenario
- **Guidance**: User-authored instructions for the judge
- **Training Samples**: Few-shot examples used to guide the judge
- **Test Samples**: Samples used to calculate alignment with human scores
- **Alignment Score**: Pearson correlation coefficient between judge and human quality scores
- **Judgements**: LLM-generated notes and quality scores for results
- Judges evolve over time - new versions can be created with updated guidance or samples
- When a run completes, the latest judge for that scenario automatically evaluates it

## Workflows

1. **Single Run**: One scenario, one executor
2. **Comparative Run**: One scenario, multiple executors
3. **Trials**: Same scenario+executor repeated N times
4. **Batch Evaluation**: Dataset of scenarios, multiple executors with trials and minimal mode

## MVP Features

### CLI
- `vibelab run` - Execute scenario against executor(s)
- `vibelab scenario create|list|get` - Manage scenarios
- `vibelab dataset create|list|get|run` - Manage datasets and batch evaluation
- `vibelab result list|get|diff|update-notes|update-quality|update` - View and update results
- `vibelab executor list` - List available executors
- `vibelab start` - Launch web UI

### Web UI
- Dashboard with recent scenarios
- Scenarios table view
- Datasets table view with scenario counts
- Dataset detail page with scenario management
- Dataset analytics: Matrix view showing scenario-executor status across all combinations
- Runs table view (all runs across scenarios, filterable by executor)
- Executors page: Single table view of all executor tuples (harness:provider:model) with:
  - Filtering by harness, provider, or model
  - Checkbox selection for multiple executors
  - "Start Run" button to create runs with selected executors
  - Links to view runs filtered by executor spec
- Run creation form (supports pre-filling executors via URL parameter)
- Scenario detail with result table, judge management tab, and judgement display
- Side-by-side comparison of two results
- Diff viewer, log viewer, metrics comparison
- Notes and quality score editing on result detail page
- Quality score display in runs table
- LLM Judge management: Create, update, train judges with alignment scores
- Judgements page: View all judgements and pending judgements across scenarios
- Accept judgements: Copy LLM judge assessment to human feedback with one click

### Execution
- Local driver using git worktrees
- Claude Code harness
- OpenAI Codex harness

## Constraints

- Results are immutable (except annotations)
- Executors run sequentially (local driver)
- Evaluation data stored separately from target repos
- SQLite database with automatic migrations
- Storage in `~/.vibelab/`

## Out of Scope (Future)

- Real-time log streaming (implemented via SSE)
- Docker/Modal execution drivers (Docker/Modal drivers implemented)
- LLM Judges and automatic scoring (implemented)
- Export/import functionality
- Multi-media prompts
- MCP configuration
- Public leaderboards

## Success Criteria

1. User can run a scenario against 2+ agents from CLI
2. User can view and compare results in web UI
3. Results are persisted and reproducible
4. Adding new harnesses requires only implementing the Harness protocol
