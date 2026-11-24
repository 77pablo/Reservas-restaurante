from repositorios.base_repositorio import BaseRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from modelos.empleado import Empleado


class EmpleadoRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__()
        self._usuario_repo = UsuarioRepositorio()

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