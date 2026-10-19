"""Menú de consola del sistema de reservas."""

from datetime import datetime, time

from datos.conexion import db
from datos.modelos.orm_models import (
    crear_tablas,
    UsuarioORM,
    ClienteORM,
    EmpleadoORM,
    DisponibilidadORM,
)
from dominio.cliente import Cliente
from dominio.empleado import Empleado
from dominio.restaurant import Restaurant
from dominio.zona import Zona
from dominio.mesa import Mesa

from repositorios.cliente_repositorio import ClienteRepositorio
from repositorios.empleado_repositorio import EmpleadoRepositorio
from repositorios.restaurant_repositorio import RestaurantRepositorio
from repositorios.zona_repositorio import ZonaRepositorio
from repositorios.mesa_repositorio import MesaRepositorio
from negocio.servicios.reserva_servicio import ReservaServicio


def leer_entero(mensaje, minimo=1):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"Introduce un número igual o mayor que {minimo}.")
                continue
            return valor
        except ValueError:
            print("Introduce un número entero válido.")


def leer_hora(mensaje):
    while True:
        try:
            return datetime.strptime(
                input(mensaje).strip(), "%H:%M"
            ).time()
        except ValueError:
            print("Formato incorrecto. Usa HH:MM, por ejemplo 19:30.")


