
from datetime import date, time

from peewee import DoesNotExist

from datos.conexion import probar_conexion, probar_conexion_pymysql, db
from datos.modelos.orm_models import (
    crear_tablas,
    RestaurantORM,
    ZonaORM,
    MesaORM,
    DisponibilidadORM,
    ReservaORM,
)

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


def obtener_o_crear_restaurante():
    registro = RestaurantORM.get_or_none(
        RestaurantORM.nombre == "EcoTech Bistro"
    )

    if registro:
        return RestaurantRepositorio.obtener_por_id(registro.id_restaurant)

    restaurant = Restaurant(
        nombre="EcoTech Bistro",
        direccion="Av. Siempre Verde 123, Temuco",
        telefono="+56912345000",
        horario_apertura=time(12, 0),
        horario_cierre=time(23, 0),
    )
    return RestaurantRepositorio.crear(restaurant)


def obtener_o_crear_zona(restaurant):
    registro = ZonaORM.get_or_none(
        (ZonaORM.restaurant == restaurant.id_restaurant)
        & (ZonaORM.nombre_zona == "Terraza")
    )

    if registro:
        return ZonaRepositorio.obtener_por_id(registro.id_zona)

    zona = Zona(
        id_restaurant=restaurant.id_restaurant,
        nombre_zona="Terraza",
        permite_fumadores=False,
    )
    restaurant.agregarZona(zona)
    return ZonaRepositorio.crear(zona)


def obtener_o_crear_mesa(zona):
    registro = MesaORM.get_or_none(
        (MesaORM.zona == zona.id_zona)
        & (MesaORM.numero_mesa == 1)
    )

    if registro:
        return MesaRepositorio.obtener_por_id(registro.id_mesa)

    mesa = Mesa(
        id_zona=zona.id_zona,
        numero_mesa=1,
        capacidad=4,
        activa=True,
    )
    zona.agregarMesa(mesa)
    return MesaRepositorio.crear(mesa)


def obtener_o_crear_franja(mesa):
    hoy = date.today()

    registro = DisponibilidadORM.get_or_none(
        (DisponibilidadORM.mesa == mesa.id_mesa)
        & (DisponibilidadORM.fecha == hoy)
        & (DisponibilidadORM.hora_inicio == time(19, 0))
        & (DisponibilidadORM.hora_fin == time(21, 0))
    )

    if registro:
        return DisponibilidadRepositorio._a_dominio(registro)

    franja = Disponibilidad(
        id_mesa=mesa.id_mesa,
        fecha=hoy,
        hora_inicio=time(19, 0),
        hora_fin=time(21, 0),
        estado_franja="Disponible",
    )
    return DisponibilidadRepositorio.crear(franja)


def main():
    print("=" * 65)
    print(" EcoTech Solutions - Sistema de Reservas de Restaurante")
    print("=" * 65)

    print("\n--- Paso 1: Prueba de conexión a la base de datos ---")
    if not probar_conexion_pymysql() or not probar_conexion():
        print("[ERROR] No se pudo conectar a MySQL.")
        return

    print("\n--- Paso 2: Sincronización de tablas ---")
    crear_tablas()

    print("\n--- Paso 3: Demostración CRUD orientada a objetos ---")

    # Reutilizar restaurante, zona y mesa.
    with db.connection_context():
        restaurant = obtener_o_crear_restaurante()
        print(f"[OK] Restaurante: {restaurant.nombre} (ID {restaurant.id_restaurant})")

        zona = obtener_o_crear_zona(restaurant)
        print(f"[OK] Zona: {zona.nombre_zona} (ID {zona.id_zona})")

        mesa = obtener_o_crear_mesa(zona)
        print(f"[OK] Mesa: N{mesa.numero_mesa} (ID {mesa.id_mesa})")

        franja = obtener_o_crear_franja(mesa)
        print(
            f"[OK] Franja: {franja.fecha} "
            f"{franja.hora_inicio}-{franja.hora_fin} "
            f"(ID {franja.id_disponibilidad})"
        )

        cliente = Cliente(
            nombre_completo="Pablo Espinoza",
            correo="pablo.espinoza@correo.cl",
            telefono="+56912345678",
            contrasena="password123",
            preferencias="Sin restricciones",
            puntos_fidelidad=100,
        )
        cliente = ClienteRepositorio.crear(cliente)
        print(f"[OK] Cliente: {cliente.nombre_completo} (ID {cliente.id_cliente})")

        empleado = Empleado(
            nombre_completo="Ana Torres",
            correo="ana.torres@ecotech.cl",
            telefono="+56987654321",
            contrasena="clave12345",
            cargo="Jefe de comedor",
            turno="Tarde",
        )
        empleado = EmpleadoRepositorio.crear(empleado)
        print(f"[OK] Empleado: {empleado.nombre_completo} (ID {empleado.id_empleado})")

        # No crear reservas automáticamente en cada ejecución.
        print("\n--- Reservas existentes ---")
        reservas = ReservaRepositorio.listar_todas()

        if not reservas:
            print("No hay reservas registradas.")
        else:
            for r in reservas:
                print(
                    f"Reserva #{r.id_reserva} | Cliente {r.id_cliente} | "
                    f"{r.cant_personas} personas | Estado: {r.estado}"
                )

    print("\n[OK] Prototipo estructural ejecutado correctamente.")


if __name__ == "__main__":
    main()
