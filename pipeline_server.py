import asyncio
import os
import time
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import (
    InputAudioRawFrame,
    TranscriptionFrame,
    InterimTranscriptionFrame,
    Frame
)
from pipecat.services.deepgram.stt import DeepgramSTTService, DeepgramSTTSettings
from pipecat.serializers.base_serializer import FrameSerializer
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketTransport,
    FastAPIWebsocketParams
)

load_dotenv()

app = FastAPI()


class RawAudioSerializer(FrameSerializer):
    async def setup(self, frame):
        pass

    async def deserialize(self, data: bytes | str):
        if isinstance(data, bytes) and len(data) > 0:
            return InputAudioRawFrame(
                audio=data,
                sample_rate=16000,
                num_channels=1
            )
        return None

    async def serialize(self, frame: Frame):
        return None


class TranscriptionLogger(FrameProcessor):
    async def process_frame(self, frame: Frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            print(f"[{time.time():.3f}] FINAL transcript: '{frame.text}'")

        elif isinstance(frame, InterimTranscriptionFrame):
            print(f"[{time.time():.3f}] interim: '{frame.text}'")

        await self.push_frame(frame, direction)


@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_in_enabled=True,
                audio_out_enabled=True,
                serializer=RawAudioSerializer(),
                allowed_origins=[]
            )
        )

        deepgram = DeepgramSTTService(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            encoding="linear16",
            sample_rate=16000,
            settings=DeepgramSTTSettings(
                interim_results=True,
                utterance_end_ms=1000,
            )
        )

        pipeline = Pipeline([
            transport.input(),
            deepgram,
            TranscriptionLogger(),
            transport.output(),
        ])

        task = PipelineTask(pipeline)
        runner = PipelineRunner()

        await runner.run(task)

    except Exception as e:
        print(f"ERROR IN ENDPOINT: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()