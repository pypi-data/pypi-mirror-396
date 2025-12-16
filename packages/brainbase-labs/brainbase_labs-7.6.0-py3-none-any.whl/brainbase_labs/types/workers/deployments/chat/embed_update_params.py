# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["EmbedUpdateParams"]


class EmbedUpdateParams(TypedDict, total=False):
    worker_id: Required[Annotated[str, PropertyInfo(alias="workerId")]]

    agent_logo_url: Annotated[Optional[str], PropertyInfo(alias="agentLogoUrl")]

    agent_name: Annotated[Optional[str], PropertyInfo(alias="agentName")]

    primary_color: Annotated[Optional[str], PropertyInfo(alias="primaryColor")]

    styling: Optional[object]

    welcome_message: Annotated[Optional[str], PropertyInfo(alias="welcomeMessage")]
