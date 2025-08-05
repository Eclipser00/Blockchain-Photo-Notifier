# config.py

import os

# URL de acceso al nodo Ethereum (Infura, Alchemy, nodo propio…)
ETH_NODE_URL = os.getenv(
    "ETH_NODE_URL",
    #"https://mainnet.infura.io/v3/241d032baf63455ba9aec20c3d18ed7a"
    "http://127.0.0.1:7545"
)

# Dirección del contrato de notarización desplegado
CONTRACT_ADDRESS = os.getenv(
    "CONTRACT_ADDRESS",
    "0x83Caa00c48ddC65DDdE8F6c2cdE33560dFDd2798"
)

# ID de la red (1 = Mainnet, 4 = Rinkeby, 137 = Polygon, etc.)
CHAIN_ID = int(os.getenv("CHAIN_ID", "1"))

# Clave alias para el par de claves en KeyStore / Secure Enclave
KEY_ALIAS = os.getenv("KEY_ALIAS", "notarizacion_alias")

# Parámetros de gas
GAS_LIMIT = int(os.getenv("GAS_LIMIT", "100_000"))
GAS_PRICE_GWEI = float(os.getenv("GAS_PRICE_GWEI", "1.0"))

# Carpeta donde guardaremos fotos temporales
TMP_PHOTO_DIR = os.getenv("TMP_PHOTO_DIR", "./tmp_photos")

# Opciones de la cámara (para Plyer o Kivy Camera)
CAMERA_RESOLUTION = (
    int(os.getenv("CAMERA_WIDTH", "1280")),
    int(os.getenv("CAMERA_HEIGHT", "720"))
)
