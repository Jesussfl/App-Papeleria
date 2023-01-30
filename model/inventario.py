import configparser

import mysql
from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.screen import MDScreen
from mysql.connector import cursor


class Inventario(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        db = self.conectar_bd()

        self.validar_nivel_usuario(db)
        self.agregar_estilos_topbar()

    def on_pre_enter(self, *args):
        self.cargar_productos()
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

    def cargar_productos(self):
        db = self.conectar_bd()
        cursor = db.cursor()
        query = 'SELECT * FROM inventario'
        cursor.execute(query)
        data = cursor.fetchall()
        if db.is_connected():
            db.close()
        cols = ['Código', 'Producto', 'Descripción', 'Cantidad', 'Precio', 'Marca', 'Imágen', 'Estado',
                'Fecha de Modificación']
        self.eliminar_lista_desactualizada()
        table = MDDataTable(
            elevation=1,
            check=True,
            row_data=data,
            column_data=[(col, dp(40)) for col in cols]

        )
        # Vincular DataTable
        table.bind(on_check_press=self.fila_seleccionada)
        table.bind(on_row_press=self.fila_presionada)
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

    def fila_seleccionada(self, instance_table, current_row):
        # Metodo para revisar fila seleccionada
        print(instance_table, current_row)

    # Function for row presses
    def fila_presionada(self, instance_table, instance_row):
        # Metodo para revisar fila presionada
        print(instance_table, instance_row)

    def eliminar_lista_desactualizada(self):
        rows = [i for i in self.ids.listContainer.children]
        for row1 in rows:
            if isinstance(row1, MDDataTable):
                self.ids.listContainer.remove_widget(row1)

    def cambiar_pantalla(self, *args):
        self.ids.bottomNavigation.switch_tab('inventario-screen')

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"
        self.ids.toolbar.ids.label_title.font_size = '15sp'
