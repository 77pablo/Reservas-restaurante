from peewee import DoesNotExist

from datos.modelos.models import ClienteDB, UsuarioDB


class ClienteRepositorio:

    @staticmethod
    def buscar_por_nombre_y_correo(nombre_completo, correo_electronico):
        """
        Busca un cliente por su nombre y correo electrónico.
        Devuelve el registro Peewee o None si no existe.
        """
        nombre = nombre_completo.strip()
        correo = correo_electronico.strip().lower()

        if not nombre or not correo:
            return None

        consulta = (
            ClienteDB
            .select(ClienteDB, UsuarioDB)
            .join(
                UsuarioDB,
                on=(ClienteDB.id_usuario == UsuarioDB.id_usuario),
            )
            .where(
                (UsuarioDB.nombre_completo == nombre)
                & (UsuarioDB.correo_electronico == correo)
            )
        )

        try:
            return consulta.get()
        except DoesNotExist:
            return None

    @staticmethod
    def obtener_por_id(id_cliente):
        try:
            return ClienteDB.get(
                ClienteDB.id_cliente == id_cliente
            )
        except DoesNotExist:
            return None
