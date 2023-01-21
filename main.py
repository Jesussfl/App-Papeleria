from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.factory import Factory


Window.size = (350, 580)


class Papeleria(MDApp):

    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("view/pre-splash.kv"))
        screen_manager.add_widget(Builder.load_file("view/login.kv"))
        screen_manager.add_widget(Builder.load_file("view/signup.kv"))
        screen_manager.add_widget(Builder.load_file("view/recover-password/recover-password.kv"))
        return screen_manager

    def on_start(self):
        Clock.schedule_once(self.login, 1)

    def login(self, *args):
        screen_manager.current = "login"



if __name__ == "__main__":
    Papeleria().run()
