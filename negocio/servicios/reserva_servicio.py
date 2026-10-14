
from datos.repositorio.reserva_repositorio import (
    ReservaRepositorio,
)


class ReservaServicio:

    @staticmethod
    def crear_reserva(
        id_cliente,
        cantidad_personas,
        fecha,
        hora_inicio,
        hora_fin,
        observaciones=None,
        id_mesa=None,
    ):
        return ReservaRepositorio.crear_reserva(
            id_cliente=id_cliente,
            cantidad_personas=cantidad_personas,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            observaciones=observaciones,
            id_mesa=id_mesa,
        )

    @staticmethod
    def obtener_todas():
        return ReservaRepositorio.obtener_todas()

    @staticmethod
    def obtener_todas_con_horario():
        return (
            ReservaRepositorio.obtener_todas_con_horario()
        )

    @staticmethod
    def obtener_por_id(id_reserva):
        return ReservaRepositorio.obtener_por_id(id_reserva)

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        return ReservaRepositorio.cambiar_estado(
            id_reserva,
            nuevo_estado,
        )
