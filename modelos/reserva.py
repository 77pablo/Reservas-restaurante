from datetime import date, time, datetime

class Reserva:
    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada", "Completada")
    MAX_PERSONAS = 20

    def __init__(self, id_cliente, fecha, hora, cant_personas,
                 estado="Pendiente", observaciones="",
                 fecha_creacion=None, id_reserva=None):
        self._id_reserva = id_reserva
        self._fecha_creacion = fecha_creacion or datetime.now()
        self.id_cliente = id_cliente
        self.fecha = fecha
        self.hora = hora
        self.cant_personas = cant_personas
        self.estado = estado
        self.observaciones = observaciones

    @property
    def id_reserva(self): return self._id_reserva
    @id_reserva.setter
    def id_reserva(self, v): self._id_reserva = v

    @property
    def id_cliente(self): return self._id_cliente
    @id_cliente.setter
    def id_cliente(self, v): self._id_cliente = v

    @property
    def fecha(self): return self._fecha
    @fecha.setter
    def fecha(self, v):
        if not isinstance(v, date):
            raise ValueError("La fecha debe ser válida (formato AAAA-MM-DD).")
        self._fecha = v

    @property
    def hora(self): return self._hora
    @hora.setter
    def hora(self, v):
        if not isinstance(v, time):
            raise ValueError("La hora debe ser válida (formato HH:MM).")
        self._hora = v

    @property
    def cant_personas(self): return self._cant_personas
    @cant_personas.setter
    def cant_personas(self, v):
        if not isinstance(v, int) or not 1 <= v <= self.MAX_PERSONAS:
            raise ValueError(f"La cantidad de personas debe ser entre 1 y {self.MAX_PERSONAS}.")
        self._cant_personas = v

    @property
    def estado(self): return self._estado
    @estado.setter
    def estado(self, v):
        if v not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Use uno de: {', '.join(self.ESTADOS_VALIDOS)}.")
        self._estado = v

    @property
    def observaciones(self): return self._observaciones
    @observaciones.setter
    def observaciones(self, v): self._observaciones = (v or "").strip()

    @property
    def fecha_creacion(self): return self._fecha_creacion

    def crear(self):
        return self.id_cliente is not None and self.cant_personas > 0

    def actualizar_estado(self):
        return self.estado in self.ESTADOS_VALIDOS