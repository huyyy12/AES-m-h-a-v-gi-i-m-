# server.py
import asyncio
import websockets
import json
import os
from datetime import datetime

FILE_DIR = "uploaded_files"
os.makedirs(FILE_DIR, exist_ok=True)

files_storage = {
    "A": {},
    "B": {}
}

upload_log = []
clients = set()

async def save_file(source, filename, encrypted_data):
    path = os.path.join(FILE_DIR, f"{source}_{filename}")
    with open(path, "wb") as f:
        f.write(encrypted_data.encode("utf-8"))
    files_storage[source][filename] = encrypted_data
    upload_log.append({
        "source": source,
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    print(f"[{source}] Saved file: {filename}")

async def get_file_list(source):
    return list(files_storage[source].keys())

async def get_file(source, filename):
    return files_storage[source].get(filename, None)

async def broadcast_message(sender_ws, message_obj):
    for client in clients:
        if client != sender_ws:
            await client.send(json.dumps(message_obj))

async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
                continue

            action = data.get("action")
            source = data.get("source")

            if action == "send_encrypted_A":
                filename = data.get("filename")
                fileData = data.get("fileData")
                if filename and fileData:
                    await save_file("A", filename, fileData)
                    await websocket.send(json.dumps({"status": "file_received_A"}))

            elif action == "send_encrypted_B":
                filename = data.get("filename")
                fileData = data.get("fileData")
                if filename and fileData:
                    await save_file("B", filename, fileData)
                    await websocket.send(json.dumps({"status": "file_received_B"}))

            elif action == "list_files_A":
                files = await get_file_list("A")
                await websocket.send(json.dumps({"status": "list_files_A", "files": files}))

            elif action == "list_files_B":
                files = await get_file_list("B")
                await websocket.send(json.dumps({"status": "list_files_B", "files": files}))

            elif action == "request_file_A":
                filename = data.get("filename")
                fileData = await get_file("A", filename)
                if fileData:
                    await websocket.send(json.dumps({
                        "status": "file_ready_A",
                        "file": fileData,
                        "filename": filename
                    }))
                else:
                    await websocket.send(json.dumps({"status": "no_file_A"}))

            elif action == "request_file_B":
                filename = data.get("filename")
                fileData = await get_file("B", filename)
                if fileData:
                    await websocket.send(json.dumps({
                        "status": "file_ready_B",
                        "file": fileData,
                        "filename": filename
                    }))
                else:
                    await websocket.send(json.dumps({"status": "no_file_B"}))

            elif action == "get_upload_log":
                await websocket.send(json.dumps({
                    "status": "upload_log",
                    "log": upload_log
                }))

            elif action == "send_message":
                msg = data.get("message")
                sender = data.get("sender")
                if msg and sender:
                    msg_obj = {
                        "status": "chat_message",
                        "sender": sender,
                        "message": msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    }
                    await broadcast_message(websocket, msg_obj)

    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        clients.discard(websocket)

async def main():
    print("Starting server on ws://localhost:8080")
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
