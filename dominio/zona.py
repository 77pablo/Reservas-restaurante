"""Clase Zona."""


class Zona:
    def __init__(self, id_zona=None, id_restaurant=None, nombre_zona="",
                 permite_fumadores=False):
        self._id_zona = id_zona
        self._id_restaurant = id_restaurant
        self._nombre_zona = nombre_zona
        self._permite_fumadores = permite_fumadores
        self._mesas = []  # Asociacion Zona 1 -- * Mesa

    @property
    def id_zona(self):
        return self._id_zona

    @id_zona.setter
    def id_zona(self, valor):
        self._id_zona = valor

    @property
    def id_restaurant(self):
        return self._id_restaurant

    @id_restaurant.setter
    def id_restaurant(self, valor):
        self._id_restaurant = valor

    @property
    def nombre_zona(self):
        return self._nombre_zona

    @nombre_zona.setter
    def nombre_zona(self, valor):
        self._nombre_zona = valor

    @property
    def permite_fumadores(self):
        return self._permite_fumadores

    @permite_fumadores.setter
    def permite_fumadores(self, valor):
        self._permite_fumadores = bool(valor)

    def agregarMesa(self, mesa):
        """void."""
        mesa.id_zona = self._id_zona
        self._mesas.append(mesa)

    def obtenerMesas(self):
        """Retorna List<Mesa>."""
        return list(self._mesas)