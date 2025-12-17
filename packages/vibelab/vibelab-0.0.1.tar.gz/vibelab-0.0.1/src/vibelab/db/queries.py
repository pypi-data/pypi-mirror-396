"""Database queries."""

import sqlite3
from datetime import datetime
from typing import Any

from ..models.result import Result, ResultStatus
from ..models.scenario import Scenario
from ..models.dataset import Dataset
from ..models.judge import LLMScenarioJudge, Judgement


def create_scenario(conn: sqlite3.Connection, scenario: Scenario) -> Scenario:
    """Create a new scenario."""
    data = scenario.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO scenarios (code_type, code_ref, prompt, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (data["code_type"], data["code_ref"], data["prompt"], data["created_at"]),
    )
    conn.commit()
    return Scenario.from_db_dict(
        {
            "id": cursor.lastrowid,
            "code_type": data["code_type"],
            "code_ref": data["code_ref"],
            "prompt": data["prompt"],
            "created_at": data["created_at"],
        }
    )


def get_scenario(conn: sqlite3.Connection, scenario_id: int) -> Scenario | None:
    """Get scenario by ID."""
    cursor = conn.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Scenario.from_db_dict(dict(row))


def list_scenarios(conn: sqlite3.Connection, limit: int | None = None) -> list[Scenario]:
    """List scenarios."""
    query = "SELECT * FROM scenarios ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {limit}"
    cursor = conn.execute(query)
    return [Scenario.from_db_dict(dict(row)) for row in cursor.fetchall()]


