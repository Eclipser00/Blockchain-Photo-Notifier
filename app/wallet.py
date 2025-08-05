# app/wallet.py
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


def sign_hash(hash_bytes: bytes, private_key) -> bytes:
    """
    Firma el hash usando ECDSA con clave privada.
    """
    signature = private_key.sign(
        hash_bytes,
        ec.ECDSA(hashes.SHA256())
    )
    return signature

def verify_signature(hash_bytes: bytes, signature: bytes, public_key) -> bool:
    """
    Verifica la firma ECDSA del hash.
    """
    try:
        public_key.verify(
            signature,
            hash_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        return False