import configparser
import re
from datetime import datetime

from kivy.app import App
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
import mysql
import mysql.connector
from mysql.connector import Error


class Signup(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Cédula",
                "on_release": lambda x=f"Cédula": self.set_item(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"RIF",
                "on_release": lambda x=f"RIF": self.set_item(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.menu_,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )

    def set_item(self, text__item):
        self.ids.menu_.text = text__item
        self.menu.dismiss()

    def validate_name(self, name):
        if not name.text.strip():
            return False
        elif " " not in name.text:
            self.ids.inputFullName.error = True
            self.ids.inputFullName.helper_text = "Por favor ingresa tu nombre completo."
            self.ids.inputFullName.helper_text_mode = "on_error"
            return False
        self.ids.inputFullName.error = False
        return True

    def validate_numbers(self, instance, value):
        if not value.isdigit():
            self.textfield.text = ""

    def connect(self):
        with open('model/session.txt', 'w') as mytextfile:
            mytextfile.truncate()

        app = App.get_running_app()
        inputFullName = app.manager.get_screen('signup').ids['inputFullName'].text
        inputPhone = app.manager.get_screen('signup').ids['inputPhone'].text
        inputDNI = app.manager.get_screen('signup').ids['inputDNI'].text
        inputAddress = app.manager.get_screen('signup').ids['inputAddress'].text
        inputGender = app.manager.get_screen('signup').ids['inputSex'].text
        inputEmail = app.manager.get_screen('signup').ids['inputEmail'].text
        inputPassword = app.manager.get_screen('signup').ids['inputPassword'].text
        typeDNI = app.manager.get_screen('signup').ids['menu_'].text
        lastTime = datetime.now()
        self.manager.current = 'catalogo'
        # Validando que no hayan campos vacíos
        if not inputFullName or not inputPhone or not inputDNI or not inputAddress or not inputGender or not inputEmail or not inputPassword or not lastTime or not typeDNI:
            self.show_error("Por favor llene todos los campos requeridos.")
            return

        # Validando que el correo electrónico sea válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", inputEmail):
            self.show_error("Por favor ingrese un correo electrónico válido.")
            return

        if not len(inputPhone) in (11, 12):
            self.show_error("El numero de telefono no es valido.")
            return
        else:
            # Formatear el numero telefonico para guardarlo correctamente en la base de datos
            inputPhone = "+58-" + inputPhone[-11:-7] + "-" + inputPhone[-7:-4] + "-" + inputPhone[-4:]

        # Validando que la cedula o rif tenga la cantidad de caracteres necesarias
        if not len(inputDNI) in (7, 9):
            self.show_error("Por favor ingrese un numero de documento válido.")
            return

        # Validando que la contraseña tenga al menos una letra mayúscula, una minúscula y un número
        if not re.search("[a-z]", inputPassword):
            self.show_error("La contraseña debe tener al menos una letra minúscula.")
            return
        if not re.search("[A-Z]", inputPassword):
            self.show_error("La contraseña debe tener al menos una letra mayúscula.")
            return
        if not re.search("[0-9]", inputPassword):
            self.show_error("La contraseña debe tener al menos un número.")
            return

        try:
            userLevels = ('Usuario', 'Empleado', 'Administrador')
            config = configparser.ConfigParser()
            config.read('config.ini')

            host = config['mysql']['host']
            user = config['mysql']['user']
            password = config['mysql']['password']
            dbname = config['mysql']['db']

            db = mysql.connector.connect(host=str(host), user=str(user), password=str(password), database=str(dbname))
            if db.is_connected():
                cursor = db.cursor()

                query = "Insert into usuarios (cedula, tipo_documento, nombre_completo, telefono, direccion, correo, contraseña, ultimo_inicio, sexo, tipo_usuario)" \
                        " values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')".format(
                    inputDNI,
                    typeDNI,
                    inputFullName,
                    inputPhone,
                    inputAddress,
                    inputEmail,
                    inputPassword,
                    lastTime,
                    inputGender,
                    userLevels[1])
                cursor.execute(query)
                db.commit()
                with open('model/session.txt', 'w') as mytextfile:
                    mytextfile.write(inputEmail)

                print("Datos Registrados Correctamente")
                toast('Sesión Iniciada')
                self.manager.current = 'catalogo'
        except Error as ex:
            print("Error durante la conexion:", ex)

            if ex.errno == 1062:
                self.show_error("El usuario ya existe.")
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
