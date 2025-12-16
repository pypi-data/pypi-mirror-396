"""
Asynchronous wrapper for the pythonik library.

This module provides asynchronous versions of all pythonik functionality,
allowing them to be used in async applications without blocking the event loop.

It works by running the synchronous operations in a thread pool executor,
similar to how `aioboto3` wraps `boto3`.

Usage:
    >>> import asyncio
    ... from aiopythonik import AsyncPythonikClient
    ...
    >>> async def main():
    ...    client = AsyncPythonikClient(
    ...        app_id="your_app_id",
    ...        auth_token="your_auth_token",
    ...        timeout=60,
    ...        base_url="https://app.iconik.io",
    ...    )
    ...
    >>>    asset = await client.assets().get("asset_id")
    ...
    >>> if __name__ == "__main__":
    ...    asyncio.run(main())
    ...
"""

from ._pythonik_patches._logger import logger
from ._pythonik_patches.models import (
    FieldValue,
    FieldValues,
    MutationMetadataValues,
    UpdateMetadata,
    ViewMetadata,
)
from .client import (
    AsyncPythonikClient,
    AsyncPythonikClientContext,
    create_async_client,
)
from .helpers import (
    get_attribute,
    has_attribute,
    is_pydantic_model,
    normalize_pattern,
)
from .rate_limiting import RateLimitConfig, RateLimitHandler
from .specs import (
    AsyncAssetSpec,
    AsyncCollectionSpec,
    AsyncFilesSpec,
    AsyncJobSpec,
    AsyncMetadataSpec,
    AsyncSearchSpec,
    AsyncSpec,
    AsyncSpecWrapper,
)


__all__ = [
    "AsyncPythonikClient",
    "AsyncPythonikClientContext",
    "create_async_client",
    "AsyncSpecWrapper",
    "AsyncSpec",
    "AsyncAssetSpec",
    "AsyncCollectionSpec",
    "AsyncFilesSpec",
    "AsyncJobSpec",
    "AsyncMetadataSpec",
    "AsyncSearchSpec",
    "FieldValue",
    "FieldValues",
    "MutationMetadataValues",
    "RateLimitConfig",
    "RateLimitHandler",
    "UpdateMetadata",
    "ViewMetadata",
    "logger",
    "get_attribute",
    "has_attribute",
    "is_pydantic_model",
    "normalize_pattern",
]
__version__ = "2025.12-beta.2"
