
from datos.repositorio.cliente_repositorio import (
    ClienteRepositorio,
)


class ClienteServicio:

    @staticmethod
    def buscar_por_nombre_y_correo(
        nombre_completo,
        correo_electronico,
    ):
        if not nombre_completo or not correo_electronico:
            return None

        return (
            ClienteRepositorio.buscar_por_nombre_y_correo(
                nombre_completo,
                correo_electronico,
            )
        )
