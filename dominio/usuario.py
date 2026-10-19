"""Clase Usuario - traduccion directa del UML (clase base)."""


class Usuario:
    def __init__(self, id_usuario=None, nombre_completo="", correo="",
                 telefono="", contrasena=""):
        self._id_usuario = id_usuario
        self._nombre_completo = nombre_completo
        self._correo = correo
        self._telefono = telefono
        self._contrasena = contrasena

    @property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, valor):
        self._id_usuario = valor

    @property
    def nombre_completo(self):
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre completo no puede estar vacio.")
        self._nombre_completo = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor:
            raise ValueError("El correo electronico no es valido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = valor

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor):
        if len(valor) < 6:
            raise ValueError("La contrasena debe tener al menos 6 caracteres.")
        self._contrasena = valor

    def iniciarSesion(self, correo_ingresado, contrasena_ingresada):
        """Retorna boolean."""
        return (self._correo == correo_ingresado
                and self._contrasena == contrasena_ingresada)

    def cerrarSesion(self):
        """void. Metodo base: las subclases lo sobrescriben (polimorfismo)."""
        print(f"[Sesion] {self._nombre_completo} cerro sesion.")

    def obtener_rol(self):
        """Metodo polimorfico: cada subclase retorna su propio rol.

        En la clase base retorna un valor generico; Cliente y Empleado
        lo sobrescriben para demostrar polimorfismo por sobrescritura.
        """
        return "Usuario"

    def realizar_accion_principal(self):
        """Metodo polimorfico: comportamiento por defecto.

        Cliente y Empleado sobrescriben este metodo con su propia logica,
        de modo que una misma llamada produce resultados distintos segun
        el tipo real del objeto (polimorfismo en tiempo de ejecucion).
        """
        return f"{self._nombre_completo} no tiene una accion principal definida."

    def __str__(self):
        return f"Usuario(id={self._id_usuario}, nombre='{self._nombre_completo}')"