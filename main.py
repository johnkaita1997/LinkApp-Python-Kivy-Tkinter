from kivy import Config
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView


Config.set('graphics', 'multisamples', '0')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from BaseAdmin.admin import AdminWindow

from tkinter import *

# New size
size = (1100, 630)

# Get the actual pos and knowing the old size calcu +late the new one
top = Window.top * Window.size[1] / size[0]
left = Window.left * Window.size[1] / size[0]

# Change the size
Window.size = size

# Fixing pos
Window.top = top
Window.left = left

class Notify(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (.3, .3)


class MainWindow(BoxLayout):

    admin_widget = AdminWindow()  # An instance of our Pdmin wdindow


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ids.scrn_admin.add_widget(self.admin_widget)

    def showAlert(self, message):
        self.notify.add_widget(Label(text='[color=#FF0000][b]' + message + '[/b][/color]', markup=True))
        self.notify.open()
        Clock.schedule_once(self.killswitch, 5)

    def killswitch(self, dtx):
        self.notify.dismiss()
        self.notify.clear_widgets()


class MainApp(App):

    def build(self):
        return MainWindow()

if __name__ == '__main__':
    app = MainApp()
    app.run()