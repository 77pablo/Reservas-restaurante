from datetime import date, time, datetime

from peewee import DoesNotExist

from datos.conexion import database
from datos.modelos.models import Reserva, Mesa, Disponibilidad, Cliente


class ReservaRepositorio:

    @staticmethod
    def crear_reserva(
        id_cliente,
        cantidad_personas,
        fecha,
        hora_inicio,
        hora_fin,
        observaciones=None,
        id_mesa=None
    ):
        """Crea una reserva y ocupa una franja de una mesa disponible."""
        try:
            fecha = date.fromisoformat(fecha) if isinstance(fecha, str) else fecha
            hora_inicio = time.fromisoformat(hora_inicio) if isinstance(hora_inicio, str) else hora_inicio
            hora_fin = time.fromisoformat(hora_fin) if isinstance(hora_fin, str) else hora_fin

            if cantidad_personas < 1:
              print("Error: debe haber al menos una persona.")
              return None

            if hora_inicio >= hora_fin:
               print("Error: la hora de inicio debe ser anterior a la hora de fin.")
               return None

            if fecha < date.today():
                print("Error: no se permiten reservas en fechas pasadas.")
                return None
            
            if not Cliente.select().where(Cliente.id_cliente == id_cliente).exists():
                print(f"Error: no existe el cliente con ID {id_cliente}.")
                return None

            with database.atomic():
                franjas = (
                    Disponibilidad
                    .select()
                    .join(Mesa, on=(Disponibilidad.id_mesa == Mesa.id_mesa))
                    .where(
                        (Disponibilidad.fecha == fecha)
                        & (Disponibilidad.hora_inicio <= hora_inicio)
                        & (Disponibilidad.hora_fin >= hora_fin)
                        & (Disponibilidad.estado_franja == "Disponible")
                        & (Mesa.activa == True)
                        & (Mesa.capacidad_comensales >= cantidad_personas)
                    )
                    .order_by(Mesa.capacidad_comensales)
                    .for_update()
                )

                # Si se especificó una mesa, solo buscamos esa mesa.
                if id_mesa is not None:
                    franjas = franjas.where(
                        Disponibilidad.id_mesa == id_mesa
                    )

                franja = franjas.first()

                if franja is None:
                    print(
                        "No hay una mesa disponible para ese horario "
                        "y cantidad de personas."
                    )
                    return None

                reserva = Reserva.create(
                    id_cliente=id_cliente,
                    cantidad_personas=cantidad_personas,
                    estado="Pendiente",
                    observaciones_especiales=observaciones
                )

                franja.estado_franja = "Reservada"
                franja.id_reserva = reserva.id_reserva
                franja.save()

                return reserva

        except Exception as e:
            print(f"Error al crear la reserva: {e}")
            return None

    @staticmethod
    def obtener_todas():
        """Retorna todas las reservas registradas."""
        return Reserva.select()

    @staticmethod
    def cambiar_estado(id_reserva, nuevo_estado):
        """Actualiza el estado de una reserva."""
        # Aquí va el código de la función

        transiciones_validas = {
            "Pendiente": {"Confirmada", "Cancelada"},
            "Confirmada": {"Cancelada", "Completada"},
            "Cancelada": set(),
            "Completada": set()
        }

        if nuevo_estado not in {
            "Pendiente", "Confirmada", "Cancelada", "Completada"
        }:
            print("Error: estado de reserva no válido.")
            return False

        try:
            with database.atomic():
                reserva = Reserva.get_by_id(id_reserva)

                if nuevo_estado == reserva.estado:
                    return True

                estados_permitidos = transiciones_validas.get(
                    reserva.estado, set()
                )

                if nuevo_estado not in estados_permitidos:
                    print(
                        f"Transición no permitida: "
                        f"{reserva.estado} -> {nuevo_estado}"
                    )
                    return False

                if nuevo_estado == "Cancelada":
                    franjas = Disponibilidad.select().where(
                        Disponibilidad.id_reserva == id_reserva
                    )

                    for franja in franjas:
                        franja.estado_franja = "Disponible"
                        franja.id_reserva = None
                        franja.save()

                reserva.estado = nuevo_estado
                reserva.save()

                return True

        except DoesNotExist:
            return False

        except Exception as e:
            print(f"Error al cambiar el estado: {e}")
            return False