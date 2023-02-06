import configparser
from datetime import datetime

from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error

from model.catalogo import Catalogo
from model.editarProducto import EditarProducto
from model.inventario import Inventario
from model.perfil import Perfil


class Login(MDScreen):

    def iniciar_sesion(self):

        try:
            app = App.get_running_app()
            # Almacenando los datos de los campos en variables
            correo = app.manager.get_screen('login').ids['inputEmail'].text
            contraseña = app.manager.get_screen('login').ids['inputPassword'].text
            tiempo_actual = datetime.now()
            tiempo_actual_formateado = tiempo_actual.strftime("%Y-%m-%d %H:%M:%S")

            conexion, conteo, cursor = self.validar_usuario(contraseña, correo)

            if not conteo:
                toast("Datos Incorrectos.")
                return False
            else:
                toast('Sesión Iniciada')

                self.actualizar_ultimo_inicio(conexion, correo, cursor, tiempo_actual_formateado)

                self.manager.add_widget(Catalogo(name='catalogo'))
                self.manager.add_widget(Perfil(name='perfil'))
                self.manager.add_widget(Inventario(name='inventario'))
                self.manager.add_widget(EditarProducto(name='editarProducto'))

                self.manager.current = 'catalogo'

        except Error as ex:
            print("Error durante la conexion:", ex)

            self.mostrar_error(f"Error MySQL {ex.errno}: {ex.msg}")

        finally:
            if conexion.is_connected():
                conexion.close()
                print("Se cerro la base de datos")

        pass

    def actualizar_ultimo_inicio(self, conexion, correo, cursor, tiempo_actual_formateado):
        with open('model/session.txt', 'w') as mytextfile:
            mytextfile.write(correo)
        query = "update usuarios set ultimo_inicio='" + tiempo_actual_formateado + "' WHERE correo = '" + str(
            correo) + "'"
        cursor.execute(query)
        conexion.commit()

    def validar_usuario(self, contraseña, correo):

        # Conectando la base de datos
        config = configparser.ConfigParser()
        config.read('config.ini')
        host = config['mysql']['host']
        user = config['mysql']['user']
        password = config['mysql']['password']
        dbname = config['mysql']['db']
        conexion = mysql.connector.connect(host=str(host), user=str(user), password=str(password),
                                           database=str(dbname))
        cursor = conexion.cursor()
        # Ejecutando el query para validar los datos introducidos
        query = "SELECT count(*) FROM usuarios where correo='" + str(correo) + "' and contraseña = '" + str(
            contraseña) + "'"
        cursor.execute(query)
        datos = cursor.fetchone()
        conteo = datos[0]

        return conexion, conteo, cursor

    def mostrar_error(self, mensaje_error):
        # aquí podría mostrar un dialogo o una alerta con el mensaje de error
        toast(f"{mensaje_error}")
