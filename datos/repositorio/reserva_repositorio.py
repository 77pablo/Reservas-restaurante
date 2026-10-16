
from datetime import date, datetime, time

from peewee import DoesNotExist, fn

from datos.conexion import database
from datos.modelos.models import (
    Reserva,
    Mesa,
    Disponibilidad,
    ClienteDB,
    UsuarioDB,
)


class ReservaRepositorio:
    """Gestiona las operaciones de reservas en MySQL."""

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
    def _convertir_fecha(valor):
        """Convierte una fecha ISO o datetime en date."""
        if isinstance(valor, datetime):
            return valor.date()

        if isinstance(valor, date):
            return valor

        if isinstance(valor, str):
            return date.fromisoformat(valor.strip())

        raise ValueError("La fecha no es válida.")

    @staticmethod
    def _convertir_hora(valor):
        """Convierte una hora ISO en time."""
        if isinstance(valor, datetime):
            valor = valor.time()
        elif isinstance(valor, str):
            valor = time.fromisoformat(valor.strip())

        if not isinstance(valor, time):
            raise ValueError("La hora no es válida.")

        if valor.tzinfo is not None:
            raise ValueError("La hora no debe incluir zona horaria.")

        return valor

    @staticmethod
    def _convertir_cantidad(valor):
        """Convierte la cantidad recibida desde un formulario."""
        if isinstance(valor, bool):
            raise ValueError("La cantidad de personas no es válida.")

        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                raise ValueError("Indica la cantidad de personas.")
            valor = int(valor)

        if not isinstance(valor, int) or valor < 1:
            raise ValueError("La cantidad debe ser un entero positivo.")

        return valor

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
        Crea una reserva y bloquea una franja que cubra
        completamente el horario solicitado.

        Devuelve la reserva creada o None si no hay una
        franja compatible o los datos no son válidos.
        """
        try:
            fecha = ReservaRepositorio._convertir_fecha(fecha)
            hora_inicio = ReservaRepositorio._convertir_hora(
                hora_inicio
            )
            hora_fin = ReservaRepositorio._convertir_hora(hora_fin)
            cantidad_personas = (
                ReservaRepositorio._convertir_cantidad(
                    cantidad_personas
                )
            )

            if hora_inicio >= hora_fin:
                return None

            if fecha < date.today():
                return None

            ahora = datetime.now()
            if fecha == ahora.date() and hora_inicio <= ahora.time():
                return None

            cliente = ClienteDB.get_or_none(
                ClienteDB.id_cliente == id_cliente
            )
            if cliente is None:
                return None

            if id_mesa is not None:
                if isinstance(id_mesa, str):
                    id_mesa = id_mesa.strip()
                    if not id_mesa:
                        id_mesa = None
                    else:
                        id_mesa = int(id_mesa)

            with database.atomic():
                consulta = (
                    Disponibilidad.select(Disponibilidad, Mesa)
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
                            fn.LOWER(fn.TRIM(
                                Disponibilidad.estado_franja
                            )) == "disponible"
                        )
                        & (Mesa.activa == True)
                        & (
                            Mesa.capacidad_comensales
                            >= cantidad_personas
                        )
                    )
                    .order_by(
                        Mesa.capacidad_comensales.asc(),
                        Mesa.id_mesa.asc(),
                    )
                    .for_update()
                )

                if id_mesa is not None:
                    consulta = consulta.where(
                        Mesa.id_mesa == id_mesa
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
                franja.save(
                    only=[
                        Disponibilidad.estado_franja,
                        Disponibilidad.id_reserva,
                    ]
                )

                return reserva

        except (TypeError, ValueError):
            return None

    @staticmethod
    def obtener_todas():
        """Obtiene las reservas de la más reciente a la más antigua."""
        return list(
            Reserva.select().order_by(
                Reserva.id_reserva.desc()
            )
        )

    @staticmethod
    def obtener_todas_con_horario():
        """Obtiene reservas con cliente, horario y número de mesa."""
        resultado = []

        for reserva in ReservaRepositorio.obtener_todas():
            cliente = ClienteDB.get_or_none(
                ClienteDB.id_cliente == reserva.id_cliente
            )

            nombre_cliente = "Cliente desconocido"
            correo_cliente = ""

            if cliente is not None:
                usuario = UsuarioDB.get_or_none(
                    UsuarioDB.id_usuario == cliente.id_usuario
                )

                if usuario is not None:
                    nombre_cliente = usuario.nombre_completo
                    correo_cliente = usuario.correo_electronico

            franjas = list(
                Disponibilidad.select().where(
                    Disponibilidad.id_reserva
                    == reserva.id_reserva
                )
            )

            datos_reserva = {
                "id_reserva": reserva.id_reserva,
                "nombre_cliente": nombre_cliente,
                "correo_cliente": correo_cliente,
                "cantidad_personas": reserva.cantidad_personas,
                "estado": reserva.estado,
                "observaciones": reserva.observaciones_especiales,
            }

            if not franjas:
                resultado.append({
                    **datos_reserva,
                    "fecha": None,
                    "hora_inicio": None,
                    "hora_fin": None,
                    "numero_mesa": "",
                })
                continue

            for franja in franjas:
                mesa = Mesa.get_or_none(
                    Mesa.id_mesa == franja.id_mesa
                )

                resultado.append({
                    **datos_reserva,
                    "fecha": franja.fecha,
                    "hora_inicio": franja.hora_inicio,
                    "hora_fin": franja.hora_fin,
                    "numero_mesa": (
                        mesa.numero_mesa if mesa is not None else ""
                    ),
                })

        return resultado

    @staticmethod
    def obtener_por_id(id_reserva):
        """Busca una reserva por su identificador."""
        try:
            return Reserva.get(
                Reserva.id_reserva == id_reserva
            )
        except DoesNotExist:
            return None

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        """
        Cambia el estado respetando las transiciones permitidas.
        Si se cancela, libera la franja vinculada a la reserva.
        """
        if nuevo_estado not in ReservaRepositorio.ESTADOS_VALIDOS:
            return False

        try:
            with database.atomic():
                reserva = (
                    Reserva.select()
                    .where(Reserva.id_reserva == id_reserva)
                    .for_update()
                    .get()
                )

                estado_actual = reserva.estado
                permitidos = (
                    ReservaRepositorio.TRANSICIONES_PERMITIDAS.get(
                        estado_actual, set()
                    )
                )

                if nuevo_estado not in permitidos:
                    return False

                reserva.estado = nuevo_estado
                reserva.save(only=[Reserva.estado])

                if nuevo_estado == "Cancelada":
                    (
                        Disponibilidad.update(
                            estado_franja="Disponible",
                            id_reserva=None,
                        )
                        .where(
                            Disponibilidad.id_reserva
                            == reserva.id_reserva
                        )
                        .execute()
                    )

                return True

        except DoesNotExist:
            return False
