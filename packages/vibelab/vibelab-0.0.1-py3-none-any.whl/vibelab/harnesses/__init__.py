"""Agent harnesses for VibeLab."""

from .base import Harness, HarnessOutput, ModelInfo
from .claude_code import ClaudeCodeHarness
from .cursor import CursorHarness
from .gemini import GeminiHarness
from .openai_codex import OpenAICodexHarness

HARNESSES: dict[str, Harness] = {
    "claude-code": ClaudeCodeHarness(),
    "openai-codex": OpenAICodexHarness(),
    "cursor": CursorHarness(),
    "gemini": GeminiHarness(),
}

__all__ = ["Harness", "HarnessOutput", "ModelInfo", "ClaudeCodeHarness", "OpenAICodexHarness", "CursorHarness", "GeminiHarness", "HARNESSES"]
