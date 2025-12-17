"""Utilities for extracting token usage and cost from harness output."""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def parse_claude_code_usage(stdout: str, stderr: str) -> dict[str, Any] | None:
    """
    Parse token usage from Claude Code CLI output.
    
    Claude Code uses --output-format stream-json which outputs JSONL.
    Look for usage metadata in the JSON lines.
    """
    usage_data = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    
    # Parse JSONL output
    for line in stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        try:
            data = json.loads(line)
            
            # Look for usage fields in various possible formats
            if "usage" in data:
                usage = data["usage"]
                if isinstance(usage, dict):
                    usage_data["input_tokens"] = usage.get("input_tokens") or usage.get("prompt_tokens")
                    usage_data["output_tokens"] = usage.get("output_tokens") or usage.get("completion_tokens")
                    if usage_data["input_tokens"] and usage_data["output_tokens"]:
                        usage_data["total_tokens"] = usage_data["input_tokens"] + usage_data["output_tokens"]
            
            # Also check for direct fields
            if "input_tokens" in data:
                usage_data["input_tokens"] = data["input_tokens"]
            if "output_tokens" in data:
                usage_data["output_tokens"] = data["output_tokens"]
            if "total_tokens" in data:
                usage_data["total_tokens"] = data["total_tokens"]
            
        except json.JSONDecodeError:
            continue
    
    # Also check stderr for usage information
    for line in stderr.split("\n"):
        # Look for patterns like "Tokens used: 1234" or "Usage: 1234 tokens" or "1234 tokens"
        # Pattern allows for words between "tokens" and ":"
        patterns = [
            r'tokens?\s+\w+[:\s]+(\d+)',  # "Tokens used: 1234"
            r'usage[:\s]+(\d+)',  # "Usage: 1234"
            r'(\d+)[\s]+tokens?',  # "1234 tokens"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and not usage_data["total_tokens"]:
                usage_data["total_tokens"] = int(match.group(1))
                break
    
    if any(usage_data.values()):
        return usage_data
    
    return None


def parse_openai_codex_usage(stdout: str, stderr: str) -> dict[str, Any] | None:
    """
    Parse token usage from OpenAI Codex CLI output.
    
    Codex exec command may output usage in JSON format or stderr.
    """
    usage_data = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    
    # Try parsing JSON from stdout (could be JSONL or single JSON)
    for line in stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        try:
            data = json.loads(line)
            
            # OpenAI API format
            if "usage" in data:
                usage = data["usage"]
                if isinstance(usage, dict):
                    usage_data["input_tokens"] = usage.get("prompt_tokens") or usage_data.get("input_tokens")
                    usage_data["output_tokens"] = usage.get("completion_tokens") or usage_data.get("output_tokens")
                    usage_data["total_tokens"] = usage.get("total_tokens") or usage_data.get("total_tokens")
            
            # Also check for direct fields at top level
            if "prompt_tokens" in data:
                usage_data["input_tokens"] = data["prompt_tokens"]
            if "completion_tokens" in data:
                usage_data["output_tokens"] = data["completion_tokens"]
            if "total_tokens" in data:
                usage_data["total_tokens"] = data["total_tokens"]
            
        except json.JSONDecodeError:
            # Try to find usage info in non-JSON lines
            patterns = [
                r'prompt[_\s]tokens?[:\s]+(\d+)',
                r'completion[_\s]tokens?[:\s]+(\d+)',
                r'total[_\s]tokens?[:\s]+(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if 'prompt' in pattern.lower():
                        usage_data["input_tokens"] = int(match.group(1))
                    elif 'completion' in pattern.lower():
                        usage_data["output_tokens"] = int(match.group(1))
                    elif 'total' in pattern.lower():
                        usage_data["total_tokens"] = int(match.group(1))
    
    # Check stderr for usage patterns (often where CLI tools output metadata)
    for line in stderr.split("\n"):
        # Look for patterns like "Tokens used: 1234" or "Usage: 1234 tokens" or "1234 tokens"
        patterns = [
            r'prompt[_\s]tokens?[:\s]+(\d+)',
            r'completion[_\s]tokens?[:\s]+(\d+)',
            r'total[_\s]tokens?[:\s]+(\d+)',
            r'tokens?\s+\w+[:\s]+(\d+)',  # "Tokens used: 1234"
            r'usage[:\s]+(\d+)',  # "Usage: 1234"
            r'(\d+)[\s]+tokens?',  # "1234 tokens"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                token_count = int(match.group(1))
                if 'prompt' in pattern.lower() and not usage_data["input_tokens"]:
                    usage_data["input_tokens"] = token_count
                elif 'completion' in pattern.lower() and not usage_data["output_tokens"]:
                    usage_data["output_tokens"] = token_count
                elif 'total' in pattern.lower() and not usage_data["total_tokens"]:
                    usage_data["total_tokens"] = token_count
                elif not usage_data["total_tokens"]:
                    usage_data["total_tokens"] = token_count
    
    # Calculate total if we have input/output but not total
    if usage_data["input_tokens"] and usage_data["output_tokens"] and not usage_data["total_tokens"]:
        usage_data["total_tokens"] = usage_data["input_tokens"] + usage_data["output_tokens"]
    
    if any(usage_data.values()):
        return usage_data
    
    return None


def parse_cursor_usage(stdout: str, stderr: str) -> dict[str, Any] | None:
    """
    Parse token usage from Cursor CLI output.
    
    Cursor uses --output-format stream-json which outputs JSONL.
    Similar format to Claude Code, but may have Cursor-specific fields.
    """
    usage_data = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    
    # Parse JSONL output (similar to Claude Code)
    for line in stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        try:
            data = json.loads(line)
            
            # Look for usage fields in various possible formats
            if "usage" in data:
                usage = data["usage"]
                if isinstance(usage, dict):
                    usage_data["input_tokens"] = usage.get("input_tokens") or usage.get("prompt_tokens")
                    usage_data["output_tokens"] = usage.get("output_tokens") or usage.get("completion_tokens")
                    if usage_data["input_tokens"] and usage_data["output_tokens"]:
                        usage_data["total_tokens"] = usage_data["input_tokens"] + usage_data["output_tokens"]
            
            # Also check for direct fields
            if "input_tokens" in data:
                usage_data["input_tokens"] = data["input_tokens"]
            if "output_tokens" in data:
                usage_data["output_tokens"] = data["output_tokens"]
            if "total_tokens" in data:
                usage_data["total_tokens"] = data["total_tokens"]
            
            # Cursor-specific: check for token_count or similar fields
            if "token_count" in data:
                if not usage_data["total_tokens"]:
                    usage_data["total_tokens"] = data["token_count"]
            
        except json.JSONDecodeError:
            continue
    
    # Also check stderr for usage information
    for line in stderr.split("\n"):
        patterns = [
            r'tokens?\s+\w+[:\s]+(\d+)',  # "Tokens used: 1234"
            r'usage[:\s]+(\d+)',  # "Usage: 1234"
            r'(\d+)[\s]+tokens?',  # "1234 tokens"
            r'prompt[_\s]tokens?[:\s]+(\d+)',
            r'completion[_\s]tokens?[:\s]+(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                token_count = int(match.group(1))
                if 'prompt' in pattern.lower() and not usage_data["input_tokens"]:
                    usage_data["input_tokens"] = token_count
                elif 'completion' in pattern.lower() and not usage_data["output_tokens"]:
                    usage_data["output_tokens"] = token_count
                elif not usage_data["total_tokens"]:
                    usage_data["total_tokens"] = token_count
                break
    
    # Calculate total if we have input/output but not total
    if usage_data["input_tokens"] and usage_data["output_tokens"] and not usage_data["total_tokens"]:
        usage_data["total_tokens"] = usage_data["input_tokens"] + usage_data["output_tokens"]
    
    if any(usage_data.values()):
        return usage_data
    
    return None


def parse_gemini_usage(stdout: str, stderr: str) -> dict[str, Any] | None:
    """
    Parse token usage from Gemini API output.
    
    Gemini API outputs usage metadata in JSON format.
    """
    usage_data = {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }
    
    # Parse JSON from stdout (usage info is appended as JSON line)
    for line in stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        try:
            data = json.loads(line)
            
            # Look for usage fields
            if "usage" in data:
                usage = data["usage"]
                if isinstance(usage, dict):
                    usage_data["input_tokens"] = usage.get("prompt_tokens") or usage.get("input_tokens")
                    usage_data["output_tokens"] = usage.get("completion_tokens") or usage.get("output_tokens")
                    usage_data["total_tokens"] = usage.get("total_tokens")
            
            # Also check for direct fields
            if "prompt_tokens" in data:
                usage_data["input_tokens"] = data["prompt_tokens"]
            if "completion_tokens" in data:
                usage_data["output_tokens"] = data["completion_tokens"]
            if "total_tokens" in data:
                usage_data["total_tokens"] = data["total_tokens"]
            
        except json.JSONDecodeError:
            continue
    
    # Check stderr for usage patterns
    for line in stderr.split("\n"):
        patterns = [
            r'tokens?\s+\w+[:\s]+(\d+)',
            r'usage[:\s]+(\d+)',
            r'(\d+)[\s]+tokens?',
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match and not usage_data["total_tokens"]:
                usage_data["total_tokens"] = int(match.group(1))
                break
    
    if any(usage_data.values()):
        return usage_data
    
    return None

