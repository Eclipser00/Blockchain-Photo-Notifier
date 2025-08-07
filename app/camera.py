# app/camera.py

import os
import json
import platform
import subprocess
import shutil
import time
from pathlib import Path
from plyer import camera as plyer_camera
import cv2  # Para fallback en escritorio

import config
from app.metadata import extract_exif, extract_sensors, extract_device_id, combine_metadata
from app.hasher import compute_hash
from app.keystore import load_private_key, load_public_key
from app.wallet import sign_hash
from app.blockchain import build_transaction, send_transaction, wait_for_confirmation
from cryptography.hazmat.primitives import serialization

# Archivo temporal para intercambio con ConfirmScreen
TEMP_FILE = Path(config.TMP_PHOTO_DIR) / 'last_capture.json'


def capture_photo_with_native(on_complete):
    """
    Lanza la cámara nativa en Android/iOS o usa OpenCV en Windows/macOS/Linux.
    Al completar, llama a on_complete(path).
    """
    os.makedirs(config.TMP_PHOTO_DIR, exist_ok=True)
    filename = Path(config.TMP_PHOTO_DIR) / f"photo_{int(Path.cwd().stat().st_mtime)}.jpg"
    sys = platform.system()
    if sys in ('Android', 'iOS'):
        # Móvil: invocar cámara nativa
        plyer_camera.take_picture(str(filename), lambda path: on_complete(path))
    elif sys == 'Windows':
        # Abrir la cámara nativa de Windows y continuar tras la captura
        pictures_dir = Path.home() / 'Pictures' / 'Camera Roll'
        existing = {p: p.stat().st_mtime for p in list(pictures_dir.glob('*.jpg')) + list(pictures_dir.glob('*.png'))}
        subprocess.Popen(['start', 'microsoft.windows.camera:'], shell=True)
        latest_photo = None
        while True:
            time.sleep(1)
            candidates = list(pictures_dir.glob('*.jpg')) + list(pictures_dir.glob('*.png'))
            if not candidates:
                continue
            newest = max(candidates, key=lambda p: p.stat().st_mtime)
            if newest not in existing or newest.stat().st_mtime != existing[newest]:
                latest_photo = newest
                break
        shutil.copy(latest_photo, filename)
        on_complete(str(filename))
    else:
        # Otros escritorios: usar OpenCV como fallback
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo acceder a la cámara desktop")
        # Desecho de primeros frames
        for _ in range(10):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("No se capturó correctamente la imagen")
        # Guardar imagen
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

