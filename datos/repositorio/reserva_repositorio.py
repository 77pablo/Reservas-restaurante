
from datetime import date, time

from peewee import DoesNotExist

from datos.conexion import database
from datos.modelos.models import (
    Reserva,
    Mesa,
    Disponibilidad,
    Cliente,
)


class ReservaRepositorio:

    ESTADOS_VALIDOS = {
        "Pendiente",
        "Confirmada",
        "Cancelada",
        "Completada",
    }

    TRANSICIONES_PERMITIDAS = {
        "Pendiente": {"Confirmada", "Cancelada"},
        "Confirmada": {"Cancelada", "Completada"},
        "Cancelada": set(),
        "Completada": set(),
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
        try:
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)

            if isinstance(hora_inicio, str):
                hora_inicio = time.fromisoformat(hora_inicio)

            if isinstance(hora_fin, str):
                hora_fin = time.fromisoformat(hora_fin)

            if not isinstance(fecha, date):
                return None

            if not isinstance(hora_inicio, time):
                return None

            if not isinstance(hora_fin, time):
                return None

            if (
                isinstance(cantidad_personas, bool)
                or not isinstance(cantidad_personas, int)
                or cantidad_personas < 1
            ):
                return None

            if fecha < date.today():
                return None

            if hora_inicio >= hora_fin:
                return None

            if id_mesa is not None:
                if (
                    isinstance(id_mesa, bool)
                    or not isinstance(id_mesa, int)
                    or id_mesa < 1
                ):
                    return None

            if not Cliente.select().where(
                Cliente.id_cliente == id_cliente
            ).exists():
                return None

            with database.atomic():
                consulta = (
                    Disponibilidad
                    .select(Disponibilidad, Mesa)
                    .join(
                        Mesa,
                        on=(
                            Disponibilidad.id_mesa
                            == Mesa.id_mesa
                        ),
                    )
                    .where(
                        (Disponibilidad.fecha == fecha)
                        & (
                            Disponibilidad.hora_inicio
                            <= hora_inicio
                        )
                        & (
                            Disponibilidad.hora_fin
                            >= hora_fin
                        )
                        & (
                            Disponibilidad.estado_franja
                            == "Disponible"
                        )
                        & (Mesa.activa == True)
                        & (
                            Mesa.capacidad_comensales
                            >= cantidad_personas
                        )
                    )
                    .order_by(
                        Mesa.capacidad_comensales.asc(),
                        Disponibilidad.id_mesa.asc(),
                    )
                    .for_update()
                )

                if id_mesa is not None:
                    consulta = consulta.where(
                        Disponibilidad.id_mesa == id_mesa
                    )

                franja = consulta.first()

                if franja is None:
                    return None

                reserva = Reserva.create(
                    id_cliente=id_cliente,
                    cantidad_personas=cantidad_personas,
                    estado="Pendiente",
                    observaciones_especiales=observaciones,
                )

                franja.estado_franja = "Reservada"
                franja.id_reserva = reserva.id_reserva
                franja.save()

                return reserva

        except (TypeError, ValueError):
            return None
        except Exception:
            # El registro detallado debe revisarse en los logs
            # de la aplicación si ocurre un error inesperado.
            raise

    @staticmethod
    def obtener_todas():
        return (
            Reserva
            .select()
            .order_by(Reserva.id_reserva.desc())
        )

    @staticmethod
    def obtener_todas_con_horario():
        """
        Devuelve las reservas con fecha, horas y mesa.
        Una reserva puede tener más de una franja asociada;
        por eso se conservan todas las coincidencias.
        """
        resultado = []

        reservas = ReservaRepositorio.obtener_todas()

        for reserva in reservas:
            franjas = list(
                Disponibilidad
                .select()
                .where(
                    Disponibilidad.id_reserva
                    == reserva.id_reserva
                )
                .order_by(
                    Disponibilidad.hora_inicio.asc()
                )
            )

            if not franjas:
                resultado.append({
                    "id_reserva": reserva.id_reserva,
                    "id_cliente": reserva.id_cliente,
                    "cantidad_personas": reserva.cantidad_personas,
                    "estado": reserva.estado,
                    "observaciones": (
                        reserva.observaciones_especiales or ""
                    ),
                    "fecha": None,
                    "hora_inicio": None,
                    "hora_fin": None,
                    "id_mesa": None,
                })
                continue

            for franja in franjas:
                mesa = Mesa.get_or_none(
                    Mesa.id_mesa == franja.id_mesa
                )

                resultado.append({
                    "id_reserva": reserva.id_reserva,
                    "id_cliente": reserva.id_cliente,
                    "cantidad_personas": reserva.cantidad_personas,
                    "estado": reserva.estado,
                    "observaciones": (
                        reserva.observaciones_especiales or ""
                    ),
                    "fecha": franja.fecha,
                    "hora_inicio": franja.hora_inicio,
                    "hora_fin": franja.hora_fin,
                    "id_mesa": (
                        mesa.numero_mesa if mesa else franja.id_mesa
                    ),
                })

        return resultado

    @staticmethod
    def obtener_por_id(id_reserva):
        try:
            return Reserva.get(
                Reserva.id_reserva == id_reserva
            )
        except DoesNotExist:
            return None

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        if nuevo_estado not in ReservaRepositorio.ESTADOS_VALIDOS:
            return False

        with database.atomic():
            reserva = (
                Reserva
                .select()
                .where(Reserva.id_reserva == id_reserva)
                .for_update()
                .first()
            )

            if reserva is None:
                return False

            if nuevo_estado not in (
                ReservaRepositorio.TRANSICIONES_PERMITIDAS[
                    reserva.estado
                ]
            ):
                return False

            reserva.estado = nuevo_estado
            reserva.save()

            if nuevo_estado == "Cancelada":
                (
                    Disponibilidad
                    .update(
                        estado_franja="Disponible",
                        id_reserva=None,
                    )
                    .where(
                        (Disponibilidad.id_reserva == id_reserva)
                        & (
                            Disponibilidad.estado_franja
                            == "Reservada"
                        )
                    )
                    .execute()
                )

            return True
