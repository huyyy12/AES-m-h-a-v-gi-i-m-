from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

# Tạo thư mục lưu khóa nếu chưa có
os.makedirs("client_a/keys", exist_ok=True)

# Tạo khóa riêng RSA 2048 bit
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Ghi private key vào file PEM
with open("client_a/keys/private_a.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Tạo và ghi public key
public_key = private_key.public_key()
with open("client_a/keys/public_a.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✅ Đã tạo xong private_a.pem và public_a.pem trong thư mục client_a/keys/")
