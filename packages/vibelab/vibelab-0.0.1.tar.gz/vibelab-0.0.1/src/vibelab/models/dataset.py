"""Dataset model definitions."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Dataset(BaseModel):
    """A collection of scenarios for evaluation."""

    id: int
    name: str
    description: str | None = None
    created_at: datetime

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_db_dict(cls, data: dict) -> "Dataset":
        """Create from database dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

