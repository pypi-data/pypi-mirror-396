import asyncio
import json
from audio_connector_sdk.vonage_video.models import AudioConnectorConnectionData


class AudioConnectorConnection:
    """
    Represents an individual WebSocket connection in the AudioConnectorServer.

    This class wraps the low-level WebSocket and provides:
    - Callback hooks for message, disconnect, and error handling
    - A method to send messages to the client
    - Metadata extraction from the connection request
    """

    # 1. Constructor
    def __init__(self, websocket, logger):
        headers = websocket.request.headers
        self.websocket = websocket
        self.logger = logger
        self.path = websocket.request.path
        self._headers = dict(headers)
        self.id = headers.get("connectionId") or websocket.id
        self.conferenceId = headers.get("x-opentok-ws-conferenceid")
        self.connectionId = headers.get("x-opentok-ws-connectionid")
        self.sessionId = headers.get("x-opentok-ws-sessionid")

        self._active_seconds = 5
        self._active_frame_limit = self._calculate_active_frame_limit()
        self._queue_warn_threshold = 15000  # warn when queued frames exceed this

        self._queue: asyncio.Queue[tuple[int, bytes]] = asyncio.Queue()
        self._gen = 0
        self._closed = False
        self._sender_task = asyncio.create_task(self._run_sender())

        self.on_message = None
        self.on_disconnect = None
        self.on_error = None

        self.flush_buffer_message = '{"event":"websocket:cleared"}'

    # 2. Public API methods
    async def send_json_packet(self, data):
        """
        Send a JSON-encoded message to the connected WebSocket client.

        :param data: The data to send, which will be converted to a JSON string.
        """
        if not isinstance(data, str):
            raise ValueError("Data must be a valid JSON string.")

        try:
            json.loads(data)
            await self.websocket.send(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")
        except Exception as e:
            raise ValueError(f"Error processing data: {e}")

    async def send_audio_buffer(
        self,
        audio_data: bytes,
        *,
        bytes_per_sample=640,
        frames_ms=20,
        pad_last_frame=False,
        flush_buffer=False,
    ):
        """
        Send a PCM audio stream to the connected WebSocket client.
        :param audio_data: The PCM audio data to send as bytes.
        :param bytes_per_sample: Number of bytes in each audio frame. For Opentok/Vonage, use 640 or 320 bytes depending on the `audio_rate` configured in the audio connector API.
        :param frames_ms: The duration of each frame in milliseconds. It can be either 10 or 20.
        :param pad_last_frame: If True, pads the last frame with zeros if it is shorter than bytes_per_sample.
        :param flush_buffer: If True, flushes any buffered packets before sending new data.
        """
        try:
            if bytes_per_sample <= 0:
                raise ValueError("Invalid sample size")

            if not isinstance(audio_data, bytes):
                raise ValueError("audio_data must be bytes")

            if flush_buffer:
                await self.flush_buffer()

            if frames_ms == 10:
                bytes_per_sample = 320

            total = len(audio_data)
            if total < bytes_per_sample:
                self.logger.debug("Insufficient audio data to send.")
                return

            frames: list[bytes] = []
            for i in range(0, total, bytes_per_sample):
                chunk = audio_data[i : i + bytes_per_sample]
                if len(chunk) < bytes_per_sample:
                    if pad_last_frame:
                        chunk = chunk + b"\x00" * (
                            bytes_per_sample - len(chunk)
                        )  # Pad the last frame if needed
                    else:
                        pass
                frames.append(chunk)

            if self._queue.empty() and total < self._active_frame_limit:
                # Send directly in case of live streams
                for frame in frames:
                    await self.websocket.send(frame)
            else:
                # Split into frames for larger data
                self.logger.debug(
                    "using background sender task for sending audio frames"
                )
                gen_snapshot = self._gen
                for frame in frames:
                    await self._queue.put((gen_snapshot, frame))

        except Exception as e:
            raise ValueError(f"Error sending audio packet: {e}")

    async def flush_buffer(self):
        """
        Flush any buffered packets to the WebSocket client.
        """
        if self.websocket:
            try:
                self._gen += 1
                # Send flush event to freeswitch
                await self.send_json_packet(self.flush_buffer_message)

                while not self._queue.empty():
                    try:
                        self._queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break
                self.logger.info("Audio frame queue flushed")
            except Exception as e:
                raise ValueError(f"Error flushing packets: {e}")

    def set_handler(self, on_message=None, on_disconnect=None, on_error=None):
        """
        Register per-connection event handlers.

        :param on_message: Coroutine to be called when a message is received.
        :param on_disconnect: Coroutine to be called when the connection closes.
        :param on_error: Coroutine to be called when an error occurs.
        """
        self.on_message = on_message
        self.on_disconnect = on_disconnect
        self.on_error = on_error

    def set_buffer_timing(self, active_seconds: float = None) -> None:
        """
        Update pacing parameters for the audio frame sender.

        :param active_seconds: Duration (seconds) to actively send frames per cycle.
        """
        if active_seconds is not None:
            if active_seconds <= 0:
                raise ValueError("active_seconds must be > 0")
            self._active_seconds = active_seconds
            self._active_frame_limit = self._calculate_active_frame_limit()
            self.logger.info(
                f"Time for sending audio frames updated to active_seconds: {active_seconds} seconds, "
                f"_active_frame_limit: {self._active_frame_limit} frames"
            )

    def info(self) -> AudioConnectorConnectionData:
        """
        Retrieve metadata about the connection extracted from request headers.

        :return: A dictionary containing:
            - sessionId: The session ID from the headers (if present).
            - url: The URL path of the WebSocket connection.
            - connectionId: The unique identifier for the connection.
            - customHeaders: All headers sent with the connection request.
            - id: Alias to connectionId.
        """
        return AudioConnectorConnectionData(
            uri=self.path,
            id=str(self.id),
            customHeaders=self._headers,
            conferenceId=self.conferenceId,
            connectionId=self.connectionId,
            sessionId=self.sessionId,
        )

    def disconnect(self):
        """
        Close the WebSocket connection.

        This method can be called to gracefully close the connection.
        """
        try:
            if self._closed:
                return
            self._closed = True
            if self._sender_task:
                self._sender_task.cancel()
            if self.websocket:
                asyncio.create_task(self.websocket.close())
                self.websocket = None
        except Exception as e:
            raise ValueError(f"Error disconnecting WebSocket: {e}")

    # 3. Private/internal helpers
    def _warn_queue_pressure(self):
        size = self._queue.qsize()
        if size > self._queue_warn_threshold:
            self.logger.warning(
                f"Audio frame queue high: size={size} threshold={self._queue_warn_threshold}"
            )

    async def _run_sender(self):
        try:
            while not self._closed:
                active_frames_limit = self._calculate_active_frame_limit()
                pause_seconds = self._active_seconds * 0.9
                sent_bytes = 0
                frame_count = 0
                while sent_bytes < active_frames_limit and not self._closed:
                    gen, frame = await self._queue.get()
                    if gen != self._gen:
                        continue  # flushed
                    if not self.websocket or self._closed:
                        return
                    try:
                        await self.websocket.send(frame)
                    except Exception as e:
                        self.logger.error(f"Send error: {e}")
                        return
                    sent_bytes += len(frame)
                    frame_count += 1
                    if frame_count % 200 == 0:
                        self._warn_queue_pressure()

                    if self._queue.empty():
                        # No more frames to send
                        pause_seconds = 0
                        break
                if not self._closed and pause_seconds > 0:
                    await asyncio.sleep(pause_seconds)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Sender task error: {e}")

    def _calculate_active_frame_limit(self) -> int:
        return self._active_seconds * 16000 * 2 * 1
