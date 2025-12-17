"""OpenAI Codex harness."""

import os
import shutil
import subprocess
import threading
from pathlib import Path

from ..models.executor import ModelInfo
from .base import Harness, HarnessOutput, PricingInfo, StreamCallback


class OpenAICodexHarness:
    """Harness for OpenAI Codex CLI."""

    id = "openai-codex"
    name = "OpenAI Codex"
    supported_providers = ["openai"]
    preferred_driver = None

    def get_models(self, provider: str) -> list[ModelInfo]:
        """Get available models."""
        if provider != "openai":
            return []
        return [
            ModelInfo(id="gpt-4o", name="GPT-4o"),
            ModelInfo(id="o3", name="o3"),
            ModelInfo(id="o4-mini", name="o4-mini"),
        ]

    def get_pricing(self, provider: str, model: str) -> PricingInfo | None:
        """Get pricing information for OpenAI models."""
        if provider != "openai":
            return None
        
        # Pricing per 1M tokens as of 2024
        # Source: https://openai.com/api/pricing/
        pricing_map = {
            "gpt-4o": PricingInfo(input_price_per_1m=2.50, output_price_per_1m=10.0),
            "o3": PricingInfo(input_price_per_1m=5.0, output_price_per_1m=15.0),  # Estimated
            "o4-mini": PricingInfo(input_price_per_1m=0.15, output_price_per_1m=0.60),  # Estimated
        }
        
        return pricing_map.get(model)

    def check_available(self) -> tuple[bool, str | None]:
        """Check if Codex CLI is available."""
        if shutil.which("codex") is None:
            return False, "Codex CLI not found. Install: npm install -g @openai/codex"
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
        """Execute Codex CLI with optional streaming."""
        # Use 'exec' subcommand for non-interactive mode to avoid "stdout is not a terminal" error
        # Use '--sandbox workspace-write' to allow file modifications in the isolated worktree
        # Use '--skip-git-repo-check' to allow execution in directories that may not be trusted git repos
        cmd = [
            "codex",
            "exec",
            "--sandbox",
            "workspace-write",
            "--skip-git-repo-check",
            "--model",
            model,
            prompt,
        ]

        # If streaming callbacks provided, use Popen for real-time output
        if on_stdout or on_stderr:
            return self._run_streaming(cmd, workdir, timeout_seconds, on_stdout, on_stderr)

        try:
            result = subprocess.run(
                cmd,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
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
        return os.getenv("VIBELAB_OPENAI_CODEX_IMAGE", "vibelab/openai-codex:latest")
