from peewee import DoesNotExist, IntegrityError
from werkzeug.security import generate_password_hash
import secrets

from datos.conexion import database
from datos.modelos.models import ClienteDB, UsuarioDB


class ClienteRepositorio:
    """Repositorio para consultar y registrar clientes."""

    @staticmethod
    def buscar_por_nombre_y_correo(nombre_completo, correo_electronico):
        nombre = (nombre_completo or "").strip()
        correo = (correo_electronico or "").strip().lower()

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
        if id_cliente is None:
            return None

        try:
            return ClienteDB.get(
                ClienteDB.id_cliente == id_cliente
            )
        except DoesNotExist:
            return None

    @staticmethod
    def obtener_o_crear_por_nombre_y_correo(
        nombre_completo,
        correo_electronico,
    ):
        """
        Busca al cliente por correo. Si no existe, crea el usuario
        y su perfil de cliente para permitirle reservar sin contraseña.
        """
        nombre = (nombre_completo or "").strip()
        correo = (correo_electronico or "").strip().lower()

        if not nombre or not correo:
            return None

        if len(nombre) > 150 or len(correo) > 100:
            return None

        if "@" not in correo or "." not in correo.rsplit("@", 1)[-1]:
            return None

        try:
            with database.atomic():
                usuario = UsuarioDB.get_or_none(
                    UsuarioDB.correo_electronico == correo
                )

                if usuario is not None:
                    # No cambiar el nombre de una cuenta existente.
                    return ClienteDB.get_or_none(
                        ClienteDB.id_usuario == usuario.id_usuario
                    )

                # La cuenta nueva no necesita contraseña para reservar.
                # Se genera una clave aleatoria no conocida por el cliente.
                clave_aleatoria = secrets.token_urlsafe(32)
                hash_clave = generate_password_hash(clave_aleatoria)

                usuario = UsuarioDB.create(
                    nombre_completo=nombre,
                    correo_electronico=correo,
                    contrasena=hash_clave,
                )

                cliente = ClienteDB.create(
                    id_usuario=usuario.id_usuario,
                    puntos_fidelidad=0,
                )

                return cliente

        except IntegrityError:
            # Si otra solicitud registró el correo al mismo tiempo,
            # intentamos recuperar el perfil que ya se creó.
            usuario = UsuarioDB.get_or_none(
                UsuarioDB.correo_electronico == correo
            )

            if usuario is None:
                return None

            return ClienteDB.get_or_none(
                ClienteDB.id_usuario == usuario.id_usuario
            )
