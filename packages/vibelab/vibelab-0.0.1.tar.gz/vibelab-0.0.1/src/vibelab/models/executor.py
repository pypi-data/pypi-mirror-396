"""Executor model definitions."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    """Information about an available model."""

    id: str
    name: str


class ExecutorSpec(BaseModel):
    """Executor specification: harness:provider:model."""

    harness: str
    provider: str
    model: str

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.harness}:{self.provider}:{self.model}"

    @classmethod
    def parse(cls, spec: str) -> "ExecutorSpec":
        """Parse executor specification string."""
        parts = spec.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid executor spec: {spec}. Expected format: harness:provider:model")
        return cls(harness=parts[0], provider=parts[1], model=parts[2])
