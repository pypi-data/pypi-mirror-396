import asyncio
import websockets
import logging
from ssl import SSLContext
from audio_connector_sdk.vonage_video.models import (
    AudioConnectorServerConfig,
    AudioConnectorServerHandle,
)
from audio_connector_sdk.vonage_video.errors import AudioConnectorStartServerError
from . import AudioConnectorConnection

logger = logging.getLogger("opentok")


class AudioConnectorServer:
    """
    Manages the lifecycle of the WebSocket server and delegates connection events
    to user-defined handler coroutines.

    This class is responsible for starting and stopping the server, handling new
    connections, and invoking provided callbacks for connection events such as
    startup, shutdown, and new client connections.
    """

    def __init__(self):
        self._server = None
        self._loop = asyncio.get_event_loop()

    async def _handler(self, websocket):
        connection = AudioConnectorConnection(websocket, logger)
        try:
            if self.on_connect:
                await self.on_connect(connection)

            async for message in websocket:
                if connection.on_message:
                    await connection.on_message(message)
        except Exception as e:
            if connection.on_error:
                await connection.on_error(e)
        finally:
            if connection.on_disconnect:
                await connection.on_disconnect()

    async def _start_server(self):
        if not self.host or not self.port:
            raise ValueError("Host and port must be set before starting the server.")
        if self.on_start:
            if not asyncio.iscoroutinefunction(self.on_start):
                raise ValueError("on_start must be a coroutine function.")
        if self.on_stop:
            if not asyncio.iscoroutinefunction(self.on_stop):
                raise ValueError("on_stop must be a coroutine function.")
        # Start the WebSocket server
        if not self._loop.is_running():
            raise RuntimeError(
                "Event loop is not running. Ensure the event loop is started before calling this method."
            )
        if self.ssl_context:
            if not isinstance(self.ssl_context, SSLContext):
                raise ValueError("ssl_context must be an instance of SSLContext.")

        try:
            if self.ssl_context:
                self._server = await websockets.serve(
                    self._handler, self.host, self.port, ssl=self.ssl_context
                )
            else:
                self._server = await websockets.serve(
                    self._handler, self.host, self.port
                )

            logger.debug(f"WebSocket server started on {self.host}:{self.port}")
            if self.on_start:
                await self.on_start()

        except OSError as e:
            if e.errno == 98:
                raise AudioConnectorStartServerError(
                    f"Port {self.port} is already in use. Please choose a different port."
                )
            elif e.errno == 48:
                raise AudioConnectorStartServerError(
                    f"Address {self.host}:{self.port} is already in use. Please choose a different address."
                )
            raise AudioConnectorStartServerError("Failed to bind WebSocket server")

        except Exception:
            raise AudioConnectorStartServerError("Failed to start WebSocket server")

    async def start_server(
        self, config: AudioConnectorServerConfig
    ) -> AudioConnectorServerHandle:
        """
        Start the WebSocket server using a ServerConfig object containing settings and callbacks.

        :param config: A ServerConfig object with server host, port, and handler coroutines.
        """
        self.host = config.host
        self.port = config.port
        self.on_start = config.on_start
        self.on_stop = config.on_stop
        self.on_connect = config.on_connect
        self.ssl_context = config.ssl

        try:
            await self._start_server()
        except Exception as e:
            raise e

        # Return a handle to the server with stop functionality
        return AudioConnectorServerHandle(
            host=self.host,
            port=self.port,
            running=True,
            secure=self.ssl_context is not None,
            stop_callback=self.stop,
        )

    async def stop(self):
        """
        Stops the WebSocket server and cleans up resources.
        This method can be called to gracefully stop the server.
        """
        if self._server:
            self._server.close()
        await self._server.wait_closed()
        if self.on_stop:
            await self.on_stop()
