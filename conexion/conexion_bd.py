import mysql.connector
from mysql.connector import Error
from config.configuracion import Configuracion

class ConexionBD:
    def __init__(self):
        self._host = Configuracion.DB_HOST
        self._port = Configuracion.DB_PORT
        self._database = Configuracion.DB_NAME
        self._user = Configuracion.DB_USER
        self._password = Configuracion.DB_PASSWORD

    def obtener_conexion(self):
        return mysql.connector.connect(
            host=self._host, port=self._port, database=self._database,
            user=self._user, password=self._password, charset="utf8mb4"
        )

    def probar_conexion(self):
        conexion = None
        try:
            conexion = self.obtener_conexion()
            if conexion.is_connected():
                print(f"[OK] Conexión exitosa a MySQL. Versión: {conexion.get_server_info()}")
                return True
            return False
        except Error as error:
            print(f"[ERROR] No fue posible conectar a MySQL: {error}")
            return False
        finally:
            if conexion is not None and conexion.is_connected():
                conexion.close()
