"""
Patched Pydantic models for the Pythonik SDK that fix validation issues
with the Iconik API responses.

This module contains fixed versions of models that have validation issues
when dealing with actual API responses from Iconik.
"""

from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, RootModel
from pythonik.models.files.format import Format
from pythonik.models.metadata.view_responses import (
    ViewListResponse as _ViewListResponse,
)
from pythonik.models.metadata.view_responses import (
    ViewResponse as _ViewResponse,
)
from pythonik.models.metadata.views import (
    CreateViewRequest as _CreateViewRequest,
)
from pythonik.models.metadata.views import MetadataValues
from pythonik.models.metadata.views import (
    UpdateViewRequest as _UpdateViewRequest,
)
from pythonik.models.metadata.views import View as _View
from pythonik.models.metadata.views import ViewField as _ViewField
from pythonik.models.metadata.views import ViewMetadata as _ViewMetadata
from pythonik.models.metadata.views import ViewOption as _ViewOption
from pythonik.models.mutation.metadata.mutate import FieldValue as _FieldValue
from pythonik.models.mutation.metadata.mutate import (
    FieldValues as _FieldValues,
)
from pythonik.models.mutation.metadata.mutate import (
    UpdateMetadata as _UpdateMetadata,
)
from pythonik.models.search.search_response import Object as _Object
from pythonik.models.search.search_response import (
    SearchResponse as _SearchResponse,
)


class FieldValue(_FieldValue):
    """
    Patched version of FieldValue model with support for additional fields.

    The Iconik API returns field values that can include:
    - score: For tag_cloud fields (e.g., {"score": 1, "value": "John"})
    - label: For url and drop_down fields
      (e.g., {"label": "Click here", "value": "https://..."})

    This patched model adds these known fields as Optional and enables
    extra='allow' for future-proofing against new API fields.
    """

    model_config = ConfigDict(extra="allow")

    value: Any
    score: Optional[int] = None
    label: Optional[str] = None


class FieldValues(_FieldValues):
    """
    Patched version of FieldValues using the patched FieldValue model.

    This ensures that field_values lists use the enhanced FieldValue
    model that supports score and label fields.
    """

    field_values: Optional[List[FieldValue]] = None


class MutationMetadataValues(RootModel):
    """
    Patched version of MetadataValues (from mutation module) using
    the patched FieldValues model.

    This RootModel wraps a dictionary mapping field names to FieldValues,
    enabling proper parsing of metadata with score/label fields.
    """

    root: Dict[str, FieldValues]

    def __iter__(self):
        """Iterate over field names."""
        return iter(self.root)

    def __getitem__(self, item: str) -> FieldValues:
        """Get FieldValues by field name."""
        return self.root[item]


class UpdateMetadata(_UpdateMetadata):
    """
    Patched version of UpdateMetadata using the patched
    MutationMetadataValues model.

    Use this model when creating or updating metadata that includes
    tag_cloud fields (with scores) or url/dropdown fields (with labels).
    """

    metadata_values: Optional[MutationMetadataValues] = None


class ViewOption(_ViewOption):
    """Patched version of ViewOption model with nullable label."""

    label: Optional[str] = None
    value: Optional[str] = None


class ViewField(_ViewField):
    """
    Patched version of ViewField model with all potentially null fields
    made optional.

    Fixes validation error in views endpoint where the API returns null for
    the label field that is required in the original model.
    """

    name: str
    label: Optional[str] = None  # Changed from required to optional
    auto_set: Optional[bool] = None
    date_created: Optional[str] = None
    date_modified: Optional[str] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    field_type: Optional[str] = None
    field_id: Optional[str] = None  # Sometimes included
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


class ViewResponse(_ViewResponse):
    """Patched ViewResponse with nullable fields."""

    id: str
    name: str
    description: Optional[str] = None
    date_created: str
    date_modified: str
    view_fields: List[ViewField]
    fields: Optional[List[ViewField]] = None  # Sometimes the API includes this


class ViewListResponse(_ViewListResponse):
    """Patched ViewListResponse using patched ViewResponse model."""

    objects: List[ViewResponse]


class View(_View):
    """Patched View model with patched ViewField."""

    id: str
    name: str
    description: Optional[str] = None
    date_created: str
    date_modified: str
    view_fields: List[ViewField]


class CreateViewRequest(_CreateViewRequest):
    """Patched CreateViewRequest with patched ViewField."""

    name: str
    description: Optional[str] = None
    view_fields: List[ViewField]


class UpdateViewRequest(_UpdateViewRequest):
    """Patched UpdateViewRequest with patched ViewField."""

    name: Optional[str] = None
    description: Optional[str] = None
    view_fields: Optional[List[ViewField]] = None


class ViewMetadata(_ViewMetadata):
    date_created: Optional[str] = ""
    date_modified: Optional[str] = ""
    metadata_values: Optional[MetadataValues] = None
    object_id: Optional[str] = ""
    object_type: Optional[str] = ""
    version_id: Optional[str] = ""

    # pylint: disable=line-too-long
    def __init__(self, **data: Any) -> None:
        """Initialize with fallback for metadata_values.

        This method transforms the input data structure when 'metadata_values'
        is not provided by moving 'values' fields to 'field_values' within a
        nested structure.

        Args:
            **data: Input data for initialization
        """
        if "metadata_values" not in data or data["metadata_values"] is None:
            metadata_values = {}

            # Check if any dictionary in values contains a 'values' key
            has_values = any(
                "values" in item
                for item in data.values()
                if isinstance(item, dict)
            )

            if has_values:
                # Transform each field
                for key, value in list(data.items()):
                    if isinstance(value, dict) and "values" in value:
                        # Get the values list, ensuring it's not None
                        values_list = value.get("values", [])
                        if values_list is None:
                            # If values is None, create an empty FieldValues with None
                            metadata_values[key] = {"field_values": None}
                        else:
                            # Otherwise, use the values list
                            metadata_values[key] = {"field_values": values_list}
                        # Don't remove the key from the original data to preserve it

                # Set metadata_values in the data dictionary
                data["metadata_values"] = MetadataValues(root=metadata_values)

        # Initialize with all data fields
        super().__init__(**data)


class Object(_Object):
    formats: Optional[List[Format]] = []
    in_collections: Optional[List[str]] = []
    permissions: Optional[List[str]] = []
    external_id: Optional[str] = None
    external_link: Optional[str] = None
    model_config = {"extra": "allow"}


class SearchResponse(_SearchResponse):
    objects: Optional[List[Object]] = []


# Update forward references
CreateViewRequest.model_rebuild()
FieldValue.model_rebuild()
FieldValues.model_rebuild()
MutationMetadataValues.model_rebuild()
Object.model_rebuild()
SearchResponse.model_rebuild()
UpdateMetadata.model_rebuild()
UpdateViewRequest.model_rebuild()
View.model_rebuild()
ViewField.model_rebuild()
ViewListResponse.model_rebuild()
ViewMetadata.model_rebuild()
ViewOption.model_rebuild()
ViewResponse.model_rebuild()
