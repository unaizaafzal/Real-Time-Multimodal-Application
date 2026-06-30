import asyncio
import time
import websockets

async def main():
    uri = "ws://127.0.0.1:8000/ws/echo"
    async with websockets.connect(uri) as websocket:
        message = "hello server"
        
        start = time.time()
        await websocket.send(message)
        print(f"[{start:.3f}] sent: {message}")
        
        response = await websocket.recv()
        end = time.time()
        print(f"[{end:.3f}] received: {response}")
        print(f"round trip: {(end - start)*1000:.2f} ms")

asyncio.run(main())