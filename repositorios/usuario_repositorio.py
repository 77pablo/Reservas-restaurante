from repositorios.base_repositorio import BaseRepositorio
from modelos.usuario import Usuario

class UsuarioRepositorio(BaseRepositorio):
    def crear(self, usuario: Usuario):
        sql = "INSERT INTO usuario (nombre_completo, correo, telefono, contrasena) VALUES (%s, %s, %s, %s)"
        parametros = (usuario.nombre_completo, usuario.correo, usuario.telefono, usuario.contrasena)
        nuevo_id = self._ejecutar_consulta(sql, parametros, obtener_id=True)
        if nuevo_id: usuario.id_usuario = nuevo_id
        return nuevo_id

    def actualizar(self, usuario: Usuario):
        sql = "UPDATE usuario SET nombre_completo=%s, correo=%s, telefono=%s, contrasena=%s WHERE id_usuario=%s"
        parametros = (usuario.nombre_completo, usuario.correo, usuario.telefono, usuario.contrasena, usuario.id_usuario)
        return self._ejecutar_consulta(sql, parametros)
