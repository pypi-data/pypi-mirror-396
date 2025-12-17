"""Modal driver for cloud-based container execution."""

import base64
import logging
import os
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any

from ..db.connection import get_vibelab_home
from ..drivers.base import Driver, ExecutionContext, RunOutput
from ..harnesses.base import HarnessOutput, StreamCallback

logger = logging.getLogger(__name__)

try:
    import modal
except ImportError:
    modal = None  # type: ignore


class ModalDriver:
    """Modal execution driver for cloud-based containers."""

    id = "modal"

    def __init__(self) -> None:
        """Initialize Modal driver."""
        if modal is None:
            raise ImportError(
                "Modal SDK not installed. Install with: pip install modal or uv pip install -e '.[modal]'"
            )
        self._check_modal_available()
        self.app = modal.App("vibelab")

    def _check_modal_available(self) -> None:
        """Check if Modal is configured."""
        if modal is None:
            raise ImportError("Modal SDK not installed")

        # Check if Modal token is configured
        token_id = os.getenv("MODAL_TOKEN_ID")
        token_secret = os.getenv("MODAL_TOKEN_SECRET")

        if not token_id or not token_secret:
            # Try to use modal token file
            try:
                modal_token_path = Path.home() / ".modal" / "token.json"
                if not modal_token_path.exists():
                    raise RuntimeError(
                        "Modal not configured. Run 'modal token new' or set MODAL_TOKEN_ID and MODAL_TOKEN_SECRET"
                    )
            except Exception as e:
                raise RuntimeError(f"Modal not configured: {e}")

    def setup(self, ctx: ExecutionContext) -> None:
        """Prepare Modal function and upload code."""
        # Get container image from harness
        image = ctx.harness.get_container_image()
        if not image:
            raise ValueError(f"Harness {ctx.harness.id} doesn't support containerized execution")

        # Prepare code as tar archive
        code_tar = self._prepare_code_tar(ctx)
        ctx._code_tar = code_tar  # Store for cleanup

        # Store harness info for execution
        ctx._harness_id = ctx.harness.id
        ctx._image = image

    def _prepare_code_tar(self, ctx: ExecutionContext) -> bytes:
        """Prepare code as tar archive for upload."""
        home = get_vibelab_home()
        temp_base = home / "modal" / ctx.result_id
        temp_base.mkdir(parents=True, exist_ok=True)
        temp_dir = temp_base / "workspace"

        # Load code based on scenario type
        if ctx.scenario.code_type.value == "github":
            self._setup_github(ctx, temp_dir)
        elif ctx.scenario.code_type.value == "local":
            self._setup_local(ctx, temp_dir)
        elif ctx.scenario.code_type.value == "empty":
            self._setup_empty(temp_dir)
        else:
            raise ValueError(f"Unknown code type: {ctx.scenario.code_type}")

        # Create tar archive
        tar_buffer = tempfile.NamedTemporaryFile(delete=False)
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            tar.add(temp_dir, arcname="workspace")

        tar_buffer.seek(0)
        tar_data = tar_buffer.read()
        tar_buffer.close()

        # Cleanup temp directory (we have the tar now)
        import shutil

        shutil.rmtree(temp_base, ignore_errors=True)

        return tar_data

    def _setup_github(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup GitHub repository by cloning."""
        import subprocess

        from ..models.scenario import GitHubCodeRef

        code_ref = ctx.scenario.code_ref
        if not isinstance(code_ref, GitHubCodeRef):
            raise ValueError("Expected GitHubCodeRef")

        # Clone repository
        url = f"https://github.com/{code_ref.owner}/{code_ref.repo}.git"
        subprocess.run(
            ["git", "clone", url, str(workdir)],
            check=True,
            capture_output=True,
        )

        # Checkout specific commit
        subprocess.run(
            ["git", "checkout", code_ref.commit_sha],
            cwd=workdir,
            check=True,
            capture_output=True,
        )

    def _setup_local(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup local directory by copying."""
        import shutil

        from ..models.scenario import LocalCodeRef

        code_ref = ctx.scenario.code_ref
        if not isinstance(code_ref, LocalCodeRef):
            raise ValueError("Expected LocalCodeRef")

        source = Path(code_ref.path).expanduser()
        if not source.exists():
            raise ValueError(f"Local path does not exist: {source}")
        shutil.copytree(source, workdir, dirs_exist_ok=True)

    def _setup_empty(self, workdir: Path) -> None:
        """Setup empty directory."""
        workdir.mkdir(parents=True, exist_ok=True)

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        """Execute harness in Modal container with streaming output."""
        from ..engine.streaming import StreamingLog

        if not hasattr(ctx, "_code_tar") or not hasattr(ctx, "_harness_id"):
            raise ValueError("Modal function not set up")

        start_time = time.time()

        # Create streaming log for real-time output
        streaming_log = StreamingLog(result_id=int(ctx.result_id))

        # Define callbacks for streaming
        def on_stdout(data: str) -> None:
            streaming_log.append_stdout(data)

        def on_stderr(data: str) -> None:
            streaming_log.append_stderr(data)

        try:
            # Build harness command before creating function
            cmd = self._build_harness_command(ctx._harness_id, ctx.scenario.prompt, ctx.provider, ctx.model)

            # Create Modal function dynamically
            function = self._create_modal_function(ctx, cmd)

            # Execute function
            result = function.remote(
                code_tar_base64=base64.b64encode(ctx._code_tar).decode(),
                cmd=cmd,
                timeout_seconds=ctx.timeout_seconds,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Extract output from result
            output = HarnessOutput(
                exit_code=result.get("exit_code", 1),
                stdout=result.get("stdout", ""),
                stderr=result.get("stderr", ""),
            )

            patch = result.get("patch")

            # Save patch to streaming location
            if patch:
                home = get_vibelab_home()
                result_dir = home / "results" / ctx.result_id
                result_dir.mkdir(parents=True, exist_ok=True)
                (result_dir / "patch.diff").write_text(patch)

            # Finalize streaming log
            streaming_log.finalize(final_stdout=output.stdout, final_stderr=output.stderr)

            return RunOutput(
                exit_code=output.exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                duration_ms=duration_ms,
                patch=patch,
            )
        except Exception as e:
            streaming_log.mark_failed()
            logger.exception(f"Modal execution failed: {e}")
            raise

    def _create_modal_function(self, ctx: ExecutionContext, cmd: list[str]) -> Any:
        """Create Modal function for harness execution."""
        if modal is None:
            raise ImportError("Modal SDK not installed")

        # Get secrets for API keys
        secrets = []
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                secrets.append(modal.Secret.from_name("anthropic", create_if_missing=False))
            except Exception:
                pass  # Secret may not exist
        if os.getenv("OPENAI_API_KEY"):
            try:
                secrets.append(modal.Secret.from_name("openai", create_if_missing=False))
            except Exception:
                pass
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            try:
                secrets.append(modal.Secret.from_name("google", create_if_missing=False))
            except Exception:
                pass

        # Create base image (we'll use a generic Python image and install harness CLI at runtime)
        # For production, harnesses should provide pre-built images
        image = (
            modal.Image.debian_slim()
            .pip_install("gitpython")
            .run_commands("apt-get update && apt-get install -y git")
        )

        # Create function dynamically - Modal functions need to be defined at module level
        # So we'll create a wrapper that calls the function
        def create_function():
            @modal.function(
                image=image,
                secrets=secrets,
                timeout=ctx.timeout_seconds,
                container_idle_timeout=60,
            )
            def run_harness_modal(
                code_tar_base64: str,
                cmd: list[str],
                timeout_seconds: int,
            ) -> dict[str, Any]:
                """Run harness in Modal container."""
                import base64
                import os
                import subprocess
                import tarfile
                import tempfile
                from pathlib import Path

                # Extract code tar
                code_tar = base64.b64decode(code_tar_base64)
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar_path = Path(tmpdir) / "code.tar.gz"
                    tar_path.write_bytes(code_tar)

                    workspace = Path(tmpdir) / "workspace"
                    with tarfile.open(tar_path, "r:gz") as tar:
                        tar.extractall(tmpdir)

                    # Initialize git repo
                    subprocess.run(
                        ["git", "init"],
                        cwd=workspace,
                        check=False,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["git", "config", "user.name", "VibeLab"],
                        cwd=workspace,
                        check=False,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["git", "config", "user.email", "vibelab@localhost"],
                        cwd=workspace,
                        check=False,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["git", "add", "-A"],
                        cwd=workspace,
                        check=False,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["git", "commit", "-m", "Initial state"],
                        cwd=workspace,
                        check=False,
                        capture_output=True,
                    )

                    # Execute harness command
                    try:
                        result = subprocess.run(
                            cmd,
                            cwd=workspace,
                            capture_output=True,
                            text=True,
                            timeout=timeout_seconds,
                            env=os.environ.copy(),
                        )

                        # Generate patch
                        subprocess.run(
                            ["git", "add", "-A"],
                            cwd=workspace,
                            check=False,
                            capture_output=True,
                        )
                        patch_result = subprocess.run(
                            ["git", "diff", "--cached", "HEAD"],
                            cwd=workspace,
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        patch = patch_result.stdout if patch_result.returncode == 0 else None

                        return {
                            "exit_code": result.returncode,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                            "patch": patch,
                        }
                    except subprocess.TimeoutExpired:
                        return {
                            "exit_code": 124,
                            "stdout": "",
                            "stderr": "Command timed out",
                            "patch": None,
                        }

            return run_harness_modal

        return create_function()

    def _build_harness_command(self, harness_id: str, prompt: str, provider: str, model: str) -> list[str]:
        """Build harness command based on harness type."""
        if harness_id == "claude-code":
            return [
                "claude",
                "--print",
                "--verbose",
                "--output-format",
                "stream-json",
                "--dangerously-skip-permissions",
                "--model",
                model,
                "-p",
                prompt,
            ]
        elif harness_id == "openai-codex":
            return [
                "codex",
                "exec",
                "--sandbox",
                "workspace-write",
                "--skip-git-repo-check",
                "--model",
                model,
                prompt,
            ]
        elif harness_id == "cursor":
            return [
                "cursor-agent",
                "--print",
                "--output-format",
                "stream-json",
                "--force",
                "--model",
                model,
                prompt,
            ]
        else:
            raise ValueError(f"Unknown harness: {harness_id}")

    def cleanup(self, ctx: ExecutionContext) -> None:
        """Clean up Modal resources."""
        # Modal handles cleanup automatically for ephemeral containers
        # Just clean up any local temp files
        if hasattr(ctx, "_code_tar"):
            # Tar is in memory, nothing to clean
            pass

