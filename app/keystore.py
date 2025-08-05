# app/keystore.py
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import config

# Ruta donde guardamos la clave privada cifrada
KEY_FILE = os.path.expanduser('~/.notarizacion_key.pem')
# Contraseña para cifrado PEM (en producción, usar almacenamiento seguro como Keychain o Keystore)
KEY_PASSWORD = b'mi_contrasena_segura'

def generate_keypair():
    """
    Genera un par de claves EC secp256r1 y guarda la privada en KEY_FILE.
    """
    private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
    # Serializar clave privada en PEM cifrado
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(KEY_PASSWORD)
    )
    with open(KEY_FILE, 'wb') as f:
        f.write(pem)
    return private_key

def load_private_key():
    """
    Carga la clave privada desde KEY_FILE; si no existe, la genera.
    """
    # Si no hay fichero, creamos un par nuevo
    if not os.path.exists(KEY_FILE):
        print("No existe la clave privada, generando nuevo par...")
        generate_keypair()

    # Ahora ya existe, la cargamos
    with open(KEY_FILE, 'rb') as f:
        pem_data = f.read()
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=KEY_PASSWORD,
        backend=default_backend()
    )
    return private_key


def load_public_key():
    """
    Devuelve la clave pública asociada a la privada.
    """
    private_key = load_private_key()
    return private_key.public_key()