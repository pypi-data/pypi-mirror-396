# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["VoiceCreateParams", "ExternalConfig", "SuccessCriterion", "SuccessCriterionItem"]


class VoiceCreateParams(TypedDict, total=False):
    flow_id: Required[Annotated[str, PropertyInfo(alias="flowId")]]

    name: Required[str]

    phone_number: Required[Annotated[str, PropertyInfo(alias="phoneNumber")]]

    external_config: Annotated[ExternalConfig, PropertyInfo(alias="externalConfig")]

    success_criteria: Annotated[Iterable[SuccessCriterion], PropertyInfo(alias="successCriteria")]


class ExternalConfig(TypedDict, total=False):
    ambient_sound: Required[Annotated[str, PropertyInfo(alias="ambientSound")]]

    ambient_sound_volume: Required[Annotated[str, PropertyInfo(alias="ambientSoundVolume")]]

    audio_encoding: Required[Annotated[str, PropertyInfo(alias="audioEncoding")]]

    begin_message_delay_ms: Required[Annotated[str, PropertyInfo(alias="beginMessageDelayMs")]]

    boosted_keywords: Required[Annotated[str, PropertyInfo(alias="boostedKeywords")]]

    enable_responsive_reactions: Required[Annotated[str, PropertyInfo(alias="enableResponsiveReactions")]]

    enable_transcription_formatting: Required[Annotated[str, PropertyInfo(alias="enableTranscriptionFormatting")]]

    enable_voicemail_detection: Required[Annotated[str, PropertyInfo(alias="enableVoicemailDetection")]]

    end_call_after_silence_ms: Required[Annotated[str, PropertyInfo(alias="endCallAfterSilenceMs")]]

    fallback_voice_ids: Required[Annotated[str, PropertyInfo(alias="fallbackVoiceIds")]]

    filler_audio_enabled: Required[Annotated[str, PropertyInfo(alias="fillerAudioEnabled")]]

    interruptibility: Required[str]

    language: Required[str]

    max_call_duration_ms: Required[Annotated[str, PropertyInfo(alias="maxCallDurationMs")]]

    normalize_for_speech: Required[Annotated[str, PropertyInfo(alias="normalizeForSpeech")]]

    opt_out_sensitive_data_storage: Required[Annotated[str, PropertyInfo(alias="optOutSensitiveDataStorage")]]

    pronunciation_dictionary: Required[Annotated[str, PropertyInfo(alias="pronunciationDictionary")]]

    reduce_silence: Required[Annotated[str, PropertyInfo(alias="reduceSilence")]]

    reminder_max_count: Required[Annotated[str, PropertyInfo(alias="reminderMaxCount")]]

    reminder_trigger_ms: Required[Annotated[str, PropertyInfo(alias="reminderTriggerMs")]]

    responsiveness: Required[str]

    responsive_reactions_frequency: Required[Annotated[str, PropertyInfo(alias="responsiveReactionsFrequency")]]

    responsive_reactions_words: Required[Annotated[str, PropertyInfo(alias="responsiveReactionsWords")]]

    ring_duration_ms: Required[Annotated[str, PropertyInfo(alias="ringDurationMs")]]

    sample_rate: Required[Annotated[str, PropertyInfo(alias="sampleRate")]]

    voice_emotion_enabled: Required[Annotated[str, PropertyInfo(alias="voiceEmotionEnabled")]]

    voice_id: Required[Annotated[str, PropertyInfo(alias="voiceId")]]

    voicemail_detection_timeout_ms: Required[Annotated[str, PropertyInfo(alias="voicemailDetectionTimeoutMs")]]

    voicemail_message: Required[Annotated[str, PropertyInfo(alias="voicemailMessage")]]

    voice_model: Required[Annotated[str, PropertyInfo(alias="voiceModel")]]

    voice_speed: Required[Annotated[str, PropertyInfo(alias="voiceSpeed")]]

    voice_temperature: Required[Annotated[str, PropertyInfo(alias="voiceTemperature")]]

    volume: Required[str]


class SuccessCriterionItem(TypedDict, total=False):
    description: Required[str]

    threshold: Required[float]

    title: Required[str]

    type: Required[Literal["BINARY", "SCORE"]]


class SuccessCriterion(TypedDict, total=False):
    items: Required[Iterable[SuccessCriterionItem]]

    title: Required[str]

    description: str
