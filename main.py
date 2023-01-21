from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.screen import MDScreen

Window.size = (350, 580)

Builder.load_file("view/home/perfil.kv")
Builder.load_file("view/home/catalogo.kv")
Builder.load_file("view/home/inventario.kv")


class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass


class Perfil(MDScreen):
    pass


class Inventario(MDScreen):
    pass


class Catalogo(MDScreen):
    pass


class Papeleria(MDApp):

    def build(self):


        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("view/pre-splash.kv"))
        screen_manager.add_widget(Builder.load_file("view/login.kv"))
        screen_manager.add_widget(Builder.load_file("view/signup.kv"))
        screen_manager.add_widget(Builder.load_file("view/recover-password/recover-password.kv"))
        screen_manager.add_widget(Builder.load_file("view/home/home.kv"))

        return screen_manager


    def on_start(self):
        Clock.schedule_once(self.login, 1)

    def login(self, *args):
        screen_manager.current = "login"

    def change_color(self, instance):
        if instance in self.root.get_screen("homeScreen").ids.values():
            current_id = list(self.root.get_screen("homeScreen").ids.keys())[
                list(self.root.get_screen("homeScreen").ids.values()).index(instance)]
            for i in range(4):
                if f"nav_icon{i}" == current_id:
                    self.root.get_screen("homeScreen").ids[f"nav_icon{i}"].text_color = 1, 0, 0, 1
                else:
                    self.root.get_screen("homeScreen").ids[f"nav_icon{i}"].text_color = 0, 0, 0, 1



if __name__ == "__main__":
    Papeleria().run()
