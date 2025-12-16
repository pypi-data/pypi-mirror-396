# src/aiopythonik/specs/base.pyi
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, Dict, Optional, TypeVar, Union

from pythonik.models.base import Response
from pythonik.specs.base import Spec

from ..rate_limiting import RateLimitHandler


T = TypeVar("T")


class AsyncSpecWrapper:
    _sync_spec: Any
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: Any,
        executor: Optional[ThreadPoolExecutor] = None,
        rate_limit_handler: Optional[RateLimitHandler] = None,
    ) -> None:
        ...

    def _wrap_methods(self) -> None:
        ...

    def _create_async_method(
        self, name: str
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        ...


class AsyncSpec(AsyncSpecWrapper):

    def __init__(
        self,
        sync_spec: Spec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    @staticmethod
    async def parse_response(
        response: Any, model: Optional[Any] = None
    ) -> Response:
        ...

    async def send_request(self, method: str, path: str, **kwargs) -> Any:
        ...

    async def _prepare_request(self, method: str, url: str, **kwargs) -> Any:
        ...

    async def gen_url(self, path: str) -> str:
        ...

    async def _delete(self, path: str, **kwargs) -> Response:
        ...

    async def _get(self, path: str, **kwargs) -> Response:
        ...

    async def _patch(self, path: str, **kwargs) -> Response:
        ...

    async def _post(self, path: str, **kwargs) -> Response:
        ...

    async def _put(self, path: str, **kwargs) -> Response:
        ...

    @staticmethod
    async def _prepare_model_data(
        data: Union[Any, Dict[str, Any]],
        exclude_defaults: bool = True
    ) -> Dict[str, Any]:
        ...
