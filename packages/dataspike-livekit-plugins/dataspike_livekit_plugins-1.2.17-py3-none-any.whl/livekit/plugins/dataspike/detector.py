# Copyright 2025 LiveKit, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import json
import os
import random
import time
from collections.abc import Awaitable
from typing import Any, Callable

import aiohttp

from livekit import rtc
from livekit.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    AgentSession,
    APIConnectOptions,
    APIStatusError,
    utils,
)
from livekit.agents.utils.images import EncodeOptions, encode
from livekit.plugins.dataspike.schema_pb2 import (
    DeepfakeStreamingSchemaFrameRequest,
    DeepfakeStreamingSchemaFrameRequestFormat,
    DeepfakeStreamingSchemaResultEvent,
    DeepfakeStreamingSchemaResultEventType as EventType,
)

from .log import logger


class VideoParams:
    """Configuration parameters for video frame processing.

    Attributes
    ----------
    burst_fps:
        Frame rate when SUSPICIOUS state is detected (higher rate for verification)
    normal_fps:
        Frame rate during CLEAR state (lower rate to conserve resources)
    quality:
        JPEG compression quality (0-100, where 100 is highest quality)
    """

    def __init__(
        self,
        burst_fps: float = 1,
        normal_fps: float = 0.2,
        quality: int = 75,
    ):
        self.burst_fps = burst_fps
        self.normal_fps = normal_fps
        self.quality = quality


