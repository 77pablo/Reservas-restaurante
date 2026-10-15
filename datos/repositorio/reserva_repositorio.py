
from datos.repositorio.reserva_repositorio import ReservaRepositorio


class ReservaServicio:
    """
    Capa de negocio para gestionar las reservas del restaurante.
    Coordina las operaciones entre la presentación y el repositorio.
    """

    ESTADOS_VALIDOS = {
        "Pendiente",
        "Confirmada",
        "Cancelada",
        "Completada",
    }

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
        """
        Solicita la creación de una reserva.
        Las validaciones de disponibilidad y persistencia
        corresponden al repositorio.
        """
        if not id_cliente:
            return None

        if not isinstance(cantidad_personas, int):
            return None

        if cantidad_personas < 1:
            return None

        if not fecha or not hora_inicio or not hora_fin:
            return None

        if hora_inicio >= hora_fin:
            return None

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
        """Devuelve todas las reservas."""
        return ReservaRepositorio.obtener_todas()

    @staticmethod
    def obtener_todas_con_horario():
        """Devuelve las reservas con los datos de cliente, horario y mesa."""
        return ReservaRepositorio.obtener_todas_con_horario()

    @staticmethod
    def obtener_por_id(id_reserva):
        """Busca una reserva por su identificador."""
        if not id_reserva:
            return None

        return ReservaRepositorio.obtener_por_id(id_reserva)

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        """
        Solicita el cambio de estado de una reserva.
        El repositorio comprueba las transiciones permitidas
        y actualiza la base de datos.
        """
        if not id_reserva:
            return False

        if nuevo_estado not in ReservaServicio.ESTADOS_VALIDOS:
            return False

        return ReservaRepositorio.cambiar_estado(
            id_reserva,
            nuevo_estado,
        )