"""Integration tests for OpenAI Codex harness."""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from vibelab.harnesses.openai_codex import OpenAICodexHarness


class TestOpenAICodexHarness(unittest.TestCase):
    """Tests for OpenAI Codex harness."""

    def test_check_available(self):
        """Test check_available method."""
        harness = OpenAICodexHarness()
        available, error = harness.check_available()
        # This will depend on whether codex is installed
        assert isinstance(available, bool)
        if not available:
            assert error is not None

    def test_get_models(self):
        """Test get_models returns correct models."""
        harness = OpenAICodexHarness()
        models = harness.get_models("openai")
        assert len(models) == 3
        model_ids = [m.id for m in models]
        assert "gpt-4o" in model_ids
        assert "o3" in model_ids
        assert "o4-mini" in model_ids

    def test_get_models_for_other_provider(self):
        """Test get_models returns empty list for other providers."""
        harness = OpenAICodexHarness()
        models = harness.get_models("anthropic")
        assert len(models) == 0

    def test_run_command_construction(self):
        """Test that run constructs the correct command without invalid flags."""
        harness = OpenAICodexHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "openai"
        model = "gpt-4o"
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
            assert cmd[0] == "codex"
            # CRITICAL: Verify that 'exec' subcommand is used for non-interactive mode
            # This prevents "stdout is not a terminal" error
            assert cmd[1] == "exec", "Must use 'exec' subcommand for non-interactive mode"
            # CRITICAL: Verify that --sandbox workspace-write is included
            # This allows file modifications in the isolated worktree
            assert "--sandbox" in cmd, "Must include --sandbox flag to allow file modifications"
            assert "workspace-write" in cmd, "Must use workspace-write sandbox mode to allow file modifications"
            assert "--model" in cmd
            assert model in cmd
            
            # CRITICAL: Verify that --approval-mode is NOT in the command
            # This flag doesn't exist and causes the error
            assert "--approval-mode" not in cmd, "The --approval-mode flag is invalid and should not be used"
            assert "full-auto" not in cmd, "The --approval-mode full-auto flag is invalid and should not be used"
            
            # Verify prompt is included
            assert prompt in cmd

            # Verify workdir was set correctly
            assert call_args[1]["cwd"] == workdir
            assert call_args[1]["timeout"] == timeout

    def test_run_handles_non_interactive_mode(self):
        """Test that run uses 'exec' subcommand to avoid 'stdout is not a terminal' error."""
        harness = OpenAICodexHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "openai"
        model = "gpt-4o"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "test output"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            output = harness.run(workdir, prompt, provider, model, timeout)

            # Verify subprocess.run was called
            assert mock_run.called

            # Get the call arguments
            call_args = mock_run.call_args
            cmd = call_args[0][0]

            # CRITICAL: Verify that 'exec' subcommand is used
            # This is the non-interactive mode that prevents "stdout is not a terminal" error
            assert cmd[0] == "codex"
            assert cmd[1] == "exec", "Must use 'exec' subcommand for non-interactive mode"
            # CRITICAL: Verify that --sandbox workspace-write is included
            # This allows file modifications in the isolated worktree
            assert "--sandbox" in cmd, "Must include --sandbox flag to allow file modifications"
            assert "workspace-write" in cmd, "Must use workspace-write sandbox mode to allow file modifications"
            
            # Verify that capture_output is True (non-interactive)
            assert call_args[1]["capture_output"] is True

    def test_run_handles_timeout(self):
        """Test that run handles timeout correctly."""
        harness = OpenAICodexHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "openai"
        model = "gpt-4o"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("codex", timeout)
            result = harness.run(workdir, prompt, provider, model, timeout)
            assert result.exit_code == 124
            assert result.stderr == "Command timed out"

    def test_run_captures_output(self):
        """Test that run captures stdout and stderr correctly."""
        harness = OpenAICodexHarness()
        workdir = Path("/tmp/test")
        prompt = "test prompt"
        provider = "openai"
        model = "gpt-4o"
        timeout = 60

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "test stdout"
            mock_result.stderr = "test stderr"
            mock_run.return_value = mock_result

            result = harness.run(workdir, prompt, provider, model, timeout)
            assert result.exit_code == 0
            assert result.stdout == "test stdout"
            assert result.stderr == "test stderr"

