import configparser

import mysql
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from mysql.connector import cursor


class Inventario(MDScreen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(self.set_toolbar_font_name)
        Clock.schedule_once(self.set_toolbar_font_size)

        app = MDApp.get_running_app()
        config = configparser.ConfigParser()
        config.read('config.ini')

        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))

        cursor = db.cursor()

        query = 'SELECT * FROM inventario'
        cursor.execute(query)
        data = cursor.fetchall()

        cols = ['Código', 'Producto', 'Descripción', 'Cantidad', 'Precio', 'Marca', 'Imágen', 'Estado','Fecha de Modificación']
        db.close()

        self.remove_childs()

        table = MDDataTable(
            elevation=1,
            check=True,
            row_data=data,
            column_data=[(col, dp(40)) for col in cols]

        )

        # Vincular DataTable
        table.bind(on_check_press=self.checked)
        table.bind(on_row_press=self.row_checked)
        self.ids.listContainer.add_widget(table)
        db.close()
        self.switch()

    # Function for check presses
    def checked(self, instance_table, current_row):
        print(instance_table, current_row)

    # Function for row presses
    def row_checked(self, instance_table, instance_row):
        print(instance_table, instance_row)

    def remove_childs(self):
        rows = [i for i in self.ids.listContainer.children]
        for row1 in rows:
            if isinstance(row1, MDDataTable):
                self.ids.listContainer.remove_widget(row1)

    def switch(self, *args):
        self.ids.bottomNavigation.switch_tab('inventario-screen')

    def set_toolbar_font_name(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"

    def set_toolbar_font_size(self, *args):
        self.ids.toolbar.ids.label_title.font_size = '15sp'
