try:
    from google import genai
    from google.auth.credentials import Credentials
    from google.genai import types
    from google.genai.client import DebugConfig
except ImportError:
    raise ImportError(
        "To use the Fishjam Gemini integration, you need to import the `gemini` extra. "
        "Install it with `pip install 'fishjam-server-sdk[gemini]'`"
    )

from typing import Optional, Union

from fishjam import AgentOutputOptions
from fishjam.agent import OutgoingAudioTrackOptions
from fishjam.events import TrackEncoding
from fishjam.version import get_version


def _get_headers():
    return {"x-goog-api-client": f"fishjam-python-server-sdk/{get_version()}"}


def _add_fishjam_header(
    http_options: Optional[Union[types.HttpOptions, types.HttpOptionsDict]],
) -> Union[types.HttpOptions, types.HttpOptionsDict]:
    if http_options is None:
        return _add_fishjam_header_none()
    if isinstance(http_options, types.HttpOptions):
        return _add_fishjam_header_object(http_options)
    return _add_fishjam_header_dict(http_options)


def _add_fishjam_header_object(http_options: types.HttpOptions) -> types.HttpOptions:
    http_options.headers = (http_options.headers or {}) | _get_headers()
    return http_options


def _add_fishjam_header_dict(
    http_options: types.HttpOptionsDict,
) -> types.HttpOptionsDict:
    headers = (http_options.get("headers") or {}) | _get_headers()
    return http_options | {"headers": headers}


def _add_fishjam_header_none() -> types.HttpOptionsDict:
    return {"headers": _get_headers()}


class _GeminiIntegration:
    def create_client(
        self,
        vertexai: Optional[bool] = None,
        api_key: Optional[str] = None,
        credentials: Optional[Credentials] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        debug_config: Optional[DebugConfig] = None,
        http_options: Optional[Union[types.HttpOptions, types.HttpOptionsDict]] = None,
    ):
        """Creates and configures a Fishjam-compatible Google GenAI Client.

        See `genai.Client` for configuration options.

        Returns:
            genai.Client: An instantiated and configured Gemini client.
        """
        full_http_options = _add_fishjam_header(http_options)

        return genai.Client(
            vertexai=vertexai,
            api_key=api_key,
            credentials=credentials,
            project=project,
            location=location,
            debug_config=debug_config,
            http_options=full_http_options,
        )

    @property
    def GEMINI_INPUT_AUDIO_SETTINGS(self) -> AgentOutputOptions:
        """Audio configuration required for Gemini input.

        Gemini consumes PCM16 audio at 16,000 Hz.

        Returns:
            AgentOutputOptions: Agent options compatible with the Gemini Live API.
        """
        return AgentOutputOptions(
            audio_format="pcm16",
            audio_sample_rate=16_000,
        )

    @property
    def GEMINI_OUTPUT_AUDIO_SETTINGS(self) -> OutgoingAudioTrackOptions:
        """Audio configuration for an agent's output track.

        Gemini produces PCM16 audio at 24,000 Hz.

        Returns:
            OutgoingAudioTrackOptions: Track options compatible with the Gemini Live API
        """
        return OutgoingAudioTrackOptions(
            encoding=TrackEncoding.TRACK_ENCODING_PCM16,
            sample_rate=24_000,
            channels=1,
        )

    @property
    def GEMINI_AUDIO_MIME_TYPE(self) -> str:
        """The mime type for Gemini audio input."""
        return "audio/pcm;rate=16000"


GeminiIntegration = _GeminiIntegration()
"""Integration with the Gemini Live API."""
