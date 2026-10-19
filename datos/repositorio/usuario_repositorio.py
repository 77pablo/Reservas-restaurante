from datos.modelos.orm_models import UsuarioORM
from dominio.usuario import Usuario
from datos.repositorio.base_repositorio import BaseRepositorio


class UsuarioRepositorio(BaseRepositorio):
    modelo_orm = UsuarioORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Usuario(
            id_usuario=registro.id_usuario,
            nombre_completo=registro.nombre_completo,
            correo=registro.correo,
            telefono=registro.telefono,
            contrasena=registro.contrasena,
        )

    @classmethod
    def crear(cls, usuario: Usuario):
        registro = cls.modelo_orm.create(
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
        )
        usuario.id_usuario = registro.id_usuario
        return usuario

    @classmethod
    def obtener_por_id(cls, id_usuario):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_usuario == id_usuario)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]