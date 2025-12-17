"""Hello world integration test using a small public repo."""

import pytest
from datetime import datetime

from vibelab.engine.runner import Runner
from vibelab.models.executor import ExecutorSpec
from vibelab.models.scenario import CodeType, GitHubCodeRef, Scenario


@pytest.mark.integration
def test_hello_world_scenario():
    """
    Simple hello world test using GitHub's official Hello-World repo.
    
    This is a minimal test that:
    1. Uses a tiny public repo (octocat/Hello-World)
    2. Runs a simple prompt
    3. Verifies the execution completes
    
    Run with: pytest tests/integration/test_hello_world.py -v
    """
    # Use GitHub's official Hello-World repo - it's tiny and fast to clone
    scenario = Scenario(
        id=0,
        code_type=CodeType.GITHUB,
        code_ref=GitHubCodeRef(
            owner="octocat",
            repo="Hello-World",
            commit_sha="master",  # Use master branch
        ),
        prompt="Add a comment to the README saying 'Hello from VibeLab!'",
        created_at=datetime.now(),
    )
    
    # Use haiku model (fastest/cheapest) for testing
    executor_spec = ExecutorSpec.parse("claude-code:anthropic:haiku")
    
    runner = Runner()
    
    # Run with short timeout for testing
    result = runner.run(scenario, executor_spec, timeout_seconds=300, driver_id="local")
    
    # Verify result was created
    assert result is not None
    assert result.scenario_id == scenario.id
    assert result.harness == "claude-code"
    assert result.provider == "anthropic"
    assert result.model == "haiku"
    
    # Note: We don't assert on status since it depends on whether claude CLI is available
    # This test is meant to be run manually when the CLI is set up