def leer_si_no(mensaje):
    while True:
        respuesta = input(mensaje + " (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta == "n":
            return False
        print("Responde s o n.")


def listar_clientes():
    clientes = ClienteRepositorio.listar_todos()
    print("\n=== CLIENTES ===")
    if not clientes:
        print("No hay clientes registrados.")
        return

    for c in clientes:
        print(
            f"ID {c.id_cliente} | {c.nombre_completo} | "
            f"{c.correo} | Teléfono: {c.telefono or '-'} | "
            f"Puntos: {c.puntos_fidelidad}"
        )


def crear_cliente():
    print("\n=== REGISTRAR CLIENTE ===")
    nombre = input("Nombre completo: ").strip()
    correo = input("Correo: ").strip().lower()
    telefono = input("Teléfono (opcional): ").strip()
    contrasena = input("Contraseña: ")
    preferencias = input("Preferencias (opcional): ").strip()

    if not nombre or not correo or not contrasena:
        raise ValueError("Nombre, correo y contraseña son obligatorios.")

    if UsuarioORM.get_or_none(UsuarioORM.correo == correo):
        raise ValueError(
            "Ese correo ya pertenece a un usuario. "
            "No se creó otro perfil."
        )

    cliente = Cliente(
        nombre_completo=nombre,
        correo=correo,
        telefono=telefono,
        contrasena=contrasena,
        preferencias=preferencias,
        puntos_fidelidad=0,
    )
    creado = ClienteRepositorio.crear(cliente)
    print(f"Cliente registrado. ID: {creado.id_cliente}")


def actualizar_puntos_cliente():
    listar_clientes()
    id_cliente = leer_entero("ID del cliente: ")
    puntos = leer_entero("Nuevo saldo de puntos (0 o más): ", minimo=0)

    if ClienteRepositorio.obtener_por_id(id_cliente) is None:
        print("No existe ese cliente.")
        return

    if ClienteRepositorio.actualizar_puntos(id_cliente, puntos):
        print("Puntos actualizados.")
    else:
        print("No se pudieron actualizar los puntos.")


def listar_empleados():
    empleados = EmpleadoRepositorio.listar_todos()
    print("\n=== EMPLEADOS ===")
    if not empleados:
        print("No hay empleados registrados.")
        return

    for e in empleados:
        print(
            f"ID {e.id_empleado} | {e.nombre_completo} | "
            f"{e.correo} | Cargo: {e.cargo} | Turno: {e.turno or '-'}"
        )


def crear_empleado():
    print("\n=== REGISTRAR EMPLEADO ===")
    nombre = input("Nombre completo: ").strip()
    correo = input("Correo: ").strip().lower()
    telefono = input("Teléfono (opcional): ").strip()
    contrasena = input("Contraseña: ")
    cargo = input("Cargo: ").strip()
    turno = input("Turno (opcional): ").strip()

    if not nombre or not correo or not contrasena or not cargo:
        raise ValueError(
            "Nombre, correo, contraseña y cargo son obligatorios."
        )

    if UsuarioORM.get_or_none(UsuarioORM.correo == correo):
        raise ValueError(
            "Ese correo ya pertenece a un usuario. "
            "No se creó otro perfil."
        )

    empleado = Empleado(
        nombre_completo=nombre,
        correo=correo,
        telefono=telefono,
        contrasena=contrasena,
        cargo=cargo,
        turno=turno,
    )
    creado = EmpleadoRepositorio.crear(empleado)
    print(f"Empleado registrado. ID: {creado.id_empleado}")


def listar_restaurantes():
    restaurantes = RestaurantRepositorio.listar_todos()
    print("\n=== RESTAURANTES ===")
    if not restaurantes:
        print("No hay restaurantes registrados.")
        return

    for r in restaurantes:
        print(
            f"ID {r.id_restaurant} | {r.nombre} | {r.direccion} | "
            f"Horario: {r.horario_apertura}-{r.horario_cierre}"
        )


def crear_restaurante():
    print("\n=== REGISTRAR RESTAURANTE ===")
    nombre = input("Nombre: ").strip()
    direccion = input("Dirección: ").strip()
    telefono = input("Teléfono (opcional): ").strip()
    apertura = leer_hora("Hora de apertura (HH:MM): ")
    cierre = leer_hora("Hora de cierre (HH:MM): ")

    if not nombre or not direccion:
        raise ValueError("El nombre y la dirección son obligatorios.")

    existentes = RestaurantRepositorio.listar_todos()
    duplicado = any(
        r.nombre.strip().casefold() == nombre.casefold()
        and r.direccion.strip().casefold() == direccion.casefold()
        for r in existentes
    )
    if duplicado:
        raise ValueError(
            "Ya existe un restaurante con ese nombre y dirección. "
            "No se creó otro registro."
        )

    if apertura >= cierre:
        raise ValueError(
            "La hora de apertura debe ser anterior al cierre."
        )

    restaurant = Restaurant(
        nombre=nombre,
        direccion=direccion,
        telefono=telefono,
        horario_apertura=apertura,
        horario_cierre=cierre,
    )
    creado = RestaurantRepositorio.crear(restaurant)
    print(f"Restaurante registrado. ID: {creado.id_restaurant}")


def crear_zona():
    listar_restaurantes()
    id_restaurant = leer_entero("ID del restaurante: ")

    if RestaurantRepositorio.obtener_por_id(id_restaurant) is None:
        raise ValueError("El restaurante no existe.")

    nombre = input("Nombre de la zona: ").strip()
    if not nombre:
        raise ValueError("El nombre de la zona es obligatorio.")

    zona = Zona(
        id_restaurant=id_restaurant,
        nombre_zona=nombre,
        permite_fumadores=leer_si_no("¿Permite fumar?"),
    )
    creada = ZonaRepositorio.crear(zona)
    print(f"Zona registrada. ID: {creada.id_zona}")


def listar_zonas():
    listar_restaurantes()
    id_restaurant = leer_entero("ID del restaurante: ")

    if RestaurantRepositorio.obtener_por_id(id_restaurant) is None:
        raise ValueError("El restaurante no existe.")

    zonas = ZonaRepositorio.listar_por_restaurant(id_restaurant)
    print("\n=== ZONAS ===")
    if not zonas:
        print("Este restaurante no tiene zonas registradas.")
        return

    for z in zonas:
        print(
            f"ID {z.id_zona} | {z.nombre_zona} | "
            f"Permite fumar: {'Sí' if z.permite_fumadores else 'No'}"
        )


def crear_mesa():
    listar_restaurantes()
    id_restaurant = leer_entero("ID del restaurante: ")

    if RestaurantRepositorio.obtener_por_id(id_restaurant) is None:
        raise ValueError("El restaurante no existe.")

    zonas = ZonaRepositorio.listar_por_restaurant(id_restaurant)
    if not zonas:
        print("Primero debes registrar una zona para ese restaurante.")
        return

    print("\n=== ZONAS DISPONIBLES ===")
    for z in zonas:
        print(f"ID {z.id_zona} | {z.nombre_zona}")

    id_zona = leer_entero("ID de la zona: ")
    zona = ZonaRepositorio.obtener_por_id(id_zona)

    if zona is None or zona.id_restaurant != id_restaurant:
        raise ValueError("La zona no pertenece a ese restaurante.")

    numero = leer_entero("Número de mesa: ")
    capacidad = leer_entero("Capacidad de personas: ")

    mesa = Mesa(
        id_zona=id_zona,
        numero_mesa=numero,
        capacidad=capacidad,
        activa=True,
    )
    creada = MesaRepositorio.crear(mesa)
    print(f"Mesa registrada. ID: {creada.id_mesa}")


def listar_mesas():
    listar_restaurantes()
    id_restaurant = leer_entero("ID del restaurante: ")

    if RestaurantRepositorio.obtener_por_id(id_restaurant) is None:
        raise ValueError("El restaurante no existe.")

    zonas = ZonaRepositorio.listar_por_restaurant(id_restaurant)
    if not zonas:
        print("No hay zonas registradas.")
        return

    print("\n=== MESAS ===")
    for z in zonas:
        print(f"\nZona {z.nombre_zona} (ID {z.id_zona})")
        mesas = MesaRepositorio.listar_por_zona(z.id_zona)
        if not mesas:
            print("  Sin mesas.")
            continue

        for m in mesas:
            print(
                f"  ID {m.id_mesa} | Mesa {m.numero_mesa} | "
                f"Capacidad: {m.capacidad} | "
                f"Activa: {'Sí' if m.activa else 'No'}"
            )


def listar_disponibilidades():
    print("\n=== FRANJAS DE DISPONIBILIDAD ===")
    consulta = (
        DisponibilidadORM
        .select()
        .order_by(
            DisponibilidadORM.fecha,
            DisponibilidadORM.hora_inicio,
        )
    )

    hay_franjas = False
    for f in consulta:
        hay_franjas = True
        print(
            f"ID {f.id_disponibilidad} | Mesa {f.mesa.id_mesa} | "
            f"Fecha {f.fecha} | {f.hora_inicio}-{f.hora_fin} | "
            f"Estado: {f.estado_franja}"
        )

    if not hay_franjas:
        print("No hay franjas registradas.")


def listar_reservas():
    reservas = ReservaServicio.listar_reservas()
    print("\n=== RESERVAS ===")

    if not reservas:
        print("No hay reservas registradas.")
        return

    for r in reservas:
        print(
            f"ID {r.id_reserva} | Cliente {r.id_cliente} | "
            f"Personas: {r.cant_personas} | Estado: {r.estado} | "
            f"Creación: {r.fecha_creacion}"
        )


def crear_reserva():
    print("\n=== CREAR RESERVA ===")
    listar_clientes()
    listar_disponibilidades()

    id_cliente = leer_entero("ID del cliente: ")
    id_franja = leer_entero("ID de la franja: ")
    personas = leer_entero("Cantidad de personas: ")
    observaciones = input("Observaciones (opcional): ").strip()

    reserva = ReservaServicio.crear_reserva(
        id_cliente=id_cliente,
        id_disponibilidad=id_franja,
        cant_personas=personas,
        observaciones=observaciones,
    )
    print(f"Reserva creada correctamente. ID: {reserva.id_reserva}")


def cambiar_estado_reserva():
    listar_reservas()
    id_reserva = leer_entero("ID de la reserva: ")

    print("1. Confirmar")
    print("2. Cancelar")
    print("3. Completar")
    opcion = input("Selecciona una opción: ").strip()

    estados = {
        "1": "Confirmada",
        "2": "Cancelada",
        "3": "Completada",
    }
    nuevo_estado = estados.get(opcion)

    if nuevo_estado is None:
        print("Opción no válida.")
        return

    if ReservaServicio.cambiar_estado(id_reserva, nuevo_estado):
        print("Estado actualizado correctamente.")
    else:
        print("No se pudo actualizar el estado. Comprueba la transición.")


def mostrar_menu():
    print("\n" + "=" * 52)
    print("       SISTEMA DE RESERVAS DE RESTAURANTE")
    print("=" * 52)
    print("  CLIENTES")
    print("  1. Listar clientes")
    print("  2. Registrar cliente")
    print("  3. Actualizar puntos de fidelidad")
    print("  EMPLEADOS")
    print("  4. Listar empleados")
    print("  5. Registrar empleado")
    print("  RESTAURANTE")
    print("  6. Listar restaurantes")
    print("  7. Registrar restaurante")
    print("  8. Listar zonas de un restaurante")
    print("  9. Registrar zona")
    print(" 10. Listar mesas de un restaurante")
    print(" 11. Registrar mesa")
    print("  DISPONIBILIDAD Y RESERVAS")
    print(" 12. Listar franjas")
    print(" 13. Listar reservas")
    print(" 14. Crear reserva")
    print(" 15. Cambiar estado de reserva")
    print("  0. Salir")
    print("=" * 52)


def ejecutar_menu():
    try:
        if db.is_closed():
            db.connect()

        crear_tablas()

        acciones = {
            "1": listar_clientes,
            "2": crear_cliente,
            "3": actualizar_puntos_cliente,
            "4": listar_empleados,
            "5": crear_empleado,
            "6": listar_restaurantes,
            "7": crear_restaurante,
            "8": listar_zonas,
            "9": crear_zona,
            "10": listar_mesas,
            "11": crear_mesa,
            "12": listar_disponibilidades,
            "13": listar_reservas,
            "14": crear_reserva,
            "15": cambiar_estado_reserva,
        }

        while True:
            mostrar_menu()
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "0":
                print("Saliendo del sistema.")
                break

            accion = acciones.get(opcion)
            if accion is None:
                print("Opción no válida.")
                continue

            try:
                accion()
            except (ValueError, TypeError) as error:
                print(f"Operación no completada: {error}")
            except Exception as error:
                print(
                    f"Error: {type(error).__name__}: {error}"
                )

    except Exception as error:
        print(
            f"No se pudo iniciar el sistema: "
            f"{type(error).__name__}: {error}"
        )
    finally:
        if not db.is_closed():
            db.close()

