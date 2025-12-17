"""Main CLI application."""

import typer

from . import dataset, executor, result, run, scenario, start

app = typer.Typer(name="vibelab", help="Rigorous evaluation tool for comparing LLM coding agents")

app.add_typer(run.app, name="run")
app.add_typer(scenario.app, name="scenario")
app.add_typer(result.app, name="result")
app.add_typer(executor.app, name="executor")
app.add_typer(start.app, name="start")
app.add_typer(dataset.app, name="dataset")

if __name__ == "__main__":
    app()
