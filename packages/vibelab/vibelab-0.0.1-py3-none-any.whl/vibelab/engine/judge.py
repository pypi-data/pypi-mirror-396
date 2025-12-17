"""LLM Judge execution engine."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..db import get_db, get_result, get_scenario, get_llm_scenario_judge, create_judgement
from ..db.connection import get_vibelab_home
from ..models.judge import LLMScenarioJudge, Judgement
from ..models.result import Result

logger = logging.getLogger(__name__)


class JudgeExecutor:
    """Executes LLM judges to make judgements on results."""

    def execute_judge(
        self,
        judge: LLMScenarioJudge,
        result: Result,
        judge_provider: str = "anthropic",
        judge_model: str = "claude-sonnet-4-20250514",
    ) -> Judgement:
        """Execute a judge on a result and return the judgement."""
        # Get scenario for context
        for db in get_db():
            scenario = get_scenario(db, judge.scenario_id)
            if not scenario:
                raise ValueError(f"Scenario {judge.scenario_id} not found")
            break

        # Build prompt with few-shot examples
        prompt = self._build_judge_prompt(judge, result, scenario)

        # Call LLM
        response = self._call_llm(prompt, judge_provider, judge_model)

        # Parse response
        notes, quality = self._parse_judgement_response(response)

        # Create judgement
        judgement = Judgement(
            id=0,  # Will be set by database
            result_id=result.id,
            judge_id=judge.id,
            notes=notes,
            quality=quality,
            created_at=datetime.now(timezone.utc),
        )

        for db in get_db():
            judgement = create_judgement(db, judgement)
            break

        return judgement

    def _build_judge_prompt(self, judge: LLMScenarioJudge, result: Result, scenario: Any) -> str:
        """Build the prompt for the judge with few-shot examples."""
        # Get training samples
        training_examples = []
        for db in get_db():
            for sample_id in judge.training_sample_ids:
                sample_result = get_result(db, sample_id)
                if sample_result:
                    training_examples.append(self._format_result_example(sample_result, scenario))
            break

        # Format current result
        current_result_text = self._format_result_for_judgement(result, scenario)

        # Build prompt
        prompt_parts = [
            judge.guidance,
            "",
            "## Few-shot Examples",
            "",
        ]

        for i, example in enumerate(training_examples, 1):
            prompt_parts.append(f"### Example {i}")
            prompt_parts.append(example)
            prompt_parts.append("")

        prompt_parts.extend([
            "## Result to Judge",
            "",
            current_result_text,
            "",
            "## Your Judgement",
            "",
            "Please provide your judgement in the following JSON format:",
            '{"notes": "Your detailed notes about the quality of this result...", "quality": 4}',
            "",
            "Quality scores:",
            "- 4 = Perfect: The best possible outcome",
            "- 3 = Good: Valid, but could be better",
            "- 2 = Workable: At least 1 thing is incorrect or needs revision, but directionally correct",
            "- 1 = Bad: Just not good, invalid",
        ])

        return "\n".join(prompt_parts)

    def _format_result_example(self, result: Result, scenario: Any) -> str:
        """Format a result as a few-shot example."""
        parts = [
            f"**Result ID:** {result.id}",
            f"**Executor:** {result.harness}:{result.provider}:{result.model}",
            f"**Status:** {result.status.value}",
        ]

        # Add patch if available
        patch = self._get_result_patch(result.id)
        if patch:
            parts.append(f"**Patch:**\n```diff\n{patch[:2000]}\n```")  # Limit patch size

        # Add human notes/quality if available
        if result.notes or result.quality is not None:
            parts.append("**Human Judgement:**")
            if result.quality is not None:
                quality_labels = {4: "Perfect", 3: "Good", 2: "Workable", 1: "Bad"}
                parts.append(f"- Quality: {result.quality} ({quality_labels.get(result.quality, 'Unknown')})")
            if result.notes:
                parts.append(f"- Notes: {result.notes}")

        return "\n".join(parts)

    def _format_result_for_judgement(self, result: Result, scenario: Any) -> str:
        """Format a result for judgement."""
        parts = [
            f"**Result ID:** {result.id}",
            f"**Executor:** {result.harness}:{result.provider}:{result.model}",
            f"**Status:** {result.status.value}",
            f"**Scenario Prompt:** {scenario.prompt}",
        ]

        # Add patch if available
        patch = self._get_result_patch(result.id)
        if patch:
            parts.append(f"**Patch:**\n```diff\n{patch}\n```")

        # Add logs summary
        stdout, stderr = self._get_result_logs(result.id)
        if stdout:
            parts.append(f"**Output (first 1000 chars):**\n{stdout[:1000]}")
        if stderr:
            parts.append(f"**Errors:**\n{stderr[:500]}")

        return "\n".join(parts)

    def _get_result_patch(self, result_id: int) -> str | None:
        """Get patch for a result."""
        home = get_vibelab_home()
        patch_file = home / "results" / str(result_id) / "patch.diff"
        if patch_file.exists():
            return patch_file.read_text()
        return None

    def _get_result_logs(self, result_id: int) -> tuple[str, str]:
        """Get logs for a result."""
        home = get_vibelab_home()
        stdout_file = home / "results" / str(result_id) / "stdout.log"
        stderr_file = home / "results" / str(result_id) / "stderr.log"
        stdout = stdout_file.read_text() if stdout_file.exists() else ""
        stderr = stderr_file.read_text() if stderr_file.exists() else ""
        return stdout, stderr

    def _call_llm(self, prompt: str, provider: str, model: str) -> str:
        """Call LLM API and return response."""
        if provider == "anthropic":
            return self._call_anthropic(prompt, model)
        elif provider == "openai":
            return self._call_openai(prompt, model)
        else:
            raise ValueError(f"Unsupported judge provider: {provider}")

    def _call_anthropic(self, prompt: str, model: str) -> str:
        """Call Anthropic API."""
        try:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract text from response
            if message.content:
                return message.content[0].text if isinstance(message.content[0].text, str) else str(message.content[0].text)
            return ""
        except ImportError:
            raise ValueError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            logger.exception(f"Error calling Anthropic API: {e}")
            raise

    def _call_openai(self, prompt: str, model: str) -> str:
        """Call OpenAI API."""
        try:
            import openai

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=4096,
            )

            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            return ""
        except ImportError:
            raise ValueError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            logger.exception(f"Error calling OpenAI API: {e}")
            raise

    def _parse_judgement_response(self, response: str) -> tuple[str | None, int | None]:
        """Parse LLM response to extract notes and quality."""
        # Try to extract JSON from response
        # Look for JSON block in markdown code fence or plain JSON
        import re

        # Try to find JSON in code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Fallback: treat entire response as notes
                return (response.strip() or None, None)

        try:
            data = json.loads(json_str)
            notes = data.get("notes")
            quality = data.get("quality")
            # Validate quality
            if quality is not None and (quality < 1 or quality > 4):
                quality = None
            return (notes, quality)
        except json.JSONDecodeError:
            # If JSON parsing fails, treat response as notes
            return (response.strip() or None, None)


def train_judge(
    judge: LLMScenarioJudge,
    judge_provider: str = "anthropic",
    judge_model: str = "claude-sonnet-4-20250514",
) -> float:
    """Train a judge and calculate alignment score."""
    executor = JudgeExecutor()

    # Run judge on test samples
    test_results = []
    for db in get_db():
        for test_id in judge.test_sample_ids:
            result = get_result(db, test_id)
            if result and result.status.value == "completed":
                # Only judge completed results
                try:
                    judgement = executor.execute_judge(judge, result, judge_provider, judge_model)
                    test_results.append((result, judgement))
                except Exception as e:
                    logger.warning(f"Failed to judge result {test_id}: {e}")
                    continue
        break

    if not test_results:
        logger.warning("No test results available for training")
        return 0.0

    # Calculate alignment score
    # Compare judge quality scores with human quality scores
    human_scores = []
    judge_scores = []

    for result, judgement in test_results:
        if result.quality is not None and judgement.quality is not None:
            human_scores.append(result.quality)
            judge_scores.append(judgement.quality)

    if len(human_scores) == 0:
        logger.warning("No scored results available for alignment calculation")
        return 0.0

    # Calculate correlation coefficient
    # If only one result, return 1.0 if scores match, 0.0 otherwise
    if len(human_scores) == 1:
        alignment = 1.0 if human_scores[0] == judge_scores[0] else 0.0
    else:
        alignment = _calculate_correlation(human_scores, judge_scores)

    # Update judge alignment score
    for db in get_db():
        from ..db.queries import update_llm_scenario_judge_alignment
        update_llm_scenario_judge_alignment(db, judge.id, alignment)
        break

    return alignment


def _calculate_correlation(x: list[int], y: list[int]) -> float:
    """Calculate Pearson correlation coefficient."""
    if len(x) != len(y):
        raise ValueError("Lists must have same length")

    n = len(x)
    if n < 2:
        return 0.0

    # Calculate means
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    # Calculate numerator and denominators
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))

    denominator = (sum_sq_x * sum_sq_y) ** 0.5

    if denominator == 0:
        return 0.0

    correlation = numerator / denominator
    return max(-1.0, min(1.0, correlation))  # Clamp to [-1, 1]

