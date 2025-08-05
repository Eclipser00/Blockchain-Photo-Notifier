# utils/crypto.py
import hashlib
import base64


def sha256(data: bytes) -> bytes:
    """Retorna SHA-256 de los datos."""
    return hashlib.sha256(data).digest()

def encode_base64(data: bytes) -> str:
    """Codifica bytes a Base64."""
    return base64.b64encode(data).decode('utf-8')