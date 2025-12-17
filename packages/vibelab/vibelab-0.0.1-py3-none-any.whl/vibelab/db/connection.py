"""Database connection and initialization."""

import os
import sqlite3
from pathlib import Path
from typing import Generator

from .migrations import migrate


def get_vibelab_home() -> Path:
    """Get VibeLab home directory."""
    home = os.environ.get("VIBELAB_HOME")
    if home:
        return Path(home).expanduser()
    return Path.home() / ".vibelab"


def get_db_path() -> Path:
    """Get database file path."""
    home = get_vibelab_home()
    home.mkdir(parents=True, exist_ok=True)
    return home / "data.db"


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with schema and migrations."""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        migrate(conn)
        conn.commit()
    finally:
        conn.close()
