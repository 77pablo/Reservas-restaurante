"""Clase Empleado - hereda de Usuario (reutilizacion de codigo) y
sobrescribe metodos para demostrar polimorfismo."""
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

    # ---------- Sobrescritura de metodos (polimorfismo) ----------

    def obtener_rol(self):
        return "Empleado"

    def realizar_accion_principal(self):
        return (f"{self.nombre_completo} (Empleado - {self._cargo}, turno "
                f"{self._turno}) gestiona {len(self._mesas_asignadas)} mesa(s) "
                f"y puede aprobar reservas.")

    def cerrarSesion(self):
        """Sobrescribe el metodo de Usuario, extendiendo su comportamiento."""
        super().cerrarSesion()
        print(f"[Empleado] Turno '{self._turno}' finalizado.")

    def __str__(self):
        return (f"Empleado(id={self.id_usuario}, nombre='{self.nombre_completo}', "
                f"cargo='{self._cargo}')")