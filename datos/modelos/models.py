
from datetime import datetime

from peewee import (
    Model,
    AutoField,
    IntegerField,
    CharField,
    TextField,
    DateTimeField,
    DateField,
    TimeField,
    BooleanField,
    ForeignKeyField,
    CompositeKey,
)

from datos.conexion import db


# ============================================================
# MODELO BASE
# ============================================================

class BaseModel(Model):
    class Meta:
        database = db


# ============================================================
# CLASES DE DOMINIO: UML
# ============================================================

class Usuario:
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

    def iniciarSesion(self) -> bool:
        return bool(self._correo and self._contrasena)

    def cerrarSesion(self) -> None:
        pass


class Cliente(Usuario):
    def __init__(
        self,
        id_usuario=None,
        nombre_completo="",
        correo="",
        telefono="",
        contrasena="",
        preferencias="",
        puntos_fidelidad=0,
        preferencias_alimentarias=None,
    ):
        super().__init__(
            id_usuario,
            nombre_completo,
            correo,
            telefono,
            contrasena,
        )
        if preferencias_alimentarias is not None:
            preferencias = preferencias_alimentarias

        self._preferencias = preferencias
        self._puntos_fidelidad = puntos_fidelidad

    @property
    def preferencias(self):
        return self._preferencias

    @preferencias.setter
    def preferencias(self, valor):
        self._preferencias = valor

    @property
    def preferencias_alimentarias(self):
        return self._preferencias

    @preferencias_alimentarias.setter
    def preferencias_alimentarias(self, valor):
        self._preferencias = valor

    @property
    def puntos_fidelidad(self):
        return self._puntos_fidelidad

    @puntos_fidelidad.setter
    def puntos_fidelidad(self, valor):
        self._puntos_fidelidad = valor

    def solicitarReserva(self) -> None:
        pass

    def cancelarReserva(self, id_reserva) -> bool:
        return id_reserva is not None


class Empleado(Usuario):
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
            id_usuario,
            nombre_completo,
            correo,
            telefono,
            contrasena,
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

    def aprobarReserva(self, id_reserva) -> bool:
        return id_reserva is not None

    def gestionarMesas(self) -> None:
        pass


# ============================================================
# PERSISTENCIA: TABLAS MYSQL
# ============================================================

class UsuarioDB(BaseModel):
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    correo_electronico = CharField(max_length=100, unique=True)
    telefono = CharField(max_length=20, null=True)
    contrasena = CharField(max_length=255)

    class Meta:
        table_name = "usuario"

    @property
    def correo(self):
        return self.correo_electronico

    @correo.setter
    def correo(self, valor):
        self.correo_electronico = valor


class ClienteDB(BaseModel):
    id_cliente = AutoField()
    usuario = ForeignKeyField(
        UsuarioDB,
        column_name="id_usuario",
        field="id_usuario",
        backref="cliente",
        on_delete="CASCADE",
        unique=True,
    )
    preferencias_alimentarias = TextField(null=True)
    puntos_fidelidad = IntegerField(default=0)

    class Meta:
        table_name = "cliente"

    @property
    def preferencias(self):
        return self.preferencias_alimentarias

    @preferencias.setter
    def preferencias(self, valor):
        self.preferencias_alimentarias = valor


class EmpleadoDB(BaseModel):
    id_empleado = AutoField()
    usuario = ForeignKeyField(
        UsuarioDB,
        column_name="id_usuario",
        field="id_usuario",
        backref="empleado",
        on_delete="CASCADE",
        unique=True,
    )
    cargo = CharField(max_length=50)
    fecha_contratacion = DateField(null=True)

    class Meta:
        table_name = "empleado"


class Restaurant(BaseModel):
    id_restaurant = AutoField()
    nombre = CharField(max_length=100)
    direccion = CharField(max_length=200)
    telefono_contacto = CharField(max_length=20, null=True)
    horario_apertura = TimeField()
    horario_cierre = TimeField()

    class Meta:
        table_name = "restaurant"

    @property
    def telefono(self):
        return self.telefono_contacto

    @telefono.setter
    def telefono(self, valor):
        self.telefono_contacto = valor

    def abrirJornada(self) -> None:
        pass

    def cerrarJornada(self) -> None:
        pass


# Nombre público definido en el UML.
Restaurante = Restaurant


class Zona(BaseModel):
    id_zona = AutoField()
    restaurant = ForeignKeyField(
        Restaurant,
        column_name="id_restaurant",
        field="id_restaurant",
        backref="zonas",
        on_delete="CASCADE",
    )
    nombre_zona = CharField(max_length=50)
    permite_fumadores = BooleanField(null=True, default=False)

    class Meta:
        table_name = "zona"

    @property
    def id_restaurant(self):
        return self.restaurant_id

    def agregarMesa(self, numero_mesa, capacidad, activa=True):
        if capacidad < 1:
            raise ValueError("La capacidad debe ser mayor que cero.")

        return Mesa.create(
            zona=self,
            numero_mesa=numero_mesa,
            capacidad_comensales=capacidad,
            activa=activa,
        )

    def obtenerMesas(self):
        return list(Mesa.select().where(Mesa.zona == self))


