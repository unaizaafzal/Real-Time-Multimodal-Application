from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time

app = FastAPI()

@app.websocket("/ws/echo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # NEW: open a file in binary-write mode to save the incoming audio.
    # "wb" = write binary. Each new connection overwrites this file —
    # fine for testing, we'll make it unique per session later if needed.
    audio_file = open("received_audio.webm", "wb")

    try:
        while True:
            data = await websocket.receive_bytes()
            print(f"[{time.time():.3f}] received chunk: {len(data)} bytes")

            # NEW: write this chunk to the file immediately, don't buffer it
            audio_file.write(data)

            await websocket.send_bytes(f"Message bytes was: {data}".encode())

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        # NEW: always close the file, even if the connection drops unexpectedly.
        # This matters because an unclosed file can lose buffered data
        # that never got flushed to disk.
        audio_file.close()
        print("Audio file closed and saved.")