from flask import Flask, render_template, request, flash
import socket
import os
import base64
import json
import time

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crypto.aes_utils import encrypt_file_aes
from crypto.rsa_utils import (
    sign_metadata, load_private_key, load_public_key, encrypt_session_key
)
from crypto.integrity_utils import sha512_hash

app = Flask(__name__)
app.secret_key = 'upload_secret_key'

UPLOAD_FOLDER = 'encrypted'
SENT_FOLDER = 'sent'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SENT_FOLDER, exist_ok=True)

# Cấu hình các node cloud
NODES = [
    ("127.0.0.1", 9001, "keys/public_b.pem"),  # Node B
    ("127.0.0.1", 9002, "keys/public_c.pem"),  # Node C
]

@app.route('/')
def index():
    sent_files = os.listdir(SENT_FOLDER)
    return render_template('send.html', files=sent_files)

@app.route('/send', methods=['POST'])
def send_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        flash("Chưa chọn file.")
        return render_template('send.html', files=os.listdir(SENT_FOLDER))

    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)

    # 1. Mã hóa AES
    ciphertext, iv, session_key = encrypt_file_aes(filepath)

    # 2. Metadata + chữ ký
    timestamp = str(int(time.time()))
    metadata = {
        "filename": filename,
        "timestamp": timestamp,
        "transaction_id": "TXN-" + timestamp
    }
    private_key = load_private_key("keys/private_a.pem")
    signature = sign_metadata(private_key, metadata)

    # 3. Tính hash toàn vẹn
    hash_value = sha512_hash(iv + ciphertext)

    # 4. Gửi đồng thời tới từng node
    success_nodes = 0
    for host, port, pubkey_path in NODES:
        try:
            public_key_node = load_public_key(pubkey_path)
            enc_session_key = encrypt_session_key(public_key_node, session_key)

            packet = {
                "metadata": metadata,
                "iv": base64.b64encode(iv).decode(),
                "cipher": base64.b64encode(ciphertext).decode(),
                "hash": hash_value,
                "signature": base64.b64encode(signature).decode(),
                "session_key": base64.b64encode(enc_session_key).decode()
            }

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall((json.dumps(packet) + "\n").encode())
                response = s.recv(1024).decode()

            if response == "ACK":
                success_nodes += 1
                print(f"✅ Gửi thành công tới {host}:{port}")
            else:
                print(f"❌ Bị từ chối bởi {host}:{port}")

        except Exception as e:
            print(f"❌ Lỗi gửi tới {host}:{port} - {str(e)}")

    if success_nodes == len(NODES):
        flash("📤 Gửi thành công tới cả hai node!")
        # Lưu lại file đã gửi
        with open(filepath, 'rb') as fsrc:
            with open(os.path.join(SENT_FOLDER, filename), 'wb') as fdst:
                fdst.write(fsrc.read())
    else:
        flash("⚠️ Một số node không nhận được file!")

    return render_template('send.html', files=os.listdir(SENT_FOLDER))

if __name__ == '__main__':
    app.run(debug=True)
