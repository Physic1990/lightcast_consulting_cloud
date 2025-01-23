# websocket_server.py
import asyncio
import websockets
import json

async def echo(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        print(f"Received: {data}")

        # Mock output file name and send it back
        output_file_name = "output_file.txt"
        await websocket.send(output_file_name)

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
