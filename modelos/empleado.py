from modelos.usuario import Usuario

class Empleado(Usuario):
    def __init__(self, nombre_completo, correo, telefono, contrasena=None, cargo="", turno="", id_usuario=None, id_empleado=None):
        super().__init__(nombre_completo, correo, telefono, contrasena, id_usuario)
        self._id_empleado = id_empleado
        self.cargo = cargo
        self.turno = turno

    @property
    def id_empleado(self): return self._id_empleado
    @id_empleado.setter
    def id_empleado(self, v): self._id_empleado = v
    @property
    def cargo(self): return self._cargo
    @cargo.setter
    def cargo(self, v): self._cargo = v
    @property
    def turno(self): return self._turno
    @turno.setter
    def turno(self, v): self._turno = v

    def aprobar_reserva(self, reserva):
        if reserva.estado != "Pendiente": return False
        reserva.estado = "Confirmada"
        return reserva.actualizar_estado()

    def gestionar_mesas(self, mesa, accion="liberar"):
        if accion == "liberar": mesa.liberar()
        elif accion == "activar": mesa.activa = True
        return True
