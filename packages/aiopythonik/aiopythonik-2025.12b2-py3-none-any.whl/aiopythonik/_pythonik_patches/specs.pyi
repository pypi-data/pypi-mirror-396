# src/aiopythonik/_pythonik_patches/specs.pyi
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type, TypeVar, Union

import requests
from pydantic import BaseModel
from pythonik.models.assets.assets import Asset, AssetCreate
from pythonik.models.assets.collections import Collection, Content
from pythonik.models.assets.segments import BulkDeleteSegmentsBody, SegmentBody
from pythonik.models.assets.versions import (
    AssetVersion,
    AssetVersionCreate,
    AssetVersionFromAssetCreate,
)
from pythonik.models.base import Response as PythonikResponse
from pythonik.models.files.file import File, FileCreate, FileSetCreate
from pythonik.models.files.format import Component, FormatCreate
from pythonik.models.files.keyframe import Keyframe
from pythonik.models.files.proxy import Proxy
from pythonik.models.jobs.job_body import JobBody
from pythonik.models.metadata.fields import FieldCreate, FieldUpdate
from pythonik.models.metadata.views import ViewMetadata
from pythonik.models.mutation.metadata.mutate import UpdateMetadata
from pythonik.models.search.search_body import SearchBody
from requests import Response, Session

from .models import CreateViewRequest, UpdateViewRequest


T = TypeVar("T")


class Spec:
    server: str
    api_version: str = "v1"
    base_url: str
    session: Session
    timeout: int

    @classmethod
    def set_class_attribute(cls, name: str, value: Any) -> None:
        ...

    def __init__(
        self,
        session: Session,
        timeout: int = 3,
        base_url: str = "https://app.iconik.io",
    ) -> None:
        ...

    @staticmethod
    def _prepare_model_data(
        data: Union[BaseModel, Dict[str, Any]],
        exclude_defaults: bool = True
    ) -> Dict[str, Any]:
        ...

    @staticmethod
    def parse_response(
        response: Response,
        model: Optional[Type[BaseModel]] = None
    ) -> PythonikResponse:
        ...

    @classmethod
    def gen_url(cls, path: str) -> str:
        ...

    def send_request(self, method: str, path: str, **kwargs) -> Response:
        ...

    def _prepare_request(
        self, method: str, url: str, **kwargs
    ) -> requests.PreparedRequest:
        ...

    def _delete(self, path: str, **kwargs) -> Response:
        ...

    def _get(self, path: str, **kwargs) -> Response:
        ...

    def _patch(self, path: str, **kwargs) -> Response:
        ...

    def _post(self, path: str, **kwargs) -> Response:
        ...

    def _put(self, path: str, **kwargs) -> Response:
        ...