class AudioParams:
    """Configuration parameters for audio processing.

    Per Dataspike API requirements:
    - Audio must be raw PCM format sampled at 16kHz
    - Data sent in chunks of 48,000 samples (3 seconds of audio)
    - Shorter final chunks should be zero-padded to required length

    Attributes
    ----------
    sample_rate:
        Required sampling rate in Hz (must be 16000)
    sample_size:
        Number of samples per chunk (48000 = 3 seconds at 16kHz)
    interval:
        Minimum seconds between audio samples
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        sample_size: int = 48000,  # 3 seconds * 16000 samples/sec
        interval: int = 60,
    ):
        self.sample_rate = sample_rate
        self.sample_size = sample_size
        self.interval = interval


class InputTrack:
    """Frame-sampling wrapper for a remote video track.

    An `InputTrack` decides when to sample frames (based on the current
    detection state) and enqueues JPEG-encoded frames for transmission.

    Parameters
    ----------
    track:
        The LiveKit `rtc.Track` to sample (must be a video track).
    participant_identity:
        Identity of the remote participant that owns `track`.
    video_params:
        Video processing configuration (FPS, quality).
    state:
        Initial state for adaptive sampling; defaults to `EventType.CLEAR`.

    Attributes
    ----------
    last_sampled_time:
        Timestamp of the last emitted frame (seconds). `None` until the first sample.
    running:
        Whether the consumer loop should continue sampling.
    """

    def __init__(
        self,
        *,
        track: rtc.Track,
        participant_identity: str,
        video_params: VideoParams,
        state: EventType = EventType.CLEAR,
    ):
        self.track = track
        self.participant_identity = participant_identity
        self.video_params = video_params
        self.last_sampled_time: float | None = None
        self.state = state
        self.running = False

    def _skip_frame(self, now: float) -> bool:
        """Return `True` if the current frame should be skipped given `now`."""

        target_fps = (
            self.video_params.burst_fps
            if self.state == EventType.SUSPICIOUS
            else self.video_params.normal_fps
        )
        if target_fps == 0:
            return True

        min_frame_interval = 1.0 / target_fps

        if self.last_sampled_time is None:
            self.last_sampled_time = now
            return False

        if (now - self.last_sampled_time) >= min_frame_interval:
            self.last_sampled_time = now
            return False

        return True

    async def consume(
        self,
        q: asyncio.Queue[DeepfakeStreamingSchemaFrameRequest],
    ) -> None:
        """Read frames from `track`, encode to JPEG, and put them in async Queue `q`.

        The queue is bounded; if it is full or times out, frames are dropped to keep
        latency low.

        Parameters
        ----------
        q:
            The outbound queue to receive `DeepfakeStreamingSchemaFrameRequest` items.
        """

        self.running = True
        stream = rtc.VideoStream(self.track)

        async for stream_event in stream:
            now = time.time()
            frame = stream_event.frame

            if not self.running:
                break

            if self._skip_frame(now):
                continue

            image_bytes = encode(
                frame,
                EncodeOptions(
                    format="JPEG",
                    quality=self.video_params.quality,
                ),
            )
            event = DeepfakeStreamingSchemaFrameRequest(
                participant_id=self.participant_identity,
                track_id=self.track.sid,
                timestamp_ms=int(now * 1000),
                format=DeepfakeStreamingSchemaFrameRequestFormat.JPEG,
                data=image_bytes,
            )

            try:
                await asyncio.wait_for(q.put(event), timeout=0.05)
            except asyncio.QueueFull:
                # drop message silently, we do not want stale messages to block the queue
                pass
            except asyncio.TimeoutError:
                pass

        await stream.aclose()

    def stop(self) -> None:
        """Signal the consumer loop to stop sampling."""
        self.running = False


class InputAudioTrack:
    """Audio sampling wrapper for a remote audio track.

    Accumulates audio frames into 3-second chunks (48,000 samples at 16kHz)
    and enqueues them for transmission to Dataspike API. Audio is resampled
    to the required 16kHz PCM format.

    Parameters
    ----------
    track:
        The LiveKit `rtc.Track` to sample (must be an audio track).
    participant_identity:
        Identity of the remote participant that owns `track`.
    audio_params:
        Audio processing configuration (sample rate, chunk size, interval).
    user_speaking:
        Whether the user is currently speaking (audio only processed during speech).

    Attributes
    ----------
    last_sampled_time:
        Timestamp of the last emitted audio chunk (seconds). `None` until the first sample.
    audio_buffer:
        Accumulated audio samples waiting to be sent.
    running:
        Whether the consumer loop should continue sampling.
    """

    def __init__(
        self,
        *,
        track: rtc.Track,
        participant_identity: str,
        audio_params: AudioParams,
    ):
        self.track = track
        self.participant_identity = participant_identity
        self.audio_params = audio_params
        self.last_sampled_time: float | None = None
        self.audio_buffer: bytearray = bytearray()
        self.running = False
        self.user_speaking = False

    async def consume(
        self,
        q: asyncio.Queue[DeepfakeStreamingSchemaFrameRequest],
    ) -> None:
        """Read audio frames from `track`, resample to 16kHz PCM, and accumulate into 3-second chunks.

        The queue is bounded; if it is full or times out, chunks are dropped to keep
        latency low.

        Parameters
        ----------
        q:
            The outbound queue to receive `DeepfakeStreamingSchemaFrameRequest` items.
        """

        self.running = True
        stream = rtc.AudioStream(self.track)

        # Create resampler if needed
        resampler: rtc.AudioResampler | None = None

        async for audio_event in stream:
            now = time.time()
            frame = audio_event.frame

            if not self.running:
                break

            # Only process audio when user is actively speaking
            if not self.user_speaking:
                continue

            # Enforce minimum interval between audio samples
            if (
                self.last_sampled_time is not None
                and now - self.last_sampled_time < self.audio_params.interval
            ):
                continue

            # Initialize resampler if needed (lazy initialization based on actual input rate)
            if resampler is None and frame.sample_rate != self.audio_params.sample_rate:
                resampler = rtc.AudioResampler(
                    input_rate=frame.sample_rate,
                    output_rate=self.audio_params.sample_rate,
                    quality=rtc.AudioResamplerQuality.QUICK,
                    num_channels=1,  # Dataspike expects mono audio
                )

            # Resample if necessary
            if resampler is not None:
                resampled_frames = resampler.push(frame)
                for resampled_frame in resampled_frames:
                    # Convert to bytes and accumulate
                    self.audio_buffer.extend(resampled_frame.data)
            else:
                # No resampling needed
                self.audio_buffer.extend(frame.data)

            # Send when we have a complete 3-second chunk (sample_size * 2 bytes per sample for int16)
            bytes_needed = self.audio_params.sample_size * 2  # int16 = 2 bytes per sample
            if len(self.audio_buffer) >= bytes_needed:
                chunk_data = bytes(self.audio_buffer[:bytes_needed])
                self.audio_buffer = bytearray(self.audio_buffer[bytes_needed:])
                self.last_sampled_time = now

                # Create Dataspike API request
                event = DeepfakeStreamingSchemaFrameRequest(
                    participant_id=self.participant_identity,
                    track_id=self.track.sid,
                    timestamp_ms=int(now * 1000),
                    format=DeepfakeStreamingSchemaFrameRequestFormat.PCM,
                    data=chunk_data,
                )

                # Queue for sending (drop if queue is full to avoid blocking)
                try:
                    await asyncio.wait_for(q.put(event), timeout=0.05)
                except asyncio.QueueFull:
                    # Drop message silently
                    pass
                except asyncio.TimeoutError:
                    pass

        # Flush resampler if exists
        if resampler is not None:
            resampled_frames = resampler.flush()
            for resampled_frame in resampled_frames:
                self.audio_buffer.extend(resampled_frame.data)

        await stream.aclose()

    def stop(self) -> None:
        """Signal the consumer loop to stop sampling."""
        self.running = False

    def set_speaking(self, speaking: bool) -> None:
        """Update the speaking state to control audio processing."""
        self.user_speaking = speaking


class DataspikeDetector:
    """Real-time deepfake detector for LiveKit video rooms.

    This class manages frame sampling, encoding, and streaming to the
    Dataspike API. It also handles event notifications, reconnection, and
    adaptive frame rates.
    """

    MAX_QUEUE_SIZE = 16
    NOTIFICATION_TOPIC = "deepfake_alert"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
        video_params: VideoParams | None = None,
        audio_params: AudioParams | None = None,
        notification_cb: (
            Callable[[DeepfakeStreamingSchemaResultEvent], Awaitable[None]] | None
        ) = None,
    ) -> None:
        """
        Initialize the Dataspike real-time deepfake detector.

        The detector subscribes to remote participants' video and audio tracks in a LiveKit room,
        samples frames/audio at an adaptive rate, and streams them to the Dataspike WebSocket
        API for real-time analysis.

        Under the default configuration, the detector automatically **publishes analysis
        results back to the same LiveKit room** as JSON data messages on
        ``NOTIFICATION_TOPIC`` (``"deepfake_alert"``). This allows other participants or
        in-room agents to receive detection updates instantly.

        Developers can override this behavior by providing a custom ``notification_cb``.
        The callback receives each ``DeepfakeStreamingSchemaResultEvent`` as an argument
        and can implement any desired action — such as persisting results, triggering
        moderation workflows, or routing alerts to external systems — instead of or in
        addition to publishing data messages.

        Args:
            api_key:
                Dataspike API key. If omitted, the detector reads ``DATASPIKE_API_KEY``
                from the environment. A missing key raises ``ValueError`` at startup.
            conn_options:
                Connection and retry settings for outbound API/WebSocket traffic.
                Defaults to ``DEFAULT_API_CONNECT_OPTIONS`` from ``livekit.agents``.
            video_params:
                Optional video processing configuration. If not provided, uses default
                VideoParams with burst_fps=1, normal_fps=0.2, quality=75.
            audio_params:
                Optional audio processing configuration. If provided, enables audio
                deepfake detection alongside video. Audio is resampled to 16kHz PCM
                and sent in 3-second chunks. If None, audio detection is disabled.
            notification_cb:
                Optional async callback invoked when the detector receives a result
                event from Dataspike. Signature:
                ``Callable[[DeepfakeStreamingSchemaResultEvent], Awaitable[None]]``.
                If not provided, a default notifier publishes a compact JSON payload
                to the room's data channel under ``NOTIFICATION_TOPIC``.

        Detection Flow:
            1. **Track discovery** – when a remote participant's video track is
               subscribed, the detector starts an ``InputTrack`` consumer task.
            2. **Adaptive sampling** – each consumer emits frames at either
               ``normal_fps`` or ``burst_fps`` depending on the current state
               (CLEAR → normal, SUSPICIOUS/ALERT → burst).
            3. **Encoding** – frames are encoded to JPEG with the configured
               ``quality`` and placed on a bounded async queue (``MAX_QUEUE_SIZE``)
               to prevent backpressure from stalling the media pipeline.
            4. **Streaming** – a background WebSocket task sends queued frames to
               the Dataspike API and receives result events.
            5. **State updates & notifications** – incoming events update per-track
               state and trigger notifications via ``notification_cb`` (or the
               default publisher).

        Notification Semantics:
            The default notifier publishes a JSON object like:
            ``{"type": "deepfake_alert", "level": "<clear|suspicious|alert>", "level_code": <int>,
              "participant_id": "...", "track_id": "...", "message": "...", "timestamp_ms": ...}``.
            For example:
              • CLEAR  → "No active manipulation detected."
              • SUSPICIOUS → "Possible manipulation indicators detected."
              • ALERT → "High likelihood of manipulation detected."

        Reliability & Reconnection:
            The detector maintains a persistent WebSocket connection to Dataspike and
            automatically reconnects on errors or unexpected closes, using exponential
            backoff with jitter. Notification errors are contained and logged so they
            do not terminate the stream.

        Performance & Backpressure:
            • Frame sampling is time-based (FPS), not frame-count based.
            • The send queue is bounded to ``MAX_QUEUE_SIZE``; when full, frames are
              dropped to keep latency low and avoid cascading stalls.
            • JPEG quality lets you trade off detail vs. bandwidth; consider lowering
              quality or FPS for large rooms.

        Security:
            • The detector only transmits encoded frames and minimal metadata required
              for analysis.
            • Store ``DATASPIKE_API_KEY`` securely (env vars or secret manager). Avoid
              hard-coding in source.

        Usage Patterns:

            **As part of a ROOM worker (recommended for scaling):**
                >>> async def entrypoint(ctx: JobContext):
                ...     await ctx.connect()
                ...     session = AgentSession(...)
                ...     detector = DataspikeDetector()
                ...     await detector.start(session, room=ctx.room)
                ...     await session.start(agent=Agent(...), room=ctx.room)

            **Standalone participant (immediate join of a specific room):**
                Create an ``rtc.Room()``, connect with a valid token, then:
                >>> detector = DataspikeDetector()
                >>> await detector.start(agent_session, room)

        Notes:
            • The detector listens to ``track_subscribed`` / ``track_unsubscribed``
              events and is robust to tracks appearing/disappearing while the agent runs.
        """

        self._ws_url = os.getenv(
            "DATASPIKE_WS_URL", "wss://api.dataspike.io/api/v4/deepfake/stream"
        )
        self._api_key = api_key or os.getenv("DATASPIKE_API_KEY")

        if not self._api_key:
            raise ValueError("DATASPIKE_API_KEY must be set")

        self._video_params = video_params if video_params is not None else VideoParams()
        self._audio_params = audio_params if audio_params is not None else AudioParams()

        self._conn_options = conn_options
        self._session: aiohttp.ClientSession | None = None
        self._agent_session: AgentSession | None = None
        self._room: rtc.Room | None = None

        self._pool = utils.ConnectionPool[aiohttp.ClientWebSocketResponse](
            connect_cb=self._connect_ws,
            close_cb=self._close_ws,
        )
        self._send_queue: asyncio.Queue[DeepfakeStreamingSchemaFrameRequest] = asyncio.Queue(
            maxsize=self.MAX_QUEUE_SIZE
        )
        self._input_tracks: list[InputTrack] = []
        self._input_audio_tracks: list[InputAudioTrack] = []

        self._notification_cb = notification_cb or self._notify

    async def start(
        self, agent_session: AgentSession, room: rtc.Room, vad_stream: Any = None
    ) -> None:
        """Attach the detector to an agent session and a LiveKit room.

        This method:
        1) Caches `agent_session` and `room`.
        2) Starts the WebSocket sender/receiver tasks.
        3) Scans existing remote participants for video and audio tracks and begins sampling.
        4) Subscribes to room events to track future subscribe/unsubscribe events.
        5) Optionally integrates with a VAD stream for speech detection.

        Parameters
        ----------
        agent_session:
            The running `AgentSession` coordinating the LiveKit agent.
        room:
            The connected `rtc.Room` whose remote video and audio tracks will be monitored.
        vad_stream:
            Optional VAD stream for detecting when users are speaking. If provided,
            audio will only be processed during speech activity.
        """

        self._agent_session = agent_session
        self._room = room

        asyncio.create_task(self._run_ws_forever())

        # If VAD stream is provided, start monitoring it for speech events
        if vad_stream:
            asyncio.create_task(self._monitor_vad(vad_stream))

        logger.info("Dataspike deepfake detector started")

        for participant in self._room.remote_participants.values():
            for pub in participant.track_publications.values():
                track = pub.track  # may be None until subscribed
                if track and track.kind == rtc.TrackKind.KIND_VIDEO:
                    self._add_track(participant, track)
                elif track and track.kind == rtc.TrackKind.KIND_AUDIO:
                    self._add_audio_track(participant, track)

        @self._room.on("track_subscribed")
        def on_track_subscribed(
            track: rtc.Track,
            publication: rtc.RemoteTrackPublication,
            participant: rtc.RemoteParticipant,
        ) -> None:
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                self._add_track(participant, track)
            elif track.kind == rtc.TrackKind.KIND_AUDIO:
                self._add_audio_track(participant, track)

        @self._room.on("track_unsubscribed")
        def on_track_unsubscribed(
            track: rtc.Track,
            publication: rtc.TrackPublication,
            participant: rtc.RemoteParticipant,
        ) -> None:
            if track.kind == rtc.TrackKind.KIND_VIDEO:
                self._remove_track(track)
            elif track.kind == rtc.TrackKind.KIND_AUDIO:
                self._remove_audio_track(track)

    def _add_track(self, participant: rtc.RemoteParticipant, track: rtc.Track) -> None:
        if track.kind != rtc.TrackKind.KIND_VIDEO:
            return

        input_track = InputTrack(
            track=track,
            participant_identity=participant.identity,
            video_params=self._video_params,
        )
        self._input_tracks.append(input_track)

        logger.debug(f"track subscribed: {track.sid} by {participant.identity} kind={track.kind}")
        asyncio.create_task(input_track.consume(self._send_queue))

    def _remove_track(self, track: rtc.Track) -> None:
        if track.kind != rtc.TrackKind.KIND_VIDEO:
            return

        input_track = next((t for t in self._input_tracks if t.track.sid == track.sid), None)
        if input_track:
            logger.debug(
                f"track unsubscribed: {track.sid} by {input_track.participant_identity} kind={track.kind}"
            )
            input_track.stop()
            self._input_tracks.remove(input_track)

    def _add_audio_track(self, participant: rtc.RemoteParticipant, track: rtc.Track) -> None:
        if track.kind != rtc.TrackKind.KIND_AUDIO:
            return

        input_audio_track = InputAudioTrack(
            track=track,
            participant_identity=participant.identity,
            audio_params=self._audio_params,
        )
        self._input_audio_tracks.append(input_audio_track)

        logger.debug(f"audio track subscribed: {track.sid} by {participant.identity}")
        asyncio.create_task(input_audio_track.consume(self._send_queue))

    def _remove_audio_track(self, track: rtc.Track) -> None:
        if track.kind != rtc.TrackKind.KIND_AUDIO:
            return

        input_audio_track = next(
            (t for t in self._input_audio_tracks if t.track.sid == track.sid), None
        )
        if input_audio_track:
            logger.debug(
                f"audio track unsubscribed: {track.sid} by {input_audio_track.participant_identity}"
            )
            input_audio_track.stop()
            self._input_audio_tracks.remove(input_audio_track)

    async def _monitor_vad(self, vad_stream: Any) -> None:
        """Monitor VAD stream and update audio track speaking states.

        This method listens for VAD events (START_OF_SPEECH, END_OF_SPEECH) and
        updates all audio tracks to enable/disable audio processing based on
        speech activity.

        Parameters
        ----------
        vad_stream:
            VAD stream that emits speech detection events.
        """
        try:
            # Import VADEventType dynamically to avoid hard dependency
            from livekit.agents import VADEventType

            async for vad_event in vad_stream:
                if vad_event.type == VADEventType.START_OF_SPEECH:
                    logger.debug("User started speaking - enabling audio processing")
                    for audio_track in self._input_audio_tracks:
                        audio_track.set_speaking(True)
                elif vad_event.type == VADEventType.END_OF_SPEECH:
                    logger.debug("User stopped speaking - disabling audio processing")
                    for audio_track in self._input_audio_tracks:
                        audio_track.set_speaking(False)
        except ImportError:
            logger.warning("VAD support requires livekit.agents.VADEventType")
        except Exception as e:
            logger.error(f"Error monitoring VAD stream: {e}", exc_info=e)

    async def _notify(self, event: DeepfakeStreamingSchemaResultEvent) -> None:
        """Default notifier: publish a compact JSON alert into the room data channel."""
        if self._room is None:
            logger.warning("Cannot send notification: no active room.")
            return

        pid = event.participant_id
        if event.type == EventType.CLEAR:
            msg = f"No active manipulation detected for {pid}."
        elif event.type == EventType.SUSPICIOUS:
            msg = f"Potential signs of manipulation detected for {pid}."
        elif event.type == EventType.ALERT:
            msg = f"High likelihood of manipulation detected for {pid}."

        data = {
            "type": "deepfake_alert",
            "level": EventType(event.type).name.lower(),
            "participant_id": pid,
            "track_id": event.track_id,
            "message": msg,
            "timestamp_ms": int(time.time() * 1000),
        }

        logger.debug(f"sending notification: {data}")

        await self._room.local_participant.publish_data(
            topic=self.NOTIFICATION_TOPIC,
            payload=json.dumps(data).encode("utf-8"),
        )

    def _ensure_session(self) -> aiohttp.ClientSession:
        if not self._session:
            self._session = utils.http_context.http_session()

        return self._session

    async def _connect_ws(self, timeout: float) -> aiohttp.ClientWebSocketResponse:
        session = self._ensure_session()
        url = self._ws_url
        headers = {"Authorization": f"Bearer {self._api_key}"}
        return await asyncio.wait_for(session.ws_connect(url, headers=headers), timeout)

    async def _close_ws(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        await ws.close()

    async def _run_ws(self) -> None:
        """Run the Dataspike WS send/receive tasks until closed or cancelled."""

        # This task is responsible for sending events from the send queue to the websocket.
        async def _send_task(ws: aiohttp.ClientWebSocketResponse) -> None:
            while True:
                event = await self._send_queue.get()
                try:
                    await ws.send_bytes(event.SerializeToString())
                finally:
                    self._send_queue.task_done()

        # This task handles receiving messages from the websocket.
        async def _recv_task(ws: aiohttp.ClientWebSocketResponse) -> None:
            while True:
                msg = await ws.receive()
                if msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                ):
                    raise APIStatusError("Dataspike websocket connection closed unexpectedly")

                if msg.type != aiohttp.WSMsgType.BINARY:
                    logger.warning("unexpected Dataspike message type %s", msg.type)
                    continue

                resp = DeepfakeStreamingSchemaResultEvent()
                try:
                    resp = resp.parse(msg.data)
                except Exception as e:
                    logger.warning("failed to parse Dataspike message", exc_info=e)
                    continue

                # For suspicious events, update the state of the corresponding input track.
                # Input track will apply the appropriate action based on the state.
                if resp.type == EventType.SUSPICIOUS:
                    for input_track in self._input_tracks:
                        if input_track.track.sid == resp.track_id:
                            input_track.state = resp.type
                            break
                elif resp.type == EventType.CLEAR:
                    for input_track in self._input_tracks:
                        if input_track.track.sid == resp.track_id:
                            # only send notification if the state was ALERT
                            if input_track.state == EventType.ALERT:
                                await self._notification_cb(resp)
                            input_track.state = resp.type
                            break
                elif resp.type == EventType.ALERT:
                    for input_track in self._input_tracks:
                        if input_track.track.sid == resp.track_id:
                            # only send notification if the state is not already ALERT
                            if input_track.state != EventType.ALERT:
                                await self._notification_cb(resp)
                            input_track.state = resp.type
                            break

        # Create a websocket connection to the Dataspike API.
        async with self._pool.connection(timeout=self._conn_options.timeout) as ws:
            tasks = [
                asyncio.create_task(_send_task(ws)),
                asyncio.create_task(_recv_task(ws)),
            ]
            try:
                await asyncio.gather(*tasks)
            finally:
                await utils.aio.gracefully_cancel(*tasks)

    async def _run_ws_forever(self) -> None:
        """Keep the WS alive with exponential backoff and jitter on failure."""

        delay = 1.0
        while True:
            try:
                logger.info("Connecting to Dataspike websocket…")
                await self._run_ws()  # exits normally only if closed cleanly
            except asyncio.CancelledError:
                # shutting down; propagate cancel
                raise
            except Exception as e:
                logger.warning(f"Dataspike WS connection lost: {e!r}")
            # exponential backoff with jitter
            delay = min(delay * 2, 60)
            sleep_for = delay + random.uniform(0, delay / 2)
            logger.info(f"Reconnecting in {sleep_for:.1f}s…")
            await asyncio.sleep(sleep_for)
            # reset delay after successful connection next iteration
            delay = 1.0