class Mesa(BaseModel):
    id_mesa = AutoField()
    zona = ForeignKeyField(
        Zona,
        column_name="id_zona",
        field="id_zona",
        backref="mesas",
        on_delete="CASCADE",
    )
    numero_mesa = IntegerField()
    capacidad_comensales = IntegerField()
    activa = BooleanField(null=True, default=True)

    class Meta:
        table_name = "mesa"

    @property
    def id_zona(self):
        return self.zona_id

    @property
    def capacidad(self):
        return self.capacidad_comensales

    @capacidad.setter
    def capacidad(self, valor):
        self.capacidad_comensales = valor

    def asignarReserva(self, reserva) -> None:
        if not self.activa:
            return

        if not isinstance(reserva, Reserva):
            raise TypeError("Se requiere una instancia de Reserva.")

        franja = (
            Disponibilidad.select()
            .where(
                (Disponibilidad.mesa == self)
                & (Disponibilidad.estado_franja == "Disponible")
                & Disponibilidad.reserva.is_null()
            )
            .first()
        )

        if franja is not None:
            franja.reserva = reserva
            franja.estado_franja = "Reservada"
            franja.save()

    def liberar(self) -> None:
        # La liberación transaccional se realiza en el repositorio
        # para evitar liberar franjas de otras reservas.
        pass


class Reserva(BaseModel):
    id_reserva = AutoField()
    cliente = ForeignKeyField(
        ClienteDB,
        column_name="id_cliente",
        field="id_cliente",
        backref="reservas",
        on_delete="CASCADE",
    )
    fecha_creacion = DateTimeField(default=datetime.now)
    cantidad_personas = IntegerField()
    estado = CharField(max_length=20)
    observaciones_especiales = TextField(null=True)
    fecha_reserva = DateField(null=True)
    hora_inicio_reserva = TimeField(null=True)
    hora_fin_reserva = TimeField(null=True)
    numero_mesa_reserva = IntegerField(null=True)

    class Meta:
        table_name = "reserva"

    @property
    def id_cliente(self):
        return self.cliente_id

    @property
    def cant_personas(self):
        return self.cantidad_personas

    @cant_personas.setter
    def cant_personas(self, valor):
        self.cantidad_personas = valor

    @property
    def observaciones(self):
        return self.observaciones_especiales

    @observaciones.setter
    def observaciones(self, valor):
        self.observaciones_especiales = valor

    def crear(self) -> bool:
        if self.get_id() is not None:
            return True
        return bool(self.save(force_insert=True))

    def actualizarEstado(self, nuevo_estado) -> bool:
        from datos.repositorio.reserva_repositorio import (
            ReservaRepositorio,
        )

        resultado = ReservaRepositorio.cambiar_estado(
            self.id_reserva,
            nuevo_estado,
        )

        if resultado:
            self.estado = nuevo_estado

        return bool(resultado)


class Disponibilidad(BaseModel):
    id_disponibilidad = AutoField()
    mesa = ForeignKeyField(
        Mesa,
        column_name="id_mesa",
        field="id_mesa",
        backref="disponibilidades",
        on_delete="CASCADE",
    )
    reserva = ForeignKeyField(
        Reserva,
        column_name="id_reserva",
        field="id_reserva",
        backref="disponibilidades",
        null=True,
        on_delete="SET NULL",
    )
    fecha = DateField()
    hora_inicio = TimeField()
    hora_fin = TimeField()
    estado_franja = CharField(max_length=20)

    class Meta:
        table_name = "disponibilidad"

    @property
    def id_mesa(self):
        return self.mesa_id

    @property
    def id_reserva(self):
        return self.reserva_id

    def verificarEstado(self) -> bool:
        return self.estado_franja.strip().lower() == "disponible"

    def bloquearHorario(self, reserva=None) -> None:
        if self.estado_franja.strip().lower() != "disponible":
            return

        if reserva is not None and not isinstance(reserva, Reserva):
            raise TypeError("Se requiere una instancia de Reserva.")

        self.reserva = reserva
        self.estado_franja = "Reservada"
        self.save()


class EmpleadoRestaurant(BaseModel):
    empleado = ForeignKeyField(
        EmpleadoDB,
        column_name="id_empleado",
        field="id_empleado",
        backref="restaurantes_asignados",
        on_delete="CASCADE",
    )
    restaurant = ForeignKeyField(
        Restaurant,
        column_name="id_restaurant",
        field="id_restaurant",
        backref="empleados_asignados",
        on_delete="CASCADE",
    )
    turno = CharField(max_length=50)

    class Meta:
        table_name = "empleado_restaurant"
        primary_key = CompositeKey("empleado", "restaurant")


# ============================================================
# REGISTRO DE MODELOS
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


# ============================================================
# UTILIDADES DE BASE DE DATOS
# ============================================================

def probar_conexion():
    """Comprueba la conexión a MySQL ejecutando una consulta sencilla."""
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
    """Crea las tablas declaradas que todavía no existan."""
    db.connect(reuse_if_open=True)
    try:
        db.create_tables(MODELOS, safe=True)
    finally:
        if not db.is_closed():
            db.close()
