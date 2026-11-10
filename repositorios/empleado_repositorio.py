from repositorios.base_repositorio import BaseRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from modelos.empleado import Empleado

class EmpleadoRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__()
        self._usuario_repo = UsuarioRepositorio()

    def crear(self, empleado: Empleado):
        id_usuario = self._usuario_repo.crear(empleado)
        if not id_usuario: return None
        sql = "INSERT INTO empleado (id_usuario, cargo, turno) VALUES (%s, %s, %s)"
        id_empleado = self._ejecutar_consulta(sql, (id_usuario, empleado.cargo, empleado.turno), obtener_id=True)
        if id_empleado: empleado.id_empleado = id_empleado
        return id_empleado

    def actualizar(self, empleado: Empleado):
        self._usuario_repo.actualizar(empleado)
        sql = "UPDATE empleado SET cargo = %s, turno = %s WHERE id_empleado = %s"
        return self._ejecutar_consulta(sql, (empleado.cargo, empleado.turno, empleado.id_empleado))
