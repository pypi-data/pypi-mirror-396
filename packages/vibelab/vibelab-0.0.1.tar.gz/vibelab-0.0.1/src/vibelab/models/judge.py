"""Judge model definitions."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LLMScenarioJudge(BaseModel):
    """An LLM judge trained for a specific scenario."""

    id: int
    scenario_id: int
    guidance: str
    training_sample_ids: list[int] = Field(default_factory=list)
    test_sample_ids: list[int] = Field(default_factory=list)
    alignment_score: float | None = None
    created_at: datetime

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        import json

        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "guidance": self.guidance,
            "training_sample_ids": json.dumps(self.training_sample_ids),
            "test_sample_ids": json.dumps(self.test_sample_ids),
            "alignment_score": self.alignment_score,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "LLMScenarioJudge":
        """Create from database dictionary."""
        import json

        return cls(
            id=data["id"],
            scenario_id=data["scenario_id"],
            guidance=data["guidance"],
            training_sample_ids=json.loads(data["training_sample_ids"]) if data.get("training_sample_ids") else [],
            test_sample_ids=json.loads(data["test_sample_ids"]) if data.get("test_sample_ids") else [],
            alignment_score=data.get("alignment_score"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


class Judgement(BaseModel):
    """A judgement made by an LLM judge on a result."""

    id: int
    result_id: int
    judge_id: int
    notes: str | None = None
    quality: int | None = Field(None, ge=1, le=4, description="Quality score: 4=Perfect, 3=Good, 2=Workable, 1=Bad")
    created_at: datetime

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "result_id": self.result_id,
            "judge_id": self.judge_id,
            "notes": self.notes,
            "quality": self.quality,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "Judgement":
        """Create from database dictionary."""
        return cls(
            id=data["id"],
            result_id=data["result_id"],
            judge_id=data["judge_id"],
            notes=data.get("notes"),
            quality=data.get("quality"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

