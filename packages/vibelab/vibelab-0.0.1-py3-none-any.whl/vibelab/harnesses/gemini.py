"""Google Gemini harness."""

import json
import os
from pathlib import Path
from typing import Any

from ..models.executor import ModelInfo
from .base import Harness, HarnessOutput, PricingInfo, StreamCallback


class GeminiHarness:
    """Harness for Google Gemini API."""

    id = "gemini"
    name = "Google Gemini"
    supported_providers = ["google"]
    preferred_driver = None

    def get_models(self, provider: str) -> list[ModelInfo]:
        """Get available models."""
        if provider != "google":
            return []
        return [
            ModelInfo(id="gemini-2.0-flash-exp", name="Gemini 2.0 Flash (Experimental)"),
            ModelInfo(id="gemini-1.5-pro", name="Gemini 1.5 Pro"),
            ModelInfo(id="gemini-1.5-flash", name="Gemini 1.5 Flash"),
        ]

    def get_pricing(self, provider: str, model: str) -> PricingInfo | None:
        """Get pricing information for Gemini models."""
        if provider != "google":
            return None
        
        # Pricing per 1M tokens as of 2024
        # Source: https://ai.google.dev/pricing
        pricing_map = {
            "gemini-2.0-flash-exp": PricingInfo(input_price_per_1m=0.0, output_price_per_1m=0.0),  # Free during experimental phase
            "gemini-1.5-pro": PricingInfo(input_price_per_1m=1.25, output_price_per_1m=5.0),
            "gemini-1.5-flash": PricingInfo(input_price_per_1m=0.075, output_price_per_1m=0.30),
        }
        
        return pricing_map.get(model)

    def check_available(self) -> tuple[bool, str | None]:
        """Check if Gemini API is available."""
        # Check for Google Generative AI SDK
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError:
            return False, "Google Generative AI SDK not found. Install: pip install google-generativeai"
        
        # Check for API key
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return False, "GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set"
        
        return True, None

    def run(
        self,
        workdir: Path,
        prompt: str,
        provider: str,
        model: str,
        timeout_seconds: int,
        on_stdout: StreamCallback | None = None,
        on_stderr: StreamCallback | None = None,
    ) -> HarnessOutput:
        """Execute Gemini API with optional streaming."""
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError:
            return HarnessOutput(
                exit_code=1,
                stdout="",
                stderr="Google Generative AI SDK not found. Install: pip install google-generativeai",
            )

        # Get API key from environment
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return HarnessOutput(
                exit_code=1,
                stdout="",
                stderr="GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set",
            )

        genai.configure(api_key=api_key)

        # If streaming callbacks provided, use streaming
        if on_stdout or on_stderr:
            return self._run_streaming(genai, model, prompt, timeout_seconds, on_stdout, on_stderr)

        # Non-streaming execution
        try:
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Lower temperature for code generation
                },
            )

            # Extract usage information from response
            usage_info = {}
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage_info = {
                    "prompt_tokens": getattr(response.usage_metadata, "prompt_token_count", None),
                    "completion_tokens": getattr(response.usage_metadata, "completion_token_count", None),
                    "total_tokens": getattr(response.usage_metadata, "total_token_count", None),
                }

            # Format output similar to other harnesses
            stdout_lines = []
            if response.text:
                stdout_lines.append(response.text)
            
            # Add usage info as JSON line for parsing
            if usage_info:
                stdout_lines.append(json.dumps({"usage": usage_info}))

            return HarnessOutput(
                exit_code=0 if response.text else 1,
                stdout="\n".join(stdout_lines),
                stderr="",
            )

        except Exception as e:
            return HarnessOutput(
                exit_code=1,
                stdout="",
                stderr=f"Error calling Gemini API: {e}",
            )

    def _run_streaming(
        self,
        genai: Any,
        model: str,
        prompt: str,
        timeout_seconds: int,
        on_stdout: StreamCallback | None,
        on_stderr: StreamCallback | None,
    ) -> HarnessOutput:
        """Run Gemini API with streaming output."""
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        usage_info = {}

        try:
            model_instance = genai.GenerativeModel(model)
            
            # Stream the response
            response = model_instance.generate_content(
                prompt,
                stream=True,
                generation_config={
                    "temperature": 0.1,
                },
            )

            # Collect streamed chunks and track usage
            final_chunk = None
            for chunk in response:
                final_chunk = chunk  # Keep track of last chunk for usage metadata
                if chunk.text:
                    stdout_chunks.append(chunk.text)
                    if on_stdout:
                        on_stdout(chunk.text)
            
            # Extract usage from final chunk (usage_metadata is typically on the last chunk)
            if final_chunk and hasattr(final_chunk, "usage_metadata") and final_chunk.usage_metadata:
                usage_info = {
                    "prompt_tokens": getattr(final_chunk.usage_metadata, "prompt_token_count", None),
                    "completion_tokens": getattr(final_chunk.usage_metadata, "completion_token_count", None),
                    "total_tokens": getattr(final_chunk.usage_metadata, "total_token_count", None),
                }

            # Add usage info as JSON line
            if usage_info:
                usage_json = json.dumps({"usage": usage_info})
                stdout_chunks.append(usage_json)
                if on_stdout:
                    on_stdout(usage_json + "\n")

            return HarnessOutput(
                exit_code=0,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
            )

        except Exception as e:
            error_msg = f"Error calling Gemini API: {e}"
            stderr_chunks.append(error_msg)
            if on_stderr:
                on_stderr(error_msg + "\n")
            return HarnessOutput(
                exit_code=1,
                stdout="".join(stdout_chunks),
                stderr="".join(stderr_chunks),
            )

    def get_container_image(self) -> str | None:
        """Return container image if available."""
        # Default to vibelab image, can be overridden via environment
        return os.getenv("VIBELAB_GEMINI_IMAGE", "vibelab/gemini:latest")

