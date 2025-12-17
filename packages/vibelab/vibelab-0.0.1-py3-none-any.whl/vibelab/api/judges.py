"""Judge API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..db import (
    get_db,
    get_llm_scenario_judge,
    list_llm_scenario_judges,
    get_latest_llm_scenario_judge,
    create_llm_scenario_judge,
    delete_llm_scenario_judge,
    get_scenario,
    list_results,
    get_result,
    list_judgements,
    get_judgement_for_result,
    get_judgement,
    update_result_notes_and_quality,
)
from ..models.judge import LLMScenarioJudge, Judgement
from ..models.result import ResultStatus
from ..engine.judge import train_judge, JudgeExecutor
from datetime import datetime, timezone

router = APIRouter()


class CreateJudgeRequest(BaseModel):
    """Request to create an LLM scenario judge."""

    scenario_id: int
    guidance: str
    training_sample_ids: list[int] = Field(default_factory=list)
    test_sample_ids: list[int] = Field(default_factory=list)


class TrainJudgeRequest(BaseModel):
    """Request to train a judge."""

    judge_provider: str = "anthropic"
    judge_model: str = "claude-sonnet-4-20250514"


@router.post("")
def create_judge(request: CreateJudgeRequest):
    """Create a new LLM scenario judge."""
    for db in get_db():
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")

        # Validate sample IDs
        all_sample_ids = request.training_sample_ids + request.test_sample_ids
        for sample_id in all_sample_ids:
            result = get_result(db, sample_id)
            if not result:
                raise HTTPException(status_code=404, detail=f"Result {sample_id} not found")
            if result.scenario_id != request.scenario_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Result {sample_id} does not belong to scenario {request.scenario_id}",
                )

        judge = LLMScenarioJudge(
            id=0,  # Will be set by database
            scenario_id=request.scenario_id,
            guidance=request.guidance,
            training_sample_ids=request.training_sample_ids,
            test_sample_ids=request.test_sample_ids,
            alignment_score=None,
            created_at=datetime.now(timezone.utc),
        )
        judge = create_llm_scenario_judge(db, judge)
        return judge.model_dump()


@router.put("/{judge_id}")
def update_judge(judge_id: int, request: CreateJudgeRequest):
    """Update an existing LLM scenario judge (creates a new version)."""
    # For now, we'll just create a new judge since judges evolve over time
    # But we validate the judge exists first
    for db in get_db():
        existing_judge = get_llm_scenario_judge(db, judge_id)
        if not existing_judge:
            raise HTTPException(status_code=404, detail="Judge not found")
        
        # Create new judge with updated data
        return create_judge(request)


@router.get("")
def list_judges(scenario_id: int | None = None):
    """List LLM scenario judges."""
    for db in get_db():
        judges = list_llm_scenario_judges(db, scenario_id=scenario_id)
        return [j.model_dump() for j in judges]


@router.get("/judgements/all")
def list_all_judgements():
    """List all judgements across all judges."""
    for db in get_db():
        judgements = list_judgements(db)
        # Enrich with result and judge info
        enriched = []
        for judgement in judgements:
            result = get_result(db, judgement.result_id)
            judge = get_llm_scenario_judge(db, judgement.judge_id)
            enriched.append({
                **judgement.model_dump(),
                "result": result.model_dump() if result else None,
                "judge": judge.model_dump() if judge else None,
            })
        return enriched


@router.get("/judgements/pending")
def list_pending_judgements():
    """List completed results that don't have judgements yet (for informational purposes only).
    
    Note: Judgements are now triggered manually from the UI, one at a time.
    This endpoint is kept for informational purposes but doesn't represent a queue.
    """
    for db in get_db():
        from ..db import list_results, get_latest_llm_scenario_judge
        from ..models.result import ResultStatus
        
        # Get all completed results
        all_results = list_results(db)
        completed_results = [r for r in all_results if r.status == ResultStatus.COMPLETED]
        
        # Find results that don't have judgements but have judges available
        pending = []
        for result in completed_results:
            judge = get_latest_llm_scenario_judge(db, result.scenario_id)
            if judge:
                # Check if judgement exists
                existing_judgement = get_judgement_for_result(db, result.id, judge.id)
                if not existing_judgement:
                    pending.append({
                        "result": result.model_dump(),
                        "judge": judge.model_dump(),
                    })
        
        return pending


@router.get("/scenarios/{scenario_id}/judgements")
def list_scenario_judgements(scenario_id: int):
    """List all judgements for a scenario (from all judges)."""
    for db in get_db():
        from ..db import list_results, list_llm_scenario_judges
        from ..models.result import ResultStatus
        
        # Get all judges for this scenario
        judges = list_llm_scenario_judges(db, scenario_id=scenario_id)
        latest_judge_id = judges[0].id if judges else None
        
        # Get all results for this scenario
        results = list_results(db, scenario_id=scenario_id)
        
        # Get all judgements for these results
        enriched_judgements = []
        for result in results:
            # Get all judgements for this result
            result_judgements = list_judgements(db, result_id=result.id)
            for judgement in result_judgements:
                # Find the judge that made this judgement
                judge = next((j for j in judges if j.id == judgement.judge_id), None)
                if judge:
                    enriched_judgements.append({
                        **judgement.model_dump(),
                        "result": result.model_dump(),
                        "judge": judge.model_dump(),
                        "is_latest_judge": judgement.judge_id == latest_judge_id,
                    })
        
        return enriched_judgements


@router.post("/judgements/{judgement_id}/accept")
def accept_judgement(judgement_id: int):
    """Accept a judgement by copying its notes and quality to the result's human feedback."""
    for db in get_db():
        from ..db import get_judgement, update_result_notes_and_quality
        
        judgement = get_judgement(db, judgement_id)
        if not judgement:
            raise HTTPException(status_code=404, detail="Judgement not found")
        
        # Copy judgement notes and quality to result
        update_result_notes_and_quality(db, judgement.result_id, judgement.notes, judgement.quality)
        
        # Return updated result
        from ..db import get_result
        result = get_result(db, judgement.result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        return result.model_dump()


@router.get("/{judge_id}")
def get_judge(judge_id: int):
    """Get judge detail."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")
        return judge.model_dump()


@router.post("/{judge_id}/train")
def train_judge_endpoint(judge_id: int, request: TrainJudgeRequest, background_tasks: BackgroundTasks):
    """Train a judge and calculate alignment score."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # Run training in background
        background_tasks.add_task(
            train_judge,
            judge,
            request.judge_provider,
            request.judge_model,
        )

        return {"status": "training", "judge_id": judge_id}


@router.delete("/{judge_id}")
def delete_judge_endpoint(judge_id: int):
    """Delete a judge."""
    for db in get_db():
        deleted = delete_llm_scenario_judge(db, judge_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Judge not found")
        return {"status": "deleted", "judge_id": judge_id}


@router.get("/{judge_id}/judgements")
def list_judge_judgements(judge_id: int):
    """List judgements made by a judge."""
    for db in get_db():
        judgements = list_judgements(db, judge_id=judge_id)
        return [j.model_dump() for j in judgements]


@router.post("/{judge_id}/judge-result/{result_id}")
def judge_result_endpoint(judge_id: int, result_id: int, request: TrainJudgeRequest):
    """Manually trigger judge execution on a result synchronously."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        if result.scenario_id != judge.scenario_id:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} does not belong to scenario {judge.scenario_id}",
            )

        if result.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} is not completed (status: {result.status})",
            )

        # Check if judgement already exists - if it's from an older judge version, allow replacement
        existing_judgement = get_judgement_for_result(db, result.id, judge_id)
        if existing_judgement:
            # Allow replacing if it's from an older judge version
            from ..db import get_latest_llm_scenario_judge
            latest_judge = get_latest_llm_scenario_judge(db, judge.scenario_id)
            if latest_judge and existing_judgement.judge_id == latest_judge.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Judgement already exists for result {result_id} from the latest judge",
                )
            # If it's from an older judge, we'll replace it (delete old, create new)
            from ..db import delete_judgement
            delete_judgement(db, existing_judgement.id)

        executor = JudgeExecutor()
        try:
            judgement = executor.execute_judge(judge, result, request.judge_provider, request.judge_model)
            return judgement.model_dump()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to execute judge {judge_id} on result {result_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute judge: {str(e)}",
            )


class ApplyJudgeRequest(BaseModel):
    """Request to apply judge to results."""

    result_ids: list[int] | None = None  # If None, apply to all completed results for scenario
    judge_provider: str = "anthropic"
    judge_model: str = "claude-sonnet-4-20250514"


@router.post("/{judge_id}/apply")
def apply_judge_endpoint(judge_id: int, request: ApplyJudgeRequest):
    """Apply judge to a single result synchronously. For multiple results, call this endpoint multiple times."""
    for db in get_db():
        judge = get_llm_scenario_judge(db, judge_id)
        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # Only process one result at a time
        if not request.result_ids or len(request.result_ids) != 1:
            raise HTTPException(
                status_code=400,
                detail="Must provide exactly one result_id. For multiple results, call this endpoint multiple times."
            )

        result_id = request.result_ids[0]
        result = get_result(db, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        if result.scenario_id != judge.scenario_id:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} does not belong to scenario {judge.scenario_id}",
            )

        if result.status != ResultStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Result {result_id} is not completed (status: {result.status})",
            )

        # Check if judgement already exists - if it's from an older judge version, allow replacement
        existing_judgement = get_judgement_for_result(db, result.id, judge_id)
        if existing_judgement:
            # Allow replacing if it's from an older judge version
            from ..db import get_latest_llm_scenario_judge
            latest_judge = get_latest_llm_scenario_judge(db, judge.scenario_id)
            if latest_judge and existing_judgement.judge_id == latest_judge.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Judgement already exists for result {result_id} from the latest judge",
                )
            # If it's from an older judge, we'll replace it (delete old, create new)
            from ..db import delete_judgement
            delete_judgement(db, existing_judgement.id)

        # Execute judge synchronously
        executor = JudgeExecutor()
        try:
            judgement = executor.execute_judge(judge, result, request.judge_provider, request.judge_model)
            return judgement.model_dump()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception(f"Failed to execute judge {judge_id} on result {result_id}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute judge: {str(e)}",
            )

