from typing import Optional, Callable, Awaitable
from ssl import SSLContext
from pydantic import BaseModel, Field


class AudioConnectorServerConfig(BaseModel):
    """The audio connector websocket server configurations.

    Args:
        host (str): The host for server.
        port (int): The port for server.
        ssl (Optional[SSLContext]): The SSL context for secure connections.
        on_start: Coroutine to be called once the server has started.
        on_stop: Coroutine to be called once the server has stopped.
        on_connect: Coroutine to be called when a new client connection is accepted.
    """

    host: str
    port: int
    ssl: Optional[SSLContext] = None
    on_start: Optional[Callable[[], Awaitable[None]]] = None
    on_stop: Optional[Callable[[], Awaitable[None]]] = None
    on_connect: Optional[Callable[[], Awaitable[None]]] = None

    class Config:
        """Configuration for the Pydantic model."""

        arbitrary_types_allowed = True


class AudioConnectorServerHandle(BaseModel):
    """The audio connector websocket server handle to provide information about server.

    Args:
        host (str): The host for server.
        port (int): The port for server.
        running (bool): Whether the server is running.
        stop_callback: Internal callback to stop the server.
    """

    host: str
    port: int
    running: bool = Field(default=False)
    secure: bool = Field(default=False)
    stop_callback: Optional[Callable[[], None]] = None

    async def stop(self):
        """Stops the audio connector websocket server."""
        await self.stop_callback()
        self.running = False

    def get_address(self) -> str:
        """Returns the address of the audio connector websocket server."""
        protocol = "wss" if self.secure else "ws"
        return f"{protocol}://{self.host}:{self.port}"


class AudioConnectorConnectionData(BaseModel):
    """Metadata about the connection extracted from request headers.
    Args:
        sessionId (str): The session ID from the headers (if present).
        conferenceId (str): The conference ID from the headers (if present).
        connectionId (str): The conference ID from the headers (if present).
        uri (str): The URL path of the WebSocket connection.
        customHeaders (str): All headers sent with the connection request.
        id (str): The unique identifier for the connection.
    """

    sessionId: Optional[str] = None
    conferenceId: Optional[str] = None
    uri: Optional[str] = None
    connectionId: Optional[str] = None
    customHeaders: Optional[dict] = None
    id: Optional[str] = None
