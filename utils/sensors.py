# utils/sensors.py
from plyer import accelerometer, gyroscope


def get_accelerometer() -> dict:
    """Lee valores actuales del acelerómetro."""
    try:
        vals = accelerometer.acceleration
        return {'x': vals[0], 'y': vals[1], 'z': vals[2]}
    except:
        return {'x': 0, 'y': 0, 'z': 0}

def get_gyroscope() -> dict:
    """Lee valores actuales del giroscopio."""
    try:
        vals = gyroscope.rotation
        return {'x': vals[0], 'y': vals[1], 'z': vals[2]}
    except:
        return {'x': 0, 'y': 0, 'z': 0}