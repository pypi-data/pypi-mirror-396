class VideoError(Exception):
    """Indicates an error when using the Vonage Video API."""


class AudioConnectorConfigError(VideoError):
    """The configurations provided for server were invalid."""


class AudioConnectorStartServerError(VideoError):
    """The configurations provided for server were invalid."""
