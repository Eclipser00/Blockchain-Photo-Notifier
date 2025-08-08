# app/metadata.py
from PIL import Image
import piexif
from utils.sensors import get_accelerometer, get_gyroscope
import os
import platform
import uuid
from kivy.utils import platform as kivy_platform

def dms_to_degrees(dms):
    """
    Convierte coordenadas GPS en formato DMS (grados/minutos/segundos) a grados
    decimales.  ``dms`` puede ser una lista de tuplas (numerador, denominador)
    tal y como devuelve ``piexif``.  Devuelve ``None`` si los datos no son
    válidos.
    """
    try:
        # Cada elemento es (numerador, denominador)
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1]
        seconds = dms[2][0] / dms[2][1]
        return degrees + minutes / 60 + seconds / 3600
    except Exception:
        return None


def extract_exif(image_path: str) -> dict:
    """Extrae metadatos EXIF relevantes de una imagen (fecha, hora y GPS)."""
    try:
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get('GPS', {})
        # Obtener coordenadas si existen y convertirlas a decimales
        lat_raw = gps.get(piexif.GPSIFD.GPSLatitude)
        lon_raw = gps.get(piexif.GPSIFD.GPSLongitude)
        lat = dms_to_degrees(lat_raw) if lat_raw else None
        lon = dms_to_degrees(lon_raw) if lon_raw else None
        datetime = exif_dict['0th'].get(piexif.ImageIFD.DateTime)
        return {
            'datetime': datetime.decode() if datetime else None,
            'gps_latitude': lat,
            'gps_longitude': lon,
        }
    except Exception:
        # Si no hay EXIF o no se puede parsear, devolvemos diccionario vacío
        return {}

def extract_sensors() -> dict:
    """Lee datos de acelerómetro y giroscopio."""
    try:
        accel = get_accelerometer()
    except Exception:
        accel = {'x': 0, 'y': 0, 'z': 0}
    try:
        gyro = get_gyroscope()
    except Exception:
        gyro = {'x': 0, 'y': 0, 'z': 0}
    return {
        'accelerometer': accel,
        'gyroscope': gyro
    }

def extract_device_id() -> str:
    """
    Obtiene un identificador único del dispositivo en función de la plataforma.

    * En Android se utiliza el servicio ``uniqueid`` de Plyer para obtener el
      ANDROID_ID.  Si falla, se genera un UUID persistente usando ``uuid.getnode()``.
    * En iOS se lee de la variable de entorno ``IOS_VENDOR_ID`` (cuando se empaqueta
      con PyObjus/pyto), o se genera un identificador anónimo.
    * En Windows, Linux y macOS se usa el nombre de host con
      ``platform.node()``, y si éste está vacío se genera un UUID basado en
      la dirección MAC.
    """
    plat = kivy_platform
    if plat == 'android':
        try:
            from plyer import uniqueid
            return uniqueid.id or str(uuid.getnode())
        except Exception:
            return str(uuid.getnode())
    elif plat == 'ios':
        return os.getenv('IOS_VENDOR_ID', 'unknown') or str(uuid.getnode())
    else:
        node = platform.node()
        return node if node else str(uuid.getnode())

def combine_metadata(exif: dict, sensors: dict, device_id: str) -> dict:
    """Combina todos los metadatos en un solo dict."""
    data = {}
    data.update(exif)
    data.update(sensors)
    data['device_id'] = device_id
    return data