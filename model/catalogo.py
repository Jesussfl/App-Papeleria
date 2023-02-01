import configparser

import mysql
import mysql.connector
from kivy.core.window import Window
from kivymd.uix.list import ImageLeftWidget, ThreeLineAvatarListItem
from kivymd.uix.navigationdrawer import MDNavigationDrawerItem
from kivymd.uix.screen import MDScreen
from mysql.connector import Error
from kivy.uix.image import AsyncImage

Window.size = (350, 580)



class Catalogo(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cursor, db = self.conectar_bd()

        self.validar_nivel_usuario(db)
        self.agregar_estilos_topbar()

    def on_pre_enter(self, *args):
        self.cambiar_pantalla()
        self.cargar_productos("SELECT * FROM inventario")

    def cambiar_pantalla(self):
        self.ids.bottomNavigation.switch_tab('catalogo-screen')

    def agregar_estilos_topbar(self):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

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

    def buscar_producto(self):
        nombre_producto = self.ids.inputBuscar.text
        self.cargar_productos(
            "SELECT * FROM inventario WHERE codigo LIKE '%{0}%' or nombre LIKE '%{0}%' OR descripcion LIKE '%{0}%' OR "
            "marca LIKE '%{0}%'".format(
                nombre_producto))

    def cargar_productos(self, consulta):

        try:
            cursor, db = self.conectar_bd()

            # Ejecutando el query para seleccionar todos los productos disponibles del inventario
            query = consulta
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()

            # Remover la lista desactualizada del cache
            self.eliminar_lista_desactualizada()

            # Leer los productos y colocarlos en el contenedor
            for i in range(len(data)):
                precio_bolivares = data[i][4] * 22
                self.ids.listContainer.add_widget(
                    ThreeLineAvatarListItem(ImageLeftWidget(source=data[i][6]),
                                            text=f"{data[i][1]} - {data[i][5]}", secondary_text=f"[size=13sp]{data[i][3]} Disponibles[/size]",
                                            tertiary_text=f"[size=12sp]{data[i][4]}$ -- {precio_bolivares} Bs[/size]")
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
