import os
import json
import time
import shutil
import subprocess
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

TEMP_FILE = Path(config.TMP_PHOTO_DIR) / 'last_capture.json'


def capture_photo_with_native(on_complete):
    """
    Captura una fotografía utilizando la cámara disponible según la plataforma.

    * En Android se invoca la cámara nativa mediante Plyer y se solicitan
      permisos de cámara y almacenamiento si la API lo permite.
    * En Windows 11 se abre la app Cámara de Windows.
    * En otras plataformas (Linux, macOS, iOS) también se utiliza OpenCV.

    Una vez terminada la captura (o al volver de la app nativa), se llama
    al callback ``on_complete`` con la ruta del fichero guardado.
    """
    os.makedirs(config.TMP_PHOTO_DIR, exist_ok=True)
    filename = Path(config.TMP_PHOTO_DIR) / f"photo_{int(time.time()*1000)}.jpg"

    plat = kivy_platform

    if plat == 'android':
        # (igual que antes…)
        try:
            permissions_mod = importlib.import_module('android.permissions')
            request_permissions = getattr(permissions_mod, 'request_permissions', None)
            Permission = getattr(permissions_mod, 'Permission', None)
            if request_permissions and Permission:
                request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
        except Exception:
            pass
        plyer_camera.take_picture(str(filename), lambda path: on_complete(path))

    elif plat == 'win':
        # Abrir la app Cámara de Windows 11
        try:
            # Opción A: usando URI de la app
            subprocess.run('start microsoft.windows.camera:', shell=True, check=True)
        except subprocess.CalledProcessError:
            # Opción B: ruta directa a la UWP (ajusta el paquete si varia)
            uwp_path = r'explorer.exe shell:appsFolder\Microsoft.WindowsCamera_8wekyb3d8bbwe!App'
            subprocess.run(uwp_path, shell=True, check=True)

        # Aquí deberías esperar a que el usuario cierre la app Cámara
        # o bien preguntar por la ruta de la foto resultante.
        # Por simplicidad, seguimos con el fallback OpenCV tras un breve sleep:
        time.sleep(5)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("No se pudo acceder a la cámara tras abrir la app nativa")
        for _ in range(10):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("No se capturó correctamente la imagen con OpenCV")
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


