from repositorios.base_repositorio import BaseRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from modelos.cliente import Cliente

class ClienteRepositorio(BaseRepositorio):
    def __init__(self):
        super().__init__()
        self._usuario_repo = UsuarioRepositorio()

    def crear(self, cliente: Cliente):
        id_usuario = self._usuario_repo.crear(cliente)
        if not id_usuario:
            return None  # Ej: correo ya registrado. Quien llama debe avisar al usuario.
        sql = "INSERT INTO cliente (id_usuario, preferencias, puntos_fidelidad) VALUES (%s, %s, %s)"
        id_cliente = self._ejecutar_consulta(
            sql, (id_usuario, cliente.preferencias, cliente.puntos_fidelidad), obtener_id=True
        )
        if id_cliente:
            cliente.id_cliente = id_cliente
        return id_cliente

    def buscar_por_correo(self, correo):
        sql = """
            SELECT c.id_cliente, c.preferencias, c.puntos_fidelidad,
                   u.id_usuario, u.nombre_completo, u.correo, u.telefono, u.contrasena
            FROM cliente c
            JOIN usuario u ON u.id_usuario = c.id_usuario
            WHERE u.correo = %s
        """
        fila = self._consultar(sql, (correo.strip().lower(),), uno=True)
        if not fila:
            return None
        return Cliente(
            nombre_completo=fila["nombre_completo"],
            correo=fila["correo"],
            telefono=fila["telefono"],
            contrasena=fila["contrasena"],  # ya es el hash bcrypt guardado en la BD
            preferencias=fila["preferencias"],
            puntos_fidelidad=fila["puntos_fidelidad"],
            id_usuario=fila["id_usuario"],
            id_cliente=fila["id_cliente"],
        )