"""Result commands."""

import json
import sys

import typer

from ..db import (
    get_db,
    get_result,
    list_results,
    delete_result,
    update_result_notes,
    update_result_quality,
    update_result_notes_and_quality,
    get_scenario,
    create_result,
)
from ..db.connection import get_vibelab_home, init_db
from ..models.result import ResultStatus, Result
from ..models.executor import ExecutorSpec
from ..engine.runner import Runner
from datetime import datetime, timezone

app = typer.Typer()


@app.command()
def list_cmd(
    scenario: int | None = typer.Option(None, "--scenario", help="Filter by scenario ID"),
    executor: str | None = typer.Option(None, "--executor", help="Filter by executor spec"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
):
    """List results."""
    init_db()
    status_enum = ResultStatus(status) if status else None
    for db in get_db():
        results = list_results(db, scenario_id=scenario, executor_spec=executor, status=status_enum)
        typer.echo(json.dumps([r.model_dump() for r in results], indent=2, default=str))
        break


@app.command()
def get_cmd(result_id: int = typer.Argument(..., help="Result ID")):
    """Get result details."""
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        typer.echo(json.dumps(result.model_dump(), indent=2, default=str))
        break


@app.command()
def diff(result_id: int = typer.Argument(..., help="Result ID")):
    """Show result diff."""
    init_db()
    home = get_vibelab_home()
    patch_file = home / "results" / str(result_id) / "patch.diff"
    if not patch_file.exists():
        typer.echo(f"Patch not found for result {result_id}", err=True)
        sys.exit(1)
    typer.echo(patch_file.read_text())


@app.command()
def delete(
    result_id: int = typer.Argument(..., help="Result ID"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """Delete a result."""
    import shutil
    
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        
        # Confirm deletion
        if not force:
            typer.echo(f"Warning: This will delete result {result_id}.", err=True)
            typer.echo(f"Executor: {result.harness}:{result.provider}:{result.model}", err=True)
            typer.echo(f"Status: {result.status}", err=True)
            confirm = typer.confirm("Are you sure you want to delete this result?", default=False)
            if not confirm:
                typer.echo("Deletion cancelled.", err=True)
                sys.exit(0)
        
        # Delete result files
        result_dir = get_vibelab_home() / "results" / str(result_id)
        if result_dir.exists():
            shutil.rmtree(result_dir)
        
        # Delete from database
        deleted = delete_result(db, result_id)
        if not deleted:
            typer.echo(f"Failed to delete result {result_id}", err=True)
            sys.exit(1)
        
        typer.echo(f"Deleted result {result_id}.")
        break


@app.command()
def rerun(
    result_id: int = typer.Argument(..., help="Result ID to rerun"),
    driver: str = typer.Option("local", "--driver", help="Execution driver"),
):
    """Rerun a result with the same settings."""
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        
        scenario = get_scenario(db, result.scenario_id)
        if not scenario:
            typer.echo(f"Scenario {result.scenario_id} not found", err=True)
            sys.exit(1)
        
        # Build executor spec from result
        executor_spec_str = f"{result.harness}:{result.provider}:{result.model}"
        executor_spec = ExecutorSpec.parse(executor_spec_str)
        
        # Use timeout from original result, or default
        timeout_seconds = result.timeout_seconds or 1800
        
        typer.echo(f"Rerunning result {result_id}...", err=True)
        typer.echo(f"Scenario: {scenario.id}", err=True)
        typer.echo(f"Executor: {executor_spec_str}", err=True)
        typer.echo(f"Timeout: {timeout_seconds}s", err=True)
        
        # Run using the Runner
        runner = Runner()
        try:
            new_result = runner.run(scenario, executor_spec, timeout_seconds, driver)
            typer.echo(json.dumps(new_result.model_dump(), indent=2, default=str))
        except Exception as e:
            typer.echo(f"Failed to rerun: {e}", err=True)
            sys.exit(1)
        
        break


@app.command()
def update_notes(
    result_id: int = typer.Argument(..., help="Result ID"),
    notes: str = typer.Option(None, "--notes", help="Notes text (use '-' to read from stdin)"),
    clear: bool = typer.Option(False, "--clear", help="Clear notes"),
):
    """Update result notes."""
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        
        if clear:
            notes_text = None
        elif notes == "-":
            # Read from stdin
            notes_text = sys.stdin.read()
        elif notes:
            notes_text = notes
        else:
            typer.echo("Error: Must provide --notes or --clear", err=True)
            sys.exit(1)
        
        update_result_notes(db, result_id, notes_text)
        typer.echo(f"Updated notes for result {result_id}")
        break


@app.command()
def update_quality(
    result_id: int = typer.Argument(..., help="Result ID"),
    quality: int = typer.Option(None, "--quality", help="Quality score (1=Bad, 2=Workable, 3=Good, 4=Perfect)"),
    clear: bool = typer.Option(False, "--clear", help="Clear quality score"),
):
    """Update result quality score."""
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        
        if clear:
            quality_value = None
        elif quality is not None:
            if quality < 1 or quality > 4:
                typer.echo("Error: Quality must be between 1 and 4", err=True)
                sys.exit(1)
            quality_value = quality
        else:
            typer.echo("Error: Must provide --quality or --clear", err=True)
            sys.exit(1)
        
        update_result_quality(db, result_id, quality_value)
        quality_labels = {1: "Bad", 2: "Workable", 3: "Good", 4: "Perfect"}
        if quality_value:
            typer.echo(f"Updated quality for result {result_id} to {quality_value} ({quality_labels[quality_value]})")
        else:
            typer.echo(f"Cleared quality for result {result_id}")
        break


@app.command()
def update(
    result_id: int = typer.Argument(..., help="Result ID"),
    notes: str = typer.Option(None, "--notes", help="Notes text (use '-' to read from stdin)"),
    quality: int = typer.Option(None, "--quality", help="Quality score (1=Bad, 2=Workable, 3=Good, 4=Perfect)"),
    clear_notes: bool = typer.Option(False, "--clear-notes", help="Clear notes"),
    clear_quality: bool = typer.Option(False, "--clear-quality", help="Clear quality score"),
):
    """Update result notes and/or quality score."""
    init_db()
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            typer.echo(f"Result {result_id} not found", err=True)
            sys.exit(1)
        
        notes_value = None
        if clear_notes:
            notes_value = None
        elif notes == "-":
            notes_value = sys.stdin.read()
        elif notes:
            notes_value = notes
        
        quality_value = None
        if clear_quality:
            quality_value = None
        elif quality is not None:
            if quality < 1 or quality > 4:
                typer.echo("Error: Quality must be between 1 and 4", err=True)
                sys.exit(1)
            quality_value = quality
        
        if notes_value is None and quality_value is None and not clear_notes and not clear_quality:
            typer.echo("Error: Must provide at least one of --notes, --quality, --clear-notes, or --clear-quality", err=True)
            sys.exit(1)
        
        update_result_notes_and_quality(db, result_id, notes_value, quality_value)
        
        updates = []
        if notes_value is not None or clear_notes:
            updates.append("notes")
        if quality_value is not None or clear_quality:
            quality_labels = {1: "Bad", 2: "Workable", 3: "Good", 4: "Perfect"}
            if quality_value:
                updates.append(f"quality={quality_value} ({quality_labels[quality_value]})")
            else:
                updates.append("quality cleared")
        
        typer.echo(f"Updated {', '.join(updates)} for result {result_id}")
        break
