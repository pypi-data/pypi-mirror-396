"""Run command."""

import json
import sys
from datetime import datetime, timezone, timezone

import typer

from ..db import get_db, create_scenario, get_scenario, list_scenarios
from ..db.connection import init_db
from ..engine.runner import Runner
from ..lib import resolve_github_code_ref
from ..models.executor import ExecutorSpec
from ..models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario

app = typer.Typer()


def parse_code_ref(code_str: str) -> tuple[CodeType, GitHubCodeRef | LocalCodeRef | None]:
    """Parse code reference string."""
    if code_str.startswith("github:"):
        parts = code_str[7:].split("@")
        owner_repo = parts[0].split("/")
        if len(owner_repo) != 2:
            raise ValueError("Invalid GitHub reference format: github:owner/repo@sha")
        ref = parts[1] if len(parts) > 1 else "main"
        code_ref = GitHubCodeRef(owner=owner_repo[0], repo=owner_repo[1], commit_sha=ref)
        # Resolve branch/tag names to commit SHAs
        code_ref = resolve_github_code_ref(code_ref)
        return CodeType.GITHUB, code_ref
    elif code_str.startswith("local:"):
        path = code_str[6:]
        return CodeType.LOCAL, LocalCodeRef(path=path)
    elif code_str == "empty":
        return CodeType.EMPTY, None
    else:
        raise ValueError(f"Invalid code reference: {code_str}")


@app.command()
def run_cmd(
    code: str = typer.Option(..., "--code", help="Code reference (github:owner/repo@sha, local:/path, empty)"),
    prompt: str = typer.Option(..., "--prompt", help="Task prompt"),
    executor: list[str] = typer.Option(..., "--executor", help="Executor spec (harness:provider:model)"),
    timeout: int = typer.Option(1800, "--timeout", help="Timeout in seconds"),
    driver: str = typer.Option("local", "--driver", help="Execution driver"),
):
    """Run a scenario against executor(s)."""
    init_db()

    code_type, code_ref = parse_code_ref(code)
    # Note: code_ref is already resolved to commit SHA at this point

    # Find or create scenario
    scenario_obj = None
    for db in get_db():
        scenarios = list_scenarios(db)
        for s in scenarios:
            if s.code_type == code_type and s.prompt == prompt:
                if code_type == CodeType.GITHUB and isinstance(code_ref, GitHubCodeRef):
                    if isinstance(s.code_ref, GitHubCodeRef):
                        # Match on owner, repo, AND commit SHA (after resolution)
                        if (
                            s.code_ref.owner == code_ref.owner
                            and s.code_ref.repo == code_ref.repo
                            and s.code_ref.commit_sha == code_ref.commit_sha
                        ):
                            scenario_obj = s
                            break
                elif code_type == CodeType.LOCAL and isinstance(code_ref, LocalCodeRef):
                    if isinstance(s.code_ref, LocalCodeRef):
                        if s.code_ref.path == code_ref.path:
                            scenario_obj = s
                            break
                elif code_type == CodeType.EMPTY:
                    scenario_obj = s
                    break

        if not scenario_obj:
            scenario_obj = Scenario(
                id=0,
                code_type=code_type,
                code_ref=code_ref,
                prompt=prompt,
                created_at=datetime.now(timezone.utc),
            )
            scenario_obj = create_scenario(db, scenario_obj)
        break

    if not scenario_obj:
        typer.echo("Failed to create scenario", err=True)
        sys.exit(1)

    runner = Runner()
    results = []

    for executor_spec_str in executor:
        try:
            executor_spec = ExecutorSpec.parse(executor_spec_str)
            typer.echo(f"Running {executor_spec}...", err=True)
            result = runner.run(scenario_obj, executor_spec, timeout, driver)
            results.append(result)
            typer.echo(f"Completed: {result.status}", err=True)
        except Exception as e:
            typer.echo(f"Failed: {e}", err=True)
            continue

    # Output JSON summary
    output = {
        "scenario_id": scenario_obj.id,
        "results": [r.model_dump() for r in results],
    }
    typer.echo(json.dumps(output, indent=2, default=str))


app.command()(run_cmd)
