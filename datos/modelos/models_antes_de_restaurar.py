from peewee import (
    AutoField,
    IntegerField,
    TextField,
    CharField,
    DateField,
    TimeField,
    DateTimeField,
    Model,
    SQL,
    CompositeKey,
    BooleanField,
    ForeignKeyField,
)

from datos.conexion import database


# =========================================================
# MODELOS DE DOMINIO: REPRESENTAN LA HERENCIA DEL UML
# =========================================================

class Usuario:
    """Clase base de dominio para los usuarios."""

    def __init__(
        self,
        nombre_completo="",
        correo_electronico="",
        contrasena="",
        telefono=None,
    ):
        self.nombre_completo = nombre_completo
        self.correo_electronico = correo_electronico
        self.contrasena = contrasena
        self.telefono = telefono

    def iniciarSesion(self):
        return bool(self.correo_electronico and self.contrasena)

    def cerrarSesion(self):
        return True


class ClienteDB(Usuario):
    """Cliente: hereda los atributos y métodos de Usuario."""

    def __init__(
        self,
        nombre_completo="",
        correo_electronico="",
        contrasena="",
        telefono=None,
        preferencias_alimentarias=None,
        puntos_fidelidad=0,
    ):
        super().__init__(
            nombre_completo,
            correo_electronico,
            contrasena,
            telefono,
        )
        self.preferencias_alimentarias = preferencias_alimentarias
        self.puntos_fidelidad = puntos_fidelidad

    def solicitarReserva(self):
        return True

    def cancelarReserva(self):
        return True


class EmpleadoDB(Usuario):
    """Empleado: hereda los atributos y métodos de Usuario."""

    def __init__(
        self,
        nombre_completo="",
        correo_electronico="",
        contrasena="",
        telefono=None,
        cargo="",
        fecha_contratacion=None,
    ):
        super().__init__(
            nombre_completo,
            correo_electronico,
            contrasena,
            telefono,
        )
        self.cargo = cargo
        self.fecha_contratacion = fecha_contratacion

    def aprobarReserva(self):
        return True

    def gestionarMesas(self):
        return True


# =========================================================
# MODELOS DE PERSISTENCIA: TABLAS REALES DE MYSQL
# =========================================================

class BaseModel(Model):
    class Meta:
        database = database


class UsuarioDB(BaseModel):
    contrasena = CharField()
    correo_electronico = CharField(max_length=100, unique=True)
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    telefono = CharField(max_length=20, null=True)

    class Meta:
        table_name = "usuario"


class ClienteDB(BaseModel):
    id_cliente = AutoField()
    id_usuario = IntegerField(unique=True)
    preferencias_alimentarias = TextField(null=True)
    puntos_fidelidad = IntegerField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )

    class Meta:
        table_name = "cliente"


class EmpleadoDB(BaseModel):
    cargo = CharField(max_length=50)
    fecha_contratacion = DateField(null=True)
    id_empleado = AutoField()
    id_usuario = IntegerField(unique=True)

    class Meta:
        table_name = "empleado"

        # =========================================================
# MODELOS DE PERSISTENCIA RECUPERADOS
# =========================================================

class Restaurant(BaseModel):
    direccion = CharField(max_length=200)
    horario_apertura = TimeField()
    horario_cierre = TimeField()
    id_restaurant = AutoField()
    nombre = CharField(max_length=100)
    telefono_contacto = CharField(max_length=20, null=True)

    class Meta:
        table_name = "restaurant"

    def abrirJornada(self):
        return True

    def cerrarJornada(self):
        return True


class ZonaDB(BaseModel):
    id_restaurant = IntegerField(index=True)
    id_zona = AutoField()
    nombre_zona = CharField(max_length=50)
    permite_fumadores = BooleanField(
        constraints=[SQL("DEFAULT 0")],
        null=True,
    )

    class Meta:
        table_name = "zona"

    def agregarMesa(self):
        return True

    def obtenerMesas(self):
        return Mesa.select().where(Mesa.id_zona == self.id_zona)


class Mesa(BaseModel):
    id_mesa = AutoField()
    id_zona = IntegerField(index=True)
    numero_mesa = IntegerField()
    capacidad_comensales = IntegerField()
    activa = BooleanField(
        constraints=[SQL("DEFAULT 1")],
        null=True,
    )

    class Meta:
        table_name = "mesa"

    def asignarReserva(self):
        return True

    def liberar(self):
        return True


class ReservaDB(BaseModel):
    id_reserva = AutoField()
    id_cliente = IntegerField(index=True)
    fecha_creacion = DateTimeField(
        constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")],
        null=True,
    )
    cantidad_personas = IntegerField()
    estado = CharField(max_length=20)
    observaciones_especiales = TextField(null=True)

    class Meta:
        table_name = "reserva"

    def crear(self):
        return self.save(force_insert=True)

    def actualizarEstado(self, nuevo_estado):
        estados_validos = {
            "Pendiente",
            "Confirmada",
            "Cancelada",
            "Completada",
        }

        if nuevo_estado not in estados_validos:
            return False

        self.estado = nuevo_estado
        return self.save()


class DisponibilidadDB(BaseModel):
    id_disponibilidad = AutoField()
    id_mesa = IntegerField(index=True)
    id_reserva = IntegerField(index=True, null=True)
    fecha = DateField()
    hora_inicio = TimeField()
    hora_fin = TimeField()
    estado_franja = CharField(max_length=20)

    class Meta:
        table_name = "disponibilidad"

    def verificarEstado(self):
        return self.estado_franja == "Disponible"

    def bloquearHorario(self, id_reserva):
        if self.estado_franja != "Disponible":
            return False

        self.estado_franja = "Reservada"
        self.id_reserva = id_reserva
        return self.save()


class EmpleadoRestaurantDB(BaseModel):
    id_empleado = IntegerField()
    id_restaurant = IntegerField(index=True)
    turno = CharField(max_length=50)

    class Meta:
        table_name = "empleado_restaurant"
        primary_key = CompositeKey(
            "id_empleado",
            "id_restaurant",
        )



