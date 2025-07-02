from cryptography.hazmat.primitives import serialization

# Đường dẫn tới private key của A
private_key_path = "client_a/keys/private_a.pem"

# Đường dẫn sẽ lưu public key tương ứng
public_key_path = "client_a/keys/public_a.pem"

# Đọc private key
with open(private_key_path, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Trích xuất public key từ private key
public_key = private_key.public_key()

# Ghi public key ra file .pem
with open(public_key_path, "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

print("✅ Đã tạo lại file public_a.pem thành công.")
