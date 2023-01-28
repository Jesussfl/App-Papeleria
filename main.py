from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivymd.uix.floatlayout import MDFloatLayout

from model.agregarProducto import AgregarProducto
from model.catalogo import Catalogo
from model.inventario import Inventario
from model.login import Login
from model.perfil import Perfil
from model.signup import Signup


Window.size = (350, 580)

# Carga de widgets en caché
Builder.load_file("view/home/perfil.kv")
Builder.load_file("view/home/catalogo.kv")
Builder.load_file("view/home/inventario.kv")
Builder.load_file("view/home/agregarProducto.kv")
Builder.load_file("view/login.kv")
Builder.load_file("view/signup.kv")


class NavBar(FakeRectangularElevationBehavior, MDFloatLayout):
    pass


class Papeleria(MDApp):

    def build(self):

        # Adición de widgets al screen principal mediante el administrador de pantallas

        self.manager = ScreenManager(transition=NoTransition())

        self.manager.add_widget(Builder.load_file("view/pre-splash.kv"))
        self.manager.add_widget(Login(name='login'))
        self.manager.add_widget(Signup(name='signup'))
        self.manager.add_widget(Perfil(name='perfil'))
        self.manager.add_widget(Inventario(name='inventario'))
        self.manager.add_widget(Catalogo(name='catalogo'))
        self.manager.add_widget(AgregarProducto(name='agregarProducto'))
        self.manager.add_widget(Builder.load_file("view/recover-password/recover-password.kv"))
        self.perfilConnect = Perfil()
        return self.manager

    def on_start(self):
        # Tiempo de carga para el splash screen
        Clock.schedule_once(self.login, 1)

        with open('model/session.txt', 'w') as mytextfile:
            mytextfile.truncate()

    def login(self, *args):
        self.manager.current = "login"

    def signup(self, *args):
        self.manager.current = "signup"


if __name__ == "__main__":
    Papeleria().run()
