# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["Voicev1UpdateParams"]


class Voicev1UpdateParams(TypedDict, total=False):
    worker_id: Required[Annotated[str, PropertyInfo(alias="workerId")]]

    allowed_transfer_numbers: Annotated[List[str], PropertyInfo(alias="allowedTransferNumbers")]

    config: str

    end_sentence: Annotated[str, PropertyInfo(alias="endSentence")]

    flow_id: Annotated[str, PropertyInfo(alias="flowId")]

    functions: str

    language: str

    model: str

    name: str

    objective: str

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    resource_keys: Annotated[List[str], PropertyInfo(alias="resourceKeys")]

    start_sentence: Annotated[str, PropertyInfo(alias="startSentence")]

    voice_id: Annotated[str, PropertyInfo(alias="voiceId")]

    ws_base_url: Annotated[str, PropertyInfo(alias="wsBaseUrl")]
