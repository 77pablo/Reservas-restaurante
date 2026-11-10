from modelos.usuario import Usuario

class Cliente(Usuario):
    def __init__(self, nombre_completo, correo, telefono, contrasena=None, preferencias="", puntos_fidelidad=0, id_usuario=None, id_cliente=None):
        super().__init__(nombre_completo, correo, telefono, contrasena, id_usuario)
        self._id_cliente = id_cliente
        self.preferencias = preferencias
        self.puntos_fidelidad = puntos_fidelidad

    @property
    def id_cliente(self): return self._id_cliente
    @id_cliente.setter
    def id_cliente(self, v): self._id_cliente = v
    @property
    def preferencias(self): return self._preferencias
    @preferencias.setter
    def preferencias(self, v): self._preferencias = v or ""
    @property
    def puntos_fidelidad(self): return self._puntos_fidelidad
    @puntos_fidelidad.setter
    def puntos_fidelidad(self, v): self._puntos_fidelidad = v

    def solicitar_reserva(self, reserva):
        reserva.id_cliente = self.id_cliente
        return reserva.crear()

    def cancelar_reserva(self, reserva):
        if reserva.id_cliente != self.id_cliente: return False
        reserva.estado = "Cancelada"
        return reserva.actualizar_estado()
