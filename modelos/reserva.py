from datetime import datetime

class Reserva:
    ESTADOS_VALIDOS = {"Pendiente", "Confirmada", "Cancelada", "Completada"}
    def __init__(self, id_cliente, cant_personas, estado="Pendiente", observaciones="", fecha_creacion=None, id_reserva=None):
        self._id_reserva = id_reserva
        self.id_cliente = id_cliente
        self.cant_personas = cant_personas
        self.estado = estado
        self.observaciones = observaciones
        self._fecha_creacion = fecha_creacion or datetime.now()

    @property
    def id_reserva(self): return self._id_reserva
    @id_reserva.setter
    def id_reserva(self, v): self._id_reserva = v
    @property
    def id_cliente(self): return self._id_cliente
    @id_cliente.setter
    def id_cliente(self, v): self._id_cliente = v
    @property
    def cant_personas(self): return self._cant_personas
    @cant_personas.setter
    def cant_personas(self, v): self._cant_personas = v
    @property
    def estado(self): return self._estado
    @estado.setter
    def estado(self, v): self._estado = v
    @property
    def observaciones(self): return self._observaciones
    @observaciones.setter
    def observaciones(self, v): self._observaciones = v or ""
    @property
    def fecha_creacion(self): return self._fecha_creacion

    def crear(self): return self.id_cliente is not None and self.cant_personas > 0
    def actualizar_estado(self): return self.estado in self.ESTADOS_VALIDOS
