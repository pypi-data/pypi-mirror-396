"""Executor API endpoints."""

from fastapi import APIRouter

from ..harnesses import HARNESSES
from ..drivers import DRIVERS

router = APIRouter()


@router.get("")
def list_executors():
    """List all harnesses."""
    return {
        "harnesses": [
            {
                "id": h.id,
                "name": h.name,
                "providers": h.supported_providers,
            }
            for h in HARNESSES.values()
        ]
    }


@router.get("/drivers/list")
def list_drivers():
    """List all available drivers."""
    return {
        "drivers": [
            {
                "id": driver_id,
                "name": driver_id.capitalize(),
            }
            for driver_id, driver in DRIVERS.items()
        ]
    }


@router.get("/{harness_id}")
def list_providers(harness_id: str):
    """List providers for a harness."""
    harness = HARNESSES.get(harness_id)
    if not harness:
        return {"providers": []}
    return {
        "harness": harness_id,
        "providers": [
            {
                "id": provider,
                "models": [m.model_dump() for m in harness.get_models(provider)],
            }
            for provider in harness.supported_providers
        ],
    }


@router.get("/{harness_id}/{provider_id}")
def list_models(harness_id: str, provider_id: str):
    """List models for a harness/provider."""
    harness = HARNESSES.get(harness_id)
    if not harness:
        return {"models": []}
    return {
        "harness": harness_id,
        "provider": provider_id,
        "models": [m.model_dump() for m in harness.get_models(provider_id)],
    }
