# main.py
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
import config
from app.ui import build_screen_manager

# 1. Inicialización de la aplicación (crear carpetas, cargar configuración)
def initialize_app():
    os.makedirs(config.TMP_PHOTO_DIR, exist_ok=True)
    # Aquí podríamos inicializar logs, clientes Web3, etc.

# 2. Definición de la App Kivy
def run_app():
    initialize_app()
    class NotarizacionApp(App):
        def build(self):
            self.sm = build_screen_manager()
            return self.sm

    NotarizacionApp().run()

if __name__ == '__main__':
    run_app()