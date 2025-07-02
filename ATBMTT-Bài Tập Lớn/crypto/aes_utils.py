from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# ✅ Mã hóa file bằng AES-CBC
def encrypt_file_aes(filepath):
    session_key = get_random_bytes(32)  # AES-256
    iv = get_random_bytes(16)           # 128-bit IV
    cipher = AES.new(session_key, AES.MODE_CBC, iv)

    with open(filepath, 'rb') as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return ciphertext, iv, session_key

# ✅ Giải mã file AES-CBC và lưu ra file
def decrypt_file_aes(ciphertext, iv, session_key, output_path):
    cipher = AES.new(session_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

    with open(output_path, 'wb') as f:
        f.write(plaintext)

# ✅ Mã hóa dữ liệu bytes (cho phần tải về)
def encrypt_bytes_aes(data: bytes):
    session_key = get_random_bytes(32)
    iv = get_random_bytes(16)
    cipher = AES.new(session_key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))
    return ciphertext, iv, session_key

# ✅ Giải mã dữ liệu bytes (nếu dùng trong verify khi tải về)
def decrypt_bytes_aes(ciphertext: bytes, iv: bytes, key: bytes):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext
