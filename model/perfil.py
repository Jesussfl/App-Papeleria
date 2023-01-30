import configparser

from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
import mysql
import mysql.connector
from mysql.connector import Error


class Perfil(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app, db = self.conectar_bd()

        self.agregar_estilos_topbar()
        self.validar_nivel_usuario(db)

    def on_pre_enter(self, *args):
        self.cargar_datos_usuario()
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
                self.ids.bottom_navigation.remove_widget(self.ids.inventarioScreen)
            else:
                print("hola")

        if db.is_connected():
            db.close()
            print("Se cerro la base de datos")

    def cambiar_pantalla(self, *args):
        self.ids.bottom_navigation.switch_tab('perfil-screen')

    def agregar_estilos_topbar(self, *args):
        self.ids.toolbar.ids.label_title.font_name = "Poppins-Medium.ttf"
        self.ids.toolbar.ids.label_title.font_size = '15sp'

    def cargar_datos_usuario(self, *args):

        try:
            app, db = self.conectar_bd()

            with open('model/session.txt') as mytextfile:
                correo = mytextfile.read()

            if db.is_connected():
                cursor = db.cursor()

                # Ejecutando query para extraer datos del usuario
                query = "SELECT * FROM usuarios where correo='" + str(
                    correo) + "'"

                cursor.execute(query)
                data = cursor.fetchone()
                cursor.close()

                # Introduciendo datos en campos del perfil
                app.manager.get_screen('perfil').ids['inputDNI'].text = str(data[0])
                app.manager.get_screen('perfil').ids['inputTipo'].text = data[1]
                app.manager.get_screen('perfil').ids['label_fullname'].text = data[2]
                app.manager.get_screen('perfil').ids['inputPhone'].text = data[3]
                app.manager.get_screen('perfil').ids['inputAddress'].text = data[4]
                app.manager.get_screen('perfil').ids['inputEmail'].text = data[5]
                app.manager.get_screen('perfil').ids['inputRango'].text = data[9]

        except Error as ex:
            print("Error durante la conexion:", ex)

        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        pass

    def conectar_bd(self):
        app = MDApp.get_running_app()
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
        return app, db
