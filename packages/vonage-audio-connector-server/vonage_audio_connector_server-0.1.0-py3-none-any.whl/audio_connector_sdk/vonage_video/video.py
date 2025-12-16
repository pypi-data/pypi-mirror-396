import logging
from pydantic import validate_call
from .models.audio_connector import (
    AudioConnectorServerConfig,
    AudioConnectorServerHandle,
)
from .core.audio_connector_server import AudioConnectorServer


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("websockets").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)


class Video:
    """Calls Vonage's Video API."""

    @validate_call
    async def start_audio_connector_server(
        self, options: AudioConnectorServerConfig
    ) -> AudioConnectorServerHandle:
        """Starts the audio connector websocket server.
        Args:
            options (AudioConnectorServerConfig): The audio connector websocket server configurations.
        Returns:
            AudioConnectorServerHandle: The audio connector websocket server handle.
        Raises:
            ValueError: If the host or port is not valid.
        """

        server = AudioConnectorServer()
        server_handle = await server.start_server(options)
        return server_handle
