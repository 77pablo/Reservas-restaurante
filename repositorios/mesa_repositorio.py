from datos.modelos.orm_models import MesaORM
from dominio.mesa import Mesa
from repositorios.base_repositorio import BaseRepositorio


class MesaRepositorio(BaseRepositorio):
    modelo_orm = MesaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Mesa(
            id_mesa=registro.id_mesa,
            id_zona=registro.zona.id_zona,
            numero_mesa=registro.numero_mesa,
            capacidad=registro.capacidad,
            activa=registro.activa,
        )

    @classmethod
    def crear(cls, mesa: Mesa):
        registro = cls.modelo_orm.create(
            zona=mesa.id_zona,
            numero_mesa=mesa.numero_mesa,
            capacidad=mesa.capacidad,
            activa=mesa.activa,
        )
        mesa.id_mesa = registro.id_mesa
        return mesa

    @classmethod
    def obtener_por_id(cls, id_mesa):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_mesa == id_mesa)
        return cls._a_dominio(registro)

    @classmethod
    def listar_por_zona(cls, id_zona):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.zona == id_zona)
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def listar_disponibles(cls, capacidad_minima):
        consulta = cls.modelo_orm.select().where(
            (cls.modelo_orm.activa == True)
            & (cls.modelo_orm.capacidad >= capacidad_minima)
        )
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def actualizar(cls, mesa: Mesa):
        if mesa.id_mesa is None:
            return False
        filas = (
            cls.modelo_orm.update(
                numero_mesa=mesa.numero_mesa,
                capacidad=mesa.capacidad,
                activa=mesa.activa,
            )
            .where(cls.modelo_orm.id_mesa == mesa.id_mesa)
            .execute()
        )
        return filas > 0

    @classmethod
    def eliminar(cls, id_mesa):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_mesa == id_mesa)
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True