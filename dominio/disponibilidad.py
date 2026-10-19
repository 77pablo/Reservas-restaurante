"""Clase Disponibilidad."""


class Disponibilidad:
    def __init__(self, id_disponibilidad=None, id_mesa=None, id_reserva=None,
                 fecha=None, hora_inicio=None, hora_fin=None,
                 estado_franja="Disponible"):
        self._id_disponibilidad = id_disponibilidad
        self._id_mesa = id_mesa
        self._id_reserva = id_reserva
        self._fecha = fecha
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        self._estado_franja = estado_franja

    @property
    def id_disponibilidad(self):
        return self._id_disponibilidad

    @id_disponibilidad.setter
    def id_disponibilidad(self, valor):
        self._id_disponibilidad = valor

    @property
    def id_mesa(self):
        return self._id_mesa

    @id_mesa.setter
    def id_mesa(self, valor):
        self._id_mesa = valor

    @property
    def id_reserva(self):
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        self._id_reserva = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        self._fecha = valor

    @property
    def hora_inicio(self):
        return self._hora_inicio

    @hora_inicio.setter
    def hora_inicio(self, valor):
        self._hora_inicio = valor

    @property
    def hora_fin(self):
        return self._hora_fin

    @hora_fin.setter
    def hora_fin(self, valor):
        self._hora_fin = valor

    @property
    def estado_franja(self):
        return self._estado_franja

    def verificarEstado(self):
        """Retorna boolean."""
        return self._estado_franja.strip().lower() == "disponible"

    def bloquearHorario(self):
        """void."""
        self._estado_franja = "Bloqueado"