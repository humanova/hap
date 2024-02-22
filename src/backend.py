import asyncio
import json
import websockets

connected_clients = set()

markers = {
    1: {"id": 1, "lat": 41.0082, "lon": 28.9784, "summary": "Important news: Product recall in this area."},
    2: {"id": 2, "lat": 39.9334, "lon": 32.8597, "summary": "New competitor opening store nearby."}
}

async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        while True:
            # Wait for a message from the client
            data = await websocket.recv()
            message = json.loads(data)
            if message["action"] == "get_markers":
                await websocket.send(json.dumps({"action": "add_markers", "markers":list(markers.values())}))
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def add_marker(marker_id, data):
    markers[marker_id] = data
    for websocket in connected_clients:
        await websocket.send(json.dumps({"action": "add_marker", "marker": data}))

async def remove_marker(marker_id):
    del markers[marker_id]
    for websocket in connected_clients:
        await websocket.send(json.dumps({"action": "remove_marker", "marker": {"id": marker_id}}))

start_server = websockets.serve(handle_client, "localhost", 8765, ping_interval=20, ping_timeout=25)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

