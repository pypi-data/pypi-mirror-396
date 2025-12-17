"""Local driver using git worktrees."""

import logging
import os
import subprocess
import tempfile
from pathlib import Path

from ..db.connection import get_vibelab_home
from ..drivers.base import Driver, ExecutionContext, RunOutput
from ..harnesses.base import Harness

logger = logging.getLogger(__name__)


class LocalDriver:
    """Local execution driver using git worktrees."""

    id = "local"

    def setup(self, ctx: ExecutionContext) -> None:
        """Create git worktree for isolation."""
        if ctx.streaming_log:
            ctx.streaming_log.set_status("cloning")
        
        home = get_vibelab_home()
        worktrees_dir = home / "worktrees"
        worktrees_dir.mkdir(parents=True, exist_ok=True)

        workdir = worktrees_dir / ctx.result_id
        ctx.workdir = workdir

        # Load code based on scenario type
        if ctx.scenario.code_type.value == "github":
            self._setup_github(ctx, workdir)
        elif ctx.scenario.code_type.value == "local":
            self._setup_local(ctx, workdir)
        elif ctx.scenario.code_type.value == "empty":
            self._setup_empty(workdir)
        else:
            raise ValueError(f"Unknown code type: {ctx.scenario.code_type}")
        
        if ctx.streaming_log:
            ctx.streaming_log.set_status("running")

    def _setup_github(self, ctx: ExecutionContext, workdir: Path) -> None:
        """Setup GitHub repository by cloning."""
        from ..models.scenario import GitHubCodeRef

        code_ref = ctx.scenario.code_ref
        if not isinstance(code_ref, GitHubCodeRef):
            raise ValueError("Expected GitHubCodeRef")

        if ctx.streaming_log:
            ctx.streaming_log.append_stdout(f"Cloning repository: {code_ref.owner}/{code_ref.repo}\n")

        # Clone repository directly to workdir
        url = f"https://github.com/{code_ref.owner}/{code_ref.repo}.git"
        subprocess.run(
            ["git", "clone", url, str(workdir)],
            check=True,
            capture_output=True,
        )

        if ctx.streaming_log:
            ctx.streaming_log.append_stdout(f"Checking out commit: {code_ref.commit_sha}\n")

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

        import shutil

        source = Path(code_ref.path).expanduser()
        if not source.exists():
            raise ValueError(f"Local path does not exist: {source}")
        
        if ctx.streaming_log:
            ctx.streaming_log.append_stdout(f"Copying local directory: {source}\n")
        
        shutil.copytree(source, workdir, dirs_exist_ok=True)

    def _setup_empty(self, workdir: Path) -> None:
        """Setup empty directory and initialize git repo."""
        workdir.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repository for patch generation
        subprocess.run(
            ["git", "init"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )
        
        # Configure git user (required for commits)
        subprocess.run(
            ["git", "config", "user.name", "VibeLab"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "vibelab@localhost"],
            cwd=workdir,
            check=True,
            capture_output=True,
        )
        
        # Create initial commit with empty state for diff comparison
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial empty state"],
            cwd=workdir,
            check=False,  # May fail if no files, that's ok
            capture_output=True,
        )

    def execute(self, ctx: ExecutionContext) -> RunOutput:
        """Execute harness in worktree with streaming output."""
        import time

        if not ctx.workdir:
            raise ValueError("workdir not set")

        # Use streaming log from context if available
        streaming_log = ctx.streaming_log
        if not streaming_log:
            # Fallback: create new streaming log if not provided
            from ..engine.streaming import StreamingLog
            streaming_log = StreamingLog(result_id=int(ctx.result_id))

        start_time = time.time()

        # Define callbacks for streaming
        def on_stdout(data: str) -> None:
            if streaming_log:
                streaming_log.append_stdout(data)

        def on_stderr(data: str) -> None:
            if streaming_log:
                streaming_log.append_stderr(data)

        try:
            if streaming_log:
                streaming_log.append_stdout(f"Starting execution with {ctx.harness.id}...\n")

            # Run harness with streaming callbacks
            output = ctx.harness.run(
                workdir=ctx.workdir,
                prompt=ctx.scenario.prompt,
                provider=ctx.provider,
                model=ctx.model,
                timeout_seconds=ctx.timeout_seconds,
                on_stdout=on_stdout,
                on_stderr=on_stderr,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            if streaming_log:
                streaming_log.append_stdout(f"\nExecution completed (exit code: {output.exit_code})\n")

            # Generate patch
            patch = self._generate_patch(ctx.workdir)

            # Save patch to streaming location for live updates
            if patch:
                home = get_vibelab_home()
                result_dir = home / "results" / ctx.result_id
                (result_dir / "patch.diff").write_text(patch)

            # Note: Don't finalize here - runner will handle finalization
            # This allows runner to set final status based on exit code

            return RunOutput(
                exit_code=output.exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                duration_ms=duration_ms,
                patch=patch,
            )
        except Exception as e:
            if streaming_log:
                streaming_log.append_stderr(f"\nExecution failed: {e}\n")
                streaming_log.mark_failed()
            raise

    def _generate_patch(self, workdir: Path) -> str | None:
        """Generate git patch of changes."""
        try:
            # Check if this is a git repository
            git_check = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=workdir,
                capture_output=True,
                check=False,
            )
            if git_check.returncode != 0:
                # Not a git repo, no patch possible
                return None

            # Stage all changes (including untracked files) for proper diff
            subprocess.run(
                ["git", "add", "-A"],
                cwd=workdir,
                check=False,
                capture_output=True,
            )

            # Get diff of staged changes (modified and new files)
            diff_result = subprocess.run(
                ["git", "diff", "--cached", "HEAD"],
                cwd=workdir,
                capture_output=True,
                text=True,
                check=False,
            )

            patches = []
            if diff_result.returncode == 0 and diff_result.stdout:
                patches.append(diff_result.stdout)

            if patches:
                return "".join(patches)
            return None
        except Exception as e:
            logger.warning(f"Failed to generate patch: {e}")
            return None

    def cleanup(self, ctx: ExecutionContext) -> None:
        """Remove work directory."""
        if not ctx.workdir:
            return

        try:
            # Remove directory
            import shutil

            shutil.rmtree(ctx.workdir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup workdir: {e}")
