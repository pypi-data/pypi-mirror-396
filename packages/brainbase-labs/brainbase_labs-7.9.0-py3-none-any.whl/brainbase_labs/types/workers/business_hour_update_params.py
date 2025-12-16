# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BusinessHourUpdateParams"]


class BusinessHourUpdateParams(TypedDict, total=False):
    hours: Optional[object]

    primary_tag: Annotated[Optional[str], PropertyInfo(alias="primaryTag")]

    secondary_tag: Annotated[Optional[str], PropertyInfo(alias="secondaryTag")]

    timezone: Optional[str]
