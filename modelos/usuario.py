from abc import ABC
import bcrypt
from validaciones import validar_rut, validar_genero

class Usuario(ABC):
    def __init__(self, nombre_completo, rut, correo, telefono, genero, contrasena=None, id_usuario=None):
        self._id_usuario = id_usuario
        self.rut = rut                  # Pasa por el setter que valida con validaciones.py
        self._nombre_completo = nombre_completo
        self._correo = correo
        self._telefono = telefono
        self.genero = genero            # Pasa por el setter que valida con validaciones.py
        self._contrasena = contrasena
        self._sesion_activa = False

    @property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, v):
        self._id_usuario = v

    @property
    def rut(self):
        return self._rut

    @rut.setter
    def rut(self, v):
        # Valida el RUT usando la función centralizada
        rut_limpio, mensaje = validar_rut(v)
        if mensaje != "RUT Válido":
            raise ValueError(mensaje)
        self._rut = rut_limpio

    @property
    def nombre_completo(self):
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, v):
        self._nombre_completo = v.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, v):
        self._correo = v.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, v):
        self._telefono = v

    @property
    def genero(self):
        return self._genero

    @genero.setter
    def genero(self, v):
        # Valida el género usando la función centralizada
        genero_limpio, mensaje = validar_genero(v)
        if mensaje != "Género Válido":
            raise ValueError(mensaje)
        self._genero = genero_limpio

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, v):
        self._contrasena = v