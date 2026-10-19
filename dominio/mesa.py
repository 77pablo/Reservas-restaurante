"""Clase Mesa."""


class Mesa:
    def __init__(self, id_mesa=None, id_zona=None, numero_mesa=0,
                 capacidad=0, activa=True):
        self._id_mesa = id_mesa
        self._id_zona = id_zona
        self._numero_mesa = numero_mesa
        self._capacidad = capacidad
        self._activa = activa
        self._disponibilidades = []  # Asociacion Mesa 1 -- * Disponibilidad
        self._reserva_actual = None

    @property
    def id_mesa(self):
        return self._id_mesa

    @id_mesa.setter
    def id_mesa(self, valor):
        self._id_mesa = valor

    @property
    def id_zona(self):
        return self._id_zona

    @id_zona.setter
    def id_zona(self, valor):
        self._id_zona = valor

    @property
    def numero_mesa(self):
        return self._numero_mesa

    @numero_mesa.setter
    def numero_mesa(self, valor):
        self._numero_mesa = valor

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if valor <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")
        self._capacidad = valor

    @property
    def activa(self):
        return self._activa

    @activa.setter
    def activa(self, valor):
        self._activa = bool(valor)

    def asignarReserva(self, reserva):
        """void."""
        self._reserva_actual = reserva
        print(f"[Mesa {self._numero_mesa}] Reserva asignada.")

    def liberar(self):
        """void."""
        self._reserva_actual = None
        print(f"[Mesa {self._numero_mesa}] Liberada.")