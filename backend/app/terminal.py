import json
import websockets
import asyncio
import subprocess

async def handle_client(websocket, path):
    # Receive data from the backend
    data = await websocket.recv()
    print(f"Received data: {data}")
    parsed_data = json.loads(data)
    args_file = parsed_data["args_file"]
    script_file = parsed_data["script_file"]

    # Run the script in the terminal
    subprocess.run(["python", script_file])

    # Send the output file name back to the backend
    output_file = "output.txt"
    await websocket.send(output_file)

# Start the WebSocket server
start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
