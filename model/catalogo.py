import configparser

import mysql
import mysql.connector
from kivy.core.window import Window
from kivymd.uix.list import ImageLeftWidget, ThreeLineAvatarListItem
from kivymd.uix.screen import MDScreen
from mysql.connector import Error

Window.size = (350, 580)


class Catalogo(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cursor, db = self.conectar_bd()

        self.validar_nivel_usuario(db)
        self.agregar_estilos_topbar()

    def on_pre_enter(self, *args):
        self.cambiar_pantalla()
        self.cargar_productos()

    def cambiar_pantalla(self):
        self.ids.bottomNavigation.switch_tab('catalogo-screen')

    def agregar_estilos_topbar(self):
        self.ids.toolbar.ids.label_title.font_size = '15sp'
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"

    def eliminar_lista_desactualizada(self):
        rows = [i for i in self.ids.listContainer.children]

        for row1 in rows:
            if isinstance(row1, ThreeLineAvatarListItem):
                self.ids.listContainer.remove_widget(row1)

    def validar_nivel_usuario(self, db):
        with open('model/session.txt') as mytextfile:
            userEmail = mytextfile.read()
        cursor2 = db.cursor()
        query = "SELECT * FROM usuarios where correo='" + str(userEmail) + "'"
        cursor2.execute(query)
        usuario = cursor2.fetchone()

        if usuario[9] == "Cliente":

            if 'inventarioScreen' in self.ids:
                self.ids.bottomNavigation.remove_widget(self.ids.inventarioScreen)
            else:
                print("hola")

        if db.is_connected():
            db.close()
            print("Se cerro la base de datos")

    def cargar_productos(self):

        try:
            cursor, db = self.conectar_bd()

            # Ejecutando el query para seleccionar todos los productos disponibles del inventario
            query = "SELECT * FROM inventario"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()

            # Remover la lista desactualizada del cache
            self.eliminar_lista_desactualizada()

            # Leer los productos y colocarlos en el contenedor
            for i in range(len(data)):
                self.ids.listContainer.add_widget(
                    ThreeLineAvatarListItem(ImageLeftWidget(source="assets/images/logo-papeleria.png"),
                                            text=f"{data[i][1]}", secondary_text=f"[size=13sp]{data[i][3]}[/size]",
                                            tertiary_text=f"[size=12sp]{data[i][4]}[/size]")
                )

        except Error as ex:
            print("Error durante la conexion:", ex)
        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

    def conectar_bd(self):
        # Conectando la base de datos
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        cursor = db.cursor()

        return cursor, db
