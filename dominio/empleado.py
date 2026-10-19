"""Clase Empleado - hereda de Usuario (reutilizacion de codigo)."""
from dominio.usuario import Usuario


class Empleado(Usuario):
    def __init__(self, id_usuario=None, nombre_completo="", correo="",
                 telefono="", contrasena="", id_empleado=None,
                 cargo="", turno=""):
        super().__init__(id_usuario, nombre_completo, correo, telefono, contrasena)
        self._id_empleado = id_empleado
        self._cargo = cargo
        self._turno = turno
        self._mesas_asignadas = []

    @property
    def id_empleado(self):
        return self._id_empleado

    @id_empleado.setter
    def id_empleado(self, valor):
        self._id_empleado = valor

    @property
    def cargo(self):
        return self._cargo

    @cargo.setter
    def cargo(self, valor):
        self._cargo = valor

    @property
    def turno(self):
        return self._turno

    @turno.setter
    def turno(self, valor):
        self._turno = valor

    def aprobarReserva(self, reserva):
        """Retorna boolean."""
        return reserva.actualizarEstado("Confirmada")

    def gestionarMesas(self):
        """void."""
        print(f"[Empleado] {self.nombre_completo} gestiona "
              f"{len(self._mesas_asignadas)} mesa(s).")