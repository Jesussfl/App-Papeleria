import configparser

from kivy.clock import Clock
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget, ThreeLineAvatarListItem
from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import mysql
import mysql.connector
from mysql.connector import Error
from weakref import ref


class Catalogo(MDScreen):
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

        self.switch()
        self.connect()

    def validate_user_level(self, level):
        if level == "Usuario":

            if 'inventarioScreen' in self.ids:
                self.ids.bottomNavigation.remove_widget(self.ids.inventarioScreen)
            else:
                print("hola")

    def switch(self, *args):
        self.ids.bottomNavigation.switch_tab('catalogo-screen')

    def set_toolbar_font_name(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"

    def set_toolbar_font_size(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def remove_childs(self):
        rows = [i for i in self.ids.listContainer.children]

        for row1 in rows:
            print(rows)
            if isinstance(row1, ThreeLineAvatarListItem):
                self.ids.listContainer.remove_widget(row1)

    def connect(self, *args):

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
                # self.validate_user_level(user[9])

                self.remove_childs()
                for i in range(len(data)):
                    self.ids.listContainer.add_widget(
                        ThreeLineAvatarListItem(ImageLeftWidget(source="assets/images/logo-papeleria.png"),
                                                text=f"{data[i][1]}", secondary_text=f"[size=13sp]{data[i][3]}[/size]"
                                                , tertiary_text=f"[size=12sp]{data[i][4]}[/size]")
                    )

        except Error as ex:
            print("Error durante la conexion:", ex)
        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        pass
