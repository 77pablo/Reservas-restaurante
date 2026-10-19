"""
Repositorio base: centraliza operaciones CRUD comunes para
evitar duplicar codigo en cada repositorio especifico.
"""


class BaseRepositorio:
    modelo_orm = None  # Sobrescrito por cada subclase

    @classmethod
    def listar_todos(cls):
        return list(cls.modelo_orm.select())

    @classmethod
    def eliminar(cls, id_valor):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm._meta.primary_key == id_valor
        )
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True

    @classmethod
    def contar(cls):
        return cls.modelo_orm.select().count()