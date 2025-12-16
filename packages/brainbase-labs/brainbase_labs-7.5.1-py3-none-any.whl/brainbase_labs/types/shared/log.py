# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Log"]


class Log(BaseModel):
    id: str

    data: Optional[object] = None

    direction: Optional[str] = None

    end_time: Optional[datetime] = FieldInfo(alias="endTime", default=None)

    external_call_id: Optional[str] = FieldInfo(alias="externalCallId", default=None)

    from_number: Optional[str] = FieldInfo(alias="fromNumber", default=None)

    messages: Optional[object] = None

    recording_url: Optional[str] = FieldInfo(alias="recordingUrl", default=None)

    start_time: Optional[datetime] = FieldInfo(alias="startTime", default=None)

    to_number: Optional[str] = FieldInfo(alias="toNumber", default=None)

    transcription: Optional[str] = None
