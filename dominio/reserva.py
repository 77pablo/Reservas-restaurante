"""Clase Reserva."""
from datetime import datetime


class Reserva:
    ESTADOS_VALIDOS = {"Pendiente", "Confirmada", "Cancelada", "Completada"}
    TRANSICIONES = {
        "Pendiente": {"Confirmada", "Cancelada"},
        "Confirmada": {"Completada", "Cancelada"},
        "Cancelada": set(),
        "Completada": set(),
    }

    def __init__(self, id_reserva=None, id_cliente=None, fecha_creacion=None,
                 cant_personas=1, estado="Pendiente", observaciones=""):
        self._id_reserva = id_reserva
        self._id_cliente = id_cliente
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._cant_personas = cant_personas
        self._estado = estado
        self._observaciones = observaciones
        self._disponibilidades = []  # Asociacion Reserva 1 -- 1..* Disponibilidad

    @property
    def id_reserva(self):
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        self._id_reserva = valor

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        self._id_cliente = valor

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @property
    def cant_personas(self):
        return self._cant_personas

    @cant_personas.setter
    def cant_personas(self, valor):
        if valor < 1:
            raise ValueError("La cantidad de personas debe ser al menos 1.")
        self._cant_personas = valor

    @property
    def estado(self):
        return self._estado

    @property
    def observaciones(self):
        return self._observaciones

    @observaciones.setter
    def observaciones(self, valor):
        self._observaciones = valor

    def crear(self):
        """Valida datos minimos. Retorna boolean."""
        if self._id_cliente is None:
            return False
        if self._cant_personas < 1:
            return False
        self._estado = "Pendiente"
        return True

    def actualizarEstado(self, nuevo_estado):
        """Retorna boolean respetando transiciones validas."""
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False
        if nuevo_estado not in self.TRANSICIONES.get(self._estado, set()):
            return False
        self._estado = nuevo_estado
        return True

    def agregarDisponibilidad(self, disponibilidad):
        disponibilidad.id_reserva = self._id_reserva
        self._disponibilidades.append(disponibilidad)