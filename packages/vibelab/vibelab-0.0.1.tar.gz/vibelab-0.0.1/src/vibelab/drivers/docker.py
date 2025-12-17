"""Docker driver using OCI containers."""

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from ..db.connection import get_vibelab_home
from ..drivers.base import Driver, ExecutionContext, RunOutput
from ..harnesses.base import HarnessOutput, StreamCallback

logger = logging.getLogger(__name__)

try:
    import docker
    from docker.errors import ImageNotFound, NotFound
except ImportError:
    docker = None  # type: ignore


class DockerDriver:
    """Docker execution driver using OCI containers."""

    id = "docker"

    def __init__(self) -> None:
        """Initialize Docker driver with runtime detection."""
        if docker is None:
            raise ImportError(
                "Docker SDK not installed. Install with: pip install docker or uv pip install -e '.[docker]'"
            )
        self.runtime = self._detect_runtime()
        self.client = self._create_client()

    def _detect_runtime(self) -> str:
        """Detect available OCI runtime."""
        # Check environment variable
        env_runtime = os.getenv("VIBELAB_OCI_RUNTIME")
        if env_runtime:
            if self._check_runtime_available(env_runtime):
                return env_runtime
            raise RuntimeError(f"OCI runtime '{env_runtime}' not available")

        # Auto-detect: docker -> orbstack -> podman
        for runtime in ["docker", "orbstack", "podman"]:
            if self._check_runtime_available(runtime):
                logger.info(f"Detected OCI runtime: {runtime}")
                return runtime

        raise RuntimeError("No OCI runtime available (docker, orbstack, or podman)")

    def _check_runtime_available(self, runtime: str) -> bool:
        """Check if a runtime is available."""
        try:
            result = subprocess.run(
                ["which", runtime],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                return False

            # For docker/orbstack, check if daemon is running
            if runtime in ["docker", "orbstack"]:
                result = subprocess.run(
                    [runtime, "info"],
                    capture_output=True,
                    check=False,
                )
                return result.returncode == 0

            # For podman, check if it's available
            if runtime == "podman":
                result = subprocess.run(
                    ["podman", "info"],
                    capture_output=True,
                    check=False,
                )
                return result.returncode == 0

            return False
        except Exception:
            return False

    def _create_client(self) -> Any:
        """Create Docker client for the detected runtime."""
        if docker is None:
            raise ImportError("Docker SDK not installed")

        # For OrbStack, use Docker SDK with OrbStack socket
        if self.runtime == "orbstack":
            try:
                # OrbStack uses Docker-compatible API
                return docker.from_env()
            except Exception as e:
                raise RuntimeError(f"Failed to connect to OrbStack: {e}")

        # For Podman, use Podman socket
        if self.runtime == "podman":
            try:
                # Podman uses Docker-compatible API on different socket
                return docker.DockerClient(base_url="unix:///run/user/1000/podman/podman.sock")
            except Exception:
                # Fallback to default socket
                try:
                    return docker.from_env()
                except Exception as e:
                    raise RuntimeError(f"Failed to connect to Podman: {e}")

        # Default: Docker
        try:
            return docker.from_env()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Docker: {e}")

    def setup(self, ctx: ExecutionContext) -> None:
        """Prepare Docker container with code loaded."""
        # Get container image from harness
        image = ctx.harness.get_container_image()
        if not image:
            raise ValueError(f"Harness {ctx.harness.id} doesn't support containerized execution")

        # Prepare code in temporary directory
        temp_dir = self._prepare_code(ctx)
        ctx._temp_dir = temp_dir  # Store for cleanup

        # Ensure image is available
        self._ensure_image(image)

        # Create container with volume mount
        container_id = self._create_container(
            image=image,
            workdir_mount=temp_dir,
            env_vars=self._get_env_vars(),
            timeout=ctx.timeout_seconds,
        )

        ctx.workdir = Path("/workspace")  # Container path
        ctx._container_id = container_id  # Store for cleanup

    def _prepare_code(self, ctx: ExecutionContext) -> Path:
        """Prepare code in temporary directory for container mount."""
        home = get_vibelab_home()
        temp_base = home / "containers" / ctx.result_id
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

        return temp_dir

    def _setup_github(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup GitHub repository by cloning."""
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

    def _ensure_image(self, image: str) -> None:
        """Ensure container image is available."""
        try:
            self.client.images.get(image)
            logger.debug(f"Image {image} already available")
        except ImageNotFound:
            logger.info(f"Pulling image {image}...")
            try:
                self.client.images.pull(image)
                logger.info(f"Successfully pulled image {image}")
            except Exception as e:
                raise RuntimeError(f"Failed to pull image {image}: {e}")

    def _get_env_vars(self) -> dict[str, str]:
        """Get environment variables to pass to container."""
        env_vars: dict[str, str] = {}

        # API keys
        for key in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "CURSOR_API_KEY"]:
            value = os.getenv(key)
            if value:
                env_vars[key] = value

        # Log level
        log_level = os.getenv("VIBELAB_LOG_LEVEL", "INFO")
        env_vars["VIBELAB_LOG_LEVEL"] = log_level

        return env_vars

    def _create_container(
        self,
        image: str,
        workdir_mount: Path,
        env_vars: dict[str, str],
        timeout: int,
    ) -> str:
        """Create Docker container."""
        try:
            container = self.client.containers.create(
                image=image,
                command=["sleep", "infinity"],  # Keep container running
                volumes={str(workdir_mount): {"bind": "/workspace", "mode": "rw"}},
                environment=env_vars,
                working_dir="/workspace",
                detach=True,
                network_mode="bridge",  # Isolated network
            )
            return container.id
        except Exception as e:
            raise RuntimeError(f"Failed to create container: {e}")

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        """Execute harness in container with streaming output."""
        import time

        from ..engine.streaming import StreamingLog

        if not ctx.workdir or not hasattr(ctx, "_container_id"):
            raise ValueError("Container not set up")

        start_time = time.time()

        # Create streaming log for real-time output
        streaming_log = StreamingLog(result_id=int(ctx.result_id))

        # Define callbacks for streaming
        def on_stdout(data: str) -> None:
            streaming_log.append_stdout(data)

        def on_stderr(data: str) -> None:
            streaming_log.append_stderr(data)

        try:
            # Initialize git repo in container
            self._init_git(ctx._container_id)

            # Run harness command
            output = self._run_harness(
                ctx._container_id,
                ctx.harness,
                ctx.scenario.prompt,
                ctx.provider,
                ctx.model,
                ctx.timeout_seconds,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Generate patch from container
            patch = self._generate_patch(ctx._container_id)

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
            raise

    def _init_git(self, container_id: str) -> None:
        """Initialize git repository in container."""
        container = self.client.containers.get(container_id)

        # Check if git is installed
        result = container.exec_run(["which", "git"], user="root")
        if result.exit_code != 0:
            logger.warning("Git not found in container, patch generation may fail")
            return

        # Initialize git repo if not already initialized
        result = container.exec_run(
            ["git", "init"],
            workdir="/workspace",
            user="root",
        )
        if result.exit_code != 0:
            logger.warning(f"Failed to initialize git: {result.output.decode()}")

        # Configure git user
        container.exec_run(
            ["git", "config", "user.name", "VibeLab"],
            workdir="/workspace",
            user="root",
        )
        container.exec_run(
            ["git", "config", "user.email", "vibelab@localhost"],
            workdir="/workspace",
            user="root",
        )

        # Add all files and create initial commit
        container.exec_run(
            ["git", "add", "-A"],
            workdir="/workspace",
            user="root",
        )
        container.exec_run(
            ["git", "commit", "-m", "Initial state"],
            workdir="/workspace",
            user="root",
            check=False,  # May fail if no changes, that's ok
        )

    def _run_harness(
        self,
        container_id: str,
        harness: Any,
        prompt: str,
        provider: str,
        model: str,
        timeout_seconds: int,
        on_stdout: StreamCallback | None = None,
        on_stderr: StreamCallback | None = None,
    ) -> Any:
        """Run harness command in container with streaming."""
        from ..harnesses.base import HarnessOutput

        container = self.client.containers.get(container_id)

        # Build command based on harness
        cmd = self._build_harness_command(harness, prompt, provider, model)

        # Execute with streaming
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        exit_code = 1

        try:
            # Create exec instance for streaming
            exec_id = container.exec_create(
                cmd=cmd,
                workdir="/workspace",
                stdout=True,
                stderr=True,
            )

            # Execute with streaming
            stream = container.exec_start(exec_id, stream=True, demux=True)

            # Read stream
            for chunk in stream:
                if chunk:
                    stdout_data, stderr_data = chunk
                    if stdout_data:
                        text = stdout_data.decode("utf-8", errors="replace")
                        stdout_chunks.append(text)
                        if on_stdout:
                            on_stdout(text)
                    if stderr_data:
                        text = stderr_data.decode("utf-8", errors="replace")
                        stderr_chunks.append(text)
                        if on_stderr:
                            on_stderr(text)

            # Get exit code
            inspect_result = container.exec_inspect(exec_id)
            exit_code = inspect_result.get("ExitCode", 1)

        except Exception as e:
            logger.exception(f"Error running harness in container: {e}")
            stderr_chunks.append(f"Error: {e}\n")

        return HarnessOutput(
            exit_code=exit_code,
            stdout="".join(stdout_chunks),
            stderr="".join(stderr_chunks),
        )

    def _build_harness_command(self, harness: Any, prompt: str, provider: str, model: str) -> list[str]:
        """Build harness command based on harness type."""
        # This is a simplified version - harnesses should provide their own command builders
        # For now, we'll use a basic approach
        if harness.id == "claude-code":
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
        elif harness.id == "openai-codex":
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
        elif harness.id == "cursor":
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
            raise ValueError(f"Unknown harness: {harness.id}")

    def _generate_patch(self, container_id: str) -> str | None:
        """Generate git patch from container."""
        container = self.client.containers.get(container_id)

        try:
            # Stage all changes
            container.exec_run(
                ["git", "add", "-A"],
                workdir="/workspace",
                user="root",
                check=False,
            )

            # Get diff
            result = container.exec_run(
                ["git", "diff", "--cached", "HEAD"],
                workdir="/workspace",
                user="root",
            )

            if result.exit_code == 0 and result.output:
                return result.output.decode("utf-8", errors="replace")
            return None
        except Exception as e:
            logger.warning(f"Failed to generate patch: {e}")
            return None

    def cleanup(self, ctx: ExecutionContext) -> None:
        """Clean up container and temporary directory."""
        # Stop and remove container
        if hasattr(ctx, "_container_id"):
            try:
                container = self.client.containers.get(ctx._container_id)
                container.stop()
                container.remove()
            except NotFound:
                pass  # Container already removed
            except Exception as e:
                logger.warning(f"Failed to cleanup container: {e}")

        # Remove temporary directory
        if hasattr(ctx, "_temp_dir"):
            try:
                shutil.rmtree(ctx._temp_dir.parent, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")