def create_result(conn: sqlite3.Connection, result: Result) -> Result:
    """Create a new result."""
    data = result.to_db_dict()
    # Set updated_at to created_at on creation
    data["updated_at"] = data["created_at"]
    cursor = conn.execute(
        """
        INSERT INTO results (
            scenario_id, harness, provider, model, status, created_at, updated_at,
            started_at, finished_at, duration_ms, lines_added, lines_removed,
            files_changed, tokens_used, cost_usd, harness_metrics, annotations,
            timeout_seconds, driver, error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["scenario_id"],
            data["harness"],
            data["provider"],
            data["model"],
            data["status"],
            data["created_at"],
            data["updated_at"],
            data["started_at"],
            data["finished_at"],
            data["duration_ms"],
            data["lines_added"],
            data["lines_removed"],
            data["files_changed"],
            data["tokens_used"],
            data["cost_usd"],
            data["harness_metrics"],
            data["annotations"],
            data["timeout_seconds"],
            data["driver"],
            data["error_message"],
        ),
    )
    conn.commit()
    return Result.from_db_dict({**data, "id": cursor.lastrowid})


def get_result(conn: sqlite3.Connection, result_id: int) -> Result | None:
    """Get result by ID."""
    cursor = conn.execute("SELECT * FROM results WHERE id = ?", (result_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Result.from_db_dict(dict(row))


def list_results(
    conn: sqlite3.Connection,
    scenario_id: int | None = None,
    executor_spec: str | None = None,
    status: ResultStatus | None = None,
) -> list[Result]:
    """List results with optional filtering."""
    query = "SELECT * FROM results WHERE 1=1"
    params: list[Any] = []

    if scenario_id:
        query += " AND scenario_id = ?"
        params.append(scenario_id)

    if executor_spec:
        parts = executor_spec.split(":")
        if len(parts) >= 1:
            query += " AND harness = ?"
            params.append(parts[0])
        if len(parts) >= 2:
            query += " AND provider = ?"
            params.append(parts[1])
        if len(parts) >= 3:
            query += " AND model = ?"
            params.append(parts[2])

    if status:
        query += " AND status = ?"
        params.append(status.value)

    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    return [Result.from_db_dict(dict(row)) for row in cursor.fetchall()]


def update_result_status(
    conn: sqlite3.Connection,
    result_id: int,
    status: ResultStatus,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    duration_ms: int | None = None,
    error_message: str | None = None,
) -> None:
    """Update result status and timing."""
    updates = ["status = ?", "updated_at = ?"]
    params: list[Any] = [status.value, datetime.now().isoformat()]

    if started_at:
        updates.append("started_at = ?")
        params.append(started_at.isoformat())

    if finished_at:
        updates.append("finished_at = ?")
        params.append(finished_at.isoformat())

    if duration_ms is not None:
        updates.append("duration_ms = ?")
        params.append(duration_ms)

    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def update_result_metrics(
    conn: sqlite3.Connection,
    result_id: int,
    lines_added: int | None = None,
    lines_removed: int | None = None,
    files_changed: int | None = None,
    tokens_used: int | None = None,
    cost_usd: float | None = None,
) -> None:
    """Update result metrics."""
    updates = ["updated_at = ?"]
    params: list[Any] = [datetime.now().isoformat()]

    if lines_added is not None:
        updates.append("lines_added = ?")
        params.append(lines_added)

    if lines_removed is not None:
        updates.append("lines_removed = ?")
        params.append(lines_removed)

    if files_changed is not None:
        updates.append("files_changed = ?")
        params.append(files_changed)

    if tokens_used is not None:
        updates.append("tokens_used = ?")
        params.append(tokens_used)

    if cost_usd is not None:
        updates.append("cost_usd = ?")
        params.append(cost_usd)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def update_result_annotations(conn: sqlite3.Connection, result_id: int, annotations: dict[str, Any]) -> None:
    """Update result annotations."""
    import json

    conn.execute(
        "UPDATE results SET annotations = ? WHERE id = ?",
        (json.dumps(annotations), result_id),
    )
    conn.commit()


def update_result_notes(conn: sqlite3.Connection, result_id: int, notes: str | None) -> None:
    """Update result notes."""
    conn.execute(
        "UPDATE results SET notes = ?, updated_at = ? WHERE id = ?",
        (notes, datetime.now().isoformat(), result_id),
    )
    conn.commit()


def update_result_quality(conn: sqlite3.Connection, result_id: int, quality: int | None) -> None:
    """Update result quality score."""
    conn.execute(
        "UPDATE results SET quality = ?, updated_at = ? WHERE id = ?",
        (quality, datetime.now().isoformat(), result_id),
    )
    conn.commit()


def update_result_notes_and_quality(
    conn: sqlite3.Connection, result_id: int, notes: str | None = None, quality: int | None = None
) -> None:
    """Update result notes and/or quality score."""
    updates = ["updated_at = ?"]
    params: list[Any] = [datetime.now().isoformat()]

    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)

    if quality is not None:
        updates.append("quality = ?")
        params.append(quality)

    params.append(result_id)
    conn.execute(
        f"UPDATE results SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    conn.commit()


def delete_result(conn: sqlite3.Connection, result_id: int) -> bool:
    """Delete a result by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM results WHERE id = ?", (result_id,))
    conn.commit()
    return cursor.rowcount > 0


def delete_scenario(conn: sqlite3.Connection, scenario_id: int) -> bool:
    """Delete a scenario and all its results (cascade delete). Returns True if deleted, False if not found."""
    # First delete all results for this scenario
    conn.execute("DELETE FROM results WHERE scenario_id = ?", (scenario_id,))
    # Then delete the scenario
    cursor = conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
    conn.commit()
    return cursor.rowcount > 0


# Dataset functions
def create_dataset(conn: sqlite3.Connection, dataset: Dataset) -> Dataset:
    """Create a new dataset."""
    data = dataset.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO datasets (name, description, created_at)
        VALUES (?, ?, ?)
        """,
        (data["name"], data["description"], data["created_at"]),
    )
    conn.commit()
    return Dataset.from_db_dict(
        {
            "id": cursor.lastrowid,
            "name": data["name"],
            "description": data["description"],
            "created_at": data["created_at"],
        }
    )


def get_dataset(conn: sqlite3.Connection, dataset_id: int) -> Dataset | None:
    """Get dataset by ID."""
    cursor = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Dataset.from_db_dict(dict(row))


def list_datasets(conn: sqlite3.Connection, limit: int | None = None) -> list[Dataset]:
    """List datasets."""
    query = "SELECT * FROM datasets ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {limit}"
    cursor = conn.execute(query)
    return [Dataset.from_db_dict(dict(row)) for row in cursor.fetchall()]


def delete_dataset(conn: sqlite3.Connection, dataset_id: int) -> bool:
    """Delete a dataset. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
    conn.commit()
    return cursor.rowcount > 0


def get_dataset_scenarios(conn: sqlite3.Connection, dataset_id: int) -> list[Scenario]:
    """Get all scenarios in a dataset."""
    cursor = conn.execute(
        """
        SELECT s.* FROM scenarios s
        INNER JOIN dataset_scenarios ds ON s.id = ds.scenario_id
        WHERE ds.dataset_id = ?
        ORDER BY s.created_at DESC
        """,
        (dataset_id,),
    )
    return [Scenario.from_db_dict(dict(row)) for row in cursor.fetchall()]


def add_scenario_to_dataset(conn: sqlite3.Connection, dataset_id: int, scenario_id: int) -> None:
    """Add a scenario to a dataset."""
    conn.execute(
        """
        INSERT OR IGNORE INTO dataset_scenarios (dataset_id, scenario_id)
        VALUES (?, ?)
        """,
        (dataset_id, scenario_id),
    )
    conn.commit()


def remove_scenario_from_dataset(conn: sqlite3.Connection, dataset_id: int, scenario_id: int) -> None:
    """Remove a scenario from a dataset."""
    conn.execute(
        """
        DELETE FROM dataset_scenarios
        WHERE dataset_id = ? AND scenario_id = ?
        """,
        (dataset_id, scenario_id),
    )
    conn.commit()


# LLM Judge functions
def create_llm_scenario_judge(conn: sqlite3.Connection, judge: LLMScenarioJudge) -> LLMScenarioJudge:
    """Create a new LLM scenario judge."""
    data = judge.to_db_dict()
    cursor = conn.execute(
        """
        INSERT INTO llm_scenario_judges (scenario_id, guidance, training_sample_ids, test_sample_ids, alignment_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            data["scenario_id"],
            data["guidance"],
            data["training_sample_ids"],
            data["test_sample_ids"],
            data["alignment_score"],
            data["created_at"],
        ),
    )
    conn.commit()
    return LLMScenarioJudge.from_db_dict({**data, "id": cursor.lastrowid})


def get_llm_scenario_judge(conn: sqlite3.Connection, judge_id: int) -> LLMScenarioJudge | None:
    """Get LLM scenario judge by ID."""
    cursor = conn.execute("SELECT * FROM llm_scenario_judges WHERE id = ?", (judge_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return LLMScenarioJudge.from_db_dict(dict(row))


def list_llm_scenario_judges(conn: sqlite3.Connection, scenario_id: int | None = None) -> list[LLMScenarioJudge]:
    """List LLM scenario judges, optionally filtered by scenario."""
    if scenario_id:
        cursor = conn.execute(
            "SELECT * FROM llm_scenario_judges WHERE scenario_id = ? ORDER BY created_at DESC",
            (scenario_id,),
        )
    else:
        cursor = conn.execute("SELECT * FROM llm_scenario_judges ORDER BY created_at DESC")
    return [LLMScenarioJudge.from_db_dict(dict(row)) for row in cursor.fetchall()]


def get_latest_llm_scenario_judge(conn: sqlite3.Connection, scenario_id: int) -> LLMScenarioJudge | None:
    """Get the latest LLM scenario judge for a scenario."""
    cursor = conn.execute(
        "SELECT * FROM llm_scenario_judges WHERE scenario_id = ? ORDER BY created_at DESC LIMIT 1",
        (scenario_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return LLMScenarioJudge.from_db_dict(dict(row))


def update_llm_scenario_judge_alignment(conn: sqlite3.Connection, judge_id: int, alignment_score: float) -> None:
    """Update the alignment score for an LLM scenario judge."""
    conn.execute(
        "UPDATE llm_scenario_judges SET alignment_score = ? WHERE id = ?",
        (alignment_score, judge_id),
    )
    conn.commit()


def delete_llm_scenario_judge(conn: sqlite3.Connection, judge_id: int) -> bool:
    """Delete an LLM scenario judge by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM llm_scenario_judges WHERE id = ?", (judge_id,))
    conn.commit()
    return cursor.rowcount > 0


def create_judgement(conn: sqlite3.Connection, judgement: Judgement) -> Judgement:
    """Create a new judgement."""
    data = judgement.to_db_dict()
    cursor = conn.execute(
        """
        INSERT OR REPLACE INTO judgements (result_id, judge_id, notes, quality, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data["result_id"],
            data["judge_id"],
            data["notes"],
            data["quality"],
            data["created_at"],
        ),
    )
    conn.commit()
    return Judgement.from_db_dict({**data, "id": cursor.lastrowid})


def get_judgement(conn: sqlite3.Connection, judgement_id: int) -> Judgement | None:
    """Get judgement by ID."""
    cursor = conn.execute("SELECT * FROM judgements WHERE id = ?", (judgement_id,))
    row = cursor.fetchone()
    if not row:
        return None
    return Judgement.from_db_dict(dict(row))


def get_judgement_for_result(conn: sqlite3.Connection, result_id: int, judge_id: int) -> Judgement | None:
    """Get judgement for a specific result and judge."""
    cursor = conn.execute(
        "SELECT * FROM judgements WHERE result_id = ? AND judge_id = ?",
        (result_id, judge_id),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return Judgement.from_db_dict(dict(row))


def list_judgements(conn: sqlite3.Connection, result_id: int | None = None, judge_id: int | None = None) -> list[Judgement]:
    """List judgements with optional filtering."""
    query = "SELECT * FROM judgements WHERE 1=1"
    params: list[Any] = []

    if result_id:
        query += " AND result_id = ?"
        params.append(result_id)

    if judge_id:
        query += " AND judge_id = ?"
        params.append(judge_id)

    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, params)
    return [Judgement.from_db_dict(dict(row)) for row in cursor.fetchall()]


def delete_judgement(conn: sqlite3.Connection, judgement_id: int) -> bool:
    """Delete a judgement by ID. Returns True if deleted, False if not found."""
    cursor = conn.execute("DELETE FROM judgements WHERE id = ?", (judgement_id,))
    conn.commit()
    return cursor.rowcount > 0
