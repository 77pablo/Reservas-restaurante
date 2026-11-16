from datetime import time, timedelta
from repositorios.base_repositorio import BaseRepositorio
from modelos.reserva import Reserva


class ReservaRepositorio(BaseRepositorio):

    @staticmethod
    def _a_time(valor):
        """MySQL devuelve TIME como timedelta; lo convertimos a datetime.time."""
        if isinstance(valor, timedelta):
            segundos = int(valor.total_seconds())
            return time(segundos // 3600, (segundos % 3600) // 60, segundos % 60)
        return valor

    def _desde_fila(self, fila):
        return Reserva(
            id_cliente=fila["id_cliente"],
            fecha=fila["fecha"],
            hora=self._a_time(fila["hora"]),
            cant_personas=fila["cant_personas"],
            estado=fila["estado"],
            observaciones=fila["observaciones"],
            fecha_creacion=fila["fecha_creacion"],
            id_reserva=fila["id_reserva"],
        )

    def crear(self, reserva: Reserva):
        if not reserva.crear():
            return None
        sql = """
            INSERT INTO reserva (id_cliente, fecha, hora, cant_personas, estado, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        parametros = (
            reserva.id_cliente, reserva.fecha, reserva.hora,
            reserva.cant_personas, reserva.estado, reserva.observaciones,
        )
        nuevo_id = self._ejecutar_consulta(sql, parametros, obtener_id=True)
        if nuevo_id:
            reserva.id_reserva = nuevo_id
        return nuevo_id

    def listar_por_cliente(self, id_cliente):
        sql = "SELECT * FROM reserva WHERE id_cliente = %s ORDER BY fecha, hora"
        filas = self._consultar(sql, (id_cliente,))
        if filas is None:
            return None  # error SQL, ya impreso en consola
        return [self._desde_fila(fila) for fila in filas]

    def buscar_por_id(self, id_reserva):
        sql = "SELECT * FROM reserva WHERE id_reserva = %s"
        fila = self._consultar(sql, (id_reserva,), uno=True)
        return self._desde_fila(fila) if fila else None

    def actualizar(self, reserva: Reserva):
        # Se verifica primero que exista, porque rowcount es 0 también cuando no hubo cambios
        if self.buscar_por_id(reserva.id_reserva) is None:
            return False
        sql = """
            UPDATE reserva
            SET fecha = %s, hora = %s, cant_personas = %s, estado = %s, observaciones = %s
            WHERE id_reserva = %s
        """
        parametros = (
            reserva.fecha, reserva.hora, reserva.cant_personas,
            reserva.estado, reserva.observaciones, reserva.id_reserva,
        )
        return self._ejecutar_consulta(sql, parametros) is not None

    def eliminar(self, id_reserva):
        if self.buscar_por_id(id_reserva) is None:
            return False
        filas = self._ejecutar_consulta("DELETE FROM reserva WHERE id_reserva = %s", (id_reserva,))
        return bool(filas)