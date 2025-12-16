"""Base wrapper for asynchronous spec classes."""

from __future__ import annotations

import asyncio
import functools
import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Optional, TypeVar

from .._pythonik_patches import Spec
from ..rate_limiting import RateLimitHandler


T = TypeVar("T")


class AsyncSpecWrapper:
    """
    Base class for async spec wrappers.

    This class dynamically creates async versions of all public methods
    in the wrapped sync spec.
    """

    def __init__(
        self,
        sync_spec: Any,
        executor: Optional[ThreadPoolExecutor] = None,
        rate_limit_handler: Optional[RateLimitHandler] = None,
    ):
        """
        Initialize the async spec wrapper.

        Args:
            sync_spec: The synchronous spec to wrap
            executor: Optional executor to use for running sync operations
            rate_limit_handler: Optional handler for rate limiting
        """
        self._sync_spec = sync_spec
        self._executor = executor
        self._rate_limit_handler = rate_limit_handler
        for attr_name in dir(sync_spec):
            if not attr_name.startswith("_") and not callable(
                getattr(sync_spec, attr_name)
            ):
                try:
                    setattr(self, attr_name, getattr(sync_spec, attr_name))
                except (AttributeError, TypeError):
                    pass
        self._wrap_methods()

    def _wrap_methods(self) -> None:
        """
        Create async versions of all public methods in the sync spec.
        """
        for name in dir(self._sync_spec):
            if (
                not name.startswith("_")
                and callable(getattr(self._sync_spec, name))
                and not hasattr(self, name)
            ):
                setattr(self, name, self._create_async_method(name))

    def _create_async_method(
        self, name: str
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        """
        Create an async version of a sync method.

        Args:
            name: The name of the sync method

        Returns:
            An async method that wraps the sync method
        """
        sync_method = getattr(self._sync_spec, name)
        try:
            _ = inspect.signature(sync_method)

            @functools.wraps(sync_method)
            async def async_method(*args: Any, **kwargs: Any) -> Any:
                """Async wrapper for the sync method."""
                loop = asyncio.get_event_loop()

                def run_sync(*_args: Any, **_kwargs: Any) -> Any:
                    """Execute the sync method with the given arguments."""
                    return sync_method(*args, **kwargs)

                if self._rate_limit_handler:

                    async def execute_with_executor(
                        *_args: Any, **_kwargs: Any
                    ) -> Any:
                        """
                        Execute the sync function in the executor.

                        This function is passed to rate_limit_handler.
                        """
                        return await loop.run_in_executor(
                            self._executor, run_sync, *_args
                        )

                    return await self._rate_limit_handler.execute_with_retry(
                        execute_with_executor, *args, **kwargs
                    )
                return await loop.run_in_executor(
                    self._executor, run_sync, *args
                )

            async_method.__doc__ = sync_method.__doc__
            async_method.__annotations__ = getattr(
                sync_method, "__annotations__", {}
            )
            return async_method
        except (ValueError, TypeError):

            @functools.wraps(sync_method)
            async def async_method(*args: Any, **kwargs: Any) -> Any:
                """Async wrapper for the sync method."""
                loop = asyncio.get_event_loop()

                def run_sync(*_args: Any, **_kwargs: Any) -> Any:
                    """Execute the sync method with the given arguments."""
                    return sync_method(*args, **kwargs)

                if self._rate_limit_handler:

                    async def execute_with_executor(
                        *_args: Any, **_kwargs: Any
                    ) -> Any:
                        """
                        Execute the sync function in the executor.

                        This function is passed to rate_limit_handler.
                        """
                        return await loop.run_in_executor(
                            self._executor, run_sync, *_args
                        )

                    return await self._rate_limit_handler.execute_with_retry(
                        execute_with_executor, *args, **kwargs
                    )
                return await loop.run_in_executor(
                    self._executor, run_sync, *args
                )

            return async_method


class AsyncSpec(AsyncSpecWrapper):
    """
    Asynchronous wrapper for the pythonik base Spec.

    This class provides async versions of all methods in the base Spec,
    running them in a thread pool to avoid blocking the event loop.
    """

    def __init__(
        self,
        sync_spec: Spec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ):
        """
        Initialize the async spec.

        Args:
            sync_spec: The synchronous spec to wrap
            executor: Optional executor to use for running sync operations
            rate_limit_handler: Optional handler for rate limiting
        """
        super().__init__(
            sync_spec=sync_spec,
            executor=executor,
            rate_limit_handler=rate_limit_handler,
        )
