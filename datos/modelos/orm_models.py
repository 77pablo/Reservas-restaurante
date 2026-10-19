"""
Modelos Peewee: representan las tablas de MySQL.
Cada clase corresponde 1 a 1 con una tabla del diagrama UML.
"""
from datetime import datetime
from peewee import (
    Model, AutoField, IntegerField, CharField, TextField,
    DateTimeField, DateField, TimeField, BooleanField, ForeignKeyField,
)
from datos.conexion import db


class ModeloBase(Model):
    """Clase base: todos los modelos comparten la misma conexion."""
    class Meta:
        database = db


class UsuarioORM(ModeloBase):
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    correo = CharField(max_length=100, unique=True)
    telefono = CharField(max_length=20, null=True)
    contrasena = CharField(max_length=255)

    class Meta:
        table_name = "usuario"


class ClienteORM(ModeloBase):
    id_cliente = AutoField()
    usuario = ForeignKeyField(
        UsuarioORM, column_name="id_usuario",
        backref="cliente", unique=True, on_delete="CASCADE",
    )
    preferencias = TextField(null=True)
    puntos_fidelidad = IntegerField(default=0)

    class Meta:
        table_name = "cliente"


class EmpleadoORM(ModeloBase):
    id_empleado = AutoField()
    usuario = ForeignKeyField(
        UsuarioORM, column_name="id_usuario",
        backref="empleado", unique=True, on_delete="CASCADE",
    )
    cargo = CharField(max_length=50)
    turno = CharField(max_length=50, null=True)

    class Meta:
        table_name = "empleado"


class RestaurantORM(ModeloBase):
    id_restaurant = AutoField()
    nombre = CharField(max_length=100)
    direccion = CharField(max_length=200)
    telefono = CharField(max_length=20, null=True)
    horario_apertura = TimeField()
    horario_cierre = TimeField()

    class Meta:
        table_name = "restaurant"


class ZonaORM(ModeloBase):
    id_zona = AutoField()
    restaurant = ForeignKeyField(
        RestaurantORM, column_name="id_restaurant",
        backref="zonas", on_delete="CASCADE",
    )
    nombre_zona = CharField(max_length=50)
    permite_fumadores = BooleanField(default=False)

    class Meta:
        table_name = "zona"


class MesaORM(ModeloBase):
    id_mesa = AutoField()
    zona = ForeignKeyField(
        ZonaORM, column_name="id_zona",
        backref="mesas", on_delete="CASCADE",
    )
    numero_mesa = IntegerField()
    capacidad = IntegerField()
    activa = BooleanField(default=True)

    class Meta:
        table_name = "mesa"


class ReservaORM(ModeloBase):
    id_reserva = AutoField()
    cliente = ForeignKeyField(
        ClienteORM, column_name="id_cliente",
        backref="reservas", on_delete="CASCADE",
    )
    fecha_creacion = DateTimeField(default=datetime.now)
    cant_personas = IntegerField()
    estado = CharField(max_length=20, default="Pendiente")
    observaciones = TextField(null=True)

    class Meta:
        table_name = "reserva"


class DisponibilidadORM(ModeloBase):
    id_disponibilidad = AutoField()
    mesa = ForeignKeyField(
        MesaORM, column_name="id_mesa",
        backref="disponibilidades", on_delete="CASCADE",
    )
    reserva = ForeignKeyField(
        ReservaORM, column_name="id_reserva",
        backref="disponibilidades", null=True, on_delete="SET NULL",
    )
    fecha = DateField()
    hora_inicio = TimeField()
    hora_fin = TimeField()
    estado_franja = CharField(max_length=20, default="Disponible")

    class Meta:
        table_name = "disponibilidad"


TODOS_LOS_MODELOS = [
    UsuarioORM, ClienteORM, EmpleadoORM, RestaurantORM,
    ZonaORM, MesaORM, ReservaORM, DisponibilidadORM,
]


def crear_tablas():
    """Crea las tablas si no existen (idempotente)."""
    db.connect(reuse_if_open=True)
    try:
        db.create_tables(TODOS_LOS_MODELOS, safe=True)
        print("[OK] Tablas verificadas/creadas correctamente.")
    finally:
        if not db.is_closed():
            db.close()