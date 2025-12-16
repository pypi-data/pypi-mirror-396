"""
Asynchronous spec wrappers for pythonik.

This package provides asynchronous versions of all pythonik spec classes,
allowing them to be used in async applications without blocking the event loop.
"""

from .assets import AsyncAssetSpec
from .base import AsyncSpec, AsyncSpecWrapper
from .collection import AsyncCollectionSpec
from .files import AsyncFilesSpec
from .jobs import AsyncJobSpec
from .metadata import AsyncMetadataSpec
from .search import AsyncSearchSpec


__all__ = [
    "AsyncSpecWrapper",
    "AsyncSpec",
    "AsyncAssetSpec",
    "AsyncCollectionSpec",
    "AsyncFilesSpec",
    "AsyncJobSpec",
    "AsyncMetadataSpec",
    "AsyncSearchSpec",
]
