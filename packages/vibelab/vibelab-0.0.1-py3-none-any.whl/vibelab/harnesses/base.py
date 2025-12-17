"""Base harness protocol."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

from ..models.executor import ModelInfo


@dataclass
class HarnessOutput:
    """Output from harness execution."""

    exit_code: int
    stdout: str
    stderr: str
    metrics: dict[str, any] | None = None
    trajectory_path: Path | None = None


@dataclass
class PricingInfo:
    """Pricing information for a model."""

    input_price_per_1m: float  # Price per 1M input tokens in USD
    output_price_per_1m: float  # Price per 1M output tokens in USD


# Type for streaming callbacks
StreamCallback = Callable[[str], None]


class Harness(Protocol):
    """Protocol for agent harness implementations."""

    @property
    def id(self) -> str:
        """Unique harness identifier."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name."""
        ...

    @property
    def supported_providers(self) -> list[str]:
        """List of provider IDs this harness supports."""
        ...

    @property
    def preferred_driver(self) -> str | None:
        """Preferred driver ID, or None for system default."""
        ...

    def get_models(self, provider: str) -> list[ModelInfo]:
        """Get available models for a provider."""
        ...

    def get_pricing(self, provider: str, model: str) -> PricingInfo | None:
        """
        Get pricing information for a provider/model combination.
        
        Args:
            provider: Provider identifier
            model: Model identifier
            
        Returns:
            PricingInfo if pricing is available, None otherwise
        """
        ...

    def check_available(self) -> tuple[bool, str | None]:
        """Check if harness is available. Returns (is_available, error_message_if_not)."""
        ...

    def run(
        self,
        workdir: Path,
        prompt: str,
        provider: str,
        model: str,
        timeout_seconds: int,
        on_stdout: StreamCallback | None = None,
        on_stderr: StreamCallback | None = None,
    ) -> HarnessOutput:
        """Execute the agent with the given prompt.
        
        Args:
            workdir: Working directory for execution
            prompt: The prompt to send to the agent
            provider: Provider identifier
            model: Model identifier
            timeout_seconds: Timeout in seconds
            on_stdout: Optional callback for streaming stdout
            on_stderr: Optional callback for streaming stderr
        """
        ...

    def get_container_image(self) -> str | None:
        """Return container image for Docker/Modal drivers."""
        ...
