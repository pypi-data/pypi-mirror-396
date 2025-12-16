# src/aiopythonik/specs/collection.pyi
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Union

from pythonik.models.assets.collections import Collection, Content
from pythonik.models.base import Response

from .._pythonik_patches import CollectionSpec
from ..rate_limiting import RateLimitHandler


class AsyncCollectionSpec:
    _sync_spec: CollectionSpec
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: CollectionSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    async def get(self, collection_id: str, **kwargs) -> Response:
        ...

    async def fetch(self, **kwargs) -> Response:
        ...

    async def create(
        self,
        body: Union[Dict[str, Any], Collection],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update(
        self,
        collection_id: str,
        body: Union[Dict[str, Any], Collection],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete(self, collection_id: str, **kwargs) -> Response:
        ...

    async def get_info(self, collection_id: str, **kwargs) -> Response:
        ...

    async def get_contents(self, collection_id: str, **kwargs) -> Response:
        ...

    async def add_content(
        self,
        collection_id: str,
        body: Union[Dict[str, Any], Content],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def remove_content(
        self, collection_id: str, content_id: str, **kwargs
    ) -> Response:
        ...
