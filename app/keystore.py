# app/keystore.py
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import config

"""
Gestión de claves privadas para la aplicación.  Este módulo genera y carga
un par de claves EC (secp256k1) que se utilizan para firmar los hashes de las
fotografías.  La clave privada se almacena en un fichero PEM cifrado.

* La ruta de almacenamiento de la clave (`KEY_FILE`) depende de la plataforma:
  - En Android se utiliza el directorio de datos de usuario de Kivy (`App.user_data_dir`),
    para evitar escribir en la raíz del sistema.
  - En otras plataformas se utiliza el directorio personal del usuario (`~`).
* La contraseña de cifrado se puede establecer mediante la variable de entorno
  ``NOTARIZACION_KEY_PASSWORD``.  Si no se define, se usa una contraseña por defecto.
"""

from kivy.utils import platform as kivy_platform

def _get_key_path() -> str:
    """Devuelve la ruta donde se almacenará el archivo de la clave privada."""
    plat = kivy_platform
    # Intenta utilizar el directorio de datos de la aplicación en Android
    if plat == 'android':
        try:
            from plyer import storagepath
            # storagepath.get_application_dir() devuelve un directorio privado de la app
            app_dir = storagepath.get_application_dir()
            return os.path.join(app_dir, 'notarizacion_key.pem')
        except Exception:
            # Fallback a home si no existe storagepath
            return os.path.expanduser('~/.notarizacion_key.pem')
    else:
        return os.path.expanduser('~/.notarizacion_key.pem')


# Ruta donde guardamos la clave privada cifrada
KEY_FILE = _get_key_path()

# Contraseña para cifrado PEM.  Permitir sobrescribir mediante variable de entorno.
KEY_PASSWORD = os.environ.get('NOTARIZACION_KEY_PASSWORD', 'mi_contrasena_segura').encode('utf-8')

def generate_keypair():
    """
    Genera un par de claves EC secp256k1 y guarda la privada en KEY_FILE.
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