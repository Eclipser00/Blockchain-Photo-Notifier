# app/ui.py

import config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.app import App
import app.camera as camera_module
from app.blockchain import get_gas_price

class CaptureScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text="Abriendo cámara nativa..."))
        self.add_widget(layout)

    def on_enter(self, *args):
        """
        Cuando se entra en la pantalla de captura se intenta acceder a la cámara.
        En lugar de invocar directamente la captura, delegamos en un método
        auxiliar que captura excepciones y muestra un mensaje amigable en caso
        de fallo.  Usamos un schedule con delay cero para que la interfaz
        permanezca reactiva mientras se gestiona la cámara.
        """
        Clock.schedule_once(lambda dt: self._attempt_capture(), 0)

    def _attempt_capture(self):
        """Intenta capturar una foto y gestiona cualquier excepción."""
        try:
            camera_module.capture_photo_with_native(self.on_picture)
        except Exception as exc:
            # Si ocurre un error al abrir la cámara o capturar la foto,
            # mostramos un mensaje al usuario con opciones para salir o reintentar.
            self._show_error_popup("No se ha podido tomar la foto.\n" + str(exc))

    def on_picture(self, image_path):
        camera_module.process_photo(image_path)
        self.manager.current = 'confirm'

    def _show_error_popup(self, message: str):
        """
        Muestra un diálogo emergente con el mensaje de error y dos botones:
        uno para volver a intentar la captura y otro para cerrar la aplicación.
        """
        # Contenedor principal del popup
        content = BoxLayout(orientation='vertical', spacing=20, padding=20)
        content.add_widget(Label(text=message, halign='center'))
        # Contenedor para los botones
        btn_box = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=40)
        retry_btn = Button(text="Volver a intentar")
        exit_btn = Button(text="Salir del programa")
        btn_box.add_widget(retry_btn)
        btn_box.add_widget(exit_btn)
        content.add_widget(btn_box)
        # Crear el popup
        popup = Popup(title="Error de cámara", content=content, size_hint=(0.9, 0.5))
        # Lógica para reintentar captura
        def _retry(_instance):
            popup.dismiss()
            # Reintentar captura tras cerrar el popup
            Clock.schedule_once(lambda dt: self._attempt_capture(), 0)
        # Lógica para salir de la aplicación
        def _exit(_instance):
            popup.dismiss()
            App.get_running_app().stop()
        retry_btn.bind(on_release=_retry)
        exit_btn.bind(on_release=_exit)
        popup.open()

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

