"""Result model definitions."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResultStatus(str, Enum):
    """Status of a result execution."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    INFRA_FAILURE = "infra_failure"


class Annotations(BaseModel):
    """User-added annotations for a result."""

    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: int | None = Field(None, ge=1, le=5)
    passed: bool | None = None


class Result(BaseModel):
    """Output of running an executor on a scenario."""

    id: int
    scenario_id: int
    harness: str
    provider: str
    model: str
    status: ResultStatus
    created_at: datetime
    updated_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = None
    lines_added: int | None = None
    lines_removed: int | None = None
    files_changed: int | None = None
    tokens_used: int | None = None
    cost_usd: float | None = None
    harness_metrics: dict[str, Any] | None = None
    annotations: Annotations | None = None
    timeout_seconds: int | None = None
    driver: str = "local"
    error_message: str | None = None
    notes: str | None = None
    quality: int | None = Field(None, ge=1, le=4, description="Quality score: 4=Perfect, 3=Good, 2=Workable, 1=Bad")

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        import json

        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "harness": self.harness,
            "provider": self.provider,
            "model": self.model,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_ms": self.duration_ms,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "files_changed": self.files_changed,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "harness_metrics": json.dumps(self.harness_metrics) if self.harness_metrics else None,
            "annotations": json.dumps(self.annotations.model_dump()) if self.annotations else None,
            "timeout_seconds": self.timeout_seconds,
            "driver": self.driver,
            "error_message": self.error_message,
            "notes": self.notes,
            "quality": self.quality,
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "Result":
        """Create from database dictionary."""
        import json

        annotations = None
        if data["annotations"]:
            annotations = Annotations(**json.loads(data["annotations"]))

        harness_metrics = None
        if data["harness_metrics"]:
            harness_metrics = json.loads(data["harness_metrics"])

        return cls(
            id=data["id"],
            scenario_id=data["scenario_id"],
            harness=data["harness"],
            provider=data["provider"],
            model=data["model"],
            status=ResultStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            started_at=datetime.fromisoformat(data["started_at"]) if data["started_at"] else None,
            finished_at=datetime.fromisoformat(data["finished_at"]) if data["finished_at"] else None,
            duration_ms=data["duration_ms"],
            lines_added=data["lines_added"],
            lines_removed=data["lines_removed"],
            files_changed=data["files_changed"],
            tokens_used=data["tokens_used"],
            cost_usd=data["cost_usd"],
            harness_metrics=harness_metrics,
            annotations=annotations,
            timeout_seconds=data.get("timeout_seconds"),
            driver=data.get("driver", "local"),
            error_message=data.get("error_message"),
            notes=data.get("notes"),
            quality=data.get("quality"),
        )

    def is_stale(self) -> bool:
        """Check if this result is stale (running but past timeout)."""
        if self.status != ResultStatus.RUNNING:
            return False
        if not self.started_at or not self.timeout_seconds:
            return False
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if self.started_at.tzinfo is None:
            # Assume naive datetime is UTC
            started = self.started_at.replace(tzinfo=timezone.utc)
        else:
            started = self.started_at
        
        elapsed = (now - started).total_seconds()
        return elapsed > self.timeout_seconds
