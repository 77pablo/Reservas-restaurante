
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
    """Gestiona las reservas y la disponibilidad de las mesas."""

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

    # ---------------------------------------------------------
    # CONVERSIONES Y VALIDACIONES
    # ---------------------------------------------------------

    @staticmethod
    def _convertir_fecha(valor):
        """Convierte una fecha a date."""
        if isinstance(valor, datetime):
            return valor.date()

        if isinstance(valor, date):
            return valor

        if isinstance(valor, str):
            return date.fromisoformat(valor.strip())

        raise ValueError("La fecha no es válida.")



    @staticmethod
    def _convertir_hora(valor):
        """Convierte una hora a time y rechaza zonas horarias."""

        if isinstance(valor, datetime):
            if valor.tzinfo is not None:
                raise ValueError(
                    "La hora no debe incluir una zona horaria."
                )

            return valor.time()

        if isinstance(valor, time):
            if valor.tzinfo is not None:
                raise ValueError(
                    "La hora no debe incluir una zona horaria."
                )

            return valor

        if isinstance(valor, str):
            texto = valor.strip()

            for formato in ("%H:%M", "%H:%M:%S"):
                try:
                    return datetime.strptime(texto, formato).time()
                except ValueError:
                    continue

        raise ValueError("La hora no es válida.")



    @staticmethod
    def _convertir_cantidad(valor):
        """Convierte y valida la cantidad de personas."""
        if isinstance(valor, bool):
            raise ValueError("La cantidad de personas no es válida.")

        cantidad = int(valor)

        if cantidad < 1:
            raise ValueError(
                "La reserva debe tener al menos una persona."
            )

        return cantidad

    # ---------------------------------------------------------
    # CREAR RESERVA
    # ---------------------------------------------------------

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
        Crea una reserva y marca la franja elegida como reservada.

        Conserva fecha, horario y número de mesa directamente en
        la reserva, para que sigan disponibles después de cancelarla.
        """

        try:
            fecha = ReservaRepositorio._convertir_fecha(fecha)
            hora_inicio = ReservaRepositorio._convertir_hora(
                hora_inicio
            )
            hora_fin = ReservaRepositorio._convertir_hora(
                hora_fin
            )
            cantidad_personas = (
                ReservaRepositorio._convertir_cantidad(
                    cantidad_personas
                )
            )

            if hora_inicio >= hora_fin:
                return None

            hoy = date.today()

            if fecha < hoy:
                return None

            if fecha == hoy and hora_inicio <= datetime.now().time():
                return None

            if id_cliente is None:
                return None

            cliente = ClienteDB.get_or_none(
                ClienteDB.id_cliente == id_cliente
            )

            if cliente is None:
                return None

            if id_mesa not in (None, ""):
                id_mesa = int(id_mesa)
            else:
                id_mesa = None

            with database.atomic():
                consulta = (
                    Disponibilidad
                    .select(Disponibilidad, Mesa)
                    .join(Mesa)
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
                            fn.LOWER(
                                fn.TRIM(
                                    Disponibilidad.estado_franja
                                )
                            )
                            == "disponible"
                        )
                        & (Mesa.activa == True)
                        & (
                            Mesa.capacidad_comensales
                            >= cantidad_personas
                        )
                    )
                    .order_by(
                        Mesa.capacidad_comensales.asc(),
                        Disponibilidad.id_disponibilidad.asc(),
                    )
                    .for_update()
                )

                if id_mesa is not None:
                    consulta = consulta.where(
                        Disponibilidad.mesa == id_mesa
                    )

                franja = consulta.get_or_none()

                if franja is None:
                    return None

                # Guardar los datos originales en la reserva.
                reserva = Reserva.create(
                    cliente=cliente,
                    cantidad_personas=cantidad_personas,
                    estado="Pendiente",
                    observaciones_especiales=observaciones,
                    fecha_reserva=fecha,
                    hora_inicio_reserva=hora_inicio,
                    hora_fin_reserva=hora_fin,
                    numero_mesa_reserva=(
                        franja.mesa.numero_mesa
                    ),
                )

                # Vincular la disponibilidad con la reserva.
                franja.estado_franja = "Reservada"
                franja.reserva = reserva
                franja.save(
                    only=[
                        Disponibilidad.estado_franja,
                        Disponibilidad.reserva,
                    ]
                )

                return reserva

        except (TypeError, ValueError, OverflowError):
            return None

    # ---------------------------------------------------------
    # OBTENER TODAS LAS RESERVAS
    # ---------------------------------------------------------

    @staticmethod
    def obtener_todas():
        """Devuelve todas las reservas, de la más reciente a la antigua."""
        return list(
            Reserva.select().order_by(
                Reserva.id_reserva.desc()
            )
        )

    # ---------------------------------------------------------
    # OBTENER RESERVAS CON DATOS PARA LA ADMINISTRACION
    # ---------------------------------------------------------

    @staticmethod
    def obtener_todas_con_horario():
        """
        Devuelve las reservas con cliente, fecha, horario y mesa.

        Utiliza primero los datos guardados en Reserva. Para
        registros antiguos sin esos datos, intenta recuperarlos
        desde la disponibilidad vinculada.
        """

        resultado = []

        reservas = (
            Reserva
            .select(Reserva, ClienteDB, UsuarioDB)
            .join(ClienteDB)
            .join(UsuarioDB)
            .order_by(Reserva.id_reserva.desc())
        )

        for reserva in reservas:
            cliente = reserva.cliente
            usuario = cliente.usuario

            fecha = reserva.fecha_reserva
            hora_inicio = reserva.hora_inicio_reserva
            hora_fin = reserva.hora_fin_reserva
            numero_mesa = reserva.numero_mesa_reserva

            # Compatibilidad con reservas antiguas cuyos campos
            # originales todavía estén vacíos.
            if (
                fecha is None
                or hora_inicio is None
                or hora_fin is None
                or numero_mesa is None
            ):
                franja = (
                    Disponibilidad
                    .select(Disponibilidad, Mesa)
                    .join(Mesa)
                    .where(
                        Disponibilidad.reserva
                        == reserva.id_reserva
                    )
                    .first()
                )

                if franja is not None:
                    fecha = fecha or franja.fecha
                    hora_inicio = (
                        hora_inicio or franja.hora_inicio
                    )
                    hora_fin = hora_fin or franja.hora_fin
                    numero_mesa = (
                        numero_mesa
                        if numero_mesa is not None
                        else franja.mesa.numero_mesa
                    )

            resultado.append(
                {
                    "id_reserva": reserva.id_reserva,
                    "id_cliente": cliente.id_cliente,
                    "nombre_cliente": usuario.nombre_completo,
                    "correo": usuario.correo_electronico,
                    "telefono": usuario.telefono,
                    "cantidad_personas": (
                        reserva.cantidad_personas
                    ),
                    "estado": reserva.estado,
                    "observaciones": (
                        reserva.observaciones_especiales
                    ),
                    "fecha": fecha,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "mesa": (
                        numero_mesa
                        if numero_mesa is not None
                        else ""
                    ),
                    "fecha_creacion": reserva.fecha_creacion,
                }
            )

        return resultado

    # ---------------------------------------------------------
    # OBTENER UNA RESERVA POR ID
    # ---------------------------------------------------------

    @staticmethod
    def obtener_por_id(id_reserva):
        """Devuelve una reserva o None si no existe."""
        try:
            return Reserva.get(
                Reserva.id_reserva == id_reserva
            )
        except (DoesNotExist, TypeError, ValueError):
            return None

    # ---------------------------------------------------------
    # CAMBIAR ESTADO Y LIBERAR DISPONIBILIDAD
    # ---------------------------------------------------------

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        """
        Cambia el estado si la transición está permitida.

        Al cancelar, libera las franjas vinculadas sin borrar
        la fecha, horario ni mesa guardados en Reserva.
        """

        if nuevo_estado not in ReservaRepositorio.ESTADOS_VALIDOS:
            return False

        try:
            with database.atomic():
                reserva = (
                    Reserva
                    .select()
                    .where(
                        Reserva.id_reserva == id_reserva
                    )
                    .for_update()
                    .get_or_none()
                )

                if reserva is None:
                    return False

                estado_actual = reserva.estado

                permitidos = (
                    ReservaRepositorio
                    .TRANSICIONES_PERMITIDAS
                    .get(estado_actual, set())
                )

                if nuevo_estado not in permitidos:
                    return False

                reserva.estado = nuevo_estado
                reserva.save(only=[Reserva.estado])

                if nuevo_estado == "Cancelada":
                    (
                        Disponibilidad
                        .update(
                            estado_franja="Disponible",
                            reserva=None,
                        )
                        .where(
                            Disponibilidad.reserva
                            == reserva.id_reserva
                        )
                        .execute()
                    )

                return True

        except (DoesNotExist, TypeError, ValueError):
            return False
