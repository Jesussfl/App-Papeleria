import configparser
from datetime import datetime

from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error


class Login(MDScreen):
    pass

    def connect(self):

        try:
            app = App.get_running_app()
            input_email = app.manager.get_screen('login').ids['inputEmail'].text
            input_password = app.manager.get_screen('login').ids['inputPassword'].text
            now = datetime.now()
            now_formated = now.strftime("%Y-%m-%d %H:%M:%S")

            config = configparser.ConfigParser()
            config.read('config.ini')

            host = config['mysql']['host']
            user = config['mysql']['user']
            password = config['mysql']['password']
            dbname = config['mysql']['db']

            db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
            cursor = db.cursor()

            query = "SELECT count(*) FROM usuarios where correo='" + str(input_email) + "' and contraseña = '" + str(
                input_password) + "'"
            cursor.execute(query)
            data = cursor.fetchone()
            count = data[0]

            if not count:
                toast("Datos Incorrectos.")
            else:
                toast('Sesión Iniciada')

                with open('model/session.txt', 'w') as mytextfile:
                    mytextfile.write(input_email)
                query = "update usuarios set ultimo_inicio='" + now_formated + "' WHERE correo = '" + str(
                    input_email) + "'"
                cursor.execute(query)
                db.commit()
                self.manager.current = 'catalogo'
                return True

        except Error as ex:
            print("Error durante la conexion:", ex)

            self.show_error(f"Error MySQL {ex.errno}: {ex.msg}")

        finally:
            if db.is_connected():
                db.close()
                print("Se cerro la base de datos")

        return input_email
        pass

    def show_error(self, error_message):
        # aquí podría mostrar un dialogo o una alerta con el mensaje de error
        toast(f"{error_message}")
