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

    def iniciar_sesion(self) -> bool:
        """Valida que existan los datos mínimos para iniciar sesión.

        La autenticación real debe realizarse en el servicio de autenticación.
        """
        return bool(self.correo and self.contrasena)

    def cerrar_sesion(self) -> None:
        """La gestión real de la sesión corresponde a la capa de presentación."""
        return None

    # Alias para conservar compatibilidad con el UML y llamadas anteriores.
    iniciarSesion = iniciar_sesion  # NOSONAR
    cerrarSesion = cerrar_sesion  # NOSONAR


class Cliente(Usuario):
    """Cliente del restaurante; hereda los datos comunes de Usuario."""

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

    def solicitar_reserva(self) -> bool:
        """Indica si el cliente tiene identidad registrada para solicitar."""
        return self.id_usuario is not None

    def cancelar_reserva(self, id_reserva):
        """Valida el identificador; la cancelación real la hace el servicio."""
        return id_reserva is not None

    # Alias para conservar compatibilidad con el UML y llamadas anteriores.
    solicitarReserva = solicitar_reserva
    cancelarReserva = cancelar_reserva


class Empleado(Usuario):
    """Empleado del restaurante; hereda los datos comunes de Usuario."""

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

    def aprobar_reserva(self, id_reserva):
        """Valida que se haya indicado una reserva para gestionar."""
        return id_reserva is not None

    def gestionar_mesas(self) -> bool:
        """Indica si el empleado está identificado en el sistema."""
        return self.id_empleado is not None

    # Alias para conservar compatibilidad con el UML y llamadas anteriores.
    aprobarReserva = aprobar_reserva
    gestionarMesas = gestionar_mesas


# ============================================================
# MODELOS DE PERSISTENCIA: TABLAS MYSQL
# ============================================================

class UsuarioDB(BaseModel):
    id_usuario = AutoField()
    nombre_completo = CharField(max_length=150)
    correo_electronico = CharField(max_length=100, unique=True)
    telefono = CharField(max_length=20, null=True)
    contrasena = CharField(max_length=255)

    class Meta:
        table_name = "usuario"


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

    def abrir_jornada(self) -> bool:
        """Comprueba que el restaurante tenga un horario configurado."""
        return self.horario_apertura is not None and self.horario_cierre is not None

    def cerrar_jornada(self) -> bool:
        """Comprueba que el restaurante tenga un horario configurado."""
        return self.horario_apertura is not None and self.horario_cierre is not None

    # Alias para conservar compatibilidad con el UML y llamadas anteriores.
    abrirJornada = abrir_jornada
    cerrarJornada = cerrar_jornada


# Alias en español para coincidir con el nombre de la clase del UML.
# Se conserva Restaurant para no romper importaciones existentes.
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

    def agregar_mesa(self, numero_mesa, capacidad, activa=True):
        """Crea una mesa asociada a esta zona."""
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")

        return Mesa.create(
            zona=self,
            numero_mesa=numero_mesa,
            capacidad_comensales=capacidad,
            activa=activa,
        )

    def obtener_mesas(self):
        """Devuelve las mesas asociadas a esta zona."""
        return list(Mesa.select().where(Mesa.zona == self))

    agregarMesa = agregar_mesa
    obtenerMesas = obtener_mesas


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

    def asignar_reserva(self, reserva):
        """Asocia esta mesa con una reserva mediante una franja disponible."""
        if not self.activa:
            raise ValueError("No se puede asignar una mesa inactiva.")
        if not isinstance(reserva, Reserva):
            raise TypeError("reserva debe ser una instancia de Reserva.")

        disponibilidad = (
            Disponibilidad.select()
            .where(
                (Disponibilidad.mesa == self)
                & (Disponibilidad.estado_franja == "Disponible")
                & (Disponibilidad.reserva.is_null(True))
            )
            .first()
        )
        if disponibilidad is None:
            raise ValueError("No hay una franja disponible para esta mesa.")

        disponibilidad.reserva = reserva
        disponibilidad.estado_franja = "Reservada"
        disponibilidad.save()
        return disponibilidad

    asignarReserva = asignar_reserva

    def liberar(self):
        """No libera franjas directamente para evitar liberar reservas activas.

        La liberación debe gestionarse desde
        ReservaRepositorio.cambiar_estado(), que conoce la reserva concreta
        y solo libera sus franjas cuando se cancela.
        """
        return 0


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
    def cant_personas(self):
        """Alias del UML para cantidad_personas."""
        return self.cantidad_personas

    @cant_personas.setter
    def cant_personas(self, valor):
        self.cantidad_personas = valor

    @property
    def observaciones(self):
        """Alias del UML para observaciones_especiales."""
        return self.observaciones_especiales

    @observaciones.setter
    def observaciones(self, valor):
        self.observaciones_especiales = valor

    def crear(self):
        """Guarda la reserva si todavía no existe en la base de datos."""
        if self.id_reserva is not None:
            self.save()
            return self.id_reserva
        self.save(force_insert=True)
        return self.id_reserva

    def actualizar_estado(self, nuevo_estado):
        """Actualiza el estado usando las reglas del repositorio existente."""
        from datos.repositorio.reserva_repositorio import ReservaRepositorio

        if self.id_reserva is None:
            raise ValueError("La reserva debe guardarse antes de cambiar su estado.")

        actualizado = ReservaRepositorio.cambiar_estado(
            self.id_reserva,
            nuevo_estado,
        )
        if actualizado:
            self.estado = nuevo_estado
        return actualizado

    actualizarEstado = actualizar_estado


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

    def verificar_estado(self) -> str:
        """Devuelve el estado actual de la franja."""
        return self.estado_franja

    def bloquear_horario(self, reserva=None):
        """Marca la franja como reservada y opcionalmente la asocia."""
        if self.estado_franja != "Disponible":
            return False
        if reserva is not None and not isinstance(reserva, Reserva):
            raise TypeError("reserva debe ser una instancia de Reserva.")

        self.reserva = reserva
        self.estado_franja = "Reservada"
        self.save()
        return True

    verificarEstado = verificar_estado
    bloquearHorario = bloquear_horario


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
# UTILIDADES
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
