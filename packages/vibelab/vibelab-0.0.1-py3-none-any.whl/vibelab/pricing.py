"""Pricing and token cost calculation utilities."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..harnesses.base import Harness


def calculate_cost(
    harness: "Harness",
    provider: str,
    model: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    total_tokens: int | None = None,
) -> float | None:
    """
    Calculate cost in USD based on token usage.
    
    Gets pricing information from the harness implementation.
    
    Args:
        harness: Harness instance
        provider: Provider identifier
        model: Model identifier
        input_tokens: Number of input tokens (preferred)
        output_tokens: Number of output tokens (preferred)
        total_tokens: Total tokens if input/output breakdown not available
    
    Returns:
        Cost in USD, or None if pricing not available
    """
    pricing = harness.get_pricing(provider, model)
    if not pricing:
        return None
    
    # Prefer input/output breakdown
    if input_tokens is not None and output_tokens is not None:
        input_cost = (input_tokens / 1_000_000) * pricing.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * pricing.output_price_per_1m
        return input_cost + output_cost
    
    # Fallback to total tokens (assume 50/50 split for estimation)
    if total_tokens is not None:
        # Estimate: assume equal input/output split
        estimated_input = total_tokens / 2
        estimated_output = total_tokens / 2
        input_cost = (estimated_input / 1_000_000) * pricing.input_price_per_1m
        output_cost = (estimated_output / 1_000_000) * pricing.output_price_per_1m
        return input_cost + output_cost
    
    return None

