"""Integration tests for Claude Code harness."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibelab.harnesses.claude_code import ClaudeCodeHarness


class TestClaudeCodeHarness:
    """Tests for Claude Code harness."""

    def test_check_available_when_claude_not_found(self):
        """Test check_available when claude CLI is not found."""
        harness = ClaudeCodeHarness()
        with patch("shutil.which", return_value=None):
            available, error = harness.check_available()
            assert available is False
            assert "Claude Code CLI not found" in error

    def test_check_available_when_claude_found(self):
        """Test check_available when claude CLI is found."""
        harness = ClaudeCodeHarness()
        with patch("shutil.which", return_value="/usr/local/bin/claude"):
            available, error = harness.check_available()
            assert available is True
            assert error is None

    def test_get_models_for_anthropic(self):
        """Test get_models for anthropic provider."""
        harness = ClaudeCodeHarness()
        models = harness.get_models("anthropic")
        assert len(models) == 3
        model_ids = [m.id for m in models]
        assert "opus" in model_ids
        assert "sonnet" in model_ids
        assert "haiku" in model_ids

    def test_get_models_for_other_provider(self):
        """Test get_models for non-anthropic provider."""
        harness = ClaudeCodeHarness()
        models = harness.get_models("openai")
        assert len(models) == 0

    def test_run_command_construction(self):
        """Test that run constructs the correct command with --verbose."""
        harness = ClaudeCodeHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "anthropic"
        model = "opus"
        timeout = 60

        with patch("subprocess.run") as mock_run:
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
            assert cmd[0] == "claude"
            assert "--print" in cmd
            assert "--verbose" in cmd
            assert "--dangerously-skip-permissions" in cmd  # Skip permission prompts
            assert "--output-format" in cmd
            assert "stream-json" in cmd
            assert "--model" in cmd
            assert model in cmd
            assert "-p" in cmd
            assert prompt in cmd

            # Verify workdir was set correctly
            assert call_args[1]["cwd"] == workdir
            assert call_args[1]["timeout"] == timeout

    def test_run_handles_timeout(self):
        """Test that run handles timeout correctly."""
        harness = ClaudeCodeHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "anthropic"
        model = "opus"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("claude", timeout)

            output = harness.run(workdir, prompt, provider, model, timeout)

            assert output.exit_code == 124
            assert output.stdout == ""
            assert "timed out" in output.stderr.lower()

    def test_run_captures_output(self):
        """Test that run captures stdout and stderr correctly."""
        harness = ClaudeCodeHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "anthropic"
        model = "opus"
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

