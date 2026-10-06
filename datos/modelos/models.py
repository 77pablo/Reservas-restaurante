from peewee import MySQLDatabase,AutoField,IntegerField,TextField,CharField,DateField,TimeField,DateTimeField,Model,SQL,CompositeKey,BooleanField
from decouple import config 

database = MySQLDatabase(config('database'), **
                         {'charset': 'utf8mb4', 
                          'host': config('host'), 
                          'port': config('port'), 
                          'user': config('user'), 
                          'password': config('password')})

class UnknownField(object):
    def __init__(self, *_, **__):
        # Es necesario para mapear campos desconocidos
        pass
class BaseModel(Model):
    class Meta:
        database = database

class Cliente(BaseModel):
    id_cliente = AutoField()
    id_usuario = IntegerField(unique=True)
    preferencias_alimentarias = TextField(null=True)
    puntos_fidelidad = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)

    class Meta:
        table_name = 'cliente'

class Disponibilidad(BaseModel):
    estado_franja = CharField(max_length=20)
    fecha = DateField()
    hora_fin = TimeField()
    hora_inicio = TimeField()
    id_disponibilidad = AutoField()
    id_mesa = IntegerField(index=True)
    id_reserva = IntegerField(index=True, null=True)

    class Meta:
        table_name = 'disponibilidad'

class Empleado(BaseModel):
    cargo = CharField(max_length=50)
    fecha_contratacion = DateField(null=True)
    id_empleado = AutoField()
    id_usuario = IntegerField(unique=True)

    class Meta:
        table_name = 'empleado'

class EmpleadoRestaurant(BaseModel):
    id_empleado = IntegerField()
    id_restaurant = IntegerField(index=True)
    turno = CharField(max_length=50)

    class Meta:
        table_name = 'empleado_restaurant'
        indexes = (
            (('id_empleado', 'id_restaurant'), True),
        )
        primary_key = CompositeKey('id_empleado', 'id_restaurant')

class Mesa(BaseModel):
    activa = BooleanField(constraints=[SQL("DEFAULT 1")], null=True)
    capacidad_comensales = IntegerField()
    id_mesa = AutoField()
    id_zona = IntegerField(index=True)
    numero_mesa = IntegerField()

    class Meta:
        table_name = 'mesa'

class Reserva(BaseModel):
    cantidad_personas = IntegerField()
    estado = CharField(max_length=20)
    fecha_creacion = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    id_cliente = IntegerField(index=True)
    id_reserva = AutoField()
    observaciones_especiales = TextField(null=True)

    class Meta:
        table_name = 'reserva'

class Restaurant(BaseModel):
    direccion = CharField(max_length=200)
    horario_apertura = TimeField()
    horario_cierre = TimeField()
    id_restaurant = AutoField()
    nombre = CharField(max_length=100)
    telefono_contacto = CharField(max_length=20, null=True)

    class Meta:
        table_name = 'restaurant'

class Usuario(BaseModel):
    contrasena = CharField()
    correo_electronico = CharField(max_length=100, unique=True)
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    telefono = CharField(max_length=20, null=True)

    class Meta:
        table_name = 'usuario'

class Zona(BaseModel):
    id_restaurant = IntegerField(index=True)
    id_zona = AutoField()
    nombre_zona = CharField(max_length=50)
    permite_fumadores = BooleanField(constraints=[SQL("DEFAULT 0")], null=True)

    class Meta:
        table_name = 'zona'

