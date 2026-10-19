from peewee import IntegrityError

from datos.modelos.orm_models import ClienteORM, UsuarioORM
from dominio.cliente import Cliente
from repositorios.base_repositorio import BaseRepositorio


class ClienteRepositorio(BaseRepositorio):
    modelo_orm = ClienteORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None

        usuario = registro.usuario

        return Cliente(
            id_usuario=usuario.id_usuario,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
            id_cliente=registro.id_cliente,
            preferencias=registro.preferencias,
            puntos_fidelidad=registro.puntos_fidelidad,
        )

    @classmethod
    def crear(cls, cliente: Cliente):
        correo = cliente.correo.strip().lower()

        usuario_registro = UsuarioORM.get_or_none(
            UsuarioORM.correo == correo
        )

        if usuario_registro is None:
            try:
                usuario_registro = UsuarioORM.create(
                    nombre_completo=cliente.nombre_completo,
                    correo=correo,
                    telefono=cliente.telefono,
                    contrasena=cliente.contrasena,
                )
            except IntegrityError:
                usuario_registro = UsuarioORM.get_or_none(
                    UsuarioORM.correo == correo
                )
                if usuario_registro is None:
                    raise

        cliente.id_usuario = usuario_registro.id_usuario

        cliente_registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.usuario == usuario_registro.id_usuario
        )

        if cliente_registro is None:
            cliente_registro = cls.modelo_orm.create(
                usuario=usuario_registro,
                preferencias=cliente.preferencias,
                puntos_fidelidad=cliente.puntos_fidelidad,
            )

        cliente.id_cliente = cliente_registro.id_cliente
        return cls._a_dominio(cliente_registro)

    @classmethod
    def obtener_por_id(cls, id_cliente):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_cliente == id_cliente
        )
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [
            cls._a_dominio(registro)
            for registro in cls.modelo_orm.select()
        ]

    @classmethod
    def actualizar_puntos(cls, id_cliente, nuevos_puntos):
        filas = (
            cls.modelo_orm.update(puntos_fidelidad=nuevos_puntos)
            .where(cls.modelo_orm.id_cliente == id_cliente)
            .execute()
        )
        return filas > 0

    @classmethod
    def actualizar(cls, cliente: Cliente):
        """Actualiza los datos del usuario base y del cliente asociado."""
        if cliente.id_cliente is None:
            return False

        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_cliente == cliente.id_cliente
        )
        if registro is None:
            return False

        usuario_registro = registro.usuario
        usuario_registro.nombre_completo = cliente.nombre_completo
        usuario_registro.correo = cliente.correo.strip().lower()
        usuario_registro.telefono = cliente.telefono
        usuario_registro.contrasena = cliente.contrasena
        usuario_registro.save()

        registro.preferencias = cliente.preferencias
        registro.puntos_fidelidad = cliente.puntos_fidelidad
        registro.save()
        return True

    @classmethod
    def eliminar(cls, id_cliente):
        """Elimina el registro de cliente (y en cascada sus reservas)."""
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_cliente == id_cliente
        )
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True