"""LLM client wrapper using LiteLLM for multi-provider support."""

import asyncio
import json
import time
from typing import Any, Optional, Type, TypeVar, Union

import litellm
from pydantic import BaseModel, ValidationError

from dataops_llm.config import LLMConfig
from dataops_llm.exceptions import LLMError
from dataops_llm.llm.json_utils import clean_json_response, JSONRepairError

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Unified LLM client using LiteLLM.

    This client provides a consistent interface for any LLM provider
    supported by LiteLLM (OpenAI, Anthropic, Google, etc.) with features like:
    - Automatic retry with exponential backoff
    - Structured output support (Pydantic models)
    - Token usage tracking
    - Error handling and logging

    Attributes:
        config: LLM configuration
        total_tokens: Total tokens used across all requests
        total_requests: Total number of requests made
    """

    def __init__(self, config: LLMConfig):
        """Initialize the LLM client.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.total_tokens = 0
        self.total_requests = 0

        # Configure LiteLLM
        litellm.set_verbose = False  # Disable verbose logging
        if config.base_url:
            litellm.api_base = config.base_url

    def _parse_retry_after(self, error_message: str) -> Optional[float]:
        """Extract retry-after time from rate limit error message.

        Parses common retry time patterns from LLM provider error messages.

        Args:
            error_message: Error message from LiteLLM

        Returns:
            Retry time in seconds, or None if not found
        """
        import re

        patterns = [
            r"retry in ([\d.]+)s",
            r"retry after ([\d.]+)s",
            r"Please retry in ([\d.]+)s",
        ]

        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[T]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Union[str, T]:
        """Generate completion asynchronously.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_format: Optional Pydantic model for structured output
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments for LiteLLM

        Returns:
            String response or Pydantic model instance if response_format provided

        Raises:
            LLMError: If generation fails after all retries
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Merge config with kwargs
        call_kwargs = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout,
            "api_key": self.config.api_key,
            **kwargs,
        }

        # Add response format for structured output if provided
        if response_format:
            call_kwargs["response_format"] = {"type": "json_object"}

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    litellm.completion,
                    **call_kwargs
                )

                # Track usage
                self.total_requests += 1
                if hasattr(response, "usage") and response.usage:
                    self.total_tokens += response.usage.total_tokens

                # Extract content
                content = response.choices[0].message.content

                # Parse structured output if requested
                if response_format:
                    try:
                        # Clean the response first
                        try:
                            cleaned_content = clean_json_response(content)
                        except JSONRepairError as repair_error:
                            # If not last retry, try again
                            if attempt < max_retries - 1:
                                print(f"[Warning] JSON repair failed, retrying... (attempt {attempt + 2}/{max_retries})")
                                await asyncio.sleep(2 ** attempt)
                                continue

                            # Last attempt failed
                            raise LLMError(
                                f"Failed to parse LLM response as valid JSON after {max_retries} attempts. "
                                f"Error: {repair_error}"
                            )

                        # Parse cleaned JSON
                        json_data = json.loads(cleaned_content)

                        # Validate with Pydantic
                        return response_format(**json_data)

                    except (json.JSONDecodeError, ValidationError) as e:
                        # If not last retry, try again
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)
                            continue

                        raise LLMError(
                            f"Failed to parse LLM response as {response_format.__name__}: {e}"
                        )

                return content

            except litellm.exceptions.RateLimitError as e:
                last_error = e

                # Parse retry-after hint from error message
                retry_after = self._parse_retry_after(str(e))

                if attempt < max_retries - 1:
                    # Use parsed time or exponential backoff (capped at 60s)
                    wait_time = retry_after if retry_after else min(2 ** attempt, 60)

                    print(f"[Rate Limit] Waiting {wait_time:.0f}s before retry (attempt {attempt + 2}/{max_retries})...")

                    await asyncio.sleep(wait_time)
                    continue

                raise LLMError(
                    f"Rate limit exceeded after {max_retries} attempts. "
                    f"Please wait ~60 seconds before trying again. "
                    f"Original error: {e}"
                )

            except litellm.exceptions.Timeout as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise LLMError(f"Request timeout after {max_retries} attempts: {e}")

            except litellm.exceptions.AuthenticationError as e:
                # Don't retry authentication errors
                raise LLMError(f"Authentication failed: {e}")

            except litellm.exceptions.BadRequestError as e:
                # Don't retry bad request errors
                raise LLMError(f"Bad request: {e}")

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise LLMError(f"Unexpected error after {max_retries} attempts: {e}")

        raise LLMError(f"Failed after {max_retries} attempts. Last error: {last_error}")

    def generate_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[T]] = None,
        max_retries: int = 3,
        **kwargs,
    ) -> Union[str, T]:
        """Generate completion synchronously.

        This is a synchronous wrapper around the async generate method.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_format: Optional Pydantic model for structured output
            max_retries: Maximum number of retry attempts
            **kwargs: Additional arguments for LiteLLM

        Returns:
            String response or Pydantic model instance if response_format provided

        Raises:
            LLMError: If generation fails after all retries
        """
        return asyncio.run(
            self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                response_format=response_format,
                max_retries=max_retries,
                **kwargs,
            )
        )

    def reset_stats(self) -> None:
        """Reset token and request counters."""
        self.total_tokens = 0
        self.total_requests = 0

    def get_stats(self) -> dict[str, int]:
        """Get current usage statistics.

        Returns:
            Dictionary with total_tokens and total_requests
        """
        return {
            "total_tokens": self.total_tokens,
            "total_requests": self.total_requests,
        }

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"LLMClient(model={self.config.model}, "
            f"requests={self.total_requests}, "
            f"tokens={self.total_tokens})"
        )