class AssetSpec(Spec):
    server: str = "API/assets/"
    _collection_spec: "CollectionSpec"

    def __init__(
        self,
        session: Session,
        timeout: int = 3,
        base_url: str = "https://app.iconik.io",
    ) -> None:
        ...

    @property
    def collections(self) -> "CollectionSpec":
        ...

    def permanently_delete(self, **kwargs) -> PythonikResponse:
        ...

    def bulk_delete(
        self,
        body: Union[Dict[str, Any], Any],
        permanently_delete: bool = False,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_asset(
        self,
        asset_id: str,
        body: Union[Asset, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def create(
        self,
        body: Union[AssetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_segment(
        self,
        asset_id: str,
        body: Union[SegmentBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_segment(
        self,
        asset_id: str,
        segment_id: str,
        body: Union[SegmentBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_segment(
        self,
        asset_id: str,
        segment_id: str,
        body: Union[SegmentBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def bulk_delete_segments(
        self,
        asset_id: str,
        body: Union[BulkDeleteSegmentsBody, Dict[str, Any]],
        immediately: bool = True,
        ignore_reindexing: bool = False,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete_segment(
        self,
        asset_id: str,
        segment_id: str,
        soft_delete: bool = True,
        **kwargs
    ) -> PythonikResponse:
        ...

    def create_version(
        self,
        asset_id: str,
        body: Union[AssetVersionCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_version_from_asset(
        self,
        asset_id: str,
        source_asset_id: str,
        body: Union[AssetVersionFromAssetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def partial_update_version(
        self, asset_id: str, version_id: str, body: AssetVersion, **kwargs
    ) -> PythonikResponse:
        ...

    def update_version(
        self, asset_id: str, version_id: str, body: AssetVersion, **kwargs
    ) -> PythonikResponse:
        ...

    def promote_version(
        self, asset_id: str, version_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def delete_old_versions(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def delete_version(
        self,
        asset_id: str,
        version_id: str,
        hard_delete: bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def fetch(self, **kwargs) -> PythonikResponse:
        ...

    def list_all(self, **kwargs) -> PythonikResponse:
        ...

    def fetch_asset_history_entities(
        self, asset_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def list_asset_history_entities(
        self, asset_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def create_history_entity(
        self,
        asset_id: str,
        operation_description: str,
        operation_type: str,
        **kwargs,
    ) -> PythonikResponse:
        ...


class CollectionSpec(Spec):
    server: str = "API/assets/"

    def delete(self, collection_id: str, **kwargs) -> PythonikResponse:
        ...

    def get(self, collection_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_info(self, collection_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_contents(self, collection_id: str, **kwargs) -> PythonikResponse:
        ...

    def create(
        self,
        body: Union[Collection, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def add_content(
        self,
        collection_id: str,
        body: Union[Content, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def fetch(self, **kwargs) -> PythonikResponse:
        ...

    def list_all(self, **kwargs) -> PythonikResponse:
        ...


class FilesSpec(Spec):
    server: str = "API/files/"

    def create_storage_file(
        self,
        storage_id: str,
        body: Union[File, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_asset_format_component(
        self,
        asset_id: str,
        format_id: str,
        body: Union[Component, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete_asset_file(
        self, asset_id: str, file_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def delete_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        keep_source: bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete_asset_keyframe(
        self, asset_id: str, keyframe_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_file(
        self, asset_id: str, file_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_file_set_files(
        self, asset_id: str, file_sets_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_keyframe(
        self, asset_id: str, keyframe_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_keyframes(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def create_asset_keyframe(
        self,
        asset_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_proxy(
        self, asset_id: str, proxy_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def update_asset_proxy(
        self,
        asset_id: str,
        proxy_id: str,
        body: Union[Proxy, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_asset_proxy(
        self,
        asset_id: str,
        body: Union[Proxy, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_keyframe(
        self,
        asset_id: str,
        keyframe_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_keyframe(
        self,
        asset_id: str,
        keyframe_id: str,
        body: Union[Keyframe, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_upload_id_for_keyframe(
        self, keyframe: Keyframe
    ) -> PythonikResponse:
        ...

    def get_upload_id_for_proxy(
        self, asset_id: str, proxy_id: str
    ) -> PythonikResponse:
        ...

    def get_s3_presigned_url(
        self,
        asset_id: str,
        proxy_id: str,
        upload_id: str,
        part_number: int,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_s3_complete_url(
        self, asset_id: str, proxy_id: str, upload_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_proxies(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def create_asset_format(
        self,
        asset_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_asset_file(
        self,
        asset_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_asset_filesets(
        self,
        asset_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_asset_file_sets(
        self,
        asset_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_file_sets_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        file_count: Optional[bool] = None,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_filesets(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_asset_formats(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_asset_format(
        self, asset_id: str, format_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def get_asset_files(self, asset_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_storage(self, storage_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_storages(self, **kwargs) -> PythonikResponse:
        ...

    def update_asset_format(
        self,
        asset_id: str,
        format_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_asset_format(
        self,
        asset_id: str,
        format_id: str,
        body: Union[FormatCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_asset_file_set(
        self,
        asset_id: str,
        file_set_id: str,
        body: Union[FileSetCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_asset_file(
        self,
        asset_id: str,
        file_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def partial_update_asset_file(
        self,
        asset_id: str,
        file_id: str,
        body: Union[FileCreate, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_formats_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_files_by_version(
        self,
        asset_id: str,
        version_id: str,
        per_page: Optional[int] = None,
        last_id: Optional[str] = None,
        generate_signed_url: Optional[bool] = None,
        content_disposition: Optional[str] = None,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_deleted_file_sets(self, **kwargs) -> PythonikResponse:
        ...

    def get_deleted_filesets(self, **kwargs) -> PythonikResponse:
        ...

    def get_deleted_formats(self, **kwargs) -> PythonikResponse:
        ...

    def create_mediainfo_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> PythonikResponse:
        ...

    def create_transcode_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> PythonikResponse:
        ...

    def get_files_by_checksum(
        self,
        checksum_or_file: Union[str, Path],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        chunk_size: int = 8192,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def _get_deleted_object_type(
        self, object_type: Literal["file_sets", "formats"], **kwargs
    ) -> Response:
        ...

    def fetch_asset_format_components(
        self, asset_id: str, format_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def list_asset_format_components(
        self, asset_id: str, format_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def fetch_storage_files(
        self, storage_id: str, **kwargs
    ) -> PythonikResponse:
        ...

    def list_storage_files(self, storage_id: str, **kwargs) -> PythonikResponse:
        ...


class JobSpec(Spec):
    server: str = "API/jobs/"

    def create(
        self,
        body: Union[JobBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update(
        self,
        job_id: str,
        body: Union[JobBody, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get(self, job_id: str, **kwargs) -> PythonikResponse:
        ...

    def cancel(self, job_id: str, **kwargs) -> PythonikResponse:
        ...


class MetadataSpec(Spec):
    server: str = "API/metadata/"

    def get_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def put_metadata_direct(
        self,
        object_type: str,
        object_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def put_object_view_metadata(
        self,
        asset_id: str,
        object_type: Literal["segments"],
        object_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def put_segment_view_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def put_segment_metadata(
        self,
        asset_id: str,
        segment_id: str,
        view_id: str,
        metadata: Union[UpdateMetadata, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_view(
        self,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_view(
        self,
        view_id: str,
        view: Union[UpdateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def replace_view(
        self,
        view_id: str,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_views(self, **kwargs) -> PythonikResponse:
        ...

    def get_view(
        self,
        view_id: str,
        merge_fields: Optional[bool] = None,
        **kwargs
    ) -> PythonikResponse:
        ...

    def delete_view(self, view_id: str, **kwargs) -> PythonikResponse:
        ...

    def get_object_metadata(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        view_id: str = None,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_collection_metadata(
        self,
        collection_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_segment_metadata(
        self,
        segment_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_object_metadata_direct(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        intercept_404: Union[ViewMetadata, bool] = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_asset_metadata_direct(
        self,
        asset_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_collection_metadata_direct(
        self,
        collection_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def get_segment_metadata_direct(
        self,
        segment_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_field(
        self,
        field_data: FieldCreate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_field(
        self,
        field_name: str,
        field_data: FieldUpdate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete_field(
        self,
        field_name: str,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def create_metadata_field(
        self,
        field_data: FieldCreate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def update_metadata_field(
        self,
        field_name: str,
        field_data: FieldUpdate,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...

    def delete_metadata_field(
        self,
        field_name: str,
        **kwargs,
    ) -> PythonikResponse:
        ...


class SearchSpec(Spec):
    server: str = "API/search/"

    def search(
        self,
        search_body: Union[SearchBody, Dict[str, Any]],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        scroll: Optional[bool] = None,
        scroll_id: Optional[str] = None,
        generate_signed_url: Optional[bool] = None,
        generate_signed_download_url: Optional[bool] = None,
        generate_signed_proxy_url: Optional[bool] = None,
        save_search_history: Optional[bool] = None,
        exclude_defaults: bool = True,
        **kwargs,
    ) -> PythonikResponse:
        ...
