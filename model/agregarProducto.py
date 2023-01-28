import configparser
import re
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error


class AgregarProducto(MDScreen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(self.set_toolbar_font_name)
        Clock.schedule_once(self.set_toolbar_font_size)

    def set_toolbar_font_name(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"

    def set_toolbar_font_size(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def connect(self):
        app = App.get_running_app()
        productName = app.manager.get_screen('agregarProducto').ids['inputNombreProducto'].text
        productDescription = app.manager.get_screen('agregarProducto').ids['inputDescripcion'].text
        amount = app.manager.get_screen('agregarProducto').ids['inputCantidad'].text
        price = app.manager.get_screen('agregarProducto').ids['inputPrecio'].text
        brand = app.manager.get_screen('agregarProducto').ids['inputMarca'].text
        imageSource = app.manager.get_screen('agregarProducto').ids['inputImagen'].text
        createdTime = datetime.now()
        state = "Disponible"

        # Validando que no hayan campos vacíos
        if not productName or not amount or not price or not brand or not imageSource:
            self.show_error("Por favor llene todos los campos requeridos.")
            return

        try:

            config = configparser.ConfigParser()
            config.read('config.ini')

            host = config['mysql']['host']
            user = config['mysql']['user']
            password = config['mysql']['password']
            dbname = config['mysql']['db']

            db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
            if db.is_connected():
                cursor = db.cursor()

                query = "Insert into inventario (nombre, descripcion, cantidad, precio, marca, imagen, estado, fecha_modificacion)" \
                        " values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(
                    productName,
                    productDescription,
                    amount,
                    price,
                    brand,
                    imageSource,
                    state,
                    createdTime)

                cursor.execute(query)
                db.commit()
                print("Datos Registrados Correctamente")
                toast('Producto Registrado Correctamente')
                self.manager.current = 'inventario'

        except Error as ex:
            print("Error durante la conexion:", ex)

            if ex.errno == 1062:
                self.show_error("El producto ya existe.")
            elif ex.errno == 1044:
                self.show_error("Acceso denegado para el usuario especificado.")
            elif ex.errno == 1049:
                self.show_error("Base de datos no existe.")
            else:
                self.show_error(f"Error MySQL {ex.errno}: {ex.msg}")

        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        pass

    def show_error(self, error_message):
        # aquí podría mostrar un dialogo o una alerta con el mensaje de error
        toast(f"{error_message}")
