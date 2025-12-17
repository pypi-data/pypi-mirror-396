"""Tests for models."""

from datetime import datetime

from vibelab.models import CodeType, GitHubCodeRef, Scenario


def test_scenario_creation():
    """Test creating a scenario."""
    code_ref = GitHubCodeRef(owner="test", repo="repo", commit_sha="abc123")
    scenario = Scenario(
        id=1,
        code_type=CodeType.GITHUB,
        code_ref=code_ref,
        prompt="Test prompt",
        created_at=datetime.now(),
    )
    assert scenario.code_type == CodeType.GITHUB
    assert scenario.prompt == "Test prompt"
    assert isinstance(scenario.code_ref, GitHubCodeRef)
