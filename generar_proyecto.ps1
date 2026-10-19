# ===========================================
# Script generador de todos los archivos
# del proyecto Reservas-restaurante
# ===========================================

# ---------- requirements.txt ----------
@'
peewee==3.17.6
PyMySQL==1.1.1
python-decouple==3.8
'@ | Set-Content -Path "requirements.txt" -Encoding UTF8

# ---------- .env ----------
@'
DB_NAME=reserva-restaurante
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
'@ | Set-Content -Path ".env" -Encoding UTF8

# ---------- datos/conexion.py ----------
@'
"""
Modulo de conexion a MySQL.
- Peewee: ORM utilizado para mapear las clases a tablas.
- PyMySQL: driver oficial puro-Python para MySQL (PEP 249).
"""
import pymysql
from peewee import MySQLDatabase
from decouple import config

NOMBRE_BD = config("DB_NAME")
HOST_BD = config("DB_HOST", default="127.0.0.1")
PUERTO_BD = config("DB_PORT", default=3306, cast=int)
USUARIO_BD = config("DB_USER")
PASSWORD_BD = config("DB_PASSWORD", default="")

db = MySQLDatabase(
    NOMBRE_BD,
    host=HOST_BD,
    port=PUERTO_BD,
    user=USUARIO_BD,
    password=PASSWORD_BD,
    charset="utf8mb4",
)


def probar_conexion_pymysql():
    """Prueba de conexion directa usando PyMySQL (libreria oficial)."""
    try:
        conexion = pymysql.connect(
            host=HOST_BD,
            port=PUERTO_BD,
            user=USUARIO_BD,
            password=PASSWORD_BD,
            database=NOMBRE_BD,
            charset="utf8mb4",
        )
        with conexion.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
        conexion.close()
        print(f"[OK] PyMySQL conectado correctamente. MySQL version: {version[0]}")
        return True
    except Exception as error:
        print(f"[ERROR] Fallo la conexion con PyMySQL: {error}")
        return False


def probar_conexion():
    """Prueba de conexion a traves de Peewee (capa ORM)."""
    try:
        db.connect(reuse_if_open=True)
        db.execute_sql("SELECT 1")
        print(f"[OK] Peewee conectado correctamente a {NOMBRE_BD} en {HOST_BD}:{PUERTO_BD}")
        return True
    except Exception as error:
        print(f"[ERROR] Fallo la conexion con Peewee: {error}")
        return False
    finally:
        if not db.is_closed():
            db.close()
'@ | Set-Content -Path "datos\conexion.py" -Encoding UTF8

New-Item -ItemType File -Force -Path "datos\__init__.py" | Out-Null
New-Item -ItemType File -Force -Path "datos\modelos\__init__.py" | Out-Null

# ---------- datos/modelos/orm_models.py ----------
@'
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
'@ | Set-Content -Path "datos\modelos\orm_models.py" -Encoding UTF8

# ---------- dominio/__init__.py ----------
New-Item -ItemType File -Force -Path "dominio\__init__.py" | Out-Null

# ---------- dominio/usuario.py ----------
@'
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
        return (self._correo == correo_ingresado
                and self._contrasena == contrasena_ingresada)

    def cerrarSesion(self):
        print(f"[Sesion] {self._nombre_completo} cerro sesion.")

    def __str__(self):
        return f"Usuario(id={self._id_usuario}, nombre={self._nombre_completo})"
'@ | Set-Content -Path "dominio\usuario.py" -Encoding UTF8

# ---------- dominio/cliente.py ----------
@'
"""Clase Cliente - hereda de Usuario (reutilizacion de codigo)."""
from dominio.usuario import Usuario


