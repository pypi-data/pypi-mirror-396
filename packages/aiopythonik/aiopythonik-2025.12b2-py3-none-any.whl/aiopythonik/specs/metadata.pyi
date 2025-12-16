# src/aiopythonik/specs/metadata.pyi
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Literal, Optional, Union

from pythonik.models.base import Response
from pythonik.models.metadata.fields import FieldCreate, FieldUpdate
from pythonik.models.metadata.views import ViewMetadata
from pythonik.models.mutation.metadata.mutate import UpdateMetadata

from .._pythonik_patches import MetadataSpec
from .._pythonik_patches.models import CreateViewRequest, UpdateViewRequest
from ..rate_limiting import RateLimitHandler


class AsyncMetadataSpec:
    _sync_spec: MetadataSpec
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: MetadataSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    async def get_views(self, **kwargs) -> Response:
        ...

    async def get_view(
        self,
        view_id: str,
        merge_fields: Optional[bool] = None,
        **kwargs
    ) -> Response:
        ...

    async def create_view(
        self,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_view(
        self,
        view_id: str,
        view: Union[UpdateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def replace_view(
        self,
        view_id: str,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_view(self, view_id: str, **kwargs) -> Response:
        ...

    async def get_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> Response:
        ...

    async def update_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_object_metadata(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        view_id: str,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> Response:
        ...

    async def get_object_metadata_direct(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> Response:
        ...

    async def put_metadata_direct(
        self,
        object_type: str,
        object_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def put_object_view_metadata(
        self,
        asset_id: str,
        object_type: Literal["segments"],
        object_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def put_segment_view_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def put_segment_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def create_field(
        self,
        field_data: FieldCreate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_field(
        self,
        field_name: str,
        field_data: FieldUpdate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_field(
        self,
        field_name: str,
        **kwargs,
    ) -> Response:
        ...

    async def create_metadata_field(
        self,
        field_data: FieldCreate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_metadata_field(
        self,
        field_name: str,
        field_data: FieldUpdate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_metadata_field(
        self,
        field_name: str,
        **kwargs,
    ) -> Response:
        ...
