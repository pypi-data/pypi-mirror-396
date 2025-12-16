"""
Utility functions for the Pythonik SDK.

This module contains utility functions that are used by the Pythonik SDK
extensions, but are not part of the core SDK.
"""

import hashlib
from pathlib import Path
from typing import Optional, Union


def calculate_md5(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
    """
    Calculate the MD5 hash of a file.

    Args:
        file_path: Path to the file to hash
        chunk_size: Size of chunks to read from the file

    Returns:
        MD5 hash as a hexadecimal string

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        IsADirectoryError: If file_path points to a directory
        ValueError: If file_path is not a valid path
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Path is not a file: {path}")
    md5_hash = hashlib.md5()
    with path.open("rb") as file:
        while True:
            data = file.read(chunk_size)
            if not data:
                break
            md5_hash.update(data)
    return md5_hash.hexdigest()


def batch_calculate_md5(
    file_paths: list[Union[str, Path]],
    chunk_size: int = 8192
) -> dict[str, Optional[str]]:
    """
    Calculate MD5 hashes for multiple files.

    Args:
        file_paths: List of file paths to hash
        chunk_size: Size of chunks to read from each file

    Returns:
        Dictionary mapping file paths to their MD5 hashes.
        If a file could not be hashed, its value will be None.
    """
    results = {}
    for path in file_paths:
        str_path = str(path)
        try:
            results[str_path] = calculate_md5(path, chunk_size)
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            ValueError,
        ):
            results[str_path] = None
    return results
