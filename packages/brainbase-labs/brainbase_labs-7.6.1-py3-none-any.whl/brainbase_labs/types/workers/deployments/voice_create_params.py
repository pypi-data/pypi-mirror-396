# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._types import SequenceNotStr
from ...._utils import PropertyInfo

__all__ = [
    "VoiceCreateParams",
    "Extractions",
    "ExternalConfig",
    "ExternalConfigPronunciationDictionary",
    "SuccessCriterion",
    "SuccessCriterionItem",
]


class VoiceCreateParams(TypedDict, total=False):
    enable_voice_sentiment: Required[Annotated[bool, PropertyInfo(alias="enableVoiceSentiment")]]

    extractions: Required[Dict[str, Extractions]]

    flow_id: Required[Annotated[str, PropertyInfo(alias="flowId")]]

    name: Required[str]

    phone_number: Required[Annotated[str, PropertyInfo(alias="phoneNumber")]]

    external_config: Annotated[ExternalConfig, PropertyInfo(alias="externalConfig")]

    success_criteria: Annotated[Iterable[SuccessCriterion], PropertyInfo(alias="successCriteria")]


class Extractions(TypedDict, total=False):
    description: Required[str]

    required: Required[bool]

    type: Required[Literal["string", "number", "boolean"]]


class ExternalConfigPronunciationDictionary(TypedDict, total=False):
    alphabet: Required[Literal["ipa", "cmu"]]

    phoneme: Required[str]

    word: Required[str]


class ExternalConfig(TypedDict, total=False):
    ambient_sound: Required[Annotated[Optional[str], PropertyInfo(alias="ambientSound")]]

    ambient_sound_volume: Required[Annotated[Optional[float], PropertyInfo(alias="ambientSoundVolume")]]

    audio_encoding: Required[Annotated[Optional[str], PropertyInfo(alias="audioEncoding")]]

    begin_message_delay_ms: Required[Annotated[Optional[float], PropertyInfo(alias="beginMessageDelayMs")]]

    boosted_keywords: Required[Annotated[Optional[SequenceNotStr[str]], PropertyInfo(alias="boostedKeywords")]]

    enable_responsive_reactions: Required[Annotated[Optional[bool], PropertyInfo(alias="enableResponsiveReactions")]]

    enable_transcription_formatting: Required[
        Annotated[Optional[bool], PropertyInfo(alias="enableTranscriptionFormatting")]
    ]

    enable_voicemail_detection: Required[Annotated[Optional[bool], PropertyInfo(alias="enableVoicemailDetection")]]

    end_call_after_silence_ms: Required[Annotated[Optional[float], PropertyInfo(alias="endCallAfterSilenceMs")]]

    fallback_voice_ids: Required[Annotated[Optional[SequenceNotStr[str]], PropertyInfo(alias="fallbackVoiceIds")]]

    filler_audio_enabled: Required[Annotated[Optional[bool], PropertyInfo(alias="fillerAudioEnabled")]]

    interruptibility: Required[Optional[float]]

    language: Required[Optional[str]]

    max_call_duration_ms: Required[Annotated[Optional[float], PropertyInfo(alias="maxCallDurationMs")]]

    normalize_for_speech: Required[Annotated[Optional[bool], PropertyInfo(alias="normalizeForSpeech")]]

    opt_out_sensitive_data_storage: Required[
        Annotated[Optional[bool], PropertyInfo(alias="optOutSensitiveDataStorage")]
    ]

    pronunciation_dictionary: Required[
        Annotated[
            Optional[Iterable[ExternalConfigPronunciationDictionary]], PropertyInfo(alias="pronunciationDictionary")
        ]
    ]

    reduce_silence: Required[Annotated[Optional[bool], PropertyInfo(alias="reduceSilence")]]

    reminder_max_count: Required[Annotated[Optional[float], PropertyInfo(alias="reminderMaxCount")]]

    reminder_trigger_ms: Required[Annotated[Optional[float], PropertyInfo(alias="reminderTriggerMs")]]

    responsiveness: Required[Optional[float]]

    responsive_reactions_frequency: Required[
        Annotated[Optional[float], PropertyInfo(alias="responsiveReactionsFrequency")]
    ]

    responsive_reactions_words: Required[
        Annotated[Optional[SequenceNotStr[str]], PropertyInfo(alias="responsiveReactionsWords")]
    ]

    ring_duration_ms: Required[Annotated[Optional[float], PropertyInfo(alias="ringDurationMs")]]

    sample_rate: Required[Annotated[Optional[float], PropertyInfo(alias="sampleRate")]]

    voice_emotion_enabled: Required[Annotated[Optional[bool], PropertyInfo(alias="voiceEmotionEnabled")]]

    voice_id: Required[Annotated[Optional[str], PropertyInfo(alias="voiceId")]]

    voicemail_detection_timeout_ms: Required[
        Annotated[Optional[float], PropertyInfo(alias="voicemailDetectionTimeoutMs")]
    ]

    voicemail_message: Required[Annotated[Optional[str], PropertyInfo(alias="voicemailMessage")]]

    voice_model: Required[
        Annotated[
            Optional[
                Literal[
                    "eleven_turbo_v2",
                    "eleven_flash_v2",
                    "eleven_turbo_v2_5",
                    "eleven_flash_v2_5",
                    "eleven_multilingual_v2",
                    "Play3.0-mini",
                    "PlayDialog",
                ]
            ],
            PropertyInfo(alias="voiceModel"),
        ]
    ]

    voice_speed: Required[Annotated[Optional[float], PropertyInfo(alias="voiceSpeed")]]

    voice_temperature: Required[Annotated[Optional[float], PropertyInfo(alias="voiceTemperature")]]

    volume: Required[Optional[float]]


class SuccessCriterionItem(TypedDict, total=False):
    description: Required[str]

    threshold: Required[float]

    title: Required[str]

    type: Required[Literal["BINARY", "SCORE"]]


class SuccessCriterion(TypedDict, total=False):
    items: Required[Iterable[SuccessCriterionItem]]

    title: Required[str]

    description: str
