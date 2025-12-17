"""OrbStack driver for macOS native container execution."""

import logging
import os
import subprocess
from pathlib import Path

from .docker import DockerDriver

logger = logging.getLogger(__name__)


class OrbStackDriver(DockerDriver):
    """OrbStack execution driver (macOS native, Docker-compatible)."""

    id = "orbstack"

    def __init__(self) -> None:
        """Initialize OrbStack driver."""
        if not self._check_orbstack_available():
            raise RuntimeError(
                "OrbStack not available. Install from https://orbstack.dev or use docker driver instead."
            )
        # Override runtime detection to use orbstack
        self.runtime = "orbstack"
        # Use Docker SDK with OrbStack (it's Docker-compatible)
        try:
            import docker

            if docker is None:
                raise ImportError("Docker SDK not installed")
            self.client = docker.from_env()
            logger.info("Connected to OrbStack via Docker SDK")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to OrbStack: {e}")

    def _check_orbstack_available(self) -> bool:
        """Check if OrbStack is installed and running."""
        # Check if orbctl CLI is available
        result = subprocess.run(
            ["which", "orbctl"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            # Also check for docker pointing to OrbStack
            result = subprocess.run(
                ["which", "docker"],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                return False

        # Check if OrbStack daemon is running
        # OrbStack uses Docker-compatible API, so check docker info
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return False

        # Check if it's actually OrbStack (check for OrbStack-specific indicators)
        # OrbStack sets DOCKER_HOST or we can check docker context
        docker_host = os.getenv("DOCKER_HOST", "")
        if "orbstack" in docker_host.lower():
            return True

        # Try to detect OrbStack by checking docker context
        result = subprocess.run(
            ["docker", "context", "ls"],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0 and "orbstack" in result.stdout.decode().lower():
            return True

        # If docker works and we're on macOS, assume OrbStack might be available
        # (This is a best-effort check)
        import platform

        if platform.system() == "Darwin":
            return True

        return False

