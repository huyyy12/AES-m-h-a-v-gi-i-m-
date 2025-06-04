import asyncio
import websockets
import json
from datetime import datetime

clients = set()

async def broadcast(sender_ws, message):
    for c in clients:
        if c != sender_ws:
            await c.send(json.dumps(message))

async def handler(ws):
    print(f"Client connected: {ws.remote_address}")
    clients.add(ws)
    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
            except:
                await ws.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
                continue

            action = data.get("action")

            if action == "send_file_A":
                # Dữ liệu file base64, hash sha256
                filename = data.get("filename")
                fileData = data.get("fileData")
                fileHash = data.get("fileHash")
                print(f"[A] Received file: {filename} (hash sent: {fileHash})")

                # Gửi broadcast cho Web B nhận file
                await broadcast(ws, {
                    "status": "file_from_A",
                    "filename": filename,
                    "fileData": fileData,
                    "fileHash": fileHash
                })
                await ws.send(json.dumps({"status": "file_received_A"}))

            elif action == "send_file_B":
                # Tương tự nếu Web B gửi file, nếu có
                pass

    except websockets.ConnectionClosed:
        print(f"Client disconnected: {ws.remote_address}")
    finally:
        clients.discard(ws)

async def main():
    print("Server running on ws://localhost:8080")
    async with websockets.serve(handler, "localhost", 8080):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
