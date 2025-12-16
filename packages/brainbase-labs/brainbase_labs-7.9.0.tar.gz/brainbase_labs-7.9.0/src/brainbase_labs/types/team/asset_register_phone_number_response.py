# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AssetRegisterPhoneNumberResponse"]


class AssetRegisterPhoneNumberResponse(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")

    integration_id: str = FieldInfo(alias="integrationId")

    phone_number: str = FieldInfo(alias="phoneNumber")

    provider: str

    updated_at: datetime = FieldInfo(alias="updatedAt")

    caller_name: Optional[str] = FieldInfo(alias="callerName", default=None)

    country_code: Optional[str] = FieldInfo(alias="countryCode", default=None)

    metadata: Optional[object] = None

    team_id: Optional[str] = FieldInfo(alias="teamId", default=None)

    worker_id: Optional[str] = FieldInfo(alias="workerId", default=None)
