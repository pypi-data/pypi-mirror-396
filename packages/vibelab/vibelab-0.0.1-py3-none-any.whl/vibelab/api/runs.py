"""Run API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..db import get_db, get_scenario, create_result, get_result
from ..engine.runner import Runner
from ..models.executor import ExecutorSpec
from ..models.result import Result, ResultStatus
from datetime import datetime, timezone

router = APIRouter()


class CreateRunRequest(BaseModel):
    """Request to create a run."""

    scenario_id: int
    executor_spec: str
    timeout_seconds: int = 1800
    driver: str = "local"


def run_executor_task(
    result_id: int,
    scenario_id: int,
    executor_spec_str: str,
    timeout_seconds: int,
    driver: str,
) -> None:
    """Background task to run executor."""
    runner = Runner()
    executor_spec = ExecutorSpec.parse(executor_spec_str)
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            return
        try:
            # Run the execution using the existing result
            runner.run(scenario, executor_spec, timeout_seconds, driver, result_id=result_id)
        except (RuntimeError, ValueError) as e:
            # Infrastructure failures (harness unavailable, unknown driver, etc.)
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Infrastructure failure")
            from ..db import update_result_status
            error_msg = str(e)
            # Check if it's already been set to INFRA_FAILURE by runner
            result_check = get_result(db, result_id)
            if result_check and result_check.status == ResultStatus.INFRA_FAILURE:
                # Already handled by runner
                pass
            else:
                # Set it here if runner didn't catch it
                update_result_status(
                    db, result_id, ResultStatus.INFRA_FAILURE,
                    finished_at=datetime.now(timezone.utc),
                    error_message=error_msg
                )
        except Exception as e:
            # Other failures (execution errors, etc.)
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Run failed")
            from ..db import update_result_status
            error_msg = str(e)
            update_result_status(
                db, result_id, ResultStatus.FAILED,
                finished_at=datetime.now(timezone.utc),
                error_message=error_msg
            )


@router.post("")
def create_run(request: CreateRunRequest, background_tasks: BackgroundTasks):
    """Queue a new run."""
    executor_spec = ExecutorSpec.parse(request.executor_spec)
    for db in get_db():
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Create result record synchronously
        result = Result(
            id=0,  # Will be set by database
            scenario_id=request.scenario_id,
            harness=executor_spec.harness,
            provider=executor_spec.provider,
            model=executor_spec.model,
            status=ResultStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=request.timeout_seconds,
            driver=request.driver,
        )
        result = create_result(db, result)

        # Initialize streaming log early so frontend can connect immediately
        from ..engine.streaming import StreamingLog
        streaming_log = StreamingLog(result_id=result.id)
        streaming_log.set_status("queued")

        # Queue background task to execute the run
        background_tasks.add_task(
            run_executor_task,
            result.id,
            request.scenario_id,
            request.executor_spec,
            request.timeout_seconds,
            request.driver,
        )

        return {
            "status": "queued",
            "scenario_id": request.scenario_id,
            "executor_spec": request.executor_spec,
            "result_id": result.id,
        }