class Cliente(Usuario):
    def __init__(self, id_usuario=None, nombre_completo="", correo="",
                 telefono="", contrasena="", id_cliente=None,
                 preferencias="", puntos_fidelidad=0):
        super().__init__(id_usuario, nombre_completo, correo, telefono, contrasena)
        self._id_cliente = id_cliente
        self._preferencias = preferencias
        self._puntos_fidelidad = puntos_fidelidad
        self._reservas = []

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        self._id_cliente = valor

    @property
    def preferencias(self):
        return self._preferencias

    @preferencias.setter
    def preferencias(self, valor):
        self._preferencias = valor

    @property
    def puntos_fidelidad(self):
        return self._puntos_fidelidad

    @puntos_fidelidad.setter
    def puntos_fidelidad(self, valor):
        if valor < 0:
            raise ValueError("Los puntos de fidelidad no pueden ser negativos.")
        self._puntos_fidelidad = valor

    @property
    def reservas(self):
        return list(self._reservas)

    def solicitarReserva(self, reserva):
        reserva.id_cliente = self._id_cliente
        self._reservas.append(reserva)
        print(f"[Cliente] {self.nombre_completo} solicito una reserva.")

    def cancelarReserva(self, id_reserva):
        for reserva in self._reservas:
            if reserva.id_reserva == id_reserva:
                return reserva.actualizarEstado("Cancelada")
        return False
'@ | Set-Content -Path "dominio\cliente.py" -Encoding UTF8

# ---------- dominio/empleado.py ----------
@'
"""Clase Empleado - hereda de Usuario (reutilizacion de codigo)."""
from dominio.usuario import Usuario


class Empleado(Usuario):
    def __init__(self, id_usuario=None, nombre_completo="", correo="",
                 telefono="", contrasena="", id_empleado=None,
                 cargo="", turno=""):
        super().__init__(id_usuario, nombre_completo, correo, telefono, contrasena)
        self._id_empleado = id_empleado
        self._cargo = cargo
        self._turno = turno
        self._mesas_asignadas = []

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

    def aprobarReserva(self, reserva):
        return reserva.actualizarEstado("Confirmada")

    def gestionarMesas(self):
        print(f"[Empleado] {self.nombre_completo} gestiona {len(self._mesas_asignadas)} mesa(s).")
'@ | Set-Content -Path "dominio\empleado.py" -Encoding UTF8

# ---------- dominio/restaurant.py ----------
@'
"""Clase Restaurant."""


class Restaurant:
    def __init__(self, id_restaurant=None, nombre="", direccion="",
                 telefono="", horario_apertura=None, horario_cierre=None):
        self._id_restaurant = id_restaurant
        self._nombre = nombre
        self._direccion = direccion
        self._telefono = telefono
        self._horario_apertura = horario_apertura
        self._horario_cierre = horario_cierre
        self._zonas = []
        self._jornada_abierta = False

    @property
    def id_restaurant(self):
        return self._id_restaurant

    @id_restaurant.setter
    def id_restaurant(self, valor):
        self._id_restaurant = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = valor

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        self._direccion = valor

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = valor

    @property
    def horario_apertura(self):
        return self._horario_apertura

    @horario_apertura.setter
    def horario_apertura(self, valor):
        self._horario_apertura = valor

    @property
    def horario_cierre(self):
        return self._horario_cierre

    @horario_cierre.setter
    def horario_cierre(self, valor):
        self._horario_cierre = valor

    @property
    def zonas(self):
        return list(self._zonas)

    def agregarZona(self, zona):
        zona.id_restaurant = self._id_restaurant
        self._zonas.append(zona)

    def abrirJornada(self):
        self._jornada_abierta = True
        print(f"[Restaurant] {self._nombre}: jornada iniciada.")

    def cerrarJornada(self):
        self._jornada_abierta = False
        print(f"[Restaurant] {self._nombre}: jornada finalizada.")
'@ | Set-Content -Path "dominio\restaurant.py" -Encoding UTF8

# ---------- dominio/zona.py ----------
@'
"""Clase Zona."""


class Zona:
    def __init__(self, id_zona=None, id_restaurant=None, nombre_zona="",
                 permite_fumadores=False):
        self._id_zona = id_zona
        self._id_restaurant = id_restaurant
        self._nombre_zona = nombre_zona
        self._permite_fumadores = permite_fumadores
        self._mesas = []

    @property
    def id_zona(self):
        return self._id_zona

    @id_zona.setter
    def id_zona(self, valor):
        self._id_zona = valor

    @property
    def id_restaurant(self):
        return self._id_restaurant

    @id_restaurant.setter
    def id_restaurant(self, valor):
        self._id_restaurant = valor

    @property
    def nombre_zona(self):
        return self._nombre_zona

    @nombre_zona.setter
    def nombre_zona(self, valor):
        self._nombre_zona = valor

    @property
    def permite_fumadores(self):
        return self._permite_fumadores

    @permite_fumadores.setter
    def permite_fumadores(self, valor):
        self._permite_fumadores = bool(valor)

    def agregarMesa(self, mesa):
        mesa.id_zona = self._id_zona
        self._mesas.append(mesa)

    def obtenerMesas(self):
        return list(self._mesas)
