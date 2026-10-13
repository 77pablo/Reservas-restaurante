
from peewee import DoesNotExist
from datos.conexion import database
from datos.modelos.models import Cliente, Usuario


class ClienteRepositorio:

    @staticmethod
    def crear_cliente(
        nombre_completo,
        correo,
        telefono,
        contrasena,
        preferencias=None,
        puntos=0
    ):
        """Crea un usuario y su registro de cliente en una transacción."""
        try:
            with database.atomic():
                nuevo_usuario = Usuario.create(
                    nombre_completo=nombre_completo,
                    correo_electronico=correo,
                    telefono=telefono,
                    contrasena=contrasena
                )

                nuevo_cliente = Cliente.create(
                    id_usuario=nuevo_usuario.id_usuario,
                    preferencias_alimentarias=preferencias,
                    puntos_fidelidad=puntos
                )

            return nuevo_cliente

        except Exception as e:
            print(f"Error al registrar el cliente: {e}")
            return None

    @staticmethod
    def obtener_todos():
        """Retorna todos los clientes registrados."""
        return Cliente.select()

    @staticmethod
    def buscar_por_id(id_cli):
        """Busca un cliente por su ID."""
        try:
            return Cliente.get_by_id(id_cli)
        except DoesNotExist:
            return None