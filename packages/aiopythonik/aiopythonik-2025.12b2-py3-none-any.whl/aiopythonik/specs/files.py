"""Asynchronous wrapper for the pythonik FilesSpec."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Union

from pythonik.models.base import Response

from .._internal_utils import async_calculate_md5
from .._pythonik_patches import FilesSpec
from .base import AsyncSpecWrapper


class AsyncFilesSpec(AsyncSpecWrapper):
    """
    Asynchronous wrapper for the pythonik FilesSpec.

    This class provides async versions of all methods in the FilesSpec,
    running them in a thread pool to avoid blocking the event loop.
    """

    def __init__(
        self,
        sync_spec: FilesSpec,
        executor: Optional[Any] = None,
        rate_limit_handler: Optional[Any] = None,
    ):
        """
        Initialize the async files spec.

        Args:
            sync_spec: The synchronous files spec to wrap
            executor: Optional executor to use for running sync operations
            rate_limit_handler: Optional handler for rate limiting
        """
        super().__init__(
            sync_spec=sync_spec,
            executor=executor,
            rate_limit_handler=rate_limit_handler,
        )

    # noinspection Annotator
    async def get_files_by_checksum(
        self,
        checksum_or_file: Union[str, Path],
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        chunk_size: int = 8192,
        **kwargs,
    ) -> Response:
        """
        Asynchronous version of get_files_by_checksum.

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
            Response with Files model

        Raises:
            FileNotFoundError: If a file path is provided and file doesn't exist
            PermissionError: If there's no read permission for the provided file
            IOError: For other IO-related errors
            ValueError: If path is not a file or checksum format is invalid

        Examples:
            # Using a checksum string directly
            >>> client = AsyncPythonikClient(app_id='...', auth_token='...')
            >>> response = await client.files().get_files_by_checksum(
            ...     'd41d8cd98f00b204e9800998ecf8427e'
            ... )

            # Using a file path
            >>> response = await client.files().get_files_by_checksum(
            ...     'path/to/your/file.txt'
            ... )
        """
        if isinstance(checksum_or_file, (str, Path)):
            try:
                path = Path(checksum_or_file)
                if path.exists() and path.is_file():
                    checksum = await async_calculate_md5(path, chunk_size)
                else:
                    checksum = str(checksum_or_file)
            except (TypeError, ValueError):
                checksum = str(checksum_or_file)
        else:
            raise TypeError("checksum_or_file must be a string or Path object")
        if (
            not all(c in "0123456789abcdefABCDEF" for c in checksum)
            or len(checksum) != 32
        ):
            raise ValueError("Invalid MD5 checksum format")
        params: Dict[str, Any] = {}
        if per_page is not None:
            params["per_page"] = per_page
        if page is not None:
            params["page"] = page
        kwargs_params = kwargs.pop("params", {})
        params.update(kwargs_params)
        kwargs["params"] = params
        loop = asyncio.get_event_loop()

        def call_get_files_by_checksum(*_args: Any, **_kwargs: Any) -> Any:
            """Call the synchronous get_files_by_checksum method."""
            return self._sync_spec.get_files_by_checksum(
                checksum,
                per_page=per_page,
                page=page,
                chunk_size=chunk_size,
                **kwargs,
            )

        return await loop.run_in_executor(
            self._executor, call_get_files_by_checksum, None
        )
