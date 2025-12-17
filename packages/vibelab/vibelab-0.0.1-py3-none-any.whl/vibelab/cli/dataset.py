"""Dataset commands."""

import json
import sys
from datetime import datetime, timezone
from itertools import product

import typer

from ..db import (
    get_db,
    create_dataset,
    get_dataset,
    list_datasets,
    delete_dataset,
    get_dataset_scenarios,
    add_scenario_to_dataset,
    remove_scenario_from_dataset,
    list_scenarios,
    get_scenario,
    list_results,
)
from ..db.connection import init_db
from ..engine.runner import Runner
from ..models.dataset import Dataset
from ..models.executor import ExecutorSpec

app = typer.Typer()


@app.command()
def create(
    name: str = typer.Option(..., "--name", help="Dataset name"),
    description: str = typer.Option(None, "--description", help="Dataset description"),
):
    """Create a new dataset."""
    init_db()

    dataset = Dataset(
        id=0,
        name=name,
        description=description,
        created_at=datetime.now(timezone.utc),
    )

    for db in get_db():
        dataset = create_dataset(db, dataset)
        typer.echo(json.dumps(dataset.model_dump(), indent=2, default=str))
        break


@app.command()
def list_cmd(limit: int | None = typer.Option(None, "--limit", help="Limit results")):
    """List datasets."""
    init_db()
    for db in get_db():
        datasets = list_datasets(db, limit=limit)
        typer.echo(json.dumps([d.model_dump() for d in datasets], indent=2, default=str))
        break


@app.command()
def get(dataset_id: int = typer.Argument(..., help="Dataset ID")):
    """Get dataset details."""
    init_db()
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            typer.echo(f"Dataset {dataset_id} not found", err=True)
            sys.exit(1)
        scenarios = get_dataset_scenarios(db, dataset_id)
        output = {
            **dataset.model_dump(),
            "scenarios": [s.model_dump() for s in scenarios],
        }
        typer.echo(json.dumps(output, indent=2, default=str))
        break


@app.command()
def delete(
    dataset_id: int = typer.Argument(..., help="Dataset ID"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """Delete a dataset."""
    init_db()
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            typer.echo(f"Dataset {dataset_id} not found", err=True)
            sys.exit(1)

        scenarios = get_dataset_scenarios(db, dataset_id)
        scenario_count = len(scenarios)

        if not force:
            typer.echo(f"Warning: This will delete dataset {dataset_id} ({dataset.name}).", err=True)
            typer.echo(f"It contains {scenario_count} scenario(s).", err=True)
            confirm = typer.confirm("Are you sure you want to delete this dataset?", default=False)
            if not confirm:
                typer.echo("Deletion cancelled.", err=True)
                sys.exit(0)

        deleted = delete_dataset(db, dataset_id)
        if not deleted:
            typer.echo(f"Failed to delete dataset {dataset_id}", err=True)
            sys.exit(1)

        typer.echo(f"Deleted dataset {dataset_id}.")
        break


@app.command()
def add_scenario(
    dataset_id: int = typer.Option(..., "--dataset", help="Dataset ID"),
    scenario_id: int = typer.Option(..., "--scenario", help="Scenario ID"),
):
    """Add a scenario to a dataset."""
    init_db()
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            typer.echo(f"Dataset {dataset_id} not found", err=True)
            sys.exit(1)

        scenario = get_scenario(db, scenario_id)
        if not scenario:
            typer.echo(f"Scenario {scenario_id} not found", err=True)
            sys.exit(1)

        add_scenario_to_dataset(db, dataset_id, scenario_id)
        typer.echo(f"Added scenario {scenario_id} to dataset {dataset_id}")
        break


@app.command()
def remove_scenario(
    dataset_id: int = typer.Option(..., "--dataset", help="Dataset ID"),
    scenario_id: int = typer.Option(..., "--scenario", help="Scenario ID"),
):
    """Remove a scenario from a dataset."""
    init_db()
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            typer.echo(f"Dataset {dataset_id} not found", err=True)
            sys.exit(1)

        remove_scenario_from_dataset(db, dataset_id, scenario_id)
        typer.echo(f"Removed scenario {scenario_id} from dataset {dataset_id}")
        break


@app.command()
def run_cmd(
    dataset_id: int = typer.Option(..., "--dataset", help="Dataset ID"),
    executor: list[str] = typer.Option(..., "--executor", help="Executor spec (harness:provider:model)"),
    trials: int = typer.Option(1, "--trials", help="Number of trials per scenario-executor pair"),
    minimal: bool = typer.Option(False, "--minimal", help="Only run minimal scenario-executor tuples to construct total report"),
    timeout: int = typer.Option(1800, "--timeout", help="Timeout in seconds"),
    driver: str = typer.Option("local", "--driver", help="Execution driver"),
):
    """Run all scenarios in a dataset against executor(s)."""
    init_db()

    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            typer.echo(f"Dataset {dataset_id} not found", err=True)
            sys.exit(1)

        scenarios = get_dataset_scenarios(db, dataset_id)
        if not scenarios:
            typer.echo(f"Dataset {dataset_id} has no scenarios", err=True)
            sys.exit(1)

        executor_specs = [ExecutorSpec.parse(e) for e in executor]

        # Determine which scenario-executor pairs to run
        if minimal:
            # Only run pairs that don't have completed results
            pairs_to_run = []
            for scenario in scenarios:
                for executor_spec in executor_specs:
                    executor_spec_str = str(executor_spec)
                    results = list_results(db, scenario_id=scenario.id, executor_spec=executor_spec_str)
                    completed_count = sum(1 for r in results if r.status.value == "completed")
                    if completed_count == 0:
                        pairs_to_run.append((scenario, executor_spec))
        else:
            # Run all combinations with specified number of trials
            pairs_to_run = []
            for scenario, executor_spec in product(scenarios, executor_specs):
                for _ in range(trials):
                    pairs_to_run.append((scenario, executor_spec))

        typer.echo(f"Running {len(pairs_to_run)} scenario-executor pairs...", err=True)

        runner = Runner()
        results = []

        for scenario, executor_spec in pairs_to_run:
            try:
                typer.echo(f"Running scenario {scenario.id} with {executor_spec}...", err=True)
                result = runner.run(scenario, executor_spec, timeout, driver)
                results.append(result)
                typer.echo(f"Completed: {result.status}", err=True)
            except Exception as e:
                typer.echo(f"Failed: {e}", err=True)
                continue

        # Output JSON summary
        output = {
            "dataset_id": dataset_id,
            "pairs_run": len(pairs_to_run),
            "results": [r.model_dump() for r in results],
        }
        typer.echo(json.dumps(output, indent=2, default=str))
        break

