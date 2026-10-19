from datos.modelos.orm_models import RestaurantORM
from dominio.restaurant import Restaurant
from repositorios.base_repositorio import BaseRepositorio


class RestaurantRepositorio(BaseRepositorio):
    modelo_orm = RestaurantORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Restaurant(
            id_restaurant=registro.id_restaurant,
            nombre=registro.nombre,
            direccion=registro.direccion,
            telefono=registro.telefono,
            horario_apertura=registro.horario_apertura,
            horario_cierre=registro.horario_cierre,
        )

    @classmethod
    def crear(cls, restaurant: Restaurant):
        registro = cls.modelo_orm.create(
            nombre=restaurant.nombre,
            direccion=restaurant.direccion,
            telefono=restaurant.telefono,
            horario_apertura=restaurant.horario_apertura,
            horario_cierre=restaurant.horario_cierre,
        )
        restaurant.id_restaurant = registro.id_restaurant
        return restaurant

    @classmethod
    def obtener_por_id(cls, id_restaurant):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_restaurant == id_restaurant
        )
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]

    @classmethod
    def actualizar(cls, restaurant: Restaurant):
        if restaurant.id_restaurant is None:
            return False
        filas = (
            cls.modelo_orm.update(
                nombre=restaurant.nombre,
                direccion=restaurant.direccion,
                telefono=restaurant.telefono,
                horario_apertura=restaurant.horario_apertura,
                horario_cierre=restaurant.horario_cierre,
            )
            .where(cls.modelo_orm.id_restaurant == restaurant.id_restaurant)
            .execute()
        )
        return filas > 0

    @classmethod
    def eliminar(cls, id_restaurant):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_restaurant == id_restaurant
        )
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True