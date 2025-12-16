"""
Rate limiting implementation for the aiopythonik library.

This module provides a rate limiting implementation that handles the iconik API
rate limits using an exponential backoff strategy.
"""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Optional, TypeVar, cast

from ._pythonik_patches._logger import logger


T = TypeVar("T")


@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting behavior.

    Args:
        max_retries: Maximum number of retries for rate-limited requests
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_factor: Exponential factor for backoff calculation
        jitter: Whether to add randomness to backoff times
        enable_proactive_throttling: Enable proactive delays before hitting
            limits
        proactive_throttling_threshold: Start throttling when below this quota %
        max_proactive_delay: Maximum delay to apply proactively (seconds)
    """

    max_retries: int = 3
    initial_backoff: float = 1.0
    max_backoff: float = 30.0
    backoff_factor: float = 2.0
    jitter: bool = True
    enable_proactive_throttling: bool = True
    proactive_throttling_threshold: float = 0.8
    max_proactive_delay: float = 5.0


class RateLimitError(Exception):
    """
    Exception raised for API rate limit errors.

    This custom exception class includes a response attribute to allow
    access to the original response object that triggered the rate limit.
    """

    def __init__(self, message: str = "Rate limit exceeded", response=None):
        """
        Initialize the RateLimitError.

        Args:
            message: Error message
            response: Optional response object that triggered the rate limit
        """
        self.response = response
        super().__init__(message)


class ResponseLike:
    """
    A wrapper class for objects that may have response-like attributes.

    This class is used to safely check for the existence of status_code
    and other attributes without raising attribute errors.
    """

    def __init__(self, obj: Any):
        """
        Initialize with any object that might have response-like attributes.

        Args:
            obj: The object to wrap
        """
        self._obj = obj

    @property
    def status_code(self) -> Optional[int]:
        """
        Get the status code if it exists.

        Returns:
            The status code or None
        """
        return getattr(self._obj, "status_code", None)

    @property
    def headers(self) -> Optional[dict]:
        """
        Get the headers if they exist.

        Returns:
            The headers or None
        """
        return getattr(self._obj, "headers", None)


class RateLimitHandler:
    """
    Handler for API rate limiting.

    Implements retry logic with exponential backoff for rate-limited requests.
    """

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize the rate limit handler.

        Args:
            config: Optional configuration for rate limiting behavior
        """
        self.config = config or RateLimitConfig()
        self._remaining_requests: Optional[int] = None
        self._last_response_time = 0.0
        self._proactive_delay = 0.0
        self._estimated_total_quota = 1000  # Default iconik quota

    def update_limits(self, headers: dict) -> None:
        """
        Update rate limit information from response headers.

        Args:
            headers: Response headers containing rate limit information
        """
        self._last_response_time = time.time()
        if "RateLimit-Remaining" in headers:
            try:
                self._remaining_requests = int(headers["RateLimit-Remaining"])
                logger.debug(
                    "Rate limit remaining: {}", self._remaining_requests
                )
                # Update proactive throttling state based on new quota info
                self._update_proactive_delay()
            except (ValueError, TypeError):
                logger.warning("Failed to parse RateLimit-Remaining header")

    def get_backoff_time(self, retry_count: int) -> float:
        """
        Calculate backoff time for a retry attempt.

        Args:
            retry_count: The current retry attempt (0-based)

        Returns:
            float: The backoff time in seconds
        """
        backoff = min(
            self.config.max_backoff,
            self.config.initial_backoff *
            (self.config.backoff_factor**retry_count),
        )
        if self.config.jitter:
            jitter_factor = 1.0 + random.uniform(-0.15, 0.15)
            backoff *= jitter_factor
        return backoff

    def get_proactive_delay(self) -> float:
        """
        Calculate proactive delay to apply before making a request.

        Uses graduated delays based on remaining quota percentage:
        - 80%+ remaining: No delay
        - 30-20% remaining: Light throttling (0.1-0.5s)
        - 20-10% remaining: Moderate throttling (0.5-2.0s)
        - <10% remaining: Aggressive throttling (2.0-5.0s)

        Returns:
            float: Delay in seconds to apply before the request
        """
        if not self.config.enable_proactive_throttling:
            return 0.0

        if self._remaining_requests is None:
            return 0.0

        # Calculate quota percentage remaining
        quota_ratio = self._remaining_requests / self._estimated_total_quota

        if quota_ratio >= 0.8:
            # 80%+ quota remaining: No delay
            self._proactive_delay = 0.0
        elif quota_ratio >= 0.3:
            # 30-80% quota remaining: No throttling yet
            self._proactive_delay = 0.0
        elif quota_ratio >= 0.2:
            # 20-30% quota remaining: Light throttling
            delay_factor = (0.3 - quota_ratio) / 0.1  # 0.0 to 1.0
            self._proactive_delay = 0.1 + (delay_factor * 0.4)  # 0.1s to 0.5s
        elif quota_ratio >= 0.1:
            # 10-20% quota remaining: Moderate throttling
            delay_factor = (0.2 - quota_ratio) / 0.1  # 0.0 to 1.0
            self._proactive_delay = 0.5 + (delay_factor * 1.5)  # 0.5s to 2.0s
        else:
            # <10% quota remaining: Aggressive throttling
            delay_factor = min(1.0, (0.1 - quota_ratio) / 0.1)  # 0.0 to 1.0+
            self._proactive_delay = 2.0 + (delay_factor * 3.0)  # 2.0s to 5.0s

        # Cap at configured maximum
        self._proactive_delay = min(
            self._proactive_delay, self.config.max_proactive_delay
        )

        # Add jitter if enabled
        if self.config.jitter and self._proactive_delay > 0:
            jitter_factor = 1.0 + random.uniform(-0.15, 0.15)
            self._proactive_delay *= jitter_factor

        return self._proactive_delay

    def _update_proactive_delay(self) -> None:
        """
        Update proactive delay based on current remaining requests.
        Called internally by update_limits.
        """
        if not self.config.enable_proactive_throttling:
            self._proactive_delay = 0.0
            return

        if self._remaining_requests is None:
            return

        # Update estimated total quota based on observed values
        if self._remaining_requests > self._estimated_total_quota * 0.9:
            # If we see >90% of our estimated quota, update our estimate
            self._estimated_total_quota = max(
                self._estimated_total_quota,
                int(self._remaining_requests / 0.9)
            )

        # Calculate the new proactive delay
        self.get_proactive_delay()

    async def execute_with_retry(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute a function with retry logic for rate limiting.

        Args:
            func: The async function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            The result of the function call

        Raises:
            Exception: If all retries are exhausted
        """
        retries = 0
        last_exception: Optional[Exception] = None
        while retries <= self.config.max_retries:
            try:
                # Apply proactive delay before making request (prevention)
                proactive_delay = self.get_proactive_delay()
                if proactive_delay > 0:
                    logger.debug(
                        "Applying proactive delay of {:.2f}s ({}% quota remaining)",  # pylint: disable=line-too-long
                        proactive_delay,
                        int((self._remaining_requests or 0) /
                            self._estimated_total_quota * 100),
                    )
                    await asyncio.sleep(proactive_delay)

                result = await func(*args, **kwargs)

                if hasattr(result, "response"):
                    response_wrapper = ResponseLike(getattr(result, "response"))
                    if response_wrapper.headers:
                        self.update_limits(response_wrapper.headers)
                return cast(T, result)
            except Exception as e:
                last_exception = e

                is_rate_limit_error = False

                if isinstance(e, RateLimitError):
                    is_rate_limit_error = True

                elif hasattr(e, "response"):
                    response_wrapper = ResponseLike(getattr(e, "response"))
                    if response_wrapper.status_code == 429:
                        is_rate_limit_error = True
                if not is_rate_limit_error:
                    raise
                if retries >= self.config.max_retries:
                    logger.error(
                        "Rate limit exceeded and max retries ({}) reached",
                        self.config.max_retries,
                    )
                    raise
                backoff_time = self.get_backoff_time(retries)
                logger.warning(
                    "Rate limit exceeded. Retrying in {} seconds", backoff_time
                )
                await asyncio.sleep(backoff_time)
                retries += 1

        if last_exception:
            raise last_exception

        raise RuntimeError("Unexpected error in rate limit retry logic")
