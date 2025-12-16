# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["VoiceListParams"]


class VoiceListParams(TypedDict, total=False):
    deployment_id: Annotated[str, PropertyInfo(alias="deploymentId")]
    """Filter logs by deployment id"""

    flow_id: Annotated[str, PropertyInfo(alias="flowId")]
    """Filter logs by flow id"""

    direction: str
    """Filter by call direction (inbound/outbound)"""

    from_number: Annotated[str, PropertyInfo(alias="fromNumber")]
    """Filter by caller phone number (partial match)"""

    to_number: Annotated[str, PropertyInfo(alias="toNumber")]
    """Filter by called phone number (partial match)"""

    status: str
    """Filter by call status"""

    external_call_id: Annotated[str, PropertyInfo(alias="externalCallId")]
    """Filter by external call ID"""

    call_sid: Annotated[str, PropertyInfo(alias="callSid")]
    """Filter by Twilio call SID"""

    search_query: Annotated[str, PropertyInfo(alias="searchQuery")]
    """Search in call transcriptions (case-insensitive)"""

    start_time_after: Annotated[str, PropertyInfo(alias="startTimeAfter")]
    """Filter logs with startTime after this date (ISO 8601 format)"""

    start_time_before: Annotated[str, PropertyInfo(alias="startTimeBefore")]
    """Filter logs with startTime before this date (ISO 8601 format)"""

    end_time_after: Annotated[str, PropertyInfo(alias="endTimeAfter")]
    """Filter logs with endTime after this date (ISO 8601 format)"""

    end_time_before: Annotated[str, PropertyInfo(alias="endTimeBefore")]
    """Filter logs with endTime before this date (ISO 8601 format)"""

    start_date: Annotated[str, PropertyInfo(alias="startDate")]
    """Deprecated - use start_time_after instead"""

    end_date: Annotated[str, PropertyInfo(alias="endDate")]
    """Deprecated - use start_time_before instead"""

    sort_by: Annotated[str, PropertyInfo(alias="sortBy")]
    """Field to sort by (startTime, endTime, direction, fromNumber, toNumber, status, externalCallId, createdAt, updatedAt)"""

    sort_order: Annotated[str, PropertyInfo(alias="sortOrder")]
    """Sort order (asc or desc)"""

    limit: int
    """Number of items per page (max 100)"""

    page: int
    """Page number for pagination"""
