"""Dataset API endpoints."""

from datetime import datetime, timezone
from itertools import product

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..db import (
    get_db,
    create_dataset,
    get_dataset,
    list_datasets,
    delete_dataset,
    get_dataset_scenarios,
    add_scenario_to_dataset,
    remove_scenario_from_dataset,
    list_scenarios,
    get_scenario,
    list_results,
    create_result,
    list_judgements,
)
from ..engine.runner import Runner
from ..models.dataset import Dataset
from ..models.executor import ExecutorSpec
from ..models.result import Result, ResultStatus

router = APIRouter()


class CreateDatasetRequest(BaseModel):
    """Request to create a dataset."""

    name: str
    description: str | None = None


class AddScenarioRequest(BaseModel):
    """Request to add a scenario to a dataset."""

    scenario_id: int


class CreateDatasetRunRequest(BaseModel):
    """Request to create a dataset run."""

    executor_specs: list[str]
    trials: int = 1
    minimal: bool = False
    timeout_seconds: int = 1800
    driver: str = "local"


def run_dataset_executor_task(
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
            runner.run(scenario, executor_spec, timeout_seconds, driver, result_id=result_id)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Run failed")
            from ..db import update_result_status
            update_result_status(db, result_id, ResultStatus.FAILED, finished_at=datetime.now(timezone.utc))


@router.get("")
def list_datasets_endpoint(limit: int | None = None):
    """List datasets."""
    for db in get_db():
        datasets = list_datasets(db, limit=limit)
        datasets_with_scenarios = []
        for dataset in datasets:
            scenarios = get_dataset_scenarios(db, dataset.id)
            datasets_with_scenarios.append(
                {
                    **dataset.model_dump(),
                    "scenario_count": len(scenarios),
                }
            )
        return {"datasets": datasets_with_scenarios}


@router.get("/{dataset_id}")
def get_dataset_endpoint(dataset_id: int):
    """Get dataset with scenarios."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        scenarios = get_dataset_scenarios(db, dataset_id)
        return {
            "dataset": dataset.model_dump(),
            "scenarios": [s.model_dump() for s in scenarios],
        }


@router.post("")
def create_dataset_endpoint(request: CreateDatasetRequest):
    """Create a new dataset."""
    dataset = Dataset(
        id=0,
        name=request.name,
        description=request.description,
        created_at=datetime.now(timezone.utc),
    )
    for db in get_db():
        dataset = create_dataset(db, dataset)
        break
    return dataset.model_dump()


@router.delete("/{dataset_id}")
def delete_dataset_endpoint(dataset_id: int):
    """Delete a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        deleted = delete_dataset(db, dataset_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Dataset not found")
        break
    return {"status": "deleted", "dataset_id": dataset_id}


@router.post("/{dataset_id}/scenarios")
def add_scenario_endpoint(dataset_id: int, request: AddScenarioRequest):
    """Add a scenario to a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        scenario = get_scenario(db, request.scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        add_scenario_to_dataset(db, dataset_id, request.scenario_id)
        break
    return {"status": "added", "dataset_id": dataset_id, "scenario_id": request.scenario_id}


@router.delete("/{dataset_id}/scenarios/{scenario_id}")
def remove_scenario_endpoint(dataset_id: int, scenario_id: int):
    """Remove a scenario from a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        remove_scenario_from_dataset(db, dataset_id, scenario_id)
        break
    return {"status": "removed", "dataset_id": dataset_id, "scenario_id": scenario_id}


@router.post("/{dataset_id}/runs")
def create_dataset_run_endpoint(dataset_id: int, request: CreateDatasetRunRequest, background_tasks: BackgroundTasks):
    """Queue runs for all scenarios in a dataset."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        scenarios = get_dataset_scenarios(db, dataset_id)
        if not scenarios:
            raise HTTPException(status_code=400, detail="Dataset has no scenarios")

        executor_specs = [ExecutorSpec.parse(e) for e in request.executor_specs]

        # Determine which scenario-executor pairs to run
        pairs_to_run = []
        if request.minimal:
            # Only run pairs that don't have completed results
            for scenario in scenarios:
                for executor_spec in executor_specs:
                    executor_spec_str = str(executor_spec)
                    results = list_results(db, scenario_id=scenario.id, executor_spec=executor_spec_str)
                    completed_count = sum(1 for r in results if r.status.value == "completed")
                    if completed_count == 0:
                        pairs_to_run.append((scenario, executor_spec))
        else:
            # Run all combinations with specified number of trials
            for scenario, executor_spec in product(scenarios, executor_specs):
                for _ in range(request.trials):
                    pairs_to_run.append((scenario, executor_spec))

        # Create result records for all pairs
        result_ids = []
        for scenario, executor_spec in pairs_to_run:
            result = Result(
                id=0,
                scenario_id=scenario.id,
                harness=executor_spec.harness,
                provider=executor_spec.provider,
                model=executor_spec.model,
                status=ResultStatus.QUEUED,
                created_at=datetime.now(timezone.utc),
                timeout_seconds=request.timeout_seconds,
                driver=request.driver,
            )
            result = create_result(db, result)
            result_ids.append(result.id)

            # Initialize streaming log
            from ..engine.streaming import StreamingLog
            streaming_log = StreamingLog(result_id=result.id)
            streaming_log.set_status("queued")

            # Queue background task
            background_tasks.add_task(
                run_dataset_executor_task,
                result.id,
                scenario.id,
                str(executor_spec),
                request.timeout_seconds,
                request.driver,
            )

        return {
            "status": "queued",
            "dataset_id": dataset_id,
            "pairs_run": len(pairs_to_run),
            "result_ids": result_ids,
        }


@router.get("/{dataset_id}/analytics")
def get_dataset_analytics_endpoint(dataset_id: int):
    """Get analytics for a dataset showing scenario-executor matrix."""
    for db in get_db():
        dataset = get_dataset(db, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        scenarios = get_dataset_scenarios(db, dataset_id)
        
        # Get all unique executors from results
        all_results = []
        for scenario in scenarios:
            results = list_results(db, scenario_id=scenario.id)
            all_results.extend(results)

        # Build executor set
        executors_set = set()
        for result in all_results:
            executor_key = f"{result.harness}:{result.provider}:{result.model}"
            executors_set.add(executor_key)

        executors_list = sorted(list(executors_set))

        # Build matrix
        matrix = []
        for scenario in scenarios:
            row = {
                "scenario_id": scenario.id,
                "scenario_prompt": scenario.prompt[:100] + "..." if len(scenario.prompt) > 100 else scenario.prompt,
                "cells": {},
            }
            for executor_key in executors_list:
                results = list_results(db, scenario_id=scenario.id, executor_spec=executor_key)
                completed = [r for r in results if r.status.value == "completed"]
                failed = [r for r in results if r.status.value == "failed" or r.status.value == "infra_failure"]
                timeout = [r for r in results if r.status.value == "timeout"]
                running = [r for r in results if r.status.value == "running" and not r.is_stale()]
                queued = [r for r in results if r.status.value == "queued"]
                
                # Determine overall status
                if len(completed) > 0:
                    status = "completed"
                elif len(running) > 0:
                    status = "running"
                elif len(queued) > 0:
                    status = "queued"
                elif len(failed) > 0:
                    status = "failed"
                elif len(timeout) > 0:
                    status = "timeout"
                else:
                    status = "pending"

                # Collect result IDs (prefer completed, then any)
                result_ids = [r.id for r in completed] if completed else [r.id for r in results]
                
                # Calculate quality stats from completed results
                # Use human quality if available, otherwise fall back to latest judgement quality
                quality_scores = []
                for r in completed:
                    if r.quality is not None:
                        # Human quality takes precedence
                        quality_scores.append(r.quality)
                    else:
                        # Check for judgement quality
                        judgements = list_judgements(db, result_id=r.id)
                        if judgements:
                            # Get the latest judgement with a quality score
                            for j in sorted(judgements, key=lambda x: x.created_at, reverse=True):
                                if j.quality is not None:
                                    quality_scores.append(j.quality)
                                    break
                
                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else None
                
                # Calculate avg duration from completed results
                durations = [r.duration_ms for r in completed if r.duration_ms is not None]
                avg_duration_ms = sum(durations) / len(durations) if durations else None
                
                row["cells"][executor_key] = {
                    "status": status,
                    "total": len(results),
                    "completed": len(completed),
                    "failed": len(failed),
                    "timeout": len(timeout),
                    "running": len(running),
                    "queued": len(queued),
                    "result_ids": result_ids,
                    "avg_quality": avg_quality,
                    "quality_count": len(quality_scores),
                    "avg_duration_ms": avg_duration_ms,
                    "duration_count": len(durations),
                }
            matrix.append(row)

        return {
            "dataset": dataset.model_dump(),
            "executors": executors_list,
            "matrix": matrix,
        }

