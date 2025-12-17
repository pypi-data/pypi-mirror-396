"""Runner for executing scenarios."""

import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..db import get_db, create_result, get_result, update_result_metrics, update_result_status
from ..drivers import DRIVERS, Driver
from ..harnesses import HARNESSES, Harness
from ..models.executor import ExecutorSpec
from ..models.result import Result, ResultStatus
from ..models.scenario import Scenario
from .loader import CodeLoader

logger = logging.getLogger(__name__)


class Runner:
    """Runs scenarios against executors."""

    def __init__(self) -> None:
        self.loader = CodeLoader()

    def run(
        self,
        scenario: Scenario,
        executor_spec: ExecutorSpec,
        timeout_seconds: int = 1800,
        driver_id: str = "local",
        result_id: int | None = None,
    ) -> Result:
        """Run a scenario against an executor."""
        harness = HARNESSES.get(executor_spec.harness)
        if not harness:
            error_msg = f"Unknown harness: {executor_spec.harness}"
            if result_id:
                for db in get_db():
                    update_result_status(
                        db, result_id, ResultStatus.INFRA_FAILURE,
                        finished_at=datetime.now(timezone.utc),
                        error_message=error_msg
                    )
                    break
            raise ValueError(error_msg)

        available, error = harness.check_available()
        if not available:
            error_msg = f"Harness unavailable: {error}"
            if result_id:
                for db in get_db():
                    update_result_status(
                        db, result_id, ResultStatus.INFRA_FAILURE,
                        finished_at=datetime.now(timezone.utc),
                        error_message=error_msg
                    )
                    break
            raise RuntimeError(error_msg)

        driver = DRIVERS.get(driver_id)
        if not driver:
            error_msg = f"Unknown driver: {driver_id}"
            if result_id:
                for db in get_db():
                    update_result_status(
                        db, result_id, ResultStatus.INFRA_FAILURE,
                        finished_at=datetime.now(timezone.utc),
                        error_message=error_msg
                    )
                    break
            raise ValueError(error_msg)

        # Get or create result record
        if result_id:
            # Use existing result
            for db in get_db():
                result = get_result(db, result_id)
                if not result:
                    raise ValueError(f"Result {result_id} not found")
                break
        else:
            # Create new result record
            result = Result(
                id=0,  # Will be set by database
                scenario_id=scenario.id,
                harness=executor_spec.harness,
                provider=executor_spec.provider,
                model=executor_spec.model,
                status=ResultStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                timeout_seconds=timeout_seconds,
            )

            for db in get_db():
                result = create_result(db, result)
                break

        try:
            # Get or create streaming log for status updates
            from .streaming import StreamingLog, get_streaming_log
            streaming_log = get_streaming_log(result.id)
            if not streaming_log:
                # Create new streaming log if it doesn't exist (for reruns)
                streaming_log = StreamingLog(result_id=result.id)
            streaming_log.set_status("starting")

            # Update to running
            started_at = datetime.now(timezone.utc)
            for db in get_db():
                update_result_status(db, result.id, ResultStatus.RUNNING, started_at=started_at)
                break

            streaming_log.set_status("running")

            # Execute
            ctx = self._create_context(result, scenario, harness, executor_spec, timeout_seconds, streaming_log)
            output = self._execute(ctx, driver, harness)

            # Process output
            finished_at = datetime.now(timezone.utc)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            result = self._process_output(result, output, finished_at, duration_ms, ctx.workdir)

            # Check exit code - mark as failed if non-zero
            final_status = ResultStatus.COMPLETED
            if output.exit_code != 0:
                final_status = ResultStatus.FAILED
                logger.warning(f"Harness exited with code {output.exit_code}")

            # Update result status field
            result.status = final_status

            # Finalize streaming log
            from .streaming import get_streaming_log
            streaming_log = get_streaming_log(result.id)
            if streaming_log:
                if final_status == ResultStatus.COMPLETED:
                    streaming_log.finalize(final_stdout=output.stdout, final_stderr=output.stderr)
                else:
                    streaming_log.mark_failed()

            # Update status and metrics in database
            for db in get_db():
                update_result_status(
                    db,
                    result.id,
                    final_status,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                update_result_metrics(
                    db,
                    result.id,
                    lines_added=result.lines_added,
                    lines_removed=result.lines_removed,
                    files_changed=result.files_changed,
                    tokens_used=result.tokens_used,
                    cost_usd=result.cost_usd,
                )
                break

            return result

        except subprocess.TimeoutExpired:
            finished_at = datetime.now(timezone.utc)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            from .streaming import get_streaming_log
            streaming_log = get_streaming_log(result.id)
            if streaming_log:
                streaming_log.mark_failed()
            for db in get_db():
                update_result_status(
                    db,
                    result.id,
                    ResultStatus.TIMEOUT,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                )
                break
            raise
        except Exception as e:
            finished_at = datetime.now(timezone.utc)
            duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            logger.exception("Execution failed")
            error_msg = str(e)
            from .streaming import get_streaming_log
            streaming_log = get_streaming_log(result.id)
            if streaming_log:
                streaming_log.mark_failed()
            for db in get_db():
                update_result_status(
                    db,
                    result.id,
                    ResultStatus.FAILED,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    error_message=error_msg,
                )
                break
            raise

    def _create_context(
        self,
        result: Result,
        scenario: Scenario,
        harness: Harness,
        executor_spec: ExecutorSpec,
        timeout_seconds: int,
        streaming_log: "StreamingLog",  # type: ignore
    ) -> "ExecutionContext":  # type: ignore
        """Create execution context."""
        from ..drivers.base import ExecutionContext

        return ExecutionContext(
            result_id=str(result.id),
            scenario=scenario,
            harness=harness,
            provider=executor_spec.provider,
            model=executor_spec.model,
            timeout_seconds=timeout_seconds,
            streaming_log=streaming_log,
        )

    def _execute(self, ctx: "ExecutionContext", driver: Driver, harness: Harness) -> "RunOutput":  # type: ignore
        """Execute using driver."""
        driver.setup(ctx)
        try:
            return driver.execute(ctx)
        finally:
            driver.cleanup(ctx)

    def _process_output(
        self,
        result: Result,
        output: "RunOutput",  # type: ignore
        finished_at: datetime,
        duration_ms: int,
        workdir: Path | None,
    ) -> Result:
        """Process execution output and update result."""
        # Save logs
        self._save_logs(result.id, output.stdout, output.stderr)

        # Calculate metrics from patch
        lines_added, lines_removed, files_changed = self._analyze_patch(output.patch)

        # Extract token usage and calculate cost
        # Get harness instance for pricing lookup
        harness_instance = HARNESSES.get(result.harness)
        if harness_instance:
            tokens_used, cost_usd = self._extract_usage(harness_instance, result.provider, result.model, output.stdout, output.stderr)
        else:
            tokens_used, cost_usd = None, None

        # Update result
        result.finished_at = finished_at
        result.duration_ms = duration_ms
        result.lines_added = lines_added
        result.lines_removed = lines_removed
        result.files_changed = files_changed
        result.tokens_used = tokens_used
        result.cost_usd = cost_usd

        # Save patch
        if output.patch:
            self._save_patch(result.id, output.patch)

        return result

    def _save_logs(self, result_id: int, stdout: str, stderr: str) -> None:
        """Save execution logs."""
        from ..db.connection import get_vibelab_home

        home = get_vibelab_home()
        result_dir = home / "results" / str(result_id)
        result_dir.mkdir(parents=True, exist_ok=True)

        (result_dir / "stdout.log").write_text(stdout)
        (result_dir / "stderr.log").write_text(stderr)

    def _save_patch(self, result_id: int, patch: str) -> None:
        """Save git patch."""
        from ..db.connection import get_vibelab_home

        home = get_vibelab_home()
        result_dir = home / "results" / str(result_id)
        result_dir.mkdir(parents=True, exist_ok=True)

        (result_dir / "patch.diff").write_text(patch)

    def _analyze_patch(self, patch: str | None) -> tuple[int, int, int]:
        """Analyze patch to extract metrics."""
        if not patch:
            return (0, 0, 0)

        lines_added = patch.count("\n+") - patch.count("\n+++")
        lines_removed = patch.count("\n-") - patch.count("\n---")
        
        # Count unique files by extracting paths from --- and +++ lines
        # Each file appears once with --- and once with +++, so we need to deduplicate
        file_paths = set()
        for line in patch.split("\n"):
            if line.startswith("---"):
                # Extract path from "--- a/path" or "--- path"
                parts = line.split(None, 1)
                if len(parts) > 1:
                    path = parts[1].lstrip("a/")
                    if path != "/dev/null":
                        file_paths.add(path)
            elif line.startswith("+++"):
                # Extract path from "+++ b/path" or "+++ path"
                parts = line.split(None, 1)
                if len(parts) > 1:
                    path = parts[1].lstrip("b/")
                    if path != "/dev/null":
                        file_paths.add(path)
        
        files_changed = len(file_paths)

        return (lines_added, lines_removed, files_changed)

    def _extract_usage(
        self,
        harness: Harness,
        provider: str,
        model: str,
        stdout: str,
        stderr: str,
    ) -> tuple[int | None, float | None]:
        """
        Extract token usage and calculate cost from harness output.
        
        Returns:
            Tuple of (tokens_used, cost_usd) or (None, None) if not available
        """
        from ..harnesses.usage import (
            parse_claude_code_usage,
            parse_cursor_usage,
            parse_gemini_usage,
            parse_openai_codex_usage,
        )
        from ..pricing import calculate_cost

        # Parse usage based on harness type
        usage_data = None
        if harness.id == "claude-code":
            usage_data = parse_claude_code_usage(stdout, stderr)
        elif harness.id == "openai-codex":
            usage_data = parse_openai_codex_usage(stdout, stderr)
        elif harness.id == "cursor":
            usage_data = parse_cursor_usage(stdout, stderr)
        elif harness.id == "gemini":
            usage_data = parse_gemini_usage(stdout, stderr)

        if not usage_data:
            return (None, None)

        # Calculate total tokens
        tokens_used = None
        if usage_data.get("total_tokens"):
            tokens_used = usage_data["total_tokens"]
        elif usage_data.get("input_tokens") and usage_data.get("output_tokens"):
            tokens_used = usage_data["input_tokens"] + usage_data["output_tokens"]

        # Calculate cost using harness-provided pricing
        cost_usd = calculate_cost(
            harness=harness,
            provider=provider,
            model=model,
            input_tokens=usage_data.get("input_tokens"),
            output_tokens=usage_data.get("output_tokens"),
            total_tokens=tokens_used,
        )

        return (tokens_used, cost_usd)
