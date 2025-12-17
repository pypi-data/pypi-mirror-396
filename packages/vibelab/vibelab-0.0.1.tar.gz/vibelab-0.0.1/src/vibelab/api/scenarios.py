"""Scenario API endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import get_db, create_scenario, get_scenario, list_scenarios, list_results, delete_scenario
from ..db.connection import get_vibelab_home
from ..lib import resolve_github_code_ref
from ..models.result import Result
from ..models.scenario import CodeType, GitHubCodeRef, LocalCodeRef, Scenario

router = APIRouter()


class CreateScenarioRequest(BaseModel):
    """Request to create a scenario."""

    code_type: str
    code_ref: dict | None = None
    prompt: str


@router.get("")
def list_scenarios_endpoint(limit: int | None = None):
    """List scenarios."""
    for db in get_db():
        from ..db import get_latest_llm_scenario_judge
        
        scenarios = list_scenarios(db, limit=limit)
        results_by_scenario = {}
        judges_by_scenario = {}
        
        for scenario in scenarios:
            results = list_results(db, scenario_id=scenario.id)
            results_by_scenario[scenario.id] = [
                {**r.model_dump(), "is_stale": r.is_stale()} for r in results
            ]
            
            # Get latest judge for scenario
            judge = get_latest_llm_scenario_judge(db, scenario.id)
            if judge:
                judges_by_scenario[scenario.id] = {
                    "id": judge.id,
                    "alignment_score": judge.alignment_score,
                }
        
        return {
            "scenarios": [s.model_dump() for s in scenarios],
            "results_by_scenario": {
                str(k): v for k, v in results_by_scenario.items()
            },
            "judges_by_scenario": {
                str(k): v for k, v in judges_by_scenario.items()
            },
        }


@router.get("/{scenario_id}")
def get_scenario_endpoint(scenario_id: int):
    """Get scenario with results."""
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        results = list_results(db, scenario_id=scenario_id)
        return {
            "scenario": scenario.model_dump(),
            "results": [
                {**r.model_dump(), "is_stale": r.is_stale()} for r in results
            ],
        }


@router.post("")
def create_scenario_endpoint(request: CreateScenarioRequest):
    """Create a new scenario."""
    code_type = CodeType(request.code_type)

    code_ref = None
    if request.code_ref:
        if code_type == CodeType.GITHUB:
            code_ref = GitHubCodeRef(**request.code_ref)
            # Resolve branch/tag names to commit SHAs BEFORE searching
            code_ref = resolve_github_code_ref(code_ref)
        elif code_type == CodeType.LOCAL:
            code_ref = LocalCodeRef(**request.code_ref)

    # Find or create scenario (matching on resolved commit SHA)
    scenario_obj = None
    for db in get_db():
        scenarios = list_scenarios(db)
        for s in scenarios:
            if s.code_type == code_type and s.prompt == request.prompt:
                if code_type == CodeType.GITHUB and isinstance(code_ref, GitHubCodeRef):
                    if isinstance(s.code_ref, GitHubCodeRef):
                        # Match on owner, repo, AND commit SHA (after resolution)
                        if (
                            s.code_ref.owner == code_ref.owner
                            and s.code_ref.repo == code_ref.repo
                            and s.code_ref.commit_sha == code_ref.commit_sha
                        ):
                            scenario_obj = s
                            break
                elif code_type == CodeType.LOCAL and isinstance(code_ref, LocalCodeRef):
                    if isinstance(s.code_ref, LocalCodeRef):
                        if s.code_ref.path == code_ref.path:
                            scenario_obj = s
                            break
                elif code_type == CodeType.EMPTY:
                    scenario_obj = s
                    break

        if not scenario_obj:
            scenario_obj = Scenario(
                id=0,
                code_type=code_type,
                code_ref=code_ref,
                prompt=request.prompt,
                created_at=datetime.now(timezone.utc),
            )
            scenario_obj = create_scenario(db, scenario_obj)
        break

    if not scenario_obj:
        raise HTTPException(status_code=500, detail="Failed to create scenario")

    return scenario_obj.model_dump()


@router.delete("/{scenario_id}")
def delete_scenario_endpoint(scenario_id: int):
    """Delete a scenario and all its results (cascade delete)."""
    import shutil
    
    for db in get_db():
        scenario = get_scenario(db, scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Get all results for this scenario to delete their files
        results = list_results(db, scenario_id=scenario_id)
        
        # Delete the scenario (cascade deletes results in DB)
        deleted = delete_scenario(db, scenario_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Delete result files
        home = get_vibelab_home()
        for result in results:
            result_dir = home / "results" / str(result.id)
            if result_dir.exists():
                shutil.rmtree(result_dir)
        
        break
    
    return {"status": "deleted", "scenario_id": scenario_id}


@router.get("/analytics/global")
def get_global_analytics_endpoint():
    """Get analytics for ALL scenarios showing scenario-executor matrix (global report)."""
    from ..db import list_judgements
    
    for db in get_db():
        scenarios = list_scenarios(db)
        
        if not scenarios:
            return {
                "title": "Global Report",
                "description": "All scenarios across the system",
                "executors": [],
                "matrix": [],
            }
        
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
            "title": "Global Report",
            "description": f"All {len(scenarios)} scenarios across the system",
            "scenario_count": len(scenarios),
            "executors": executors_list,
            "matrix": matrix,
        }
