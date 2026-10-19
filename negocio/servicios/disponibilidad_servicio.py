"""Reglas de negocio para las disponibilidades."""

from datetime import date, time

from datos.repositorio.disponibilidad_repositorio import (
    DisponibilidadRepositorio,
)
from datos.repositorio.mesa_repositorio import MesaRepositorio


class DisponibilidadServicio:
    """Consulta las franjas disponibles para las mesas."""

    @staticmethod
    def buscar_franja(
        id_mesa,
        fecha,
        hora_inicio,
        hora_fin,
    ):
        """Busca una franja que cubra el horario solicitado."""

        if not isinstance(fecha, date):
            raise ValueError("La fecha no es válida.")

        if not isinstance(hora_inicio, time) or not isinstance(
            hora_fin, time
        ):
            raise ValueError("Las horas deben ser valores de tipo time.")

        if hora_inicio >= hora_fin:
            raise ValueError(
                "La hora de inicio debe ser anterior a la hora de fin."
            )

        mesa = MesaRepositorio.obtener_por_id(id_mesa)

        if mesa is None or not mesa.activa:
            raise ValueError("La mesa no existe o está inactiva.")

        return DisponibilidadRepositorio.buscar_franja_disponible(
            id_mesa=id_mesa,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
