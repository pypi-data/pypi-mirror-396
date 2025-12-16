"""Asynchronous wrapper for the pythonik AssetSpec."""

from typing import Any, Optional

from .._pythonik_patches import AssetSpec
from .base import AsyncSpecWrapper


class AsyncAssetSpec(AsyncSpecWrapper):
    """
    Asynchronous wrapper for the pythonik AssetSpec.

    This class provides async versions of all methods in the AssetSpec,
    running them in a thread pool to avoid blocking the event loop.
    """

    def __init__(
        self,
        sync_spec: AssetSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ):
        """
        Initialize the async asset spec.

        Args:
            sync_spec: The synchronous asset spec to wrap
            executor: Optional executor to use for running sync operations
            rate_limit_handler: Optional handler for rate limiting
        """
        super().__init__(
            sync_spec=sync_spec,
            executor=executor,
            rate_limit_handler=rate_limit_handler,
        )
