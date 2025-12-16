# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["TeamPhoneHourUpdateParams"]


class TeamPhoneHourUpdateParams(TypedDict, total=False):
    hours_id: Annotated[Optional[str], PropertyInfo(alias="hoursId")]

    phone_number: Annotated[Optional[str], PropertyInfo(alias="phoneNumber")]
