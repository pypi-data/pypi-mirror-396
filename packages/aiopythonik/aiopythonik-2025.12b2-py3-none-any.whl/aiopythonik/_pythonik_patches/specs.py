from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type, Union

import requests
from pydantic import BaseModel
from pythonik.models.base import PaginatedResponse, Response
from pythonik.models.files.file import File, Files
from pythonik.models.search.search_body import SearchBody
from pythonik.specs.assets import AssetSpec as _AssetSpec
from pythonik.specs.base import Spec as _Spec
from pythonik.specs.collection import CollectionSpec as _CollectionSpec
from pythonik.specs.files import FilesSpec as _FilesSpec
from pythonik.specs.jobs import JobSpec as _JobSpec
from pythonik.specs.metadata import MetadataSpec as _MetadataSpec
from pythonik.specs.search import SearchSpec as _SearchSpec

from ._internal_utils import calculate_md5
from ._logger import logger
from .models import (
    CreateViewRequest,
    SearchResponse,
    UpdateViewRequest,
    ViewListResponse,
    ViewMetadata,
    ViewResponse,
)


__all__ = [
    "AssetSpec",
    "CollectionSpec",
    "FilesSpec",
    "JobSpec",
    "MetadataSpec",
    "SearchSpec",
    "Spec",
]


class Spec(_Spec):

    @staticmethod
    def parse_response(
        response: requests.Response,
        model: Optional[Type[BaseModel]] = None
    ) -> Response:
        """
        Enhanced response parser that uses logging instead of print statements.

        Args:
            response: The HTTP response from the API
            model: Optional Pydantic model to validate the response against

        Returns:
            Response object containing the parsed response
        """
        if response.ok:
            logger.debug(response.text)
            if model:
                data = response.json()
                model_instance = model.model_validate(data)
                return Response(response=response, data=model_instance)
        return Response(response=response, data=None)

    def send_request(self, method, path, **kwargs) -> requests.Response:
        """
        Enhanced request sender with better logging.

        Args:
            method: HTTP method to use
            path: API endpoint path
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response object from the API
        """
        url = self.gen_url(path)
        logger.debug("Sending {} request to {}", method, url)
        request = self._prepare_request(method, url, **kwargs)
        response = self.session.send(request, timeout=self.timeout)
        return response

    def _prepare_request(self, method, url, **kwargs):
        """Prepare the request object."""
        request = requests.Request(
            method=method, url=url, headers=self.session.headers, **kwargs
        )
        return self.session.prepare_request(request)


class AssetSpec(Spec, _AssetSpec):

    def fetch(self, **kwargs) -> Response:
        """
        Get list of assets.

        Args:
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response(model=PaginatedResponse) containing paginated asset list
        """
        resp = self._get(self.gen_url("assets/"), **kwargs)
        return self.parse_response(resp, PaginatedResponse)

    list_all = fetch

    def fetch_asset_history_entities(self, asset_id: str, **kwargs) -> Response:
        """
        Get list of history entities for asset.

        Args:
            asset_id: ID of the asset
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response(model=PaginatedResponse) containing history entities
        """
        resp = self._get(self.gen_url(f"assets/{asset_id}/history/"), **kwargs)
        return self.parse_response(resp, PaginatedResponse)

    list_asset_history_entities = fetch_asset_history_entities

    def create_history_entity(
        self,
        asset_id: str,
        operation_description: str,
        operation_type: str,
        **kwargs,
    ) -> Response:
        """
        Create an asset history entity.

        Args:
            asset_id: ID of the asset
            operation_description: Description of the operation
            operation_type: Type of operation (e.g., VERSION_CREATE, ADD_FORMAT)
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with history entry creation status

        Raises:
            ValueError: If operation_type is not a valid operation type
        """
        operation_types = [
            "EXPORT",
            "TRANSCODE",
            "ANALYZE",
            "ADD_FORMAT",
            "DELETE_FORMAT",
            "RESTORE_FORMAT",
            "DELETE_FILESET",
            "DELETE_FILE",
            "RESTORE_FILESET",
            "MODIFY_FILESET",
            "APPROVE",
            "REJECT",
            "DOWNLOAD",
            "METADATA",
            "CUSTOM",
            "TRANSCRIPTION",
            "VERSION_CREATE",
            "VERSION_DELETE",
            "VERSION_UPDATE",
            "VERSION_PROMOTE",
            "RESTORE",
            "RESTORE_FROM_GLACIER",
            "ARCHIVE",
            "RESTORE_ARCHIVE",
            "DELETE",
            "TRANSFER",
            "UNLINK_SUBCLIP",
            "FACE_RECOGNITION",
        ]
        if operation_type not in operation_types:
            raise ValueError(
                f"operation_type must be one of: {'|'.join(operation_types)}"
            )
        body = {
            "operation_description": operation_description,
            "operation_type": operation_type,
        }
        resp = self._post(
            self.gen_url(f"assets/{asset_id}/history/"), json=body, **kwargs
        )
        return self.parse_response(resp, None)


