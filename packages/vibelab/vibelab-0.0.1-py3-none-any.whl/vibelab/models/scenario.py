"""Scenario model definitions."""

from datetime import datetime
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


class CodeType(str, Enum):
    """Type of code reference."""

    GITHUB = "github"
    LOCAL = "local"
    EMPTY = "empty"


class GitHubCodeRef(BaseModel):
    """Reference to a GitHub repository."""

    owner: str
    repo: str
    commit_sha: str
    branch: str | None = None


class LocalCodeRef(BaseModel):
    """Reference to a local directory."""

    path: str


class Scenario(BaseModel):
    """A specific task for an LLM agent."""

    id: int
    code_type: CodeType
    code_ref: GitHubCodeRef | LocalCodeRef | None = None
    prompt: str
    created_at: datetime

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "code_type": self.code_type.value,
            "code_ref": self.code_ref.model_dump_json() if self.code_ref else None,
            "prompt": self.prompt,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "Scenario":
        """Create from database dictionary."""
        code_type = CodeType(data["code_type"])
        code_ref = None
        if data["code_ref"]:
            if code_type == CodeType.GITHUB:
                import json

                code_ref = GitHubCodeRef(**json.loads(data["code_ref"]))
            elif code_type == CodeType.LOCAL:
                import json

                code_ref = LocalCodeRef(**json.loads(data["code_ref"]))
        return cls(
            id=data["id"],
            code_type=code_type,
            code_ref=code_ref,
            prompt=data["prompt"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
