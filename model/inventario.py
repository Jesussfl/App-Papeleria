import configparser

import mysql
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from mysql.connector import cursor
from mysql.connector import Error

from model.editarProducto import EditarProducto


class Inventario(MDScreen):
    dialog = None
    dialogDolar = None
    datos_fila_seleccionada = []
    with open('model/precioDolar.txt') as mytextfile:
        text = mytextfile.read()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        db = self.conectar_bd()

        self.validar_nivel_usuario(db)
        self.agregar_estilos_topbar()

    def on_pre_enter(self, *args):

        self.cargar_productos('SELECT * FROM inventario')
        self.cambiar_pantalla()

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
            "SELECT * FROM inventario WHERE codigo LIKE '%{0}%' or nombre LIKE '%{0}%' OR descripcion LIKE '%{0}%' OR marca LIKE '%{0}%'".format(
                nombre_producto))

    def cargar_productos(self, consulta):
        db = self.conectar_bd()
        cursor = db.cursor()
        cursor.execute(consulta)
        rows = []
        for (codigo, nombre, descripcion, cantidad, precio, marca, imagen, estado, fecha_modificacion) in cursor:
            rows.append((codigo, nombre, descripcion, cantidad, precio, marca, imagen, estado,
                         fecha_modificacion))
        self.ids.cantidadProductos.text = f"{str(len(rows))} Productos"
        if db.is_connected():
            db.close()
        cols = ['Código', 'Producto', 'Descripción', 'Cantidad', 'Precio', 'Marca', 'Imágen', 'Estado',
                'Fecha de Modificación']
        self.eliminar_lista_desactualizada()
        table = MDDataTable(
            elevation=1,
            check=True,
            row_data=rows,
            column_data=[(col, dp(40)) for col in cols],
            rows_num=100,
        )
        # Vincular DataTable
        table.bind(on_check_press=self.fila_seleccionada)
        self.ids.listContainer.add_widget(table)

    def conectar_bd(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        return db

    def fila_seleccionada(self, instance_table, instance_row):
        self.datos_fila_seleccionada = instance_row
        self.mostrar_opciones(instance_row)
        instance_table.table_data.select_all('normal')

    def eliminar_producto(self, *args):
        try:
            db = self.conectar_bd()
            cursor = db.cursor()
            codigo = self.datos_fila_seleccionada[0]
            query = "DELETE FROM inventario WHERE codigo={0}".format(codigo)
            cursor.execute(query)
            db.commit()
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
                toast('Producto Borrado Correctamente')
                self.cerrar_dialog()
                self.cargar_productos('SELECT * FROM inventario')

    def editar_producto(self, *args):
        with open('model/cache.txt', 'w') as mytextfile:
            mytextfile.truncate()
            mytextfile.write(self.datos_fila_seleccionada[0])
        print(self.datos_fila_seleccionada[0])
        self.cerrar_dialog()
        self.manager.current = 'editarProducto'

    def mostrar_opciones(self, datos):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Seleccione una opción del Producto: {0}".format(datos[1]),
                buttons=[
                    MDFlatButton(
                        text="Cerrar",
                        on_release=self.cerrar_dialog
                    ),
                    MDFlatButton(
                        text="Editar",
                        on_release=self.editar_producto
                    ),
                    MDFlatButton(
                        text="Eliminar",
                        on_release=self.eliminar_producto
                    ),
                ],
            )
        self.dialog.open()

    def abrir_precio_dolar(self):
        if not self.dialogDolar:
            self.dialogDolar = MDDialog(
                title="Desea Cambiar el Precio del Dolar?",
                type="custom",
                content_cls=MDTextField(input_filter='float', text=self.text,
                                        hint_text="Precio del Dolar", ),
                buttons=[

                    MDFlatButton(
                        text="Cancelar",
                        on_release=self.cerrar_dialogDolar
                    ),
                    MDFlatButton(
                        text="Guardar",
                        on_release=self.cambiar_precio_dolar
                    ),
                ],
            )
        self.dialogDolar.content_cls.bind(text=self.set_text)
        self.dialogDolar.open()

    def set_text(self, instance, value):
        self.text = value

    def cargar_precio(self, instance):
        with open('model/precioDolar.txt', 'w') as mytextfile:
            instance.text = mytextfile.read()

    def cambiar_precio_dolar(self, instance):
        with open('model/precioDolar.txt', 'w') as mytextfile:
            mytextfile.truncate()
            mytextfile.write(self.text)
        toast('Precio del Dolar Actualizado: ' + self.text + ' Bs')
        self.cerrar_dialogDolar()

    def cerrar_dialog(self, *args):
        self.dialog.dismiss(force=True)
        self.dialog = None

    def cerrar_dialogDolar(self, *args):
        self.dialogDolar.dismiss(force=True)

    def eliminar_lista_desactualizada(self):
        rows = [i for i in self.ids.listContainer.children]
        for row1 in rows:
            if isinstance(row1, MDDataTable):
                self.ids.listContainer.remove_widget(row1)

    def cambiar_pantalla(self, *args):
        self.ids.bottomNavigation.switch_tab('inventario-screen')

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def mostrar_error(self, error_message):
        # aquí podría mostrar un dialogo o una alerta con el mensaje de error
        toast(f"{error_message}")
