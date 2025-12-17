"""Integration tests for Cursor harness validation."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibelab.harnesses.cursor import CursorHarness


class TestCursorHarnessValidation:
    """Tests for Cursor harness model validation."""

    def test_model_name_matches_available_models(self):
        """Test that the model name we expose matches what cursor-agent expects."""
        harness = CursorHarness()
        models = harness.get_models("cursor")
        
        # Verify we expose composer-1 (not composer)
        assert len(models) > 0
        model_ids = [m.id for m in models]
        assert "composer-1" in model_ids
        assert "composer" not in model_ids  # Should not expose the wrong name

    def test_run_with_invalid_model_should_fail_gracefully(self):
        """Test that using an invalid model name results in proper error handling."""
        harness = CursorHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "cursor"
        invalid_model = "composer"  # Wrong model name
        timeout = 60

        with patch("subprocess.run") as mock_run:
            # Simulate cursor-agent returning an error about invalid model
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Cannot use this model: composer. Available models: composer-1, ..."
            mock_run.return_value = mock_result

            output = harness.run(workdir, prompt, provider, invalid_model, timeout)

            # Should capture the error
            assert output.exit_code == 1
            assert "Cannot use this model" in output.stderr or "composer" in output.stderr

    def test_run_with_valid_model_should_succeed(self):
        """Test that using the correct model name (composer-1) works."""
        harness = CursorHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "cursor"
        valid_model = "composer-1"  # Correct model name
        timeout = 60

        with patch("subprocess.run") as mock_run, patch.dict("os.environ", {"CURSOR_API_KEY": "test-key"}):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            output = harness.run(workdir, prompt, provider, valid_model, timeout)

            # Verify command includes correct model name
            call_args = mock_run.call_args
            cmd = call_args[0][0]
            
            # Find --model flag and verify the model name
            model_index = cmd.index("--model")
            assert cmd[model_index + 1] == "composer-1"
            
            assert output.exit_code == 0

