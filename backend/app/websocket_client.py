import websockets
import asyncio
import json

async def connect_to_server():
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            message = {"arg1": 5, "arg2": 10, "script_file_name": "test_script.py"}
            print(f"Sending message: {message}")
            await websocket.send(json.dumps(message))

            # Wait for the response
            response = await websocket.recv()
            print(f"Received response: {response}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the client
asyncio.run(connect_to_server())
