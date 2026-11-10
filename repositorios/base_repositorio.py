from mysql.connector import Error
from conexion.conexion_bd import ConexionBD

class BaseRepositorio:
    def __init__(self):
        self._conexion_bd = ConexionBD()

    def _ejecutar_consulta(self, sql, parametros=None, obtener_id=False):
        conexion = None
        try:
            conexion = self._conexion_bd.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros or ())
            conexion.commit()
            resultado = cursor.lastrowid if obtener_id else cursor.rowcount
            cursor.close()
            return resultado
        except Error as error:
            print(f"[ERROR SQL] {error}")
            if conexion: conexion.rollback()
            return None
        finally:
            if conexion and conexion.is_connected(): conexion.close()
