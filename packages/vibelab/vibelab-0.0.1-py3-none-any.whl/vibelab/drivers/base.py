"""Base driver protocol."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..models.scenario import Scenario


@dataclass
class ExecutionContext:
    """Context passed to driver methods."""

    result_id: str
    scenario: Scenario
    harness: "Harness"  # type: ignore
    provider: str
    model: str
    timeout_seconds: int
    workdir: Path | None = None  # Set by driver.setup()
    streaming_log: "StreamingLog | None" = None  # type: ignore


@dataclass
class RunOutput:
    """Output from driver execution."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    patch: str | None = None  # Git diff of changes


class Driver(Protocol):
    """Protocol for execution environment drivers."""

    @property
    def id(self) -> str:
        """Unique driver identifier."""
        ...

    def setup(self, ctx: ExecutionContext) -> None:
        """Prepare execution environment."""
        ...

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        """Run the harness in the prepared environment."""
        ...

    def cleanup(self, ctx: ExecutionContext) -> None:
        """Clean up execution environment."""
        ...
