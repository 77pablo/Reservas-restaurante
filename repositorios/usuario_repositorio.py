from mysql.connector import Error
from repositorios.base_repositorio import BaseRepositorio
from modelos.usuario import Usuario
from validaciones import validar_rut, validar_genero


class UsuarioRepositorio(BaseRepositorio):
    def _consultar_uno(self, sql, parametros=None):
        conexion = None
        try:
            conexion = self._conexion_bd.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(sql, parametros or ())
            fila = cursor.fetchone()
            cursor.close()
            return fila
        except Error as error:
            print(f"[ERROR SQL] {error}")
            return None
        finally:
            if conexion and conexion.is_connected():
                conexion.close()

    def _consultar_todos(self, sql, parametros=None):
        conexion = None
        try:
            conexion = self._conexion_bd.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(sql, parametros or ())
            filas = cursor.fetchall()
            cursor.close()
            return filas
        except Error as error:
            print(f"[ERROR SQL] {error}")
            return []
        finally:
            if conexion and conexion.is_connected():
                conexion.close()

    def crear(self, usuario: Usuario):
        rut_limpio, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)

        genero_limpio, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = """
            INSERT INTO usuario
            (rut, nombre_completo, correo, telefono, genero, contrasena)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (
            rut_limpio,
            usuario.nombre_completo,
            usuario.correo,
            usuario.telefono,
            genero_limpio,
            usuario.contrasena,
        )

        nuevo_id = self._ejecutar_consulta(sql, parametros, obtener_id=True)
        if nuevo_id:
            usuario.id_usuario = nuevo_id
        return nuevo_id

    def obtener_por_id(self, id_usuario: int):
        sql = """
            SELECT id_usuario, rut, nombre_completo, correo, telefono, genero, contrasena
            FROM usuario
            WHERE id_usuario = %s
        """
        return self._consultar_uno(sql, (id_usuario,))

    def buscar_por_rut(self, rut: str):
        rut_limpio, msg_rut = validar_rut(rut)
        criterio = rut_limpio if msg_rut == "RUT Válido" else rut
        sql = """
            SELECT id_usuario, rut, nombre_completo, correo, telefono, genero, contrasena
            FROM usuario
            WHERE rut = %s
        """
        return self._consultar_uno(sql, (criterio,))

    def buscar_por_correo(self, correo: str):
        sql = """
            SELECT id_usuario, rut, nombre_completo, correo, telefono, genero, contrasena
            FROM usuario
            WHERE correo = %s
        """
        return self._consultar_uno(sql, (correo,))

    def listar(self):
        sql = """
            SELECT id_usuario, rut, nombre_completo, correo, telefono, genero, contrasena
            FROM usuario
        """
        return self._consultar_todos(sql)

    def actualizar(self, usuario: Usuario):
        if usuario.id_usuario is None:
            raise ValueError("El usuario no tiene un ID asignado.")

        rut_limpio, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)

        genero_limpio, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = """
            UPDATE usuario
            SET rut=%s,
                nombre_completo=%s,
                correo=%s,
                telefono=%s,
                genero=%s,
                contrasena=%s
            WHERE id_usuario=%s
        """
        parametros = (
            rut_limpio,
            usuario.nombre_completo,
            usuario.correo,
            usuario.telefono,
            genero_limpio,
            usuario.contrasena,
            usuario.id_usuario,
        )
        return self._ejecutar_consulta(sql, parametros)

    def eliminar(self, id_usuario: int):
        sql = "DELETE FROM usuario WHERE id_usuario = %s"
        return self._ejecutar_consulta(sql, (id_usuario,))