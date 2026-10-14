
from peewee import DoesNotExist

from datos.modelos.models import Cliente, Usuario


class ClienteRepositorio:

    @staticmethod
    def buscar_por_nombre_y_correo(nombre_completo, correo_electronico):
        """
        Busca un cliente registrado cuyo nombre y correo coincidan.
        Devuelve el Cliente o None si no existe una coincidencia.
        """
        nombre = nombre_completo.strip()
        correo = correo_electronico.strip().lower()

        if not nombre or not correo:
            return None

        consulta = (
            Cliente
            .select(Cliente, Usuario)
            .join(
                Usuario,
                on=(Cliente.id_usuario == Usuario.id_usuario)
            )
            .where(
                (Usuario.nombre_completo == nombre)
                & (Usuario.correo_electronico == correo)
            )
        )

        try:
            return consulta.get()
        except DoesNotExist:
            return None

    @staticmethod
    def obtener_por_id(id_cliente):
        try:
            return Cliente.get(
                Cliente.id_cliente == id_cliente
            )
        except DoesNotExist:
            return None
