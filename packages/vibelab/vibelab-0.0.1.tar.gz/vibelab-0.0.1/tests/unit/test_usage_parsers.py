"""Unit tests for usage parsers."""

import unittest

from vibelab.harnesses.usage import (
    parse_claude_code_usage,
    parse_openai_codex_usage,
    parse_cursor_usage,
)


class TestUsageParsers(unittest.TestCase):
    """Tests for usage parsing functions."""

    def test_parse_claude_code_usage_jsonl(self):
        """Test parsing Claude Code usage from JSONL output."""
        stdout = """
{"type": "message", "content": "Hello"}
{"type": "usage", "usage": {"input_tokens": 100, "output_tokens": 50}}
"""
        result = parse_claude_code_usage(stdout, "")
        self.assertIsNotNone(result)
        self.assertEqual(result["input_tokens"], 100)
        self.assertEqual(result["output_tokens"], 50)
        self.assertEqual(result["total_tokens"], 150)

    def test_parse_claude_code_usage_direct_fields(self):
        """Test parsing Claude Code usage with direct fields."""
        stdout = """
{"input_tokens": 200, "output_tokens": 100, "total_tokens": 300}
"""
        result = parse_claude_code_usage(stdout, "")
        self.assertIsNotNone(result)
        self.assertEqual(result["input_tokens"], 200)
        self.assertEqual(result["output_tokens"], 100)
        self.assertEqual(result["total_tokens"], 300)

    def test_parse_claude_code_usage_stderr(self):
        """Test parsing Claude Code usage from stderr."""
        stderr = "Tokens used: 500"
        result = parse_claude_code_usage("", stderr)
        self.assertIsNotNone(result)
        self.assertEqual(result["total_tokens"], 500)

    def test_parse_openai_codex_usage(self):
        """Test parsing OpenAI Codex usage."""
        stdout = """
{"usage": {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225}}
"""
        result = parse_openai_codex_usage(stdout, "")
        self.assertIsNotNone(result)
        self.assertEqual(result["input_tokens"], 150)
        self.assertEqual(result["output_tokens"], 75)
        self.assertEqual(result["total_tokens"], 225)

    def test_parse_cursor_usage(self):
        """Test parsing Cursor usage (uses same parser as Claude Code)."""
        stdout = """
{"type": "usage", "usage": {"input_tokens": 300, "output_tokens": 150}}
"""
        result = parse_cursor_usage(stdout, "")
        self.assertIsNotNone(result)
        self.assertEqual(result["input_tokens"], 300)
        self.assertEqual(result["output_tokens"], 150)

    def test_parse_no_usage(self):
        """Test parsing when no usage information is present."""
        stdout = "Some regular output without usage data"
        result = parse_claude_code_usage(stdout, "")
        self.assertIsNone(result)

