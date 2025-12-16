# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["VoiceDeployment"]


class VoiceDeployment(BaseModel):
    id: str

    enable_voice_sentiment: bool = FieldInfo(alias="enableVoiceSentiment")

    agent_id: Optional[str] = FieldInfo(alias="agentId", default=None)

    external_config: Optional[object] = FieldInfo(alias="externalConfig", default=None)

    phone_number: Optional[str] = FieldInfo(alias="phoneNumber", default=None)

    voice_id: Optional[str] = FieldInfo(alias="voiceId", default=None)

    voice_provider: Optional[str] = FieldInfo(alias="voiceProvider", default=None)
