"""Clase Cliente - hereda de Usuario (reutilizacion de codigo) y
sobrescribe metodos para demostrar polimorfismo."""
from dominio.usuario import Usuario


class Cliente(Usuario):
    def __init__(self, id_usuario=None, nombre_completo="", correo="",
                 telefono="", contrasena="", id_cliente=None,
                 preferencias="", puntos_fidelidad=0):
        super().__init__(id_usuario, nombre_completo, correo, telefono, contrasena)
        self._id_cliente = id_cliente
        self._preferencias = preferencias
        self._puntos_fidelidad = puntos_fidelidad
        self._reservas = []  # Asociacion Cliente 1 -- * Reserva

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        self._id_cliente = valor

    @property
    def preferencias(self):
        return self._preferencias

    @preferencias.setter
    def preferencias(self, valor):
        self._preferencias = valor

    @property
    def puntos_fidelidad(self):
        return self._puntos_fidelidad

    @puntos_fidelidad.setter
    def puntos_fidelidad(self, valor):
        if valor < 0:
            raise ValueError("Los puntos de fidelidad no pueden ser negativos.")
        self._puntos_fidelidad = valor

    @property
    def reservas(self):
        return list(self._reservas)

    def solicitarReserva(self, reserva):
        """void."""
        reserva.id_cliente = self._id_cliente
        self._reservas.append(reserva)
        print(f"[Cliente] {self.nombre_completo} solicito una reserva.")

    def cancelarReserva(self, id_reserva):
        """Retorna boolean."""
        for reserva in self._reservas:
            if reserva.id_reserva == id_reserva:
                return reserva.actualizarEstado("Cancelada")
        return False

    # ---------- Sobrescritura de metodos (polimorfismo) ----------

    def obtener_rol(self):
        return "Cliente"

    def realizar_accion_principal(self):
        return (f"{self.nombre_completo} (Cliente) puede solicitar reservas. "
                f"Tiene {len(self._reservas)} reserva(s) en esta sesion y "
                f"{self._puntos_fidelidad} punto(s) de fidelidad.")

    def cerrarSesion(self):
        """Sobrescribe el metodo de Usuario, extendiendo su comportamiento."""
        super().cerrarSesion()
        print(f"[Cliente] Preferencias guardadas: '{self._preferencias}'.")

    def __str__(self):
        return (f"Cliente(id={self.id_usuario}, nombre='{self.nombre_completo}', "
                f"puntos={self._puntos_fidelidad})")