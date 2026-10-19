from datos.modelos.orm_models import DisponibilidadORM
from dominio.disponibilidad import Disponibilidad
from datos.repositorio.base_repositorio import BaseRepositorio


class DisponibilidadRepositorio(BaseRepositorio):
    modelo_orm = DisponibilidadORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Disponibilidad(
            id_disponibilidad=registro.id_disponibilidad,
            id_mesa=registro.mesa.id_mesa,
            id_reserva=registro.reserva.id_reserva if registro.reserva else None,
            fecha=registro.fecha,
            hora_inicio=registro.hora_inicio,
            hora_fin=registro.hora_fin,
            estado_franja=registro.estado_franja,
        )

    @classmethod
    def crear(cls, disponibilidad: Disponibilidad):
        registro = cls.modelo_orm.create(
            mesa=disponibilidad.id_mesa,
            reserva=disponibilidad.id_reserva,
            fecha=disponibilidad.fecha,
            hora_inicio=disponibilidad.hora_inicio,
            hora_fin=disponibilidad.hora_fin,
            estado_franja=disponibilidad.estado_franja,
        )
        disponibilidad.id_disponibilidad = registro.id_disponibilidad
        return disponibilidad

    @classmethod
    def buscar_franja_disponible(cls, id_mesa, fecha, hora_inicio, hora_fin):
        registro = (cls.modelo_orm.select()
                    .where((cls.modelo_orm.mesa == id_mesa)
                           & (cls.modelo_orm.fecha == fecha)
                           & (cls.modelo_orm.hora_inicio <= hora_inicio)
                           & (cls.modelo_orm.hora_fin >= hora_fin)
                           & (cls.modelo_orm.estado_franja == "Disponible"))
                    .first())
        return cls._a_dominio(registro)

    @classmethod
    def ocupar_franja(cls, id_disponibilidad, id_reserva):
        filas = (cls.modelo_orm.update(estado_franja="Ocupado", reserva=id_reserva)
                 .where(cls.modelo_orm.id_disponibilidad == id_disponibilidad).execute())
        return filas > 0

    @classmethod
    def liberar_franja(cls, id_reserva):
        filas = (cls.modelo_orm.update(estado_franja="Disponible", reserva=None)
                 .where(cls.modelo_orm.reserva == id_reserva).execute())
        return filas > 0

    @classmethod
    def eliminar(cls, id_disponibilidad):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_disponibilidad == id_disponibilidad
        )
        if registro is None:
            return False
        registro.delete_instance()
        return True