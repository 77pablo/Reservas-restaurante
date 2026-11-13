from repositorios.base_repositorio import BaseRepositorio
from modelos.usuario import Usuario
from validaciones import validar_rut, validar_genero

class UsuarioRepositorio(BaseRepositorio):
    def crear(self, usuario: Usuario):
        # Validar RUT
        _, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)
            
        # Validar Género
        _, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = "INSERT INTO usuario (rut, nombre_completo, correo, telefono, genero, contrasena) VALUES (%s, %s, %s, %s, %s, %s)"
        parametros = (usuario.rut, usuario.nombre_completo, usuario.correo, usuario.telefono, usuario.genero, usuario.contrasena)
        nuevo_id = self._ejecutar_consulta(sql, parametros, obtener_id=True)
        if nuevo_id: usuario.id_usuario = nuevo_id
        return nuevo_id

    def actualizar(self, usuario: Usuario):
        # Validar RUT
        _, msg_rut = validar_rut(usuario.rut)
        if msg_rut != "RUT Válido":
            raise ValueError(msg_rut)
            
        # Validar Género
        _, msg_gen = validar_genero(usuario.genero)
        if msg_gen != "Género Válido":
            raise ValueError(msg_gen)

        sql = "UPDATE usuario SET rut=%s, nombre_completo=%s, correo=%s, telefono=%s, genero=%s, contrasena=%s WHERE id_usuario=%s"
        parametros = (usuario.rut, usuario.nombre_completo, usuario.correo, usuario.telefono, usuario.genero, usuario.contrasena, usuario.id_usuario)
        return self._ejecutar_consulta(sql, parametros)