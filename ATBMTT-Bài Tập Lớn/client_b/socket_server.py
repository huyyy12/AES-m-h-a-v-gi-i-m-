import socket
import os
import json
import base64
from threading import Thread

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto.rsa_utils import (
    load_private_key, load_public_key,
    verify_signature, decrypt_session_key, encrypt_session_key
)
from crypto.aes_utils import decrypt_file_aes, encrypt_bytes_aes
from crypto.integrity_utils import sha512_hash

HOST = '127.0.0.1'
PORT = 9001
SAVE_FOLDER = 'decrypted'
os.makedirs(SAVE_FOLDER, exist_ok=True)

def handle_client(conn):
    try:
        data = b""
        while True:
            part = conn.recv(4096)
            if not part:
                break
            data += part
            if b"\n" in part:
                break

        request = json.loads(data.decode())

        if request.get("type") == "download_request":
            print("📩 Nhận yêu cầu tải lại file")

            metadata = request["metadata"]
            signature = base64.b64decode(request["signature"])
            public_key_a = load_public_key("keys/public_a.pem")

            if not verify_signature(public_key_a, metadata, signature):
                conn.sendall(json.dumps({"status": "INVALID_SIGNATURE"}).encode())
                print("❌ Chữ ký không hợp lệ.")
                return

            filename = metadata["filename"]
            filepath = os.path.join(SAVE_FOLDER, filename)
            if not os.path.exists(filepath):
                conn.sendall(json.dumps({"status": "NOT_FOUND"}).encode())
                print("❌ File không tồn tại.")
                return

            with open(filepath, "rb") as f:
                plaintext = f.read()
            cipher, iv, session_key = encrypt_bytes_aes(plaintext)

            enc_session_key = encrypt_session_key(public_key_a, session_key)

            response = {
                "status": "OK",
                "iv": base64.b64encode(iv).decode(),
                "cipher": base64.b64encode(cipher).decode(),
                "hash": sha512_hash(iv + cipher),
                "session_key": base64.b64encode(enc_session_key).decode()
            }
            conn.sendall((json.dumps(response) + "\n").encode())
            print(f"✅ Gửi lại file {filename} thành công.")

        else:
            # Nhận file mới
            metadata = request["metadata"]
            iv = base64.b64decode(request["iv"])
            cipher = base64.b64decode(request["cipher"])
            received_hash = request["hash"]
            signature = base64.b64decode(request["signature"])
            enc_session_key = base64.b64decode(request["session_key"])

            private_key = load_private_key("keys/private_b.pem")
            public_key = load_public_key("keys/public_a.pem")

            session_key = decrypt_session_key(private_key, enc_session_key)

            if not verify_signature(public_key, metadata, signature):
                conn.sendall(b"NACK")
                print("❌ Chữ ký không hợp lệ.")
                return

            if sha512_hash(iv + cipher) != received_hash:
                conn.sendall(b"NACK")
                print("❌ Hash không hợp lệ.")
                return

            filename = metadata["filename"]
            output_path = os.path.join(SAVE_FOLDER, filename)
            decrypt_file_aes(cipher, iv, session_key, output_path)
            conn.sendall(b"ACK")
            print(f"✅ Đã lưu file: {filename}")

    except Exception as e:
        print(f"❌ Lỗi xử lý: {e}")
        try:
            conn.sendall(b"NACK")
        except:
            pass
    finally:
        conn.close()

def start_server():
    print(f"🔌 Client B đang lắng nghe tại {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            Thread(target=handle_client, args=(conn,)).start()

if __name__ == '__main__':
    start_server()
