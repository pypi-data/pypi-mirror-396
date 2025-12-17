"""Executor commands."""

import json

import typer

from ..harnesses import HARNESSES

app = typer.Typer()


@app.command()
def list_cmd(
    harness: str | None = typer.Option(None, "--harness", help="Filter by harness"),
    provider: str | None = typer.Option(None, "--provider", help="Filter by provider"),
):
    """List available executors."""
    output = {}
    for harness_id, h in HARNESSES.items():
        if harness and harness_id != harness:
            continue
        providers = {}
        for provider_id in h.supported_providers:
            if provider and provider_id != provider:
                continue
            models = h.get_models(provider_id)
            providers[provider_id] = [m.model_dump() for m in models]
        output[harness_id] = {
            "name": h.name,
            "providers": providers,
        }
    typer.echo(json.dumps(output, indent=2))
