from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import time
app = FastAPI()
@app.websocket("/ws/echo")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
            print(f"[{time.time():.3f}] received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
print(f"[{time.time():.3f}] sending response")