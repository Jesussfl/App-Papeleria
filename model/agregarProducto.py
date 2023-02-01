import configparser
from datetime import datetime

from kivy.app import App
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error


class AgregarProducto(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            preview=True,
            current_path='C:',
            use_access=True,
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )

    def exit_manager(self, *args):
        self.remove_widget(self.file_manager)

    def select_path(self, path):
        path = path.replace('\\', '/')
        self.ids.inputImagen.text = path
        self.manager_open = False
        self.file_manager.close()
        pass

    def on_pre_enter(self, *args):
        self.agregar_estilos_topbar()

    def open_file_manager(self):
        # self.add_widget(self.file_manager)
        self.file_manager.show('C:')  # output manager to the screen
        self.manager_open = True

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def registrar_producto(self):
        app = App.get_running_app()
        nombre = app.manager.get_screen('agregarProducto').ids['inputNombreProducto'].text
        descripcion = app.manager.get_screen('agregarProducto').ids['inputDescripcion'].text
        cantidad = app.manager.get_screen('agregarProducto').ids['inputCantidad'].text
        precio = app.manager.get_screen('agregarProducto').ids['inputPrecio'].text
        marca = app.manager.get_screen('agregarProducto').ids['inputMarca'].text
        ruta_imagen = app.manager.get_screen('agregarProducto').ids['inputImagen'].text
        tiempo_creacion = datetime.now()
        estado = "Disponible"

        # Validando que no hayan campos vacíos
        if not nombre or not cantidad or not precio or not marca or not ruta_imagen:
            self.mostrar_error("Por favor llene todos los campos requeridos.")
            return

        try:

            db = self.conectar_bd()
            if db.is_connected():
                cursor = db.cursor()

                query = "Insert into inventario (nombre, descripcion, cantidad, precio, marca, imagen, estado, fecha_modificacion)" \
                        " values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(
                    nombre,
                    descripcion,
                    cantidad,
                    precio,
                    marca,
                    ruta_imagen,
                    estado,
                    tiempo_creacion)

                cursor.execute(query)
                db.commit()
                print("Datos Registrados Correctamente")
                toast('Producto Registrado Correctamente')
                self.manager.current = 'inventario'

        except Error as ex:
            print("Error durante la conexion:", ex)

            if ex.errno == 1062:
                self.mostrar_error("El producto ya existe.")
            elif ex.errno == 1044:
                self.mostrar_error("Acceso denegado para el usuario especificado.")
            elif ex.errno == 1049:
                self.mostrar_error("Base de datos no existe.")
            else:
                self.mostrar_error(f"Error MySQL {ex.errno}: {ex.msg}")

        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        pass

    def conectar_bd(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        return db

    def mostrar_error(self, error_message):
        # aquí podría mostrar un dialogo o una alerta con el mensaje de error
        toast(f"{error_message}")
