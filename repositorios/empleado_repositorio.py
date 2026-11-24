from mysql.connector import Error
from repositorios.base_repositorio import BaseRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from modelos.empleado import Empleado
from validaciones import validar_rut


class EmpleadoRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__()
        self._usuario_repo = UsuarioRepositorio()

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

    def crear(self, empleado: Empleado):
        id_usuario = self._usuario_repo.crear(empleado)
        if not id_usuario:
            return None

        sql = "INSERT INTO empleado (id_usuario, cargo, turno) VALUES (%s, %s, %s)"
        try:
            id_empleado = self._ejecutar_consulta(
                sql,
                (id_usuario, empleado.cargo, empleado.turno),
                obtener_id=True,
            )
        except Exception:
            try:
                self._ejecutar_consulta(
                    "DELETE FROM usuario WHERE id_usuario = %s",
                    (id_usuario,),
                )
            except Exception:
                pass
            raise

        if not id_empleado:
            return None

        empleado.id_empleado = id_empleado
        return id_empleado

    def obtener_por_id(self, id_empleado: int):
        sql = """
            SELECT e.id_empleado, e.id_usuario, e.cargo, e.turno,
                   u.rut, u.nombre_completo, u.correo, u.telefono, u.genero, u.contrasena
            FROM empleado e
            INNER JOIN usuario u ON e.id_usuario = u.id_usuario
            WHERE e.id_empleado = %s
        """
        return self._consultar_uno(sql, (id_empleado,))

    def buscar_por_rut(self, rut: str):
        rut_limpio, msg_rut = validar_rut(rut)
        criterio = rut_limpio if msg_rut == "RUT Válido" else rut
        sql = """
            SELECT e.id_empleado, e.id_usuario, e.cargo, e.turno,
                   u.rut, u.nombre_completo, u.correo, u.telefono, u.genero, u.contrasena
            FROM empleado e
            INNER JOIN usuario u ON e.id_usuario = u.id_usuario
            WHERE u.rut = %s
        """
        return self._consultar_uno(sql, (criterio,))

    def listar(self):
        sql = """
            SELECT e.id_empleado, e.id_usuario, e.cargo, e.turno,
                   u.rut, u.nombre_completo, u.correo, u.telefono, u.genero, u.contrasena
            FROM empleado e
            INNER JOIN usuario u ON e.id_usuario = u.id_usuario
        """
        return self._consultar_todos(sql)

    def actualizar(self, empleado: Empleado):
        if empleado.id_usuario is None:
            raise ValueError("El empleado no tiene un ID de usuario asignado.")

        filas_usuario = self._usuario_repo.actualizar(empleado)
        if not filas_usuario:
            return None

        sql = "UPDATE empleado SET cargo = %s, turno = %s WHERE id_usuario = %s"
        return self._ejecutar_consulta(
            sql,
            (empleado.cargo, empleado.turno, empleado.id_usuario),
        )

    def eliminar(self, id_empleado: int):
        registro = self.obtener_por_id(id_empleado)
        if not registro:
            return 0

        eliminado_empleado = self._ejecutar_consulta(
            "DELETE FROM empleado WHERE id_empleado = %s",
            (id_empleado,),
        )
        if not eliminado_empleado:
            return None

        self._ejecutar_consulta(
            "DELETE FROM usuario WHERE id_usuario = %s",
            (registro["id_usuario"],),
        )
        return eliminado_empleado