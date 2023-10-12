import logging
import os
import time

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.clock import Clock
from kivy.logger import Logger, LoggerHistory
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.graphics import Rotate
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
from kivy.properties import StringProperty


# Pokud aplikace běži na androidu provedou se importy a dalsi akce
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission  # Importy pro práci s Androidem
    from android import mActivity
    from android.storage import app_storage_path
    from android.storage import primary_external_storage_path
    
    # zjisti zda li má opravnění k fotoaparátu a uložišti a pokud ne, spustí okno s žádostí o tyto oprávnění
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
    # Pokud oprávnění nemá, čeká až je uživatel udělí v nekonečné smyčce
    while not (check_permission(Permission.CAMERA) and check_permission(Permission.WRITE_EXTERNAL_STORAGE)):
        Clock.schedule_once(lambda dt: None, 1) 

# Získání cesty k přístupného úložišti hlavně pro android
if platform == 'android':
    context = mActivity.getApplicationContext()
    result = context.getExternalFilesDir(None)
    if result:
        storage_path = str(result.toString())
    else:
        storage_path = app_storage_path()
else:
    storage_path = os.getcwd()                      # Pro jiné platformy než Android

# Nastavení cesty pro logovací soubor
log_file = os.path.join(storage_path, 'my_kivy_app.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.TRACE)  # Nastavení úrovně logování
file_handler.setFormatter(formatter)
Logger.addHandler(file_handler)
for record in LoggerHistory.history:
    file_handler.handle(record)
# Konec kodu potřebného pro logování do souboru


Builder.load_string('''
<CameraApp>:
    orientation: 'vertical'
    FloatLayout:
        Camera:
            id: camera
            resolution: (640, 480)
            play: False
            size_hint: 1, 0.7  # Zmenšení výšky náhledu, aby bylo místo pro tlačítka
            pos_hint: {'top': 1}
            canvas.before:
                PushMatrix
                Rotate:
                    angle: root.rotation_angle
                    origin: self.center
                Scale:        # Pro ruzné platformy nastaví jinou velikost widgetu náhledu kamery
                    x: 1.5 if app.platform_type == 'win' else 2 if app.platform_type == 'android' else 1
                    y: 1.5 if app.platform_type == 'win' else 2 if app.platform_type == 'android' else 1


                    origin: self.center
            canvas.after:
                PopMatrix
    BoxLayout:
        size_hint: 1, 0.3  # Zvětšení prostoru pro tlačítka
                    
        ToggleButton:
            text: 'Spustit'
            on_press: camera.play = not camera.play
            size_hint_y: None
            height: '48dp'
                    
        Button:
            text: 'Fotka'
            size_hint_y: None
            height: '48dp'
            on_press: root.capture()
                    
        Button:
            text: 'Otoč'
            size_hint_y: None
            height: '48dp'
            on_press: root.rotate_camera()
                    
        Button:
            text: 'Konec'
            size_hint_y: None
            height: '48dp'
            on_press: app.stop()  # Toto zavře aplikaci
''')

class CameraApp(BoxLayout, App):
    
    
    platform_type = StringProperty(platform)  # Přidání vlastnosti platform_type pro kv kód
    rotation_angle = NumericProperty(0 if platform == 'win' else 270 if platform == 'android' else 0)


    def build(self):
        return self

    def capture(self, *args):
        # Získání reference na objekt Camera
        camera = self.ids['camera']

        # Uložení fotky
        photo_path = os.path.join(storage_path, 'IMG_{}.png'.format(time.strftime("%Y%m%d_%H%M%S")))
        camera.export_to_png(photo_path)
        Logger.info(f"Captured and saved to {photo_path}")

    def rotate_camera(self):
        self.rotation_angle += 90

if __name__ == '__main__':
    CameraApp().run()