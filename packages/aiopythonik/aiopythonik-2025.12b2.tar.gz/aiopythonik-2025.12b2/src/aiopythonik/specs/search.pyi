# src/aiopythonik/specs/search.pyi
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Union

from pythonik.models.base import Response
from pythonik.models.search.search_body import SearchBody

from .._pythonik_patches import SearchSpec
from ..rate_limiting import RateLimitHandler


class AsyncSearchSpec:
    _sync_spec: SearchSpec
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: SearchSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    async def search(
        self,
        search_body: Union[SearchBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...
