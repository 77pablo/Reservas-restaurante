
from datetime import datetime, date, time
from peewee import (
    Model,
    AutoField,
    IntegerField,
    CharField,
    TextField,
    DateTimeField,
    DateField,
    TimeField,
    ForeignKeyField,
    MySQLDatabase,
)


# ============================================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================================

# La configuración se obtiene de la configuración central del proyecto.
# Si tu proyecto ya tiene una instancia de base de datos compartida,
# importa esa instancia aquí en vez de crear una nueva.
try:
    from datos.conexion import db
except ImportError:
    db = MySQLDatabase(
        "reserva-restaurante",
        user="root",
        password="",
        host="localhost",
        port=3306,
    )


# ============================================================
# MODELO BASE DE PERSISTENCIA
# ============================================================

class BaseModel(Model):
    """Modelo base que comparte la conexión de la aplicación."""

    class Meta:
        database = db


# ============================================================
# CLASES DE DOMINIO: USUARIO, CLIENTE Y EMPLEADO
# ============================================================

class Usuario:
    """Representa a un usuario del sistema."""

    def __init__(
        self,
        id_usuario=None,
        nombre_completo="",
        correo="",
        telefono="",
        contrasena="",
    ):
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
        self._nombre_completo = valor

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        self._correo = valor

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
        self._contrasena = valor

    def iniciarSesion(self):
        """Indica que el usuario solicita iniciar sesión."""
        return True

    def cerrarSesion(self):
        """Indica que el usuario solicita cerrar sesión."""
        return True


class Cliente(Usuario):
    """Cliente del restaurante. Hereda los datos de Usuario."""

    def __init__(
        self,
        id_usuario=None,
        nombre_completo="",
        correo="",
        telefono="",
        contrasena="",
        preferencias_alimentarias="",
        puntos_fidelidad=0,
    ):
        super().__init__(
            id_usuario=id_usuario,
            nombre_completo=nombre_completo,
            correo=correo,
            telefono=telefono,
            contrasena=contrasena,
        )
        self._preferencias_alimentarias = preferencias_alimentarias
        self._puntos_fidelidad = puntos_fidelidad

    @property
    def preferencias_alimentarias(self):
        return self._preferencias_alimentarias

    @preferencias_alimentarias.setter
    def preferencias_alimentarias(self, valor):
        self._preferencias_alimentarias = valor

    @property
    def puntos_fidelidad(self):
        return self._puntos_fidelidad

    @puntos_fidelidad.setter
    def puntos_fidelidad(self, valor):
        self._puntos_fidelidad = valor

    def solicitarReserva(self):
        """Representa la solicitud de una reserva."""
        return True

    def cancelarReserva(self, id_reserva):
        """Representa la solicitud de cancelación de una reserva."""
        return id_reserva


class Empleado(Usuario):
    """Empleado del restaurante. Hereda los datos de Usuario."""

    def __init__(
        self,
        id_usuario=None,
        nombre_completo="",
        correo="",
        telefono="",
        contrasena="",
        id_empleado=None,
        cargo="",
        turno="",
    ):
        super().__init__(
            id_usuario=id_usuario,
            nombre_completo=nombre_completo,
            correo=correo,
            telefono=telefono,
            contrasena=contrasena,
        )
        self._id_empleado = id_empleado
        self._cargo = cargo
        self._turno = turno

    @property
    def id_empleado(self):
        return self._id_empleado

    @id_empleado.setter
    def id_empleado(self, valor):
        self._id_empleado = valor

    @property
    def cargo(self):
        return self._cargo

    @cargo.setter
    def cargo(self, valor):
        self._cargo = valor

    @property
    def turno(self):
        return self._turno

    @turno.setter
    def turno(self, valor):
        self._turno = valor

    def aprobarReserva(self, id_reserva):
        """Representa la aprobación de una reserva."""
        return id_reserva

    def gestionarMesas(self):
        """Representa la acción de gestionar las mesas."""
        return True


# ============================================================
# MODELOS PERSISTENTES: TABLAS DE MYSQL
# ============================================================

class UsuarioDB(BaseModel):
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    correo = CharField(max_length=150, unique=True)
    telefono = CharField(max_length=30, null=True)
    contrasena = CharField(max_length=255)

    class Meta:
        table_name = "usuario"


