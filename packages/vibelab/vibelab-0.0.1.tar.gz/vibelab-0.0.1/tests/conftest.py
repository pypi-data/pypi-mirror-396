"""Pytest configuration."""

import pytest

from vibelab.db.connection import init_db


@pytest.fixture(autouse=True)
def setup_db():
    """Initialize database for tests."""
    init_db()
    yield
