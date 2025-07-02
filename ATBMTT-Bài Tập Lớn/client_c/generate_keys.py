from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

# Tạo thư mục keys nếu chưa có
os.makedirs("keys", exist_ok=True)

# Tạo khóa riêng
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Lưu khóa riêng vào file PEM
with open("keys/private_c.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Tạo và lưu khóa công khai
public_key = private_key.public_key()
with open("keys/public_c.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✅ Đã tạo xong cặp khóa RSA cho Client C.")
