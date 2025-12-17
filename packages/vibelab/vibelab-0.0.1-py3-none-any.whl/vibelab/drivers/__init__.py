"""Execution drivers for VibeLab."""

import logging

from .base import Driver, ExecutionContext, RunOutput
from .local import LocalDriver

logger = logging.getLogger(__name__)

DRIVERS: dict[str, Driver] = {
    "local": LocalDriver(),
}

# Conditionally register Docker driver
try:
    from .docker import DockerDriver

    DRIVERS["docker"] = DockerDriver()
except (ImportError, RuntimeError) as e:
    logger.debug(f"Docker driver not available: {e}")

# Conditionally register OrbStack driver
try:
    from .orbstack import OrbStackDriver

    DRIVERS["orbstack"] = OrbStackDriver()
except (ImportError, RuntimeError) as e:
    logger.debug(f"OrbStack driver not available: {e}")

# Conditionally register Modal driver
try:
    from .modal import ModalDriver

    DRIVERS["modal"] = ModalDriver()
except (ImportError, RuntimeError) as e:
    logger.debug(f"Modal driver not available: {e}")

__all__ = [
    "Driver",
    "ExecutionContext",
    "RunOutput",
    "LocalDriver",
    "DockerDriver",
    "OrbStackDriver",
    "ModalDriver",
    "DRIVERS",
]
