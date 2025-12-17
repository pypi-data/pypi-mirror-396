"""Result API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..db import (
    get_db,
    get_result,
    list_results,
    delete_result,
    update_result_annotations,
    update_result_notes,
    update_result_quality,
    update_result_notes_and_quality,
    get_scenario,
    create_result,
)
from ..db.connection import get_vibelab_home
from ..models.result import Annotations, Result, ResultStatus
from ..models.executor import ExecutorSpec
from ..engine.runner import Runner
from datetime import datetime, timezone

router = APIRouter()


@router.get("")
def list_results_endpoint(
    scenario_id: int | None = None,
    executor: str | None = None,
    status: str | None = None,
):
    """List results with optional filtering."""
    status_enum = ResultStatus(status) if status else None
    for db in get_db():
        results = list_results(db, scenario_id=scenario_id, executor_spec=executor, status=status_enum)
        return [
            {**r.model_dump(), "is_stale": r.is_stale()}
            for r in results
        ]


@router.get("/{result_id}")
def get_result_endpoint(result_id: int):
    """Get result detail."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        return {**result.model_dump(), "is_stale": result.is_stale()}


@router.get("/{result_id}/patch")
def get_result_patch(result_id: int):
    """Get result patch."""
    home = get_vibelab_home()
    patch_file = home / "results" / str(result_id) / "patch.diff"
    if not patch_file.exists():
        raise HTTPException(status_code=404, detail="Patch not found")
    return {"patch": patch_file.read_text()}


@router.get("/{result_id}/logs")
def get_result_logs(result_id: int):
    """Get result logs."""
    home = get_vibelab_home()
    stdout_file = home / "results" / str(result_id) / "stdout.log"
    stderr_file = home / "results" / str(result_id) / "stderr.log"
    return {
        "stdout": stdout_file.read_text() if stdout_file.exists() else "",
        "stderr": stderr_file.read_text() if stderr_file.exists() else "",
    }


@router.patch("/{result_id}/annotations")
def update_result_annotations_endpoint(result_id: int, annotations: dict):
    """Update result annotations."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        update_result_annotations(db, result_id, annotations)
        result = get_result(db, result_id)
        return result.model_dump() if result else None


class UpdateNotesRequest(BaseModel):
    """Request to update result notes."""

    notes: str | None = None


class UpdateQualityRequest(BaseModel):
    """Request to update result quality score."""

    quality: int | None = Field(None, ge=1, le=4)


class UpdateNotesAndQualityRequest(BaseModel):
    """Request to update result notes and quality score."""

    notes: str | None = None
    quality: int | None = Field(None, ge=1, le=4)


@router.patch("/{result_id}/notes")
def update_result_notes_endpoint(result_id: int, request: UpdateNotesRequest):
    """Update result notes."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        update_result_notes(db, result_id, request.notes)
        result = get_result(db, result_id)
        return result.model_dump() if result else None


@router.patch("/{result_id}/quality")
def update_result_quality_endpoint(result_id: int, request: UpdateQualityRequest):
    """Update result quality score."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        update_result_quality(db, result_id, request.quality)
        result = get_result(db, result_id)
        return result.model_dump() if result else None


@router.patch("/{result_id}/notes-quality")
def update_result_notes_and_quality_endpoint(result_id: int, request: UpdateNotesAndQualityRequest):
    """Update result notes and quality score."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        update_result_notes_and_quality(db, result_id, request.notes, request.quality)
        result = get_result(db, result_id)
        return result.model_dump() if result else None


@router.delete("/{result_id}")
def delete_result_endpoint(result_id: int):
    """Delete a result."""
    import shutil
    
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Delete from database
        deleted = delete_result(db, result_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Delete result files
        result_dir = get_vibelab_home() / "results" / str(result_id)
        if result_dir.exists():
            shutil.rmtree(result_dir)
        
        break
    
    return {"status": "deleted", "result_id": result_id}


@router.post("/{result_id}/rerun")
def rerun_result_endpoint(result_id: int, background_tasks: BackgroundTasks):
    """Rerun a result with the same settings."""
    for db in get_db():
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        scenario = get_scenario(db, result.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Build executor spec from result
        executor_spec_str = f"{result.harness}:{result.provider}:{result.model}"
        
        # Use timeout from original result, or default
        timeout_seconds = result.timeout_seconds or 1800
        
        # Create new result record synchronously
        from ..models.result import Result, ResultStatus
        from datetime import datetime, timezone
        new_result = Result(
            id=0,  # Will be set by database
            scenario_id=result.scenario_id,
            harness=result.harness,
            provider=result.provider,
            model=result.model,
            status=ResultStatus.QUEUED,
            created_at=datetime.now(timezone.utc),
            timeout_seconds=timeout_seconds,
        )
        new_result = create_result(db, new_result)
        
        # Initialize streaming log early so frontend can connect immediately
        from ..engine.streaming import StreamingLog
        streaming_log = StreamingLog(result_id=new_result.id)
        streaming_log.set_status("queued")
        
        # Queue background task to execute the run
        from ..api.runs import run_executor_task
        background_tasks.add_task(
            run_executor_task,
            new_result.id,
            result.scenario_id,
            executor_spec_str,
            timeout_seconds,
            "local",  # Default driver
        )
        
        break
    
    return {
        "status": "queued",
        "scenario_id": result.scenario_id,
        "executor_spec": executor_spec_str,
        "original_result_id": result_id,
        "result_id": new_result.id,
    }
