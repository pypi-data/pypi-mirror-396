# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ResourceQueryParams"]


class ResourceQueryParams(TypedDict, total=False):
    query: Required[str]

    query_params: Required[Annotated[str, PropertyInfo(alias="queryParams")]]

    resources: Required[str]

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]

    folder_name: Annotated[str, PropertyInfo(alias="folderName")]
