# src/aiopythonik/client.pyi
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

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
    _sync_client: PythonikClient
    _executor: ThreadPoolExecutor
    rate_limit_handler: Optional[RateLimitHandler]

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
    ) -> None:
        ...

    def spec(self) -> AsyncSpec:
        ...

    def assets(self) -> AsyncAssetSpec:
        ...

    def collections(self) -> AsyncCollectionSpec:
        ...

    def files(self) -> AsyncFilesSpec:
        ...

    def jobs(self) -> AsyncJobSpec:
        ...

    def metadata(self) -> AsyncMetadataSpec:
        ...

    def search(self) -> AsyncSearchSpec:
        ...

    async def close(self) -> None:
        ...


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
    ...


class AsyncPythonikClientContext:
    app_id: str
    auth_token: str
    timeout: int
    base_url: str
    max_workers: Optional[int]
    rate_limit_config: Optional[RateLimitConfig]
    disable_rate_limit_handling: bool
    pool_connections: int
    pool_maxsize: int
    client: Optional[AsyncPythonikClient]

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
    ) -> None:
        ...

    async def __aenter__(self) -> AsyncPythonikClient:
        ...

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        ...
