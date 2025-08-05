# app/hasher.py
import json
import hashlib

def compute_hash(image_bytes: bytes, metadata: dict) -> bytes:
    """
    Genera un hash SHA-256 de la imagen más los metadatos.
    """
    # Combinar los datos: imagen en hexadecimal + metadatos ordenados
    payload = {
        'image_hex': image_bytes.hex(),
        'metadata': metadata
    }
    # Serializar a JSON con claves ordenadas para consistencia
    data = json.dumps(payload, sort_keys=True).encode('utf-8')
    # Calcular hash
    return hashlib.sha256(data).digest()