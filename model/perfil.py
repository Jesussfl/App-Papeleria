import configparser

from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import mysql
import mysql.connector
from mysql.connector import Error


class Perfil(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_toolbar_font_name)
        Clock.schedule_once(self.set_toolbar_font_size)
        app = MDApp.get_running_app()
        config = configparser.ConfigParser()
        config.read('config.ini')

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']

        try:
            db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
            if db.is_connected():
                cursor = db.cursor()

                query = "SELECT * FROM inventario"

                cursor.execute(query)
                data = cursor.fetchall()
                with open('model/session.txt') as mytextfile:
                    userEmail = mytextfile.read()

                query = "SELECT * FROM usuarios where correo='" + str(
                    userEmail) + "'"
                cursor.execute(query)
                user = cursor.fetchone()
                self.validate_user_level(user[9])
        except Error as ex:
            print("Error durante la conexion:", ex)
        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

    def on_pre_enter(self, *args):
        # Clock.schedule_once(self.set_toolbar_font_name)
        # Clock.schedule_once(self.set_toolbar_font_size)
        self.connect()
        self.switch()

    def validate_user_level(self, level):
        if level == "Usuario":
            if 'inventarioScreen' in self.ids:
                self.ids.bottom_navigation.remove_widget(self.ids.inventarioScreen)
            else:
                print("hola")

    def switch(self, *args):
        self.ids.bottom_navigation.switch_tab('perfil-screen')

    def set_toolbar_font_name(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"

    def set_toolbar_font_size(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def connect(self, *args):

        app = MDApp.get_running_app()
        config = configparser.ConfigParser()
        config.read('config.ini')

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']

        with open('model/session.txt') as mytextfile:
            userEmail = mytextfile.read()

        try:
            db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
            if db.is_connected():
                cursor = db.cursor()

                query = "SELECT * FROM usuarios where correo='" + str(
                    userEmail) + "'"

                cursor.execute(query)
                data = cursor.fetchone()
                # self.validate_user_level(data[9])
                app.manager.get_screen('perfil').ids['inputDNI'].text = str(data[0])
                app.manager.get_screen('perfil').ids['inputTipo'].text = data[1]
                app.manager.get_screen('perfil').ids['label_fullname'].text = data[2]
                app.manager.get_screen('perfil').ids['inputPhone'].text = data[3]
                app.manager.get_screen('perfil').ids['inputAddress'].text = data[4]
                app.manager.get_screen('perfil').ids['inputEmail'].text = data[5]
                app.manager.get_screen('perfil').ids['inputRango'].text = data[9]

        except Error as ex:
            print("Error durante la conexion:", ex)
        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        pass
