
from repositorios.base_repositorio import BaseRepositorio
from modelos.usuario import Usuario
from validaciones import validar_rut, validar_genero


class UsuarioRepositorio(BaseRepositorio):

    def crear(self, usuario: Usuario):

        # Validar RUT
        rut_limpio, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)

        # Validar género
        genero_limpio, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = """
            INSERT INTO usuario
            (rut, nombre_completo, correo, telefono, genero, contrasena)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        parametros = (
            rut_limpio,
            usuario.nombre_completo,
            usuario.correo,
            usuario.telefono,
            genero_limpio,
            usuario.contrasena
        )

        nuevo_id = self._ejecutar_consulta(
            sql, parametros, obtener_id=True
        )

        if nuevo_id:
            usuario.id_usuario = nuevo_id

        return nuevo_id

    def actualizar(self, usuario: Usuario):

        if usuario.id_usuario is None:
            raise ValueError("El usuario no tiene un ID asignado.")

        # Validar RUT
        rut_limpio, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)

        # Validar género
        genero_limpio, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = """
            UPDATE usuario
            SET rut=%s,
                nombre_completo=%s,
                correo=%s,
                telefono=%s,
                genero=%s,
                contrasena=%s
            WHERE id_usuario=%s
        """

        parametros = (
            rut_limpio,
            usuario.nombre_completo,
            usuario.correo,
            usuario.telefono,
            genero_limpio,
            usuario.contrasena,
            usuario.id_usuario
        )

        return self._ejecutar_consulta(sql, parametros)
