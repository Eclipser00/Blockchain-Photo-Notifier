import json
import time
import subprocess
import shutil
import os
from pathlib import Path
import winreg

from plyer import camera as plyer_camera  # para Android/iOS
from kivy.utils import platform as kivy_platform

from app.metadata import extract_exif, extract_sensors, extract_device_id, combine_metadata
from app.hasher import compute_hash

# Rutas de carpeta temporal
tmp_dir = Path.home() / "tmp_photos"
TEMP_FILE = tmp_dir / 'last_capture.json'

# Rutas por defecto de la galería de Windows
DEFAULT_GALLERY_DIR = Path.home() / 'Pictures' / 'Camera Roll'
FALLBACK_PICTURES_DIR = Path.home() / 'Pictures'

# IDs UWP de apps de cámara y fotos
CAMERA_UWP_URI = 'microsoft.windows.camera:'
CAMERA_APP_ID = r'explorer.exe shell:appsFolder\Microsoft.WindowsCamera_8wekyb3d8bbwe!App'
PHOTOS_UWP_URI = 'ms-photos:'
PHOTOS_APP_ID = r'explorer.exe shell:appsFolder\Microsoft.Windows.Photos_8wekyb3d8bbwe!App'


def get_gallery_dir():
    """
    Lee del registro la carpeta 'Camera Roll'. Si no existe, usa 'My Pictures'.
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        )
        # Intentar Camera Roll
        val, _ = winreg.QueryValueEx(key, "Camera Roll")
        path = Path(os.path.expandvars(val))
        if path.exists():
            return path
        # Intentar My Pictures
        val2, _ = winreg.QueryValueEx(key, "My Pictures")
        path2 = Path(os.path.expandvars(val2))
        if path2.exists():
            return path2
    except Exception:
        pass
    # Fallback a rutas conocidas
    if DEFAULT_GALLERY_DIR.exists():
        return DEFAULT_GALLERY_DIR
    if FALLBACK_PICTURES_DIR.exists():
        return FALLBACK_PICTURES_DIR
    raise RuntimeError(f"No se encontró carpeta de imágenes en el sistema")


def launch_native_camera():
    """Intenta lanzar la app de Cámara, y si falla, abre Fotos."""
    # Intentar esquema URI de cámara
    try:
        subprocess.run(f'start {CAMERA_UWP_URI}', shell=True, check=True)
        return
    except subprocess.CalledProcessError:
        pass
    # Intentar ID de app Cámara
    try:
        subprocess.run(CAMERA_APP_ID, shell=True, check=True)
        return
    except subprocess.CalledProcessError:
        pass
    # Como última opción, abrir Fotos
    try:
        subprocess.run(f'start {PHOTOS_UWP_URI}', shell=True, check=True)
    except subprocess.CalledProcessError:
        # Intentar ID de app Fotos
        subprocess.run(PHOTOS_APP_ID, shell=True, check=False)


def capture_photo_with_native(on_complete):
    """
    1. Abre la app nativa de cámara (o Fotos si no hay cámara).
    2. Espera a que el usuario tome la foto y se guarde.
    3. Copia la foto más reciente a tmp_photos y cierra la app.
    """
    # Limpiar tmp_dir
    tmp_dir.mkdir(parents=True, exist_ok=True)
    for f in tmp_dir.iterdir():
        if f.is_file():
            f.unlink()

    plat = kivy_platform
    if plat in ('android', 'ios'):
        plyer_camera.take_picture(str(tmp_dir / 'capture.jpg'), on_complete)
        return
    elif plat == 'win':
        # Lanzar cámara o Fotos
        launch_native_camera()
        # Dar tiempo a la app
        time.sleep(1)
        # Obtener directorio de galería
        gallery_dir = get_gallery_dir()
        # Buscar imágenes recursivamente
        fotos = list(gallery_dir.rglob('*.jpg')) + list(gallery_dir.rglob('*.png'))
        if not fotos:
            raise RuntimeError("No se detectaron fotos en la carpeta de imágenes")
        latest = max(fotos, key=lambda p: p.stat().st_ctime)
        # Copiar a tmp_dir
        dest = tmp_dir / latest.name
        shutil.copy2(latest, dest)
        # Cerrar cámaras
        subprocess.run('taskkill /IM WindowsCamera.exe /F', shell=True, check=False)
        subprocess.run('taskkill /IM Microsoft.Photos.exe /F', shell=True, check=False)
        on_complete(str(dest))
        return
    # Fallback polling para otros
    timeout_s, interval = 120, 1
    elapsed = 0
    while elapsed < timeout_s:
        time.sleep(interval)
        elapsed += interval
        fotos = list(tmp_dir.iterdir())
        if fotos:
            foto = fotos[0]
            subprocess.run('taskkill /IM WindowsCamera.exe /F', shell=True, check=False)
            subprocess.run('taskkill /IM Microsoft.Photos.exe /F', shell=True, check=False)
            on_complete(str(foto))
            return
    raise RuntimeError(f"No se detectó foto en tmp_photos tras {timeout_s}s")


def process_photo(image_path: str):
    """
    Extrae metadatos y guarda hash en TEMP_FILE.
    """
    exif = extract_exif(image_path)
    sensors = extract_sensors()
    device_id = extract_device_id()
    metadata = combine_metadata(exif, sensors, device_id)
    photo_hash = compute_hash(image_path, metadata)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    data = {
        'image_path': image_path,
        'metadata': metadata,
        'photo_hash': photo_hash.hex() if hasattr(photo_hash, 'hex') else photo_hash
    }
    with open(TEMP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    # PRUEBA GITHUB CAMBIOS





