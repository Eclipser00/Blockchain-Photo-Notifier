# app/ui.py

import config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import app.camera as camera_module
from app.blockchain import get_gas_price

class CaptureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Abriendo cámara nativa..."))
        self.add_widget(layout)

    def on_enter(self, *args):
        Clock.schedule_once(lambda dt: camera_module.capture_photo_with_native(self.on_picture), 0)

    def on_picture(self, image_path):
        camera_module.process_photo(image_path)
        self.manager.current = 'confirm'

class ConfirmScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.msg = Label(text="Preparando transacción...")
        layout.add_widget(self.msg)
        self.add_widget(layout)

    def on_enter(self):
        price = get_gas_price()
        self.msg.text = f"Gas actual: {price} Gwei. Toca para confirmar."
        self.bind(on_touch_down=self._confirm)

    def _confirm(self, *args):
        self.unbind(on_touch_down=self._confirm)
        success = camera_module.confirm_and_send_transaction()
        result = self.manager.get_screen('result')
        result.display(success)
        self.manager.current = 'result'

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.result_msg = Label(text="")
        layout.add_widget(self.result_msg)
        self.add_widget(layout)

    def display(self, success: bool):
        self.result_msg.text = "¡Registración exitosa!" if success else "Error en la transacción"


def build_screen_manager():
    sm = ScreenManager()
    sm.add_widget(CaptureScreen(name='capture'))
    sm.add_widget(ConfirmScreen(name='confirm'))
    sm.add_widget(ResultScreen(name='result'))
    return sm

