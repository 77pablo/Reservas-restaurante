from modelos.usuario import Usuario
from validaciones import validar_rut, validar_genero


class Cliente(Usuario):
    def __init__(
        self,
        nombre_completo,
        correo,
        telefono,
        rut=None,
        genero=None,
        contrasena=None,
        preferencias="",
        puntos_fidelidad=0,
        id_usuario=None,
        id_cliente=None,
    ):
        super().__init__(
            nombre_completo,
            correo,
            telefono,
            contrasena=contrasena,
            id_usuario=id_usuario,
        )
        self._rut = None
        self._genero = None
        self._id_cliente = id_cliente

        if rut is not None:
            self.rut = rut
        if genero is not None:
            self.genero = genero

        self.preferencias = preferencias
        self.puntos_fidelidad = puntos_fidelidad

    @property
    def rut(self):
        return self._rut

    @rut.setter
    def rut(self, valor):
        if valor is None:
            self._rut = None
            return
        rut_limpio, mensaje = validar_rut(valor)
        if mensaje != "RUT Válido":
            raise ValueError(mensaje)
        self._rut = rut_limpio

    @property
    def genero(self):
        return self._genero

    @genero.setter
    def genero(self, valor):
        if valor is None:
            self._genero = None
            return
        genero_limpio, mensaje = validar_genero(valor)
        if mensaje != "Género Válido":
            raise ValueError(mensaje)
        self._genero = genero_limpio

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, v):
        self._id_cliente = v

    @property
    def preferencias(self):
        return self._preferencias

    @preferencias.setter
    def preferencias(self, v):
        self._preferencias = v or ""

    @property
    def puntos_fidelidad(self):
        return self._puntos_fidelidad

    @puntos_fidelidad.setter
    def puntos_fidelidad(self, v):
        self._puntos_fidelidad = v

    def solicitar_reserva(self, reserva):
        reserva.id_cliente = self.id_cliente
        return reserva.crear()

    def cancelar_reserva(self, reserva):
        if reserva.id_cliente != self.id_cliente:
            return False
        reserva.estado = "Cancelada"
        return reserva.actualizar_estado()