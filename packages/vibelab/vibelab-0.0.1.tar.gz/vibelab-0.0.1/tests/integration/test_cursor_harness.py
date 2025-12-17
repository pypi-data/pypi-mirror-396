"""Integration tests for Cursor harness."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibelab.harnesses.cursor import CursorHarness


class TestCursorHarness:
    """Tests for Cursor harness."""

    def test_check_available_when_cursor_not_found(self):
        """Test check_available when cursor-agent CLI is not found."""
        harness = CursorHarness()
        with patch("shutil.which", return_value=None):
            available, error = harness.check_available()
            assert available is False
            assert "Cursor CLI not found" in error

    def test_check_available_when_cursor_found(self):
        """Test check_available when cursor-agent CLI is found."""
        harness = CursorHarness()
        with patch("shutil.which", return_value="/usr/local/bin/cursor-agent"):
            available, error = harness.check_available()
            assert available is True
            assert error is None

    def test_get_models_for_cursor(self):
        """Test get_models for cursor provider."""
        harness = CursorHarness()
        models = harness.get_models("cursor")
        assert len(models) == 1
        assert models[0].id == "composer-1"
        assert models[0].name == "Composer"

    def test_get_models_for_other_provider(self):
        """Test get_models for non-cursor provider."""
        harness = CursorHarness()
        models = harness.get_models("anthropic")
        assert len(models) == 0

    def test_run_command_construction(self):
        """Test that run constructs the correct command."""
        harness = CursorHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "cursor"
        model = "composer-1"
        timeout = 60

        with patch("subprocess.run") as mock_run, patch.dict("os.environ", {"CURSOR_API_KEY": "test-key"}):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            harness.run(workdir, prompt, provider, model, timeout)

            # Verify subprocess.run was called
            assert mock_run.called

            # Get the command that was called
            call_args = mock_run.call_args
            cmd = call_args[0][0]

            # Verify command structure
            assert cmd[0] == "cursor-agent"
            assert "--print" in cmd
            assert "--output-format" in cmd
            assert "stream-json" in cmd
            assert "--force" in cmd
            assert "--api-key" in cmd
            assert "test-key" in cmd
            assert "--model" in cmd
            assert model in cmd
            assert prompt in cmd

            # Verify workdir was set correctly
            assert call_args[1]["cwd"] == workdir
            assert call_args[1]["timeout"] == timeout
            # Verify environment includes API key
            assert call_args[1]["env"]["CURSOR_API_KEY"] == "test-key"

    def test_run_handles_timeout(self):
        """Test that run handles timeout correctly."""
        harness = CursorHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "cursor"
        model = "composer-1"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cursor-agent", timeout)

            output = harness.run(workdir, prompt, provider, model, timeout)

            assert output.exit_code == 124
            assert output.stdout == ""
            assert "timed out" in output.stderr.lower()

    def test_run_captures_output(self):
        """Test that run captures stdout and stderr correctly."""
        harness = CursorHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "cursor"
        model = "composer-1"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "stdout content"
            mock_result.stderr = "stderr content"
            mock_run.return_value = mock_result

            output = harness.run(workdir, prompt, provider, model, timeout)

            assert output.exit_code == 0
            assert output.stdout == "stdout content"
            assert output.stderr == "stderr content"

