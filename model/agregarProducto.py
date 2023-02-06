import configparser
from datetime import datetime

from kivy.app import App
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error


class AgregarProducto(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Creando el administrador de archivos
        self.manager_open = False
        self.file_manager = MDFileManager(
            preview=True,
            current_path='C:',
            use_access=True,
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Dolar",
                "on_release": lambda x=f"Dolar": self.colocar_contenido_dropdown(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Bolivar",
                "on_release": lambda x=f"Bolivar": self.colocar_contenido_dropdown(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.inputTipoPrecio,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        self.agregar_estilos_topbar()

    def on_pre_enter(self, *args):
        self.limpiar_campos()

    def limpiar_campos(self):
        app = App.get_running_app()
        app.manager.get_screen('agregarProducto').ids['inputNombreProducto'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputDescripcion'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputCantidad'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputPrecio'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputMarca'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputImagen'].text = ""
        app.manager.get_screen('agregarProducto').ids['inputTipoPrecio'].text = ""

    def colocar_contenido_dropdown(self, text__item):
        self.ids.inputTipoPrecio.text = text__item
        self.ids.inputPrecio.disabled = False
        self.ids.inputPrecio.helper_text = ""
        self.menu.dismiss()

    def exit_manager(self, *args):
        self.remove_widget(self.file_manager)

    def select_path(self, path):
        # Almacenando la ruta del archivo seleccionado
        path = path.replace('\\', '/')
        self.ids.inputImagen.text = path
        self.manager_open = False
        self.file_manager.close()
        pass

    def open_file_manager(self):
        # Abriendo el administrador de archivos
        self.file_manager.show('/')
        self.manager_open = True

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def registrar_producto(self):
        app = App.get_running_app()
        nombre = app.manager.get_screen('agregarProducto').ids['inputNombreProducto'].text.title()
        descripcion = app.manager.get_screen('agregarProducto').ids['inputDescripcion'].text
        cantidad = int(app.manager.get_screen('agregarProducto').ids['inputCantidad'].text)
        precio = float(app.manager.get_screen('agregarProducto').ids['inputPrecio'].text)
        marca = app.manager.get_screen('agregarProducto').ids['inputMarca'].text.title()
        ruta_imagen = app.manager.get_screen('agregarProducto').ids['inputImagen'].text
        tipo_precio = app.manager.get_screen('agregarProducto').ids['inputTipoPrecio'].text
        iva = 16
        tiempo_creacion = datetime.now()

        # Validando que haya stock
        if cantidad > 0:
            estado = "Disponible"
        else:
            estado = "Agotado"

        # Guardando el precio del dolar
        with open('model/precioDolar.txt') as mytextfile:
            precio_dolar = mytextfile.read()

        if tipo_precio == "Bolivar":
            # Aplicando el iva
            precio_mas_iva = (((precio * iva) / 100) + precio)
            precio = precio_mas_iva / float(precio_dolar)
        else:
            precio_bolivar = precio * float(precio_dolar)
            precio_mas_iva = (((precio_bolivar * iva) / 100) + precio)
            precio = precio_mas_iva / float(precio_dolar)

        # Redondeando a 2 decimales
        precio = round(precio, 2)

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