'@ | Set-Content -Path "dominio\zona.py" -Encoding UTF8

# ---------- dominio/mesa.py ----------
@'
"""Clase Mesa."""


class Mesa:
    def __init__(self, id_mesa=None, id_zona=None, numero_mesa=0,
                 capacidad=0, activa=True):
        self._id_mesa = id_mesa
        self._id_zona = id_zona
        self._numero_mesa = numero_mesa
        self._capacidad = capacidad
        self._activa = activa
        self._disponibilidades = []
        self._reserva_actual = None

    @property
    def id_mesa(self):
        return self._id_mesa

    @id_mesa.setter
    def id_mesa(self, valor):
        self._id_mesa = valor

    @property
    def id_zona(self):
        return self._id_zona

    @id_zona.setter
    def id_zona(self, valor):
        self._id_zona = valor

    @property
    def numero_mesa(self):
        return self._numero_mesa

    @numero_mesa.setter
    def numero_mesa(self, valor):
        self._numero_mesa = valor

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if valor <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")
        self._capacidad = valor

    @property
    def activa(self):
        return self._activa

    @activa.setter
    def activa(self, valor):
        self._activa = bool(valor)

    def asignarReserva(self, reserva):
        self._reserva_actual = reserva
        print(f"[Mesa {self._numero_mesa}] Reserva asignada.")

    def liberar(self):
        self._reserva_actual = None
        print(f"[Mesa {self._numero_mesa}] Liberada.")
'@ | Set-Content -Path "dominio\mesa.py" -Encoding UTF8

# ---------- dominio/reserva.py ----------
@'
"""Clase Reserva."""
from datetime import datetime


class Reserva:
    ESTADOS_VALIDOS = {"Pendiente", "Confirmada", "Cancelada", "Completada"}
    TRANSICIONES = {
        "Pendiente": {"Confirmada", "Cancelada"},
        "Confirmada": {"Completada", "Cancelada"},
        "Cancelada": set(),
        "Completada": set(),
    }

    def __init__(self, id_reserva=None, id_cliente=None, fecha_creacion=None,
                 cant_personas=1, estado="Pendiente", observaciones=""):
        self._id_reserva = id_reserva
        self._id_cliente = id_cliente
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._cant_personas = cant_personas
        self._estado = estado
        self._observaciones = observaciones
        self._disponibilidades = []

    @property
    def id_reserva(self):
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        self._id_reserva = valor

    @property
    def id_cliente(self):
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(self, valor):
        self._id_cliente = valor

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @property
    def cant_personas(self):
        return self._cant_personas

    @cant_personas.setter
    def cant_personas(self, valor):
        if valor < 1:
            raise ValueError("La cantidad de personas debe ser al menos 1.")
        self._cant_personas = valor

    @property
    def estado(self):
        return self._estado

    @property
    def observaciones(self):
        return self._observaciones

    @observaciones.setter
    def observaciones(self, valor):
        self._observaciones = valor

    def crear(self):
        if self._id_cliente is None:
            return False
        if self._cant_personas < 1:
            return False
        self._estado = "Pendiente"
        return True

    def actualizarEstado(self, nuevo_estado):
        if nuevo_estado not in self.ESTADOS_VALIDOS:
            return False
        if nuevo_estado not in self.TRANSICIONES.get(self._estado, set()):
            return False
        self._estado = nuevo_estado
        return True

    def agregarDisponibilidad(self, disponibilidad):
        disponibilidad.id_reserva = self._id_reserva
        self._disponibilidades.append(disponibilidad)
'@ | Set-Content -Path "dominio\reserva.py" -Encoding UTF8

