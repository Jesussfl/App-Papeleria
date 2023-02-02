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

from model.catalogo import Catalogo
from model.inventario import Inventario
from model.perfil import Perfil


class Signup(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Cédula",
                "on_release": lambda x=f"Cédula": self.colocar_contenido_dropdown(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"RIF",
                "on_release": lambda x=f"RIF": self.colocar_contenido_dropdown(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.inputSex,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )
        super().__init__(**kwargs)
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": f"Masculino",
                "on_release": lambda x=f"Masculino": self.colocar_contenido_dropdown2(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Femenino",
                "on_release": lambda x=f"Femenino": self.colocar_contenido_dropdown2(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": f"Otro",
                "on_release": lambda x=f"Otro": self.colocar_contenido_dropdown2(x),
            }
        ]
        self.menu2 = MDDropdownMenu(
            caller=self.ids.menu_,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )

    def colocar_contenido_dropdown(self, text__item):
        self.ids.menu_.text = text__item
        self.menu.dismiss()

    def colocar_contenido_dropdown2(self, text__item):
        self.ids.inputSex.text = text__item
        self.menu.dismiss()

    def validar_nombre_completo(self, nombre):
        if not nombre.text.strip():
            return False
        elif " " not in nombre.text:
            self.ids.inputFullName.error = True
            self.ids.inputFullName.helper_text = "Por favor ingresa tu nombre completo."
            self.ids.inputFullName.helper_text_mode = "on_error"
            return False
        self.ids.inputFullName.error = False
        return True

    def aceptar_solo_numeros(self, instance, value):
        if not value.isdigit():
            self.textfield.text = ""

    def registrar_usuario(self):
        with open('model/session.txt', 'w') as mytextfile:
            mytextfile.truncate()

        app = App.get_running_app()
        nombre_completo = app.manager.get_screen('signup').ids['inputFullName'].text.title()
        telefono = app.manager.get_screen('signup').ids['inputPhone'].text
        cedula_rif = app.manager.get_screen('signup').ids['inputDNI'].text
        direccion = app.manager.get_screen('signup').ids['inputAddress'].text.title()
        genero = app.manager.get_screen('signup').ids['inputSex'].text
        correo = app.manager.get_screen('signup').ids['inputEmail'].text
        contraseña = app.manager.get_screen('signup').ids['inputPassword'].text
        tipo_documento = app.manager.get_screen('signup').ids['menu_'].text
        ultima_vez = datetime.now()

        # Validando que no hayan campos vacíos
        if not nombre_completo or not telefono or not cedula_rif or not direccion or not genero or not correo or not contraseña or not ultima_vez or not tipo_documento:
            self.mostrar_error("Por favor llene todos los campos requeridos.")
            return

        # Validando que el correo electrónico sea válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            self.mostrar_error("Por favor ingrese un correo electrónico válido.")
            return

        if not len(telefono) in (11, 12):
            self.mostrar_error("El numero de telefono no es valido.")
            return
        else:
            # Formatear el numero telefonico para guardarlo correctamente en la base de datos
            telefono = "+58-" + telefono[-11:-7] + "-" + telefono[-7:-4] + "-" + telefono[-4:]

        # Validando que la cedula o rif tenga la cantidad de caracteres necesarias
        # if not len(cedula_rif) in (6, 10):
        #     self.mostrar_error("Por favor ingrese un numero de documento válido.")
        #     return

        # Validando que la contraseña tenga al menos una letra mayúscula, una minúscula y un número
        if not re.search("[a-z]", contraseña):
            self.mostrar_error("La contraseña debe tener al menos una letra minúscula.")
            return
        if not re.search("[A-Z]", contraseña):
            self.mostrar_error("La contraseña debe tener al menos una letra mayúscula.")
            return
        if not re.search("[0-9]", contraseña):
            self.mostrar_error("La contraseña debe tener al menos un número.")
            return

        try:
            nivel_usuario = ('Cliente', 'Empleado', 'Administrador')
            db = self.conectar_bd()
            if db.is_connected():
                cursor = db.cursor()

                query = "Insert into usuarios (cedula, tipo_documento, nombre_completo, telefono, direccion, correo, contraseña, ultimo_inicio, sexo, tipo_usuario)" \
                        " values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')".format(
                    cedula_rif,
                    tipo_documento,
                    nombre_completo,
                    telefono,
                    direccion,
                    correo,
                    contraseña,
                    ultima_vez,
                    genero,
                    nivel_usuario[1])
                cursor.execute(query)
                db.commit()
                with open('model/session.txt', 'w') as mytextfile:
                    mytextfile.write(correo)

                print("Datos Registrados Correctamente")
                toast('Sesión Iniciada')
                self.manager.add_widget(Catalogo(name='catalogo'))
                self.manager.add_widget(Perfil(name='perfil'))
                self.manager.add_widget(Inventario(name='inventario'))
                self.manager.current = 'catalogo'
        except Error as ex:
            print("Error durante la conexion:", ex)

            if ex.errno == 1062:
                self.mostrar_error("El usuario ya existe.")
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
