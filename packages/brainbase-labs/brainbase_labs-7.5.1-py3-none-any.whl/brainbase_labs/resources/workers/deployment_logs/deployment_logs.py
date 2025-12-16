# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .voice import (
    VoiceResource,
    AsyncVoiceResource,
    VoiceResourceWithRawResponse,
    AsyncVoiceResourceWithRawResponse,
    VoiceResourceWithStreamingResponse,
    AsyncVoiceResourceWithStreamingResponse,
)
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["DeploymentLogsResource", "AsyncDeploymentLogsResource"]


class DeploymentLogsResource(SyncAPIResource):
    @cached_property
    def voice(self) -> VoiceResource:
        return VoiceResource(self._client)

    @cached_property
    def with_raw_response(self) -> DeploymentLogsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/BrainbaseHQ/brainbase-labs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return DeploymentLogsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeploymentLogsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/BrainbaseHQ/brainbase-labs-python-sdk#with_streaming_response
        """
        return DeploymentLogsResourceWithStreamingResponse(self)


class AsyncDeploymentLogsResource(AsyncAPIResource):
    @cached_property
    def voice(self) -> AsyncVoiceResource:
        return AsyncVoiceResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDeploymentLogsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/BrainbaseHQ/brainbase-labs-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeploymentLogsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeploymentLogsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/BrainbaseHQ/brainbase-labs-python-sdk#with_streaming_response
        """
        return AsyncDeploymentLogsResourceWithStreamingResponse(self)


class DeploymentLogsResourceWithRawResponse:
    def __init__(self, deployment_logs: DeploymentLogsResource) -> None:
        self._deployment_logs = deployment_logs

    @cached_property
    def voice(self) -> VoiceResourceWithRawResponse:
        return VoiceResourceWithRawResponse(self._deployment_logs.voice)


class AsyncDeploymentLogsResourceWithRawResponse:
    def __init__(self, deployment_logs: AsyncDeploymentLogsResource) -> None:
        self._deployment_logs = deployment_logs

    @cached_property
    def voice(self) -> AsyncVoiceResourceWithRawResponse:
        return AsyncVoiceResourceWithRawResponse(self._deployment_logs.voice)


class DeploymentLogsResourceWithStreamingResponse:
    def __init__(self, deployment_logs: DeploymentLogsResource) -> None:
        self._deployment_logs = deployment_logs

    @cached_property
    def voice(self) -> VoiceResourceWithStreamingResponse:
        return VoiceResourceWithStreamingResponse(self._deployment_logs.voice)


class AsyncDeploymentLogsResourceWithStreamingResponse:
    def __init__(self, deployment_logs: AsyncDeploymentLogsResource) -> None:
        self._deployment_logs = deployment_logs

    @cached_property
    def voice(self) -> AsyncVoiceResourceWithStreamingResponse:
        return AsyncVoiceResourceWithStreamingResponse(self._deployment_logs.voice)