# ---------- dominio/disponibilidad.py ----------
@'
"""Clase Disponibilidad."""


class Disponibilidad:
    def __init__(self, id_disponibilidad=None, id_mesa=None, id_reserva=None,
                 fecha=None, hora_inicio=None, hora_fin=None,
                 estado_franja="Disponible"):
        self._id_disponibilidad = id_disponibilidad
        self._id_mesa = id_mesa
        self._id_reserva = id_reserva
        self._fecha = fecha
        self._hora_inicio = hora_inicio
        self._hora_fin = hora_fin
        self._estado_franja = estado_franja

    @property
    def id_disponibilidad(self):
        return self._id_disponibilidad

    @id_disponibilidad.setter
    def id_disponibilidad(self, valor):
        self._id_disponibilidad = valor

    @property
    def id_mesa(self):
        return self._id_mesa

    @id_mesa.setter
    def id_mesa(self, valor):
        self._id_mesa = valor

    @property
    def id_reserva(self):
        return self._id_reserva

    @id_reserva.setter
    def id_reserva(self, valor):
        self._id_reserva = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        self._fecha = valor

    @property
    def hora_inicio(self):
        return self._hora_inicio

    @hora_inicio.setter
    def hora_inicio(self, valor):
        self._hora_inicio = valor

    @property
    def hora_fin(self):
        return self._hora_fin

    @hora_fin.setter
    def hora_fin(self, valor):
        self._hora_fin = valor

    @property
    def estado_franja(self):
        return self._estado_franja

    def verificarEstado(self):
        return self._estado_franja.strip().lower() == "disponible"

    def bloquearHorario(self):
        self._estado_franja = "Bloqueado"
'@ | Set-Content -Path "dominio\disponibilidad.py" -Encoding UTF8

# ---------- repositorios/__init__.py ----------
New-Item -ItemType File -Force -Path "repositorios\__init__.py" | Out-Null

# ---------- repositorios/base_repositorio.py ----------
@'
"""
Repositorio base: centraliza operaciones CRUD comunes para
evitar duplicar codigo en cada repositorio especifico.
"""


class BaseRepositorio:
    modelo_orm = None

    @classmethod
    def listar_todos(cls):
        return list(cls.modelo_orm.select())

    @classmethod
    def eliminar(cls, id_valor):
        registro = cls.modelo_orm.get_or_none(
            cls.modelo_orm._meta.primary_key == id_valor
        )
        if registro is None:
            return False
        registro.delete_instance(recursive=True)
        return True

    @classmethod
    def contar(cls):
        return cls.modelo_orm.select().count()
'@ | Set-Content -Path "repositorios\base_repositorio.py" -Encoding UTF8

# ---------- repositorios/usuario_repositorio.py ----------
@'
from datos.modelos.orm_models import UsuarioORM
from dominio.usuario import Usuario
from repositorios.base_repositorio import BaseRepositorio


class UsuarioRepositorio(BaseRepositorio):
    modelo_orm = UsuarioORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Usuario(
            id_usuario=registro.id_usuario,
            nombre_completo=registro.nombre_completo,
            correo=registro.correo,
            telefono=registro.telefono,
            contrasena=registro.contrasena,
        )

    @classmethod
    def crear(cls, usuario):
        registro = cls.modelo_orm.create(
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
        )
        usuario.id_usuario = registro.id_usuario
        return usuario

    @classmethod
    def obtener_por_id(cls, id_usuario):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_usuario == id_usuario)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]
'@ | Set-Content -Path "repositorios\usuario_repositorio.py" -Encoding UTF8

# ---------- repositorios/cliente_repositorio.py ----------
@'
from datos.modelos.orm_models import ClienteORM, UsuarioORM
from dominio.cliente import Cliente
from repositorios.base_repositorio import BaseRepositorio


class ClienteRepositorio(BaseRepositorio):
    modelo_orm = ClienteORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        usuario = registro.usuario
        return Cliente(
            id_usuario=usuario.id_usuario,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
            id_cliente=registro.id_cliente,
            preferencias=registro.preferencias,
            puntos_fidelidad=registro.puntos_fidelidad,
        )

    @classmethod
    def crear(cls, cliente):
        usuario_registro = UsuarioORM.create(
            nombre_completo=cliente.nombre_completo,
            correo=cliente.correo,
            telefono=cliente.telefono,
            contrasena=cliente.contrasena,
        )
        cliente.id_usuario = usuario_registro.id_usuario

        cliente_registro = cls.modelo_orm.create(
            usuario=usuario_registro,
            preferencias=cliente.preferencias,
            puntos_fidelidad=cliente.puntos_fidelidad,
        )
        cliente.id_cliente = cliente_registro.id_cliente
        return cliente

    @classmethod
    def obtener_por_id(cls, id_cliente):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_cliente == id_cliente)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]

    @classmethod
    def actualizar_puntos(cls, id_cliente, nuevos_puntos):
        filas = (cls.modelo_orm.update(puntos_fidelidad=nuevos_puntos)
                 .where(cls.modelo_orm.id_cliente == id_cliente).execute())
        return filas > 0
'@ | Set-Content -Path "repositorios\cliente_repositorio.py" -Encoding UTF8

# ---------- repositorios/empleado_repositorio.py ----------
@'
from datos.modelos.orm_models import EmpleadoORM, UsuarioORM
from dominio.empleado import Empleado
from repositorios.base_repositorio import BaseRepositorio


class EmpleadoRepositorio(BaseRepositorio):
    modelo_orm = EmpleadoORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        usuario = registro.usuario
        return Empleado(
            id_usuario=usuario.id_usuario,
            nombre_completo=usuario.nombre_completo,
            correo=usuario.correo,
            telefono=usuario.telefono,
            contrasena=usuario.contrasena,
            id_empleado=registro.id_empleado,
            cargo=registro.cargo,
            turno=registro.turno,
        )

    @classmethod
    def crear(cls, empleado):
        usuario_registro = UsuarioORM.create(
            nombre_completo=empleado.nombre_completo,
            correo=empleado.correo,
            telefono=empleado.telefono,
            contrasena=empleado.contrasena,
        )
        empleado.id_usuario = usuario_registro.id_usuario

        empleado_registro = cls.modelo_orm.create(
            usuario=usuario_registro,
            cargo=empleado.cargo,
            turno=empleado.turno,
        )
        empleado.id_empleado = empleado_registro.id_empleado
        return empleado

    @classmethod
    def obtener_por_id(cls, id_empleado):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_empleado == id_empleado)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]
'@ | Set-Content -Path "repositorios\empleado_repositorio.py" -Encoding UTF8

# ---------- repositorios/restaurant_repositorio.py ----------
@'
from datos.modelos.orm_models import RestaurantORM
from dominio.restaurant import Restaurant
from repositorios.base_repositorio import BaseRepositorio


class RestaurantRepositorio(BaseRepositorio):
    modelo_orm = RestaurantORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Restaurant(
            id_restaurant=registro.id_restaurant,
            nombre=registro.nombre,
            direccion=registro.direccion,
            telefono=registro.telefono,
            horario_apertura=registro.horario_apertura,
            horario_cierre=registro.horario_cierre,
        )

    @classmethod
    def crear(cls, restaurant):
        registro = cls.modelo_orm.create(
            nombre=restaurant.nombre,
            direccion=restaurant.direccion,
            telefono=restaurant.telefono,
            horario_apertura=restaurant.horario_apertura,
            horario_cierre=restaurant.horario_cierre,
        )
        restaurant.id_restaurant = registro.id_restaurant
        return restaurant

    @classmethod
    def obtener_por_id(cls, id_restaurant):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_restaurant == id_restaurant)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todos(cls):
        return [cls._a_dominio(r) for r in cls.modelo_orm.select()]
'@ | Set-Content -Path "repositorios\restaurant_repositorio.py" -Encoding UTF8

# ---------- repositorios/zona_repositorio.py ----------
@'
from datos.modelos.orm_models import ZonaORM
from dominio.zona import Zona
from repositorios.base_repositorio import BaseRepositorio


class ZonaRepositorio(BaseRepositorio):
    modelo_orm = ZonaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Zona(
            id_zona=registro.id_zona,
            id_restaurant=registro.restaurant.id_restaurant,
            nombre_zona=registro.nombre_zona,
            permite_fumadores=registro.permite_fumadores,
        )

    @classmethod
    def crear(cls, zona):
        registro = cls.modelo_orm.create(
            restaurant=zona.id_restaurant,
            nombre_zona=zona.nombre_zona,
            permite_fumadores=zona.permite_fumadores,
        )
        zona.id_zona = registro.id_zona
        return zona

    @classmethod
    def obtener_por_id(cls, id_zona):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_zona == id_zona)
        return cls._a_dominio(registro)

    @classmethod
    def listar_por_restaurant(cls, id_restaurant):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.restaurant == id_restaurant)
        return [cls._a_dominio(r) for r in consulta]
'@ | Set-Content -Path "repositorios\zona_repositorio.py" -Encoding UTF8

# ---------- repositorios/mesa_repositorio.py ----------
@'
from datos.modelos.orm_models import MesaORM
from dominio.mesa import Mesa
from repositorios.base_repositorio import BaseRepositorio


class MesaRepositorio(BaseRepositorio):
    modelo_orm = MesaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Mesa(
            id_mesa=registro.id_mesa,
            id_zona=registro.zona.id_zona,
            numero_mesa=registro.numero_mesa,
            capacidad=registro.capacidad,
            activa=registro.activa,
        )

    @classmethod
    def crear(cls, mesa):
        registro = cls.modelo_orm.create(
            zona=mesa.id_zona,
            numero_mesa=mesa.numero_mesa,
            capacidad=mesa.capacidad,
            activa=mesa.activa,
        )
        mesa.id_mesa = registro.id_mesa
        return mesa

    @classmethod
    def obtener_por_id(cls, id_mesa):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_mesa == id_mesa)
        return cls._a_dominio(registro)

    @classmethod
    def listar_por_zona(cls, id_zona):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.zona == id_zona)
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def listar_disponibles(cls, capacidad_minima):
        consulta = cls.modelo_orm.select().where(
            (cls.modelo_orm.activa == True)
            & (cls.modelo_orm.capacidad >= capacidad_minima)
        )
        return [cls._a_dominio(r) for r in consulta]
'@ | Set-Content -Path "repositorios\mesa_repositorio.py" -Encoding UTF8

# ---------- repositorios/disponibilidad_repositorio.py ----------
@'
from datos.modelos.orm_models import DisponibilidadORM
from dominio.disponibilidad import Disponibilidad
from repositorios.base_repositorio import BaseRepositorio


class DisponibilidadRepositorio(BaseRepositorio):
    modelo_orm = DisponibilidadORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Disponibilidad(
            id_disponibilidad=registro.id_disponibilidad,
            id_mesa=registro.mesa.id_mesa,
            id_reserva=registro.reserva.id_reserva if registro.reserva else None,
            fecha=registro.fecha,
            hora_inicio=registro.hora_inicio,
            hora_fin=registro.hora_fin,
            estado_franja=registro.estado_franja,
        )

    @classmethod
    def crear(cls, disponibilidad):
        registro = cls.modelo_orm.create(
            mesa=disponibilidad.id_mesa,
            reserva=disponibilidad.id_reserva,
            fecha=disponibilidad.fecha,
            hora_inicio=disponibilidad.hora_inicio,
            hora_fin=disponibilidad.hora_fin,
            estado_franja=disponibilidad.estado_franja,
        )
        disponibilidad.id_disponibilidad = registro.id_disponibilidad
        return disponibilidad

    @classmethod
    def buscar_franja_disponible(cls, id_mesa, fecha, hora_inicio, hora_fin):
        registro = (cls.modelo_orm.select()
                    .where((cls.modelo_orm.mesa == id_mesa)
                           & (cls.modelo_orm.fecha == fecha)
                           & (cls.modelo_orm.hora_inicio <= hora_inicio)
                           & (cls.modelo_orm.hora_fin >= hora_fin)
                           & (cls.modelo_orm.estado_franja == "Disponible"))
                    .first())
        return cls._a_dominio(registro)

    @classmethod
    def ocupar_franja(cls, id_disponibilidad, id_reserva):
        filas = (cls.modelo_orm.update(estado_franja="Ocupado", reserva=id_reserva)
                 .where(cls.modelo_orm.id_disponibilidad == id_disponibilidad).execute())
        return filas > 0

    @classmethod
    def liberar_franja(cls, id_reserva):
        filas = (cls.modelo_orm.update(estado_franja="Disponible", reserva=None)
                 .where(cls.modelo_orm.reserva == id_reserva).execute())
        return filas > 0
'@ | Set-Content -Path "repositorios\disponibilidad_repositorio.py" -Encoding UTF8

# ---------- repositorios/reserva_repositorio.py ----------
@'
from datos.modelos.orm_models import ReservaORM
from dominio.reserva import Reserva
from repositorios.base_repositorio import BaseRepositorio
from repositorios.disponibilidad_repositorio import DisponibilidadRepositorio


class ReservaRepositorio(BaseRepositorio):
    modelo_orm = ReservaORM

    @staticmethod
    def _a_dominio(registro):
        if registro is None:
            return None
        return Reserva(
            id_reserva=registro.id_reserva,
            id_cliente=registro.cliente.id_cliente,
            fecha_creacion=registro.fecha_creacion,
            cant_personas=registro.cant_personas,
            estado=registro.estado,
            observaciones=registro.observaciones,
        )

    @classmethod
    def crear(cls, reserva):
        if not reserva.crear():
            return None

        registro = cls.modelo_orm.create(
            cliente=reserva.id_cliente,
            cant_personas=reserva.cant_personas,
            estado=reserva.estado,
            observaciones=reserva.observaciones,
        )
        reserva.id_reserva = registro.id_reserva
        return reserva

    @classmethod
    def obtener_por_id(cls, id_reserva):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_reserva == id_reserva)
        return cls._a_dominio(registro)

    @classmethod
    def listar_todas(cls):
        consulta = cls.modelo_orm.select().order_by(cls.modelo_orm.id_reserva.desc())
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def listar_por_cliente(cls, id_cliente):
        consulta = cls.modelo_orm.select().where(cls.modelo_orm.cliente == id_cliente)
        return [cls._a_dominio(r) for r in consulta]

    @classmethod
    def cambiar_estado(cls, id_reserva, nuevo_estado):
        reserva = cls.obtener_por_id(id_reserva)
        if reserva is None:
            return False
        if not reserva.actualizarEstado(nuevo_estado):
            return False

        filas = (cls.modelo_orm.update(estado=nuevo_estado)
                 .where(cls.modelo_orm.id_reserva == id_reserva).execute())

        if nuevo_estado == "Cancelada":
            DisponibilidadRepositorio.liberar_franja(id_reserva)

        return filas > 0

    @classmethod
    def eliminar(cls, id_reserva):
        registro = cls.modelo_orm.get_or_none(cls.modelo_orm.id_reserva == id_reserva)
        if registro is None:
            return False
        registro.delete_instance()
        return True
'@ | Set-Content -Path "repositorios\reserva_repositorio.py" -Encoding UTF8

# ---------- main.py ----------
@'
"""
Punto de entrada del prototipo estructural.
1. Prueba de conexion a MySQL (PyMySQL + Peewee).
2. Creacion de tablas.
3. Demostracion CRUD completa usando las clases del UML.
"""
from datetime import date, time

from datos.conexion import probar_conexion, probar_conexion_pymysql
from datos.modelos.orm_models import crear_tablas

from dominio.restaurant import Restaurant
from dominio.zona import Zona
from dominio.mesa import Mesa
from dominio.cliente import Cliente
from dominio.empleado import Empleado
from dominio.reserva import Reserva
from dominio.disponibilidad import Disponibilidad

from repositorios.restaurant_repositorio import RestaurantRepositorio
from repositorios.zona_repositorio import ZonaRepositorio
from repositorios.mesa_repositorio import MesaRepositorio
from repositorios.cliente_repositorio import ClienteRepositorio
from repositorios.empleado_repositorio import EmpleadoRepositorio
from repositorios.reserva_repositorio import ReservaRepositorio
from repositorios.disponibilidad_repositorio import DisponibilidadRepositorio


