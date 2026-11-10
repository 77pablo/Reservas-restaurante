from abc import ABC
import re
import bcrypt

class Usuario(ABC):
    def __init__(self, nombre_completo, correo, telefono, contrasena=None, id_usuario=None):
        self._id_usuario = id_usuario
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.telefono = telefono
        self._contrasena = contrasena
        self._sesion_activa = False

    @property
    def id_usuario(self): return self._id_usuario
    @id_usuario.setter
    def id_usuario(self, v): self._id_usuario = v

    @property
    def nombre_completo(self): return self._nombre_completo
    @nombre_completo.setter
    def nombre_completo(self, v): self._nombre_completo = v.strip()

    @property
    def correo(self): return self._correo
    @correo.setter
    def correo(self, v): self._correo = v.strip().lower()

    @property
    def telefono(self): return self._telefono
    @telefono.setter
    def telefono(self, v): self._telefono = v

    @property
    def contrasena(self): return self._contrasena
    @contrasena.setter
    def contrasena(self, hash_db): self._contrasena = hash_db

    def establecer_contrasena(self, password_plana):
        if not password_plana or len(password_plana) < 6:
            raise ValueError("Mínimo 6 caracteres.")
        salt = bcrypt.gensalt()
        self._contrasena = bcrypt.hashpw(password_plana.encode('utf-8'), salt).decode('utf-8')

    def iniciar_sesion(self, password_plana):
        if not self._contrasena: return False
        try:
            if bcrypt.checkpw(password_plana.encode('utf-8'), self._contrasena.encode('utf-8')):
                self._sesion_activa = True
                return True
            return False
        except ValueError:
            return False

    def cerrar_sesion(self):
        self._sesion_activa = False
        return True

    def __str__(self):
        est = "Con clave" if self._contrasena else "Sin clave"
        return f"[{self.__class__.__name__}] {self.nombre_completo} <{self.correo}> ({est})"
