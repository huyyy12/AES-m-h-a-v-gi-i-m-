from hashlib import sha512

# Tính SHA-512 hash cho dữ liệu đầu vào (bytes)
def sha512_hash(data: bytes) -> str:
    return sha512(data).hexdigest()
