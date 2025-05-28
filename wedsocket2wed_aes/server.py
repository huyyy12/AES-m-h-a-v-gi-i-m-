# server.py
import asyncio
import websockets
import json
import os
from datetime import datetime

FILE_DIR = "uploaded_files"
os.makedirs(FILE_DIR, exist_ok=True)

files_storage = {
    "A": {},  # filename: encrypted_data
    "B": {}
}

upload_log = []  # Thêm log upload

async def save_file(source, filename, encrypted_data):
    # Lưu file lên ổ đĩa (ghi nhị phân để chính xác)
    path = os.path.join(FILE_DIR, f"{source}_{filename}")
    with open(path, "wb") as f:
        f.write(encrypted_data.encode('utf-8'))  # encrypted_data là chuỗi base64, encode thành bytes
    files_storage[source][filename] = encrypted_data

    # Ghi log với thời gian hiện tại
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

async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
                continue

            action = data.get("action")
            source = data.get("source")  # "A" or "B"

            if action == "send_encrypted_A":
                filename = data.get("filename")
                fileData = data.get("fileData")
                if filename and fileData:
                    await save_file("A", filename, fileData)
                    await websocket.send(json.dumps({"status": "file_received_A"}))
                else:
                    await websocket.send(json.dumps({"status": "error", "message": "Missing filename or fileData"}))

            elif action == "send_encrypted_B":
                filename = data.get("filename")
                fileData = data.get("fileData")
                if filename and fileData:
                    await save_file("B", filename, fileData)
                    await websocket.send(json.dumps({"status": "file_received_B"}))
                else:
                    await websocket.send(json.dumps({"status": "error", "message": "Missing filename or fileData"}))

            elif action == "list_files_A":
                files = await get_file_list("A")
                await websocket.send(json.dumps({"status": "list_files_A", "files": files}))

            elif action == "list_files_B":
                files = await get_file_list("B")
                await websocket.send(json.dumps({"status": "list_files_B", "files": files}))

            elif action == "request_file_A":
                filename = data.get("filename")
                if not filename:
                    await websocket.send(json.dumps({"status": "error", "message": "Missing filename"}))
                    continue
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
                if not filename:
                    await websocket.send(json.dumps({"status": "error", "message": "Missing filename"}))
                    continue
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

            else:
                await websocket.send(json.dumps({"status": "error", "message": "Unknown action"}))

    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    print("Starting server on ws://localhost:8080")
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
