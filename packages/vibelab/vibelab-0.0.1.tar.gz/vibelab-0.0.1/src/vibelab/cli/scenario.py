"""Scenario commands."""

import json
import sys
from datetime import datetime, timezone

import typer

from ..db import get_db, create_scenario, get_scenario, list_scenarios, delete_scenario, list_results
from ..db.connection import get_vibelab_home
from ..db.connection import init_db
from ..lib import resolve_github_code_ref
from ..models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario

app = typer.Typer()


@app.command()
def create(
    code: str = typer.Option(..., "--code", help="Code reference"),
    prompt: str = typer.Option(..., "--prompt", help="Task prompt"),
):
    """Create a new scenario."""
    init_db()

    if code.startswith("github:"):
        parts = code[7:].split("@")
        owner_repo = parts[0].split("/")
        ref = parts[1] if len(parts) > 1 else "main"
        code_type = CodeType.GITHUB
        code_ref = GitHubCodeRef(owner=owner_repo[0], repo=owner_repo[1], commit_sha=ref)
        # Resolve branch/tag names to commit SHAs
        code_ref = resolve_github_code_ref(code_ref)
    elif code.startswith("local:"):
        code_type = CodeType.LOCAL
        code_ref = LocalCodeRef(path=code[6:])
    elif code == "empty":
        code_type = CodeType.EMPTY
        code_ref = None
    else:
        typer.echo(f"Invalid code reference: {code}", err=True)
        sys.exit(1)

    scenario = Scenario(
        id=0,
        code_type=code_type,
        code_ref=code_ref,
        prompt=prompt,
        created_at=datetime.now(timezone.utc),
    )

    for db in get_db():
        scenario = create_scenario(db, scenario)
        typer.echo(json.dumps(scenario.model_dump(), indent=2, default=str))
        break


@app.command()
def list_cmd(limit: int | None = typer.Option(None, "--limit", help="Limit results")):
    """List scenarios."""
    init_db()
    for db in get_db():
        scenarios = list_scenarios(db, limit=limit)
        typer.echo(json.dumps([s.model_dump() for s in scenarios], indent=2, default=str))
        break


@app.command()
def get(scenario_id: int = typer.Argument(..., help="Scenario ID")):
    """Get scenario details."""
    init_db()
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            typer.echo(f"Scenario {scenario_id} not found", err=True)
            sys.exit(1)
        typer.echo(json.dumps(scenario.model_dump(), indent=2, default=str))
        break


@app.command()
def delete(
    scenario_id: int = typer.Argument(..., help="Scenario ID"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """Delete a scenario and all its results (cascade delete)."""
    import shutil
    
    init_db()
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            typer.echo(f"Scenario {scenario_id} not found", err=True)
            sys.exit(1)
        
        # Get result count
        results = list_results(db, scenario_id=scenario_id)
        result_count = len(results)
        
        # Confirm deletion
        if not force:
            typer.echo(f"Warning: This will delete scenario {scenario_id} and all {result_count} associated results.", err=True)
            typer.echo(f"Prompt: {scenario.prompt[:80]}...", err=True)
            confirm = typer.confirm("Are you sure you want to delete this scenario?", default=False)
            if not confirm:
                typer.echo("Deletion cancelled.", err=True)
                sys.exit(0)
        
        # Delete result files
        home = get_vibelab_home()
        for result in results:
            result_dir = home / "results" / str(result.id)
            if result_dir.exists():
                shutil.rmtree(result_dir)
        
        # Delete from database
        deleted = delete_scenario(db, scenario_id)
        if not deleted:
            typer.echo(f"Failed to delete scenario {scenario_id}", err=True)
            sys.exit(1)
        
        typer.echo(f"Deleted scenario {scenario_id} and {result_count} associated results.")
        break
