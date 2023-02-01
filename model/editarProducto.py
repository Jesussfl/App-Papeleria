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


class EditarProducto(MDScreen):

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
        self.cargar_producto()

    def colocar_contenido_dropdown(self, text__item):
        self.ids.inputTipoPrecio.text = text__item
        self.ids.inputPrecio.disabled = False
        self.ids.inputPrecio.helper_text = ""
        self.menu.dismiss()

    # def on_pre_enter(self, *args):

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def select_path(self, path):
        # Almacenando la ruta del archivo seleccionado
        path = path.replace('\\', '/')
        self.ids.inputImagen.text = path
        self.manager_open = False
        self.file_manager.close()
        pass

    def on_pre_enter(self, *args):
        self.agregar_estilos_topbar()

    def exit_manager(self, *args):
        self.remove_widget(self.file_manager)

    def open_file_manager(self):
        # Abriendo el administrador de archivos
        self.file_manager.show('C:')
        self.manager_open = True

    def cargar_producto(self):
        try:
            db = self.conectar_bd()

            with open('model/cache.txt') as mytextfile:
                codigo = mytextfile.read()
            if db.is_connected():
                cursor = db.cursor()

                # Ejecutando query para extraer datos del producto
                query = "SELECT * FROM inventario where codigo='" + codigo + "'"

                cursor.execute(query)
                data = cursor.fetchone()
                cursor.close()

                # Introduciendo datos en campos del producto
                self.ids['inputCodigo'].text = str(data[0])
                self.ids['inputNombreProducto'].text = data[1]
                self.ids['inputDescripcion'].text = data[2]
                self.ids['inputCantidad'].text = str(data[3])
                self.ids['inputPrecio'].text = str(data[4])
                self.ids['inputMarca'].text = data[5]
                self.ids['inputImagen'].text = data[6]

        except Error as ex:
            print("Error durante la conexion:", ex)

        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

    def editar_producto(self):
        app = App.get_running_app()
        codigo = app.manager.get_screen('editarProducto').ids['inputCodigo'].text
        nombre = app.manager.get_screen('editarProducto').ids['inputNombreProducto'].text.title()
        descripcion = app.manager.get_screen('editarProducto').ids['inputDescripcion'].text
        cantidad = int(app.manager.get_screen('editarProducto').ids['inputCantidad'].text)
        precio = float(app.manager.get_screen('editarProducto').ids['inputPrecio'].text)
        marca = app.manager.get_screen('editarProducto').ids['inputMarca'].text.title()
        tipo_precio = app.manager.get_screen('editarProducto').ids['inputTipoPrecio'].text
        ruta_imagen = app.manager.get_screen('editarProducto').ids['inputImagen'].text
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

                query = "UPDATE inventario SET nombre='{0}', descripcion='{1}', cantidad={2}, precio={3}, marca='{4}', imagen='{5}', estado='{6}', fecha_modificacion='{7}'" \
                        " WHERE codigo='{8}'".format(
                    nombre,
                    descripcion,
                    int(cantidad),
                    float(precio),
                    marca,
                    ruta_imagen,
                    estado,
                    tiempo_creacion,
                    int(codigo))

                cursor.execute(query)
                db.commit()
                print("Datos Actualizados Correctamente")
                toast('Producto Actualizado Correctamente')
                self.manager.current = 'inventario'
                self.manager.remove_widget(EditarProducto(name='editarProducto'))

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
