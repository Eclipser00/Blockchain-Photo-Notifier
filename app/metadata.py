# app/metadata.py
from PIL import Image
import piexif
from utils.sensors import get_accelerometer, get_gyroscope
import os
import platform

def extract_exif(image_path: str) -> dict:
    """Extrae EXIF de imagen (fecha, hora, GPS)."""
    try:
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get('GPS', {})
        # Obtener coordenadas si existen
        lat = gps.get(piexif.GPSIFD.GPSLatitude)
        lon = gps.get(piexif.GPSIFD.GPSLongitude)
        datetime = exif_dict['0th'].get(piexif.ImageIFD.DateTime)
        return {
            'datetime': datetime.decode() if datetime else None,
            'gps_latitude': lat,
            'gps_longitude': lon
        }
    except Exception:
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
    """Obtiene identificador único de dispositivo."""
    sys = platform.system()
    if sys == 'Android':
        # Android_ID desde entorno o Plyer
        from plyer import uniqueid
        return uniqueid.id
    elif sys == 'iOS':
        # identifierForVendor en iOS (ej. usando pyobjus)
        return os.getenv('IOS_VENDOR_ID', 'unknown')
    else:
        return platform.node()

def combine_metadata(exif: dict, sensors: dict, device_id: str) -> dict:
    """Combina todos los metadatos en un solo dict."""
    data = {}
    data.update(exif)
    data.update(sensors)
    data['device_id'] = device_id
    return data