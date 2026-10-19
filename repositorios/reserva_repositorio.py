from datos.modelos.orm_models import ReservaORM
from dominio.reserva import Reserva
from repositorios.base_repositorio import BaseRepositorio
from repositorios.disponibilidad_repositorio import DisponibilidadRepositorio


class ReservaRepositorio(BaseRepositorio):
    modelo_orm = ReservaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Reserva(
            id_reserva=registro.id_reserva,
            id_cliente=registro.cliente.id_cliente,
            fecha_creacion=registro.fecha_creacion,
            cant_personas=registro.cant_personas,
            estado=registro.estado,
            observaciones=registro.observaciones,
        )

    @classmethod
    def crear(cls, reserva: Reserva):
        if not reserva.crear():
            return None

        registro = cls.modelo_orm.create(
            cliente=reserva.id_cliente,
            cant_personas=reserva.cant_personas,
            estado=reserva.estado,
            observaciones=reserva.observaciones,
        )
        reserva.id_reserva = registro.id_reserva
        return reserva

    @classmethod
    def obtener_por_id(cls, id_reserva):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_reserva == id_reserva)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todas(cls):
        consulta = cls.modelo_orm.select().order_by(cls.modelo_orm.id_reserva.desc())
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.cliente == id_cliente)
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def cambiar_estado(cls, id_reserva, nuevo_estado):
        reserva = cls.obtener_por_id(id_reserva)
        if reserva is None:
            return False
        if not reserva.actualizarEstado(nuevo_estado):
            return False

        filas = (cls.modelo_orm.update(estado=nuevo_estado)
                 .where(cls.modelo_orm.id_reserva == id_reserva).execute())

        if nuevo_estado == "Cancelada":
            DisponibilidadRepositorio.liberar_franja(id_reserva)

        return filas > 0

    @classmethod
    def actualizar_datos(cls, id_reserva, cant_personas=None, observaciones=None):
        """Actualiza campos editables de la reserva (no su estado)."""
        campos = {}
        if cant_personas is not None:
            if cant_personas < 1:
                return False
            campos["cant_personas"] = cant_personas
        if observaciones is not None:
            campos["observaciones"] = observaciones

        if not campos:
            return False

        filas = (
            cls.modelo_orm.update(**campos)
            .where(cls.modelo_orm.id_reserva == id_reserva)
            .execute()
        )
        return filas > 0

    @classmethod
    def eliminar(cls, id_reserva):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_reserva == id_reserva)
        if registro is None:
            return False
        DisponibilidadRepositorio.liberar_franja(id_reserva)
        registro.delete_instance()
        return True