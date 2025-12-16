# src/aiopythonik/_pythonik_patches/models.pyi
from typing import Any, Dict, Iterator, List, Optional

from pydantic import BaseModel, RootModel
from pythonik.models.files.format import Format
from pythonik.models.metadata.views import MetadataValues


class FieldValue(BaseModel):
    """
    Patched version of FieldValue model with support for additional fields.

    The Iconik API returns field values that can include:
    - score: For tag_cloud fields (e.g., {"score": 1, "value": "John"})
    - label: For url and drop_down fields
    """

    value: Any
    score: Optional[int] = None
    label: Optional[str] = None

    class Config:
        extra = "allow"


class FieldValues(BaseModel):
    """
    Patched version of FieldValues using the patched FieldValue model.
    """

    field_values: Optional[List[FieldValue]] = None


class MutationMetadataValues(RootModel[Dict[str, FieldValues]]):
    """
    Patched version of MetadataValues (from mutation module) using
    the patched FieldValues model.
    """

    root: Dict[str, FieldValues]

    def __iter__(self) -> Iterator[str]:
        ...

    def __getitem__(self, item: str) -> FieldValues:
        ...


class UpdateMetadata(BaseModel):
    """
    Patched version of UpdateMetadata using the patched
    MutationMetadataValues model.
    """

    metadata_values: Optional[MutationMetadataValues] = None


class ViewOption(BaseModel):
    """Patched version of ViewOption model with nullable label."""

    label: Optional[str] = None
    value: Optional[str] = None


class ViewField(BaseModel):
    """
    Patched version of ViewField model with all potentially null fields
    made optional.
    """

    name: str
    label: Optional[str] = None
    auto_set: Optional[bool] = None
    date_created: Optional[str] = None
    date_modified: Optional[str] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    field_type: Optional[str] = None
    field_id: Optional[str] = None
    hide_if_not_set: Optional[bool] = None
    is_block_field: Optional[bool] = None
    is_warning_field: Optional[bool] = None
    mapped_field_name: Optional[str] = None
    max_value: Optional[int] = None
    min_value: Optional[int] = None
    multi: Optional[bool] = None
    options: Optional[List[ViewOption]] = None
    read_only: Optional[bool] = None
    representative: Optional[bool] = None
    required: Optional[bool] = None
    sortable: Optional[bool] = None
    source_url: Optional[str] = None
    use_as_facet: Optional[bool] = None


class ViewResponse(BaseModel):
    """Patched ViewResponse with nullable fields."""

    id: str
    name: str
    description: Optional[str] = None
    date_created: str
    date_modified: str
    view_fields: List[ViewField]
    fields: Optional[List[ViewField]] = None


class ViewListResponse(BaseModel):
    """Patched ViewListResponse using patched ViewResponse model."""

    objects: List[ViewResponse]


class View(BaseModel):
    """Patched View model with patched ViewField."""

    id: str
    name: str
    description: Optional[str] = None
    date_created: str
    date_modified: str
    view_fields: List[ViewField]


class CreateViewRequest(BaseModel):
    """Patched CreateViewRequest with patched ViewField."""

    name: str
    description: Optional[str] = None
    view_fields: List[ViewField]


class UpdateViewRequest(BaseModel):
    """Patched UpdateViewRequest with patched ViewField."""

    name: Optional[str] = None
    description: Optional[str] = None
    view_fields: Optional[List[ViewField]] = None


class ViewMetadata(BaseModel):
    """Patched ViewMetadata class with optional fields."""

    date_created: Optional[str] = ""
    date_modified: Optional[str] = ""
    metadata_values: Optional[MetadataValues] = None
    object_id: Optional[str] = ""
    object_type: Optional[str] = ""
    version_id: Optional[str] = ""

    def __init__(self, **data: Any) -> None:
        """
        Initialize with fallback for metadata_values.

        This method transforms the input data structure when 'metadata_values'
        is not provided by moving 'values' fields to 'field_values' within a
        nested structure.

        Args:
            **data: Input data for initialization
        """
        ...


class Object(BaseModel):
    """Patched Object model with optional fields."""

    formats: Optional[List[Format]] = []
    in_collections: Optional[List[str]] = []
    permissions: Optional[List[str]] = []
    external_id: Optional[str] = None
    external_link: Optional[str] = None

    class Config:
        extra = "allow"


class SearchResponse(BaseModel):
    """Patched SearchResponse with optional objects field."""

    objects: Optional[List[Object]] = []
