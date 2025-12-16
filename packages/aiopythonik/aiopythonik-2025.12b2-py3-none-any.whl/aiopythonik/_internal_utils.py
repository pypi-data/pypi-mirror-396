"""Utility functions for the aiopythonik package."""

import asyncio
from pathlib import Path
from typing import Any, Union

from ._pythonik_patches._internal_utils import calculate_md5


async def async_calculate_md5(
    file_path: Union[str, Path], chunk_size: int = 8192
) -> str:
    """
    Asynchronous version of calculate_md5.

    Args:
        file_path: Path to the file (string or Path object)
        chunk_size: Size of chunks to read (default 8192 bytes / 8KB)

    Returns:
        str: MD5 checksum as a hexadecimal string

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the path is not a file
        PermissionError: If permission is denied when accessing the file
        IOError: For other I/O errors
    """
    loop = asyncio.get_event_loop()

    def md5_calculator(*_args: Any, **_kwargs: Any) -> str:
        """Calculate MD5 checksum synchronously."""
        return calculate_md5(file_path, chunk_size)

    return await loop.run_in_executor(None, md5_calculator, None)