class CollectionSpec(Spec, _CollectionSpec):

    def fetch(self, **kwargs) -> Response:
        """
        Get list of collections.

        Args:
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response(model=PaginatedResponse) containing collection list
        """
        resp = self._get(self.gen_url("collections/"), **kwargs)
        return self.parse_response(resp, PaginatedResponse)

    list_all = fetch


class FilesSpec(Spec, _FilesSpec):

    def create_storage_file(
        self,
        storage_id: str,
        body: Union[File, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """
        Create file without associating it to an asset.

        Args:
            storage_id: The ID of the storage to retrieve
            body: Storage file creation parameters, either as File model or dict
            exclude_defaults: Whether to exclude default values when dumping
                Pydantic models
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=PaginatedResponse) with created file information
        """
        json_data = self._prepare_model_data(
            body, exclude_defaults=exclude_defaults
        )
        resp = self._post(
            self.gen_url(f"storages/{storage_id}/files/"),
            json=json_data,
            **kwargs,
        )
        return self.parse_response(resp, PaginatedResponse)

    def fetch_asset_format_components(
        self, asset_id: str, format_id: str, **kwargs
    ) -> Response:
        """
        Get all components for a format in an asset.

        Args:
            asset_id: The ID of the asset
            format_id: The ID of the format to retrieve
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=PaginatedResponse) containing format components
        """
        resp = self._get(
            self.gen_url(f"assets/{asset_id}/formats/{format_id}/components/"),
            **kwargs,
        )
        return self.parse_response(resp, PaginatedResponse)

    list_asset_format_components = fetch_asset_format_components

    def fetch_storage_files(self, storage_id: str, **kwargs) -> Response:
        """
        Get all files on a storage, or files in a storage folder.

        Args:
            storage_id: The ID of the storage to retrieve
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=PaginatedResponse) containing storage files
        """
        resp = self._get(
            self.gen_url(f"storages/{storage_id}/files/"), **kwargs
        )
        return self.parse_response(resp, PaginatedResponse)

    list_storage_files = fetch_storage_files

    def _get_deleted_object_type(
        self, object_type: Literal["file_sets", "formats"], **kwargs
    ) -> Response:
        """
        Get deleted object type.

        Args:
            object_type: The type of object to retrieve
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=None) containing deleted objects

        Raises:
            ValueError: If object_type is not 'file_sets' or 'formats'
        """
        if object_type not in ["file_sets", "formats"]:
            raise ValueError("object_type must be one of file_sets or formats")
        resp = self._get(self.gen_url(f"delete_queue/{object_type}/"), **kwargs)
        return self.parse_response(resp, None)

    def get_deleted_file_sets(self, **kwargs) -> Response:
        """
        Get deleted file sets.

        Args:
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=None) containing deleted file sets
        """
        return self._get_deleted_object_type("file_sets", **kwargs)

    # Create method alias
    get_deleted_filesets = get_deleted_file_sets

    def get_deleted_formats(self, **kwargs) -> Response:
        """
        Get deleted formats.

        Args:
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response(model=None) containing deleted formats
        """
        return self._get_deleted_object_type("formats", **kwargs)

    def get_files_by_checksum(
        self,
        checksum_or_file: Union[str, Path],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        chunk_size: int = 8192,
        **kwargs,
    ) -> Response:
        """
        Get files by their checksum. Accepts either a checksum string or a file
        path. If a file path is provided, calculates the MD5 checksum
        automatically.

        Args:
            checksum_or_file: Either an MD5 checksum string or a path to a file
            per_page: Optional number of items per page
            page: Optional page number
            chunk_size: Size of chunks when reading file (default 8192)
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with Files model containing matching files

        Raises:
            FileNotFoundError: If a file path is provided and file doesn't exist
            PermissionError: If there's no read permission for the provided file
            IOError: For other IO-related errors
            ValueError: If path is not a file or checksum format is invalid
            TypeError: If checksum_or_file is not a string or Path object
        """
        # Calculate or extract the checksum
        if isinstance(checksum_or_file, (str, Path)):
            try:
                path = Path(checksum_or_file)
                if path.exists():
                    checksum = calculate_md5(path, chunk_size=chunk_size)
                else:
                    checksum = str(checksum_or_file)
            except (TypeError, ValueError):
                checksum = str(checksum_or_file)
        else:
            raise TypeError("checksum_or_file must be a string or Path object")
        # Validate the checksum format
        if (
            not all(c in "0123456789abcdefABCDEF" for c in checksum)
            or len(checksum) != 32
        ):
            raise ValueError("Invalid MD5 checksum format")
        # Prepare request parameters
        params: Dict[str, Any] = {}
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page
        kwargs_params = kwargs.pop("params", {})
        params.update(kwargs_params)
        kwargs["params"] = params
        # Make the API request using the calculated/extracted checksum
        response = self._get(f"files/checksum/{checksum}/", **kwargs)
        return self.parse_response(response, Files)

    def create_mediainfo_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> Response:
        """
        Create a job for extracting mediainfo.

        Args:
            asset_id: ID of the asset
            file_id: ID of the file
            priority: Job priority 1-10. Default is 5
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response(model=None) with job creation status
        """
        body = {"priority": priority}
        resp = self._post(
            self.gen_url(f"assets/{asset_id}/files/{file_id}/mediainfo"),
            json=body,
            **kwargs,
        )
        return self.parse_response(resp, None)

    def create_transcode_job(
        self,
        asset_id: str,
        file_id: str,
        priority: Optional[int] = 5,
        **kwargs
    ) -> Response:
        """
        Create a transcode job for proxy and keyframes.

        Args:
            asset_id: ID of the asset
            file_id: ID of the file
            priority: Job priority 1-10. Default is 5
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response(model=None) with job creation status
        """
        body = {"priority": priority}
        resp = self._post(
            self.gen_url(f"assets/{asset_id}/files/{file_id}/keyframes"),
            json=body,
            **kwargs,
        )
        return self.parse_response(resp, None)


class JobSpec(Spec, _JobSpec):
    pass


class MetadataSpec(Spec, _MetadataSpec):

    def get_object_metadata(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        view_id: str = None,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Get object metadata by object type, object ID and view ID.

        Args:
            object_type: The type of object to retrieve
            object_id: ID of the object to retrieve
            view_id: ID of the view to retrieve
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response with ViewMetadata model containing the object metadata

        Raises:
            ValueError: If object_type is not 'assets', 'collections', or
                'segments'
        """
        if object_type not in ["assets", "collections", "segments"]:
            raise ValueError(
                "object_type must be one of assets, collections, or segments"
            )

        url = (
            self.gen_url(f"{object_type}/{object_id}/views/{view_id}/")
            if view_id is not None else
            self.gen_url(f"{object_type}/{object_id}/")
        )
        resp = self._get(url, **kwargs)

        if intercept_404 and resp.status_code == 404:
            parsed_response = self.parse_response(resp, ViewMetadata)
            parsed_response.data = intercept_404
            parsed_response.response.raise_for_status_404 = (
                parsed_response.response.raise_for_status
            )

            parsed_response.response.raise_for_status = lambda: logger.warning(
                "raise for status disabled due to intercept_404, please call"
                " raise_for_status_404 to throw an error on 404"
            )
            return parsed_response

        return self.parse_response(resp, ViewMetadata)

    def get_asset_metadata(
        self,
        asset_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            asset_id: The asset ID to get metadata for
            view_id: The view ID to get metadata from
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata(
            object_type="assets",
            object_id=asset_id,
            view_id=view_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_collection_metadata(
        self,
        collection_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            collection_id: The collection ID to get metadata for
            view_id: The view ID to get metadata from
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata(
            object_type="collections",
            object_id=collection_id,
            view_id=view_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_segment_metadata(
        self,
        segment_id: str,
        view_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            segment_id: The segment ID to get metadata for
            view_id: The view ID to get metadata from
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata(
            object_type="segments",
            object_id=segment_id,
            view_id=view_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_object_metadata_direct(
        self,
        object_type: Literal["assets", "collections", "segments"],
        object_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Get object metadata by object type and object ID.

        Args:
            object_type: The type of object to retrieve
            object_id: ID of the object to retrieve
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response with ViewMetadata model containing the object metadata

        Raises:
            ValueError: If object_type is not 'assets', 'collections', or
                'segments'
        """
        return self.get_object_metadata(
            object_type=object_type,
            object_id=object_id,
            view_id=None,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_asset_metadata_direct(
        self,
        asset_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            asset_id: The asset ID to get metadata for
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata_direct(
            object_type="assets",
            object_id=asset_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_collection_metadata_direct(
        self,
        collection_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            collection_id: The collection ID to get metadata for
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata_direct(
            object_type="collections",
            object_id=collection_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_segment_metadata_direct(
        self,
        segment_id: str,
        intercept_404: ViewMetadata | bool = False,
        **kwargs,
    ) -> Response:
        """
        Given an asset id and the asset's view id, fetch metadata from the
        asset's view

        Args:
            segment_id: The segment ID to get metadata for
            intercept_404: Iconik returns a 404 when a view has no metadata,
                intercept_404 will intercept that error and return the
                ViewMetadata model provided
            **kwargs: Additional kwargs to pass to the request

        Note:
            You can no longer call response.raise_for_status, so be careful
            using this. Call raise_for_status_404 if you still want to raise
            status on 404 error
        """
        return self.get_object_metadata_direct(
            object_type="segments",
            object_id=segment_id,
            intercept_404=intercept_404,
            **kwargs,
        )

    def get_views(self, **kwargs) -> Response:
        """
        List all views defined in the system.

        Args:
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with ViewListResponse model containing all views

        Raises:
            - 400 Bad request
            - 401 Token is invalid
        """
        resp = self._get(self.gen_url("views/"), **kwargs)
        return self.parse_response(resp, ViewListResponse)

    def get_view(
        self, view_id: str, merge_fields: bool = None, **kwargs
    ) -> Response:
        """
        Get a specific view from Iconik.

        Args:
            view_id: ID of the view to retrieve
            merge_fields: Optional boolean to control field merging
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with ViewResponse model containing the requested view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        params = {}
        if merge_fields is not None:
            params["merge_fields"] = merge_fields
        resp = self._get(
            self.gen_url(f"views/{view_id}/"), params=params, **kwargs
        )
        return self.parse_response(resp, ViewResponse)

    def create_view(
        self,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """
        Create a new view in Iconik.

        Args:
            view: The view to create, either as CreateViewRequest model or dict
            exclude_defaults: Whether to exclude default values when dumping
                Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with ViewResponse model containing the created view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
        """
        json_data = self._prepare_model_data(
            view, exclude_defaults=exclude_defaults
        )
        resp = self._post(self.gen_url("views/"), json=json_data, **kwargs)
        return self.parse_response(resp, ViewResponse)

    def update_view(
        self,
        view_id: str,
        view: Union[UpdateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """
        Update an existing view in Iconik.

        Args:
            view_id: ID of the view to update
            view: The view updates, either as UpdateViewRequest model or dict
            exclude_defaults: Whether to exclude default values when dumping
                Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with ViewResponse model containing the updated view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        json_data = self._prepare_model_data(
            view, exclude_defaults=exclude_defaults
        )
        resp = self._patch(
            self.gen_url(f"views/{view_id}/"), json=json_data, **kwargs
        )
        return self.parse_response(resp, ViewResponse)

    def replace_view(
        self,
        view_id: str,
        view: Union[CreateViewRequest, Dict[str, Any]],
        exclude_defaults: bool = True,
        **kwargs,
    ) -> Response:
        """
        Replace an existing view in Iconik with a new one.

        Unlike update_view which allows partial updates, this method requires
        all fields to be specified as it completely replaces the view.

        Args:
            view_id: ID of the view to replace
            view: The complete new view data, either as CreateViewRequest
                model or dict
            exclude_defaults: Whether to exclude default values when dumping
                Pydantic models
            **kwargs: Additional kwargs to pass to the request

        Returns:
            Response with ViewResponse model containing the replaced view

        Raises:
            - 400 Bad request
            - 401 Token is invalid
            - 404 Metadata view doesn't exist
        """
        json_data = self._prepare_model_data(
            view, exclude_defaults=exclude_defaults
        )
        resp = self._put(
            self.gen_url(f"views/{view_id}/"), json=json_data, **kwargs
        )
        return self.parse_response(resp, ViewResponse)


class SearchSpec(Spec, _SearchSpec):

    # pylint: disable=too-many-positional-arguments
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
    ) -> Response:
        """
        Search iconik.
        Corresponds to POST /v1/search/

        Args:
            search_body: Search parameters, either as SearchBody model or dict.
            per_page: The number of documents for each page.
            page: Which page number to fetch.
            scroll: If true, uses scroll pagination. (Deprecated, use
                search_after in body).
            scroll_id: Scroll ID for scroll pagination. (Deprecated).
            generate_signed_url: Set to false if you don't need a URL, will
                speed things up.
            generate_signed_download_url: Set to true if you also want the
                file download URLs generated.
            generate_signed_proxy_url: Set to true if you want to generate
                signed download urls for proxies.
            save_search_history: Set to false if you don't want to save the
                search to the history.
            exclude_defaults: Whether to exclude default values when dumping
                Pydantic models for the request body.
            **kwargs: Additional kwargs to pass to the request (e.g., headers).

        Returns:
            Response with SearchResponse data model.
        """
        json_data = self._prepare_model_data(
            search_body, exclude_defaults=exclude_defaults
        )

        params = {}
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page
        if scroll is not None:
            params["scroll"] = scroll
        if scroll_id is not None:
            params["scroll_id"] = scroll_id
        if generate_signed_url is not None:
            params["generate_signed_url"] = generate_signed_url
        if generate_signed_download_url is not None:
            params["generate_signed_download_url"] = (
                generate_signed_download_url  # pylint: disable=line-too-long
            )
        if generate_signed_proxy_url is not None:
            params["generate_signed_proxy_url"] = generate_signed_proxy_url
        if save_search_history is not None:
            params["save_search_history"] = save_search_history

        resp = self._post(
            self.gen_url("search/"),
            json=json_data,
            params=params if params else None,
            **kwargs,
        )
        return self.parse_response(resp, SearchResponse)
