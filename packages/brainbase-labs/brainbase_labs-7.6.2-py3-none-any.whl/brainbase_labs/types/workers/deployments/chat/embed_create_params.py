# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["EmbedCreateParams"]


class EmbedCreateParams(TypedDict, total=False):
    agent_logo_url: Annotated[Optional[str], PropertyInfo(alias="agentLogoUrl")]

    agent_name: Annotated[Optional[str], PropertyInfo(alias="agentName")]

    primary_color: Annotated[Optional[str], PropertyInfo(alias="primaryColor")]

    styling: Optional[object]

    welcome_message: Annotated[Optional[str], PropertyInfo(alias="welcomeMessage")]
