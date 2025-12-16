# src/aiopythonik/specs/files.pyi
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pythonik.models.base import Response
from pythonik.models.files.file import File, FileCreate, FileSetCreate
from pythonik.models.files.format import Component, FormatCreate
from pythonik.models.files.keyframe import Keyframe
from pythonik.models.files.proxy import Proxy

from .._pythonik_patches import FilesSpec
from ..rate_limiting import RateLimitHandler


class AsyncFilesSpec:
    _sync_spec: FilesSpec
    _executor: Optional[ThreadPoolExecutor]
    _rate_limit_handler: Optional[RateLimitHandler]

    def __init__(
        self,
        sync_spec: FilesSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ) -> None:
        ...

    async def get_storages(self, **kwargs) -> Response:
        ...

    async def get_storage(self, storage_id: str, **kwargs) -> Response:
        ...

    async def update_storage(
        self, storage_id: str, storage_data: Dict[str, Any], **kwargs
    ) -> Response:
        ...

    async def fetch_storage_files(self, storage_id: str, **kwargs) -> Response:
        ...

    async def create_storage_file(
        self,
        storage_id: str,
        body: Union[File, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_files(self, asset_id: str, **kwargs) -> Response:
        ...

    async def create_asset_file(
        self,
        asset_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_file(
        self, asset_id: str, file_id: str, **kwargs
    ) -> Response:
        ...

    async def update_asset_file(
        self,
        asset_id: str,
        file_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_asset_file(
        self,
        asset_id: str,
        file_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_asset_file(
        self, asset_id: str, file_id: str, **kwargs
    ) -> Response:
        ...

    async def create_asset_format(
        self,
        asset_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_format(
        self, asset_id: str, format_id: str, **kwargs
    ) -> Response:
        ...

    async def get_asset_formats(self, asset_id: str, **kwargs) -> Response:
        ...

    async def update_asset_format(
        self,
        asset_id: str,
        format_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_asset_format(
        self,
        asset_id: str,
        format_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def create_asset_format_component(
        self,
        asset_id: str,
        format_id: str,
        body: Union[Component, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def fetch_asset_format_components(
        self, asset_id: str, format_id: str, **kwargs
    ) -> Response:
        ...

    async def create_asset_file_sets(
        self,
        asset_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def create_asset_filesets(
        self,
        asset_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_filesets(self, asset_id: str, **kwargs) -> Response:
        ...

    async def get_asset_file_sets_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        file_count: Optional[bool] = None,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_file_set_files(
        self, asset_id: str, file_sets_id: str, **kwargs
    ) -> Response:
        ...

    async def update_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        keep_source: bool = False,
        **kwargs,
    ) -> Response:
        ...

    async def get_deleted_file_sets(self, **kwargs) -> Response:
        ...

    async def get_deleted_filesets(self, **kwargs) -> Response:
        ...

    async def get_deleted_formats(self, **kwargs) -> Response:
        ...

    async def get_asset_proxies(self, asset_id: str, **kwargs) -> Response:
        ...

    async def get_asset_proxy(
        self, asset_id: str, proxy_id: str, **kwargs
    ) -> Response:
        ...

    async def create_asset_proxy(
        self,
        asset_id: str,
        body: Union[Proxy, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_asset_proxy(
        self,
        asset_id: str,
        proxy_id: str,
        body: Union[Proxy, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def get_upload_id_for_proxy(
        self, asset_id: str, proxy_id: str
    ) -> Response:
        ...

    async def get_s3_presigned_url(
        self,
        asset_id: str,
        proxy_id: str,
        upload_id: str,
        part_number: int,
        **kwargs,
    ) -> Response:
        ...

    async def get_s3_complete_url(
        self, asset_id: str, proxy_id: str, upload_id: str, **kwargs
    ) -> Response:
        ...

    async def get_asset_keyframes(self, asset_id: str, **kwargs) -> Response:
        ...

    async def get_asset_keyframe(
        self, asset_id: str, keyframe_id: str, **kwargs
    ) -> Response:
        ...

    async def create_asset_keyframe(
        self,
        asset_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def update_keyframe(
        self,
        asset_id: str,
        keyframe_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def partial_update_keyframe(
        self,
        asset_id: str,
        keyframe_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        ...

    async def delete_asset_keyframe(
        self, asset_id: str, keyframe_id: str, **kwargs
    ) -> Response:
        ...

    async def get_upload_id_for_keyframe(self, keyframe: Keyframe) -> Response:
        ...

    async def get_asset_formats_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        **kwargs,
    ) -> Response:
        ...

    async def get_asset_files_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        generate_signed_url: Optional[bool] = None,
        content_disposition: Optional[str] = None,
        **kwargs,
    ) -> Response:
        ...

    async def create_mediainfo_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> Response:
        ...

    async def create_transcode_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> Response:
        ...

    async def get_files_by_checksum(
        self,
        checksum_or_file: Union[str, Path],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        chunk_size: int = 8192,
        **kwargs,
    ) -> Response:
        ...