class ClienteDB(BaseModel):
    id_cliente = AutoField()
    usuario = ForeignKeyField(
        UsuarioDB,
        column_name="id_usuario",
        backref="cliente",
        on_delete="CASCADE",
        unique=True,
    )
    preferencias_alimentarias = TextField(null=True)
    puntos_fidelidad = IntegerField(default=0)

    class Meta:
        table_name = "cliente"


class EmpleadoDB(BaseModel):
    id_empleado = AutoField()
    usuario = ForeignKeyField(
        UsuarioDB,
        column_name="id_usuario",
        backref="empleado",
        on_delete="CASCADE",
        unique=True,
    )
    cargo = CharField(max_length=80)
    turno = CharField(max_length=80, null=True)

    class Meta:
        table_name = "empleado"


class Restaurant(BaseModel):
    id_restaurant = AutoField()
    nombre = CharField(max_length=150)
    direccion = CharField(max_length=255, null=True)
    telefono = CharField(max_length=30, null=True)
    correo = CharField(max_length=150, null=True)

    class Meta:
        table_name = "restaurant"


class Zona(BaseModel):
    id_zona = AutoField()
    restaurant = ForeignKeyField(
        Restaurant,
        column_name="id_restaurant",
        backref="zonas",
        on_delete="CASCADE",
    )
    nombre = CharField(max_length=100)
    descripcion = TextField(null=True)

    class Meta:
        table_name = "zona"


class Mesa(BaseModel):
    id_mesa = AutoField()
    zona = ForeignKeyField(
        Zona,
        column_name="id_zona",
        backref="mesas",
        on_delete="CASCADE",
    )
    numero = IntegerField()
    capacidad = IntegerField()
    estado = CharField(max_length=30, default="Disponible")

    class Meta:
        table_name = "mesa"
        indexes = (
            (("zona", "numero"), True),
        )


class Reserva(BaseModel):
    id_reserva = AutoField()
    cliente = ForeignKeyField(
        ClienteDB,
        column_name="id_cliente",
        backref="reservas",
        on_delete="CASCADE",
    )
    fecha_creacion = DateTimeField(default=datetime.now)
    fecha_reserva = DateField(null=True)
    hora_inicio_reserva = TimeField(null=True)
    hora_fin_reserva = TimeField(null=True)
    cantidad_personas = IntegerField()
    numero_mesa_reserva = IntegerField(null=True)
    estado = CharField(max_length=30, default="Pendiente")
    observaciones_especiales = TextField(null=True)

    class Meta:
        table_name = "reserva"


class Disponibilidad(BaseModel):
    id_disponibilidad = AutoField()
    mesa = ForeignKeyField(
        Mesa,
        column_name="id_mesa",
        backref="disponibilidades",
        on_delete="CASCADE",
    )
    reserva = ForeignKeyField(
        Reserva,
        column_name="id_reserva",
        backref="disponibilidades",
        null=True,
        on_delete="SET NULL",
    )
    fecha = DateField()
    hora_inicio = TimeField()
    hora_fin = TimeField()
    estado_franja = CharField(max_length=30, default="Disponible")

    class Meta:
        table_name = "disponibilidad"


class EmpleadoRestaurant(BaseModel):
    id_empleado_restaurant = AutoField()
    empleado = ForeignKeyField(
        EmpleadoDB,
        column_name="id_empleado",
        backref="restaurantes_asignados",
        on_delete="CASCADE",
    )
    restaurant = ForeignKeyField(
        Restaurant,
        column_name="id_restaurant",
        backref="empleados_asignados",
        on_delete="CASCADE",
    )

    class Meta:
        table_name = "empleado_restaurant"
        indexes = (
            (("empleado", "restaurant"), True),
        )


# ============================================================
# UTILIDADES DE CONEXIÓN Y CREACIÓN DE TABLAS
# ============================================================

MODELOS = [
    UsuarioDB,
    ClienteDB,
    EmpleadoDB,
    Restaurant,
    Zona,
    Mesa,
    Reserva,
    Disponibilidad,
    EmpleadoRestaurant,
]


def probar_conexion():
    """Prueba la conexión a MySQL y devuelve True si funciona."""
    try:
        db.connect(reuse_if_open=True)
        db.execute_sql("SELECT 1")
        return True
    except Exception as error:
        print(f"Error de conexión a MySQL: {error}")
        return False
    finally:
        if not db.is_closed():
            db.close()


def crear_tablas():
    """Crea las tablas declaradas si todavía no existen."""
    db.connect(reuse_if_open=True)
    try:
        db.create_tables(MODELOS, safe=True)
    finally:
        if not db.is_closed():
            db.close()
