# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["VoiceUpdateParams", "ExternalConfig", "SuccessCriterion", "SuccessCriterionItem"]


class VoiceUpdateParams(TypedDict, total=False):
    worker_id: Required[Annotated[str, PropertyInfo(alias="workerId")]]

    enable_voice_sentiment: Annotated[str, PropertyInfo(alias="enableVoiceSentiment")]

    external_config: Annotated[ExternalConfig, PropertyInfo(alias="externalConfig")]

    flow_id: Annotated[str, PropertyInfo(alias="flowId")]

    name: str

    phone_number: Annotated[str, PropertyInfo(alias="phoneNumber")]

    success_criteria: Annotated[Iterable[SuccessCriterion], PropertyInfo(alias="successCriteria")]


class ExternalConfig(TypedDict, total=False):
    ambient_sound: Annotated[str, PropertyInfo(alias="ambientSound")]

    ambient_sound_volume: Annotated[str, PropertyInfo(alias="ambientSoundVolume")]

    audio_encoding: Annotated[str, PropertyInfo(alias="audioEncoding")]

    begin_message_delay_ms: Annotated[str, PropertyInfo(alias="beginMessageDelayMs")]

    boosted_keywords: Annotated[str, PropertyInfo(alias="boostedKeywords")]

    enable_responsive_reactions: Annotated[str, PropertyInfo(alias="enableResponsiveReactions")]

    enable_transcription_formatting: Annotated[str, PropertyInfo(alias="enableTranscriptionFormatting")]

    enable_voicemail_detection: Annotated[str, PropertyInfo(alias="enableVoicemailDetection")]

    end_call_after_silence_ms: Annotated[str, PropertyInfo(alias="endCallAfterSilenceMs")]

    fallback_voice_ids: Annotated[str, PropertyInfo(alias="fallbackVoiceIds")]

    filler_audio_enabled: Annotated[str, PropertyInfo(alias="fillerAudioEnabled")]

    interruptibility: str

    language: str

    max_call_duration_ms: Annotated[str, PropertyInfo(alias="maxCallDurationMs")]

    normalize_for_speech: Annotated[str, PropertyInfo(alias="normalizeForSpeech")]

    opt_out_sensitive_data_storage: Annotated[str, PropertyInfo(alias="optOutSensitiveDataStorage")]

    pronunciation_dictionary: Annotated[str, PropertyInfo(alias="pronunciationDictionary")]

    reduce_silence: Annotated[str, PropertyInfo(alias="reduceSilence")]

    reminder_max_count: Annotated[str, PropertyInfo(alias="reminderMaxCount")]

    reminder_trigger_ms: Annotated[str, PropertyInfo(alias="reminderTriggerMs")]

    responsiveness: str

    responsive_reactions_frequency: Annotated[str, PropertyInfo(alias="responsiveReactionsFrequency")]

    responsive_reactions_words: Annotated[str, PropertyInfo(alias="responsiveReactionsWords")]

    ring_duration_ms: Annotated[str, PropertyInfo(alias="ringDurationMs")]

    sample_rate: Annotated[str, PropertyInfo(alias="sampleRate")]

    voice_emotion_enabled: Annotated[str, PropertyInfo(alias="voiceEmotionEnabled")]

    voice_id: Annotated[str, PropertyInfo(alias="voiceId")]

    voicemail_detection_timeout_ms: Annotated[str, PropertyInfo(alias="voicemailDetectionTimeoutMs")]

    voicemail_message: Annotated[str, PropertyInfo(alias="voicemailMessage")]

    voice_model: Annotated[str, PropertyInfo(alias="voiceModel")]

    voice_speed: Annotated[str, PropertyInfo(alias="voiceSpeed")]

    voice_temperature: Annotated[str, PropertyInfo(alias="voiceTemperature")]

    volume: str


class SuccessCriterionItem(TypedDict, total=False):
    description: Required[str]

    threshold: Required[float]

    title: Required[str]

    type: Required[Literal["BINARY", "SCORE"]]


class SuccessCriterion(TypedDict, total=False):
    items: Required[Iterable[SuccessCriterionItem]]

    title: Required[str]

    description: str
