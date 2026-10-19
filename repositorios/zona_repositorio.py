from datos.modelos.orm_models import ZonaORM
from dominio.zona import Zona
from repositorios.base_repositorio import BaseRepositorio


class ZonaRepositorio(BaseRepositorio):
    modelo_orm = ZonaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Zona(
            id_zona=registro.id_zona,
            id_restaurant=registro.restaurant.id_restaurant,
            nombre_zona=registro.nombre_zona,
            permite_fumadores=registro.permite_fumadores,
        )

    @classmethod
    def crear(cls, zona: Zona):
        registro = cls.modelo_orm.create(
            restaurant=zona.id_restaurant,
            nombre_zona=zona.nombre_zona,
            permite_fumadores=zona.permite_fumadores,
        )
        zona.id_zona = registro.id_zona
        return zona

    @classmethod
    def obtener_por_id(cls, id_zona):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_zona == id_zona)
        return cls._a_dominio(registro)

    @classmethod
    def listar_por_restaurant(cls, id_restaurant):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.restaurant == id_restaurant)
        return [cls._a_dominio(r) for r in consulta]