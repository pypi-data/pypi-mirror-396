# Vonage Audio Connector Server SDK for Python

This SDK aims to provide a simple event-driven interface for creating WebSocket servers, that can handle multiple Vonage AudioConnector connections and support JSON text messages and binary audio samples. Main objective is to make it easy for customers to be able to build applications that process real-time audio from Vonage Video API sessions.

## Usage

To use the audio connector server sdk to create your own websocket server, access the feature through `video` by using `start_audio_connector_server`.

```python
video = Video()

# Define the server configuration
"""Args:
        host (str): The host for server.
        port (int): The port for server.
        ssl (Optional[SSLContext]): The SSL context for secure connections.
        on_start: Optional[Callable[[], Awaitable[None]]] = None: A optional Coroutine to be called once the server has started.
        on_stop: Optional[Callable[[], Awaitable[None]]] = None: A optional Coroutine to be called once the server has stopped.
        on_connect: Optional[Callable[[], Awaitable[None]]] = None: A optional Coroutine to be called when a new client connection is accepted.
"""
config = AudioConnectorServerConfig(
    host="localhost",
    port=8765,
    ssl=ssl_context,
    on_start=on_start,
    on_stop=on_stop,
    on_connect=on_connect
)

# Start the audio connector server
server_handle = await video.start_audio_connector_server(config)

"""start_audio_connector_server returns the AudioConnectorServerHandle:
    host (str): The host for server.
    port (int): The port for server.
    running (bool): Whether the server is running.
    stop(): A awaitable coroutine to stop the server.
    get_address() -> str: A coroutine to get the current address of server
"""
```

You need to provide the async coroutines using the websocket server and interact with the connections.

```python
async def on_message(message):
    print("Received message")
    return message

async def on_disconnect():
    print("Client disconnected.")

async def on_error(error):
    print(f"Error occurred: {error}")
```

To send and receive messages from the connection, you need to set the handlers for the connection and use send_json_packet or send_audio_buffer to send packets.
```python
async def on_connect(client):

    client.set_handler(
            on_message=on_message,
            on_disconnect=on_disconnect,
            on_error=on_error
    )
        """
        Register per-connection event handlers.

        :param on_message: Coroutine to be called when a message is received.
        :param on_disconnect: Coroutine to be called when the connection closes.
        :param on_error: Coroutine to be called when an error occurs.
        """

    await client.send_json_packet(string_json)
        """
        Send a JSON-encoded message to the connected WebSocket client.
        Args:
            :param data: The data to send, which will be converted to a JSON string.
        """

    await client.send_audio_buffer(audio_data, bytes_per_sample=640, frames_ms=20, pad_last_frame=True, flush_buffer=False,)
        """
        Send a PCM audio stream to the connected WebSocket client.

        Args:
            :param audio_data: The PCM audio data to send as bytes.
            :param bytes_per_sample: Number of bytes in each audio frame. For Opentok/Vonage, use 640 or 320 bytes depending on the `audio_rate` configured in the audio connector API.
            :param frames_ms: The duration of each frame in milliseconds. It can be either 10 or 20.
            :param pad_last_frame: If True, pads the last frame with zeros if it is shorter than bytes_per_sample.
            :param flush_buffer: If True, flushes any buffered packets before sending new data.

        Note: The raw byte buffer provided in audio_data is partitioned into fixed-size frames (typically 640 bytes, or 320 bytes as configured).
        The permissible number of frames for immediate dispatch is determined by the active frame window (configured via set_buffer_timing, based on active_seconds).
            - If the total frame count is within this active limit, frames are sent directly, one by one.
            - If it exceeds the limit, frames are queued and delivered asynchronously by a background sender task to reduce load on the SDK and application.

        Optional behaviors include padding the final partial frame and flushing any previously queued frames before sending.
        """

    client.info()
        """
        Retrieve metadata about the connection extracted from request headers.

        Returns:
            AudioConnectorConnectionData():
            Metadata about the connection extracted from request headers.
            Fields:
                sessionId (str): The session ID from the headers (if present).
                conferenceId (str): The conference ID from the headers (if present).
                connectionId (str): The conference ID from the headers (if present).
                uri (str): The URL path of the WebSocket connection.
                customHeaders (dict): All headers sent with the connection request.
                id (str): The unique identifier for the connection.
        """

    client.flush_buffer()
        """
        Flush any buffered packets to the WebSocket client.
        """

    client.disconnect():
        """
        Close the WebSocket connection.
        This method can be called to gracefully close the connection.
        """

    client.set_buffer_timing(active_seconds=7.5)
        """
        Update pacing parameters for the audio frame sender.

        :param active_seconds: Duration (seconds) to actively send frames per cycle.
        """
```
## Installation
```bash
pip install -r requirements.txt
```

## Sample App
 A sample app on how to use the sdk. for more details on the sample app, please follow its readme file:
`tests/examples/unified_sample_app/README.md`


## Unit Tests
To run the unit tests, follow thes steps:
```bash
pip install pytest
python -m pytest tests/unit/test_audio_connector_server.py
```
