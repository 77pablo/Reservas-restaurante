"""Clase Restaurant."""


class Restaurant:
    def __init__(self, id_restaurant=None, nombre="", direccion="",
                 telefono="", horario_apertura=None, horario_cierre=None):
        self._id_restaurant = id_restaurant
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._horario_apertura = horario_apertura
        self._horario_cierre = horario_cierre
        self._zonas = []  # Asociacion Restaurant 1 -- * Zona
        self._jornada_abierta = False

    @property
    def id_restaurant(self):
        return self._id_restaurant

    @id_restaurant.setter
    def id_restaurant(self, valor):
        self._id_restaurant = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        self._direccion = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = valor

    @property
    def horario_apertura(self):
        return self._horario_apertura

    @horario_apertura.setter
    def horario_apertura(self, valor):
        self._horario_apertura = valor

    @property
    def horario_cierre(self):
        return self._horario_cierre

    @horario_cierre.setter
    def horario_cierre(self, valor):
        self._horario_cierre = valor

    @property
    def zonas(self):
        return list(self._zonas)

    def agregarZona(self, zona):
        zona.id_restaurant = self._id_restaurant
        self._zonas.append(zona)

    def abrirJornada(self):
        """void."""
        self._jornada_abierta = True
        print(f"[Restaurant] {self._nombre}: jornada iniciada.")

    def cerrarJornada(self):
        """void."""
        self._jornada_abierta = False
        print(f"[Restaurant] {self._nombre}: jornada finalizada.")