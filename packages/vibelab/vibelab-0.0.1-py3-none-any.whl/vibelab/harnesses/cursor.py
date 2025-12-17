"""Cursor CLI harness."""

import os
import shutil
import subprocess
import threading
from pathlib import Path

from ..models.executor import ModelInfo
from .base import Harness, HarnessOutput, PricingInfo, StreamCallback


class CursorHarness:
    """Harness for Cursor CLI."""

    id = "cursor"
    name = "Cursor"
    supported_providers = ["cursor"]
    preferred_driver = None

    def get_models(self, provider: str) -> list[ModelInfo]:
        """Get available models."""
        if provider != "cursor":
            return []
        return [
            ModelInfo(id="composer-1", name="Composer"),
        ]

    def get_pricing(self, provider: str, model: str) -> PricingInfo | None:
        """Get pricing information for Cursor models."""
        if provider != "cursor":
            return None
        
        # Cursor pricing is opaque, using estimated values based on Claude Sonnet
        # since Composer uses Claude models
        pricing_map = {
            "composer-1": PricingInfo(input_price_per_1m=3.0, output_price_per_1m=15.0),  # Estimated
        }
        
        return pricing_map.get(model)

    def check_available(self) -> tuple[bool, str | None]:
        """Check if Cursor CLI is available."""
        if shutil.which("cursor-agent") is None:
            return False, "Cursor CLI not found. Install: curl https://cursor.com/install -fsS | bash"
        return True, None

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
        """Execute Cursor CLI with optional streaming."""
        cmd = [
            "cursor-agent",
            "--print",  # Non-interactive mode (print and exit)
            "--output-format",
            "stream-json",  # Use stream-json for structured output
            "--force",  # Force allow commands (skip permission prompts)
        ]

        # Add API key if available (from environment variable)
        api_key = os.environ.get("CURSOR_API_KEY")
        if api_key:
            cmd.extend(["--api-key", api_key])

        # Add model flag if specified (composer-1 is default, but we'll be explicit)
        if model:
            cmd.extend(["--model", model])

        # Add prompt as final argument
        cmd.append(prompt)

        # Prepare environment (ensure CURSOR_API_KEY is available even if not passed via flag)
        env = os.environ.copy()
        if api_key:
            env["CURSOR_API_KEY"] = api_key

        # If streaming callbacks provided, use Popen for real-time output
        if on_stdout or on_stderr:
            return self._run_streaming(cmd, workdir, timeout_seconds, env, on_stdout, on_stderr)

        try:
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
            )
            return HarnessOutput(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except subprocess.TimeoutExpired:
            return HarnessOutput(
                exit_code=124,
                stdout="",
                stderr="Command timed out",
            )

    def _run_streaming(
        self,
        cmd: list[str],
        workdir: Path,
        timeout_seconds: int,
        env: dict[str, str],
        on_stdout: StreamCallback | None,
        on_stderr: StreamCallback | None,
    ) -> HarnessOutput:
        """Run command with streaming output via callbacks."""
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []

        def read_stream(stream, chunks: list[str], callback: StreamCallback | None):
            """Read stream line by line and call callback."""
            try:
                for line in iter(stream.readline, ""):
                    if line:
                        chunks.append(line)
                        if callback:
                            callback(line)
            except Exception:
                pass
            finally:
                stream.close()

        try:
            process = subprocess.Popen(
                cmd,
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                env=env,
            )

            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(process.stdout, stdout_chunks, on_stdout),
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(process.stderr, stderr_chunks, on_stderr),
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for process with timeout
            try:
                exit_code = process.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout_thread.join(timeout=1)
                stderr_thread.join(timeout=1)
                return HarnessOutput(
                    exit_code=124,
                    stdout="".join(stdout_chunks),
                    stderr="".join(stderr_chunks) + "\nCommand timed out",
                )

            # Wait for threads to finish reading
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)

            return HarnessOutput(
                exit_code=exit_code,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
            )

        except Exception as e:
            return HarnessOutput(
                exit_code=1,
                stdout="".join(stdout_chunks),
                stderr=f"Error running command: {e}",
            )

    def get_container_image(self) -> str | None:
        """Return container image if available."""
        # Default to vibelab image, can be overridden via environment
        return os.getenv("VIBELAB_CURSOR_IMAGE", "vibelab/cursor:latest")

