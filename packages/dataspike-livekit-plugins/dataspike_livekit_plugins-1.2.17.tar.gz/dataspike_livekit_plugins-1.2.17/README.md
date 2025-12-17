# Dataspike Deepfake Detection Plugin for LiveKit Agents

This plugin integrates [Dataspike](https://dataspike.io/) with LiveKit Agents to provide **real-time deepfake detection**.
It enables detection of synthetic or manipulated media in both **video and audio streams** during live or recorded sessions.

## Installation

```bash
pip install dataspike-livekit-plugins
```

## Prerequisites

You’ll need a **Dataspike API key**. Set it as an environment variable before running your agent:

```bash
export DATASPIKE_API_KEY="your_api_key_here"
```

## Usage Examples

### Basic Video Detection

```python
from livekit.plugins import dataspike
from livekit.agents import AgentSession, Agent

async def entrypoint(ctx):
    await ctx.connect()
    session = AgentSession(...)
    detector = dataspike.DataspikeDetector()
    await detector.start(session, room=ctx.room)
    await session.start(agent=Agent(instructions="Talk to me!"), room=ctx.room)
```

### Video + Audio Detection

```python
from livekit.plugins import dataspike
from livekit.agents import AgentSession, Agent

async def entrypoint(ctx):
    await ctx.connect()
    session = AgentSession(...)

    # Configure video processing
    video_params = dataspike.VideoParams(
        burst_fps=1,            # Video FPS during suspicious state
        normal_fps=0.2,         # Video FPS during normal state
        quality=75,             # JPEG quality (0-100)
    )

    # Configure audio processing
    audio_params = dataspike.AudioParams(
        sample_rate=16000,      # Required: 16kHz PCM
        sample_size=48000,      # 3 seconds of audio
        interval=60,            # Minimum 60 seconds between samples
    )

    detector = dataspike.DataspikeDetector(
        video_params=video_params,
        audio_params=audio_params,
    )

    await detector.start(session, room=ctx.room)
    await session.start(agent=Agent(instructions="Talk to me!"), room=ctx.room)
```

### With Voice Activity Detection (VAD)

```python
from livekit.plugins import dataspike, silero
from livekit.agents import AgentSession, Agent

async def entrypoint(ctx):
    await ctx.connect()
    session = AgentSession(...)

    # Setup VAD for speech detection
    vad = silero.VAD.load()
    vad_stream = vad.stream()

    # Setup detector with audio processing
    detector = dataspike.DataspikeDetector(
        audio_params=dataspike.AudioParams()
    )

    # Start detector with VAD integration
    # Audio will only be processed when user is speaking
    await detector.start(session, room=ctx.room, vad_stream=vad_stream)
    await session.start(agent=Agent(instructions="Talk to me!"), room=ctx.room)
```

## Configuration

### VideoParams

Configure video processing behavior:

- **burst_fps** (float): Video sampling rate during suspicious state (default: 1)
- **normal_fps** (float): Video sampling rate during normal state (default: 0.2)
- **quality** (int): JPEG quality 0-100 (default: 75)

### AudioParams

Configure audio processing behavior:

- **sample_rate** (int): Target sample rate in Hz (default: 16000, required by Dataspike API)
- **sample_size** (int): Number of samples per chunk (default: 48000 = 3 seconds at 16kHz)
- **interval** (int): Minimum seconds between audio samples (default: 60)

### DataspikeDetector

Main detector configuration:

- **api_key** (str): Dataspike API key (or set `DATASPIKE_API_KEY` env var)
- **video_params** (VideoParams): Video processing configuration (default: VideoParams())
- **audio_params** (AudioParams): Enable audio detection (default: None, disabled)
- **notification_cb** (callable): Custom callback for detection events

## Features

- ✅ **Real-time video deepfake detection** with adaptive frame rates
- ✅ **Real-time audio deepfake detection** with automatic resampling to 16kHz PCM
- ✅ **VAD integration** to process audio only during speech activity
- ✅ **Automatic reconnection** with exponential backoff
- ✅ **Backpressure handling** with bounded queues and frame dropping
- ✅ **Customizable notifications** via callbacks or room data messages
 
## Links

- [Dataspike API](https://docs.dataspike.io/api)
- [LiveKit Agents SDK](https://github.com/livekit/agents)
