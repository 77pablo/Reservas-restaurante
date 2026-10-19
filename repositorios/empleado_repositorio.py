from peewee import IntegrityError

from datos.modelos.orm_models import EmpleadoORM, UsuarioORM
from dominio.empleado import Empleado
from repositorios.base_repositorio import BaseRepositorio


class EmpleadoRepositorio(BaseRepositorio):
    modelo_orm = EmpleadoORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None

        usuario = registro.usuario

        return Empleado(
            id_usuario=usuario.id_usuario,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
            id_empleado=registro.id_empleado,
            cargo=registro.cargo,
            turno=registro.turno,
        )

    @classmethod
    def crear(cls, empleado: Empleado):
        correo = empleado.correo.strip().lower()

        usuario_registro = UsuarioORM.get_or_none(
            UsuarioORM.correo == correo
        )

        if usuario_registro is None:
            try:
                usuario_registro = UsuarioORM.create(
                    nombre_completo=empleado.nombre_completo,
                    correo=correo,
                    telefono=empleado.telefono,
                    contrasena=empleado.contrasena,
                )
            except IntegrityError:
                usuario_registro = UsuarioORM.get_or_none(
                    UsuarioORM.correo == correo
                )
                if usuario_registro is None:
                    raise

        empleado.id_usuario = usuario_registro.id_usuario

        empleado_registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.usuario == usuario_registro.id_usuario
        )

        if empleado_registro is None:
            empleado_registro = cls.modelo_orm.create(
                usuario=usuario_registro,
                cargo=empleado.cargo,
                turno=empleado.turno,
            )

        empleado.id_empleado = empleado_registro.id_empleado
        return cls._a_dominio(empleado_registro)

    @classmethod
    def obtener_por_id(cls, id_empleado):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_empleado == id_empleado
        )
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [
            cls._a_dominio(registro)
            for registro in cls.modelo_orm.select()
        ]

    @classmethod
    def actualizar(cls, empleado: Empleado):
        if empleado.id_empleado is None:
            return False

        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_empleado == empleado.id_empleado
        )
        if registro is None:
            return False

        usuario_registro = registro.usuario
        usuario_registro.nombre_completo = empleado.nombre_completo
        usuario_registro.correo = empleado.correo.strip().lower()
        usuario_registro.telefono = empleado.telefono
        usuario_registro.contrasena = empleado.contrasena
        usuario_registro.save()

        registro.cargo = empleado.cargo
        registro.turno = empleado.turno
        registro.save()
        return True

    @classmethod
    def eliminar(cls, id_empleado):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm.id_empleado == id_empleado
        )
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True