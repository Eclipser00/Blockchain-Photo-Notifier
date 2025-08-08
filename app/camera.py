# app/camera.py

import os
import json
import time
import shutil

from pathlib import Path

# Dependencias externas para la cámara
from plyer import camera as plyer_camera
import cv2  # fallback para capturar imágenes desde la webcam
import importlib

import config

from kivy.utils import platform as kivy_platform

from app.metadata import (
    extract_exif,
    extract_sensors,
    extract_device_id,
    combine_metadata,
)
from app.hasher import compute_hash
from app.keystore import load_private_key, load_public_key
from app.wallet import sign_hash
from app.blockchain import build_transaction, send_transaction, wait_for_confirmation
from cryptography.hazmat.primitives import serialization

# Archivo temporal para intercambio con ConfirmScreen
TEMP_FILE = Path(config.TMP_PHOTO_DIR) / 'last_capture.json'


def capture_photo_with_native(on_complete):
    """
    Captura una fotografía utilizando la cámara disponible según la plataforma.

    * En Android se invoca la cámara nativa mediante Plyer y se solicitan
      permisos de cámara y almacenamiento si la API lo permite.
    * En Windows se utiliza OpenCV para acceder a la webcam por defecto.
    * En otras plataformas (Linux, macOS, iOS) también se utiliza OpenCV.

    Una vez terminada la captura, se llama al callback ``on_complete`` con
    la ruta del fichero guardado.
    """
    # Asegurarse de que el directorio de almacenamiento temporal exista
    os.makedirs(config.TMP_PHOTO_DIR, exist_ok=True)
    # Generar un nombre de archivo único en milisegundos para evitar colisiones
    filename = Path(config.TMP_PHOTO_DIR) / f"photo_{int(time.time()*1000)}.jpg"

    plat = kivy_platform
    if plat == 'android':
        # Pedir permisos en tiempo de ejecución (en Android < 6 no es necesario).
        # Importamos las clases de permisos dinámicamente para evitar referencias
        # no resueltas cuando se analiza el código en entornos de escritorio.
        try:
            permissions_mod = importlib.import_module('android.permissions')
            request_permissions = getattr(permissions_mod, 'request_permissions', None)
            Permission = getattr(permissions_mod, 'Permission', None)
            if request_permissions and Permission:
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
        except Exception:
            # Si no se puede pedir permisos o no existen las clases, continuamos.
            pass
        # Invoca la cámara nativa mediante Plyer.  El resultado se guarda en ``filename``
        plyer_camera.take_picture(str(filename), lambda path: on_complete(path))
    elif plat == 'win':
        # Uso de OpenCV en Windows para capturar desde la webcam por defecto
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo acceder a la cámara en Windows")
        # Descartar algunos frames iniciales para ajustar la imagen
        for _ in range(10):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("No se capturó correctamente la imagen")
        cv2.imwrite(str(filename), frame)
        on_complete(str(filename))
    else:
        # Fallback para Linux, macOS e iOS usando OpenCV
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo acceder a la cámara de escritorio")
        for _ in range(10):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("No se capturó correctamente la imagen")
        cv2.imwrite(str(filename), frame)
        on_complete(str(filename))


def process_photo(image_path: str) -> bool:
    """
    - Extrae metadatos (EXIF, sensores, ID de dispositivo)
    - Genera hash y firma
    - Guarda datos en JSON para ConfirmScreen
    """
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    exif = extract_exif(image_path)
    sensors = extract_sensors()
    device_id = extract_device_id()
    metadata = combine_metadata(exif, sensors, device_id)

    photo_hash = compute_hash(image_bytes, metadata)
    private_key = load_private_key()
    signature = sign_hash(photo_hash, private_key)

    public_key = load_public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    temp_data = {
        'image_path': image_path,
        'hash': photo_hash.hex(),
        'signature': signature.hex(),
        'public_key': pub_bytes.decode('utf-8'),
        'metadata': metadata
    }
    TEMP_FILE.parent.mkdir(parents=True, exist_ok=True)
    TEMP_FILE.write_text(json.dumps(temp_data, indent=2))
    return True


def confirm_and_send_transaction() -> bool:
    """
    Lee last_capture.json, construye y envía la transacción.
    Devuelve True si fue confirmada.
    """
    if not TEMP_FILE.exists():
        raise FileNotFoundError("No hay captura previa para confirmar.")

    data = json.loads(TEMP_FILE.read_text())
    photo_hash = bytes.fromhex(data['hash'])
    signature = bytes.fromhex(data['signature'])
    public_key_pem = data['public_key'].encode('utf-8')

    signed_tx = build_transaction(photo_hash, signature, public_key_pem)
    tx_hash = send_transaction(signed_tx)
    return wait_for_confirmation(tx_hash)

