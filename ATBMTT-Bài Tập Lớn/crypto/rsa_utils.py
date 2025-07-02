from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import json

# Tải private key từ file .pem
def load_private_key(path):
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )

# Tải public key từ file .pem
def load_public_key(path):
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read()
        )

# Ký metadata (dạng dict)
def sign_metadata(private_key, metadata_dict):
    metadata_bytes = json.dumps(metadata_dict, sort_keys=True).encode()
    signature = private_key.sign(
        metadata_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA512()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA512()
    )
    return signature

# Xác minh chữ ký metadata
def verify_signature(public_key, metadata_dict, signature):
    metadata_bytes = json.dumps(metadata_dict, sort_keys=True).encode()
    try:
        public_key.verify(
            signature,
            metadata_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA512()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA512()
        )
        return True
    except:
        return False

# Mã hóa SessionKey bằng RSA public key
def encrypt_session_key(public_key, session_key):
    return public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None
        )
    )

# Giải mã SessionKey bằng RSA private key
def decrypt_session_key(private_key, encrypted_key):
    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA512()),
            algorithm=hashes.SHA512(),
            label=None
        )
    )
