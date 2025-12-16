# pylint: disable=too-many-positional-arguments
"""
Asynchronous client implementation for pythonik.

This module provides the AsyncPythonikClient class, which is the main entry
point for using the asynchronous API.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from ._pythonik_patches import PythonikClient
from .rate_limiting import RateLimitConfig, RateLimitHandler
from .specs import (
    AsyncAssetSpec,
    AsyncCollectionSpec,
    AsyncFilesSpec,
    AsyncJobSpec,
    AsyncMetadataSpec,
    AsyncSearchSpec,
    AsyncSpec,
)


class AsyncPythonikClient:
    """
    Asynchronous wrapper for the PythonikClient.

    Allows pythonik operations to be used in an async context by running
    synchronous operations in a thread pool.
    """

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        timeout: int = 3,
        base_url: str = "https://app.iconik.io",
        max_workers: Optional[int] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        disable_rate_limit_handling: bool = False,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ):
        """
        Initialize the async client.

        Args:
            app_id: The app ID for authentication
            auth_token: The auth token for authentication
            timeout: The timeout for API requests
            base_url: The base URL for the API
            max_workers: Maximum number of worker threads to use
            rate_limit_config: Configuration for rate limiting behavior
            disable_rate_limit_handling: Disable automatic rate limit handling
            pool_connections: Number of urllib3 connection pools to cache.
                Default: 10.
            pool_maxsize: Maximum connections per pool. Increase for
                high-concurrency workloads to avoid connection churn.
                Default: 10.
        """
        self._sync_client = PythonikClient(
            app_id=app_id,
            auth_token=auth_token,
            timeout=timeout,
            base_url=base_url,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
        )
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.rate_limit_handler = (
            None if disable_rate_limit_handling else
            RateLimitHandler(rate_limit_config)
        )

    def spec(self) -> AsyncSpec:
        """
        Get the base spec.

        Returns:
            AsyncSpec: The async base spec
        """
        spec_args = {
            "sync_spec": self._sync_client,
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncSpec(**spec_args)

    def assets(self) -> AsyncAssetSpec:
        """
        Get the assets spec.

        Returns:
            AsyncAssetSpec: The async assets spec
        """
        spec_args = {
            "sync_spec": self._sync_client.assets(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncAssetSpec(**spec_args)

    def collections(self) -> AsyncCollectionSpec:
        """
        Get the collections spec.

        Returns:
            AsyncCollectionSpec: The async collections spec
        """
        spec_args = {
            "sync_spec": self._sync_client.collections(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncCollectionSpec(**spec_args)

    def files(self) -> AsyncFilesSpec:
        """
        Get the files spec.

        Returns:
            AsyncFilesSpec: The async files spec
        """
        spec_args = {
            "sync_spec": self._sync_client.files(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncFilesSpec(**spec_args)

    def jobs(self) -> AsyncJobSpec:
        """
        Get the jobs spec.

        Returns:
            AsyncJobSpec: The async jobs spec
        """
        spec_args = {
            "sync_spec": self._sync_client.jobs(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncJobSpec(**spec_args)

    def metadata(self) -> AsyncMetadataSpec:
        """
        Get the metadata spec.

        Returns:
            AsyncMetadataSpec: The async metadata spec
        """
        spec_args = {
            "sync_spec": self._sync_client.metadata(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncMetadataSpec(**spec_args)

    def search(self) -> AsyncSearchSpec:
        """
        Get the search spec.

        Returns:
            AsyncSearchSpec: The async search spec
        """
        spec_args = {
            "sync_spec": self._sync_client.search(),
            "executor": self._executor,
            "rate_limit_handler": self.rate_limit_handler,
        }
        return AsyncSearchSpec(**spec_args)

    async def close(self) -> None:
        """
        Close the client and release any resources.

        This should be called when the client is no longer needed.
        """
        self._executor.shutdown(wait=True)


async def create_async_client(
    app_id: str,
    auth_token: str,
    timeout: int = 3,
    base_url: str = "https://app.iconik.io",
    max_workers: Optional[int] = None,
    rate_limit_config: Optional[RateLimitConfig] = None,
    disable_rate_limit_handling: bool = False,
    pool_connections: int = 10,
    pool_maxsize: int = 10,
) -> AsyncPythonikClient:
    """
    Create an AsyncPythonikClient instance asynchronously.

    While creating the client is actually a synchronous operation,
    this function is provided for API consistency.

    Args:
        app_id: The app ID for authentication
        auth_token: The auth token for authentication
        timeout: The timeout for API requests
        base_url: The base URL for the API
        max_workers: Maximum number of worker threads to use
        rate_limit_config: Configuration for rate limiting behavior
        disable_rate_limit_handling: Disable automatic rate limit handling
        pool_connections: Number of urllib3 connection pools to cache.
            Default: 10.
        pool_maxsize: Maximum connections per pool. Increase for
            high-concurrency workloads to avoid connection churn.
            Default: 10.

    Returns:
        AsyncPythonikClient: An initialized async client
    """
    client_args = {
        "app_id": app_id,
        "auth_token": auth_token,
        "timeout": timeout,
        "base_url": base_url,
        "max_workers": max_workers,
        "rate_limit_config": rate_limit_config,
        "disable_rate_limit_handling": disable_rate_limit_handling,
        "pool_connections": pool_connections,
        "pool_maxsize": pool_maxsize,
    }
    return AsyncPythonikClient(**client_args)


# noinspection Annotator
class AsyncPythonikClientContext:
    """
    Context manager for the AsyncPythonikClient.

    This allows using the async client with the 'async with' statement,
    ensuring the client is properly closed when it's no longer needed.

    Example:
        >>> asset_id = '15f07e2e-55f9-4e1d-b1ff-0ea37c219e78'
        >>> async with AsyncPythonikClientContext(
        ...     app_id='...',
        ...     auth_token='...',
        ... ) as client:
        >>>     asset = await client.assets().get(asset_id)
        ```
    """

    def __init__(
        self,
        app_id: str,
        auth_token: str,
        timeout: int = 3,
        base_url: str = "https://app.iconik.io",
        max_workers: Optional[int] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        disable_rate_limit_handling: bool = False,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
    ):
        """
        Initialize the async client context.

        Args:
            app_id: The app ID for authentication
            auth_token: The auth token for authentication
            timeout: The timeout for API requests
            base_url: The base URL for the API
            max_workers: Maximum number of worker threads to use
            rate_limit_config: Configuration for rate limiting behavior
            disable_rate_limit_handling: Disable automatic rate limit handling
            pool_connections: Number of urllib3 connection pools to cache.
                Default: 10.
            pool_maxsize: Maximum connections per pool. Increase for
                high-concurrency workloads to avoid connection churn.
                Default: 10.
        """
        self.app_id = app_id
        self.auth_token = auth_token
        self.timeout = timeout
        self.base_url = base_url
        self.max_workers = max_workers
        self.rate_limit_config = rate_limit_config
        self.disable_rate_limit_handling = disable_rate_limit_handling
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.client: Optional[AsyncPythonikClient] = None

    async def __aenter__(self) -> AsyncPythonikClient:
        """
        Enter the async context.

        Returns:
            AsyncPythonikClient: The initialized async client
        """
        client_args = {
            "app_id": self.app_id,
            "auth_token": self.auth_token,
            "timeout": self.timeout,
            "base_url": self.base_url,
            "max_workers": self.max_workers,
            "rate_limit_config": self.rate_limit_config,
            "disable_rate_limit_handling": self.disable_rate_limit_handling,
            "pool_connections": self.pool_connections,
            "pool_maxsize": self.pool_maxsize,
        }
        self.client = await create_async_client(**client_args)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the async context.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.client:
            await self.client.close()