def main():
    print("=" * 65)
    print(" EcoTech Solutions - Sistema de Reservas de Restaurante")
    print("=" * 65)

    print("\n--- Paso 1: Prueba de conexion a la base de datos ---")
    if not probar_conexion_pymysql():
        return
    if not probar_conexion():
        return

    print("\n--- Paso 2: Sincronizacion de tablas ---")
    crear_tablas()

    print("\n--- Paso 3: Demostracion CRUD orientada a objetos ---")

    restaurant = Restaurant(
        nombre="EcoTech Bistro",
        direccion="Av. Siempre Verde 123, Temuco",
        telefono="+56912345000",
        horario_apertura=time(12, 0),
        horario_cierre=time(23, 0),
    )
    restaurant = RestaurantRepositorio.crear(restaurant)
    print(f"[+] Restaurant creado: {restaurant.nombre} (ID {restaurant.id_restaurant})")

    zona = Zona(id_restaurant=restaurant.id_restaurant,
                nombre_zona="Terraza", permite_fumadores=False)
    restaurant.agregarZona(zona)
    zona = ZonaRepositorio.crear(zona)
    print(f"[+] Zona creada: {zona.nombre_zona} (ID {zona.id_zona})")

    mesa = Mesa(id_zona=zona.id_zona, numero_mesa=1, capacidad=4, activa=True)
    zona.agregarMesa(mesa)
    mesa = MesaRepositorio.crear(mesa)
    print(f"[+] Mesa creada: N {mesa.numero_mesa} (ID {mesa.id_mesa})")

    franja = Disponibilidad(
        id_mesa=mesa.id_mesa,
        fecha=date.today(),
        hora_inicio=time(19, 0),
        hora_fin=time(21, 0),
        estado_franja="Disponible",
    )
    franja = DisponibilidadRepositorio.crear(franja)
    print(f"[+] Franja de disponibilidad creada (ID {franja.id_disponibilidad})")

    cliente = Cliente(
        nombre_completo="Pablo Espinoza",
        correo="pablo.espinoza@correo.cl",
        telefono="+56912345678",
        contrasena="password123",
        preferencias="Sin restricciones",
        puntos_fidelidad=100,
    )
    cliente = ClienteRepositorio.crear(cliente)
    print(f"[+] Cliente creado: {cliente.nombre_completo} (ID {cliente.id_cliente})")

    empleado = Empleado(
        nombre_completo="Ana Torres",
        correo="ana.torres@ecotech.cl",
        telefono="+56987654321",
        contrasena="clave12345",
        cargo="Jefe de comedor",
        turno="Tarde",
    )
    empleado = EmpleadoRepositorio.crear(empleado)
    print(f"[+] Empleado creado: {empleado.nombre_completo} (ID {empleado.id_empleado})")

    reserva = Reserva(
        id_cliente=cliente.id_cliente,
        cant_personas=4,
        observaciones="Celebracion de cumpleanos",
    )
    cliente.solicitarReserva(reserva)
    reserva = ReservaRepositorio.crear(reserva)

    if reserva:
        print(f"[+] Reserva creada (ID {reserva.id_reserva}) - Estado: {reserva.estado}")
        DisponibilidadRepositorio.ocupar_franja(franja.id_disponibilidad, reserva.id_reserva)
        mesa.asignarReserva(reserva)

        aprobada = empleado.aprobarReserva(reserva)
        ReservaRepositorio.cambiar_estado(reserva.id_reserva, "Confirmada")
        print(f"[+] Reserva aprobada por {empleado.nombre_completo}: {aprobada}")
    else:
        print("[!] No se pudo crear la reserva.")

    print("\n--- Listado final de reservas ---")
    for r in ReservaRepositorio.listar_todas():
        print(f"  Reserva #{r.id_reserva} | Cliente {r.id_cliente} | {r.cant_personas} personas | Estado: {r.estado}")

    print("\n[OK] Prototipo estructural ejecutado correctamente.")


if __name__ == "__main__":
    main()
'@ | Set-Content -Path "main.py" -Encoding UTF8

Write-Host ""
Write-Host "=========================================="
Write-Host " TODOS LOS ARCHIVOS FUERON GENERADOS"
Write-Host "=========================================="