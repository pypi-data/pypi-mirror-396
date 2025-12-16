# src/aiopythonik/specs/assets.pyi
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional, Union

from pythonik.models.assets.assets import Asset, AssetCreate, BulkDelete
from pythonik.models.assets.segments import BulkDeleteSegmentsBody, SegmentBody
from pythonik.models.assets.versions import (
    AssetVersion,
    AssetVersionCreate,
    AssetVersionFromAssetCreate,
)
from pythonik.models.base import Response

from .._pythonik_patches import AssetSpec
from ..rate_limiting import RateLimitHandler


class AsyncAssetSpec:
    _sync_spec: AssetSpec
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: AssetSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    @property
    def collections(self) -> Any:
        ...

    async def get(self, asset_id: str, **kwargs) -> Response:
        ...

    async def fetch(self, **kwargs) -> Response:
        ...

    async def create(
        self,
        body: Union[Dict[str, Any], AssetCreate],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_asset(
        self,
        asset_id: str,
        body: Union[Dict[str, Any], Asset],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_asset(
        self,
        asset_id: str,
        body: Union[Dict[str, Any], Asset],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete(self, asset_id: str, **kwargs) -> Response:
        ...

    async def bulk_delete(
        self,
        body: Union[Dict[str, Any], BulkDelete],
        permanently_delete: bool = False,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def permanently_delete(self, **kwargs) -> Response:
        ...

    async def create_version(
        self,
        asset_id: str,
        body: Union[Dict[str, Any], AssetVersionCreate],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def create_version_from_asset(
        self,
        asset_id: str,
        source_asset_id: str,
        body: Union[Dict[str, Any], AssetVersionFromAssetCreate],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_version(
        self,
        asset_id: str,
        version_id: str,
        body: Union[Dict[str, Any], AssetVersion],
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_version(
        self,
        asset_id: str,
        version_id: str,
        body: Union[Dict[str, Any], AssetVersion],
        **kwargs,
    ) -> Response:
        ...

    async def delete_version(
        self,
        asset_id: str,
        version_id: str,
        hard_delete: bool = False,
        **kwargs,
    ) -> Response:
        ...

    async def promote_version(
        self, asset_id: str, version_id: str, **kwargs
    ) -> Response:
        ...

    async def delete_old_versions(self, asset_id: str, **kwargs) -> Response:
        ...

    async def create_segment(
        self,
        asset_id: str,
        body: Union[Dict[str, Any], SegmentBody],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_segment(
        self,
        asset_id: str,
        segment_id: str,
        body: Union[Dict[str, Any], SegmentBody],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_segment(
        self,
        asset_id: str,
        segment_id: str,
        body: Union[Dict[str, Any], SegmentBody],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def bulk_delete_segments(
        self,
        asset_id: str,
        body: Union[Dict[str, Any], BulkDeleteSegmentsBody],
        immediately: bool = True,
        ignore_reindexing: bool = False,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_segment(
        self,
        asset_id: str,
        segment_id: str,
        soft_delete: bool = True,
        **kwargs
    ) -> Response:
        ...

    async def fetch_asset_history_entities(
        self, asset_id: str, **kwargs
    ) -> Response:
        ...

    async def create_history_entity(
        self,
        asset_id: str,
        operation_description: str,
        operation_type: str,
        **kwargs,
    ) -> Response:
        ...
