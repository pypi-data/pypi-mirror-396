#!/bin/bash
# Simple hello world test using GitHub's official Hello-World repo
# This is a minimal test case that's quick to run

set -e

echo "Running hello world test..."
echo "Using: github:octocat/Hello-World@master"
echo "Prompt: Add a comment to the README saying 'Hello from VibeLab!'"
echo ""

uv run vibelab run run-cmd \
  --code "github:octocat/Hello-World@master" \
  --prompt "Add a comment to the README saying 'Hello from VibeLab!'" \
  --executor "claude-code:anthropic:haiku" \
  --timeout 300

echo ""
echo "Test completed!"

