from datetime import date, time
from repositorios.cliente_repositorio import ClienteRepositorio
from repositorios.reserva_repositorio import ReservaRepositorio
from modelos.reserva import Reserva

clientes = ClienteRepositorio()
reservas = ReservaRepositorio()

cliente = clientes.buscar_por_correo("ana.prueba@mail.com")
if cliente is None:
    print("Primero ejecuta probar_cliente.py para crear a Ana.")
    raise SystemExit(1)

print("=== 1. CREAR ===")
nueva = Reserva(cliente.id_cliente, date(2026, 12, 24), time(21, 30), 4,
                observaciones="Mesa cerca de la ventana")
print("ID creada:", reservas.crear(nueva))

print("\n=== 2. LEER ===")
lista = reservas.listar_por_cliente(cliente.id_cliente)
print("Reservas de Ana:", len(lista))
for r in lista:
    print(f"  #{r.id_reserva} | {r.fecha} {r.hora} | {r.estado} | {r.cant_personas} personas")
encontrada = reservas.buscar_por_id(nueva.id_reserva)
print("Buscada por ID:", encontrada.id_reserva, encontrada.fecha, encontrada.hora)
print("Tipo de hora leída:", type(encontrada.hora))

print("\n=== 3. ACTUALIZAR ===")
encontrada.estado = "Confirmada"
encontrada.cant_personas = 6
print("Actualizada:", reservas.actualizar(encontrada))
actualizada = reservas.buscar_por_id(nueva.id_reserva)
print("Después:", actualizada.estado, "-", actualizada.cant_personas, "personas")

print("\n=== 4. ELIMINAR ===")
print("Eliminada:", reservas.eliminar(nueva.id_reserva))
print("Buscar después de eliminar:", reservas.buscar_por_id(nueva.id_reserva))

print("\n=== 5. CAMINOS DE ERROR ===")
print("Eliminar una reserva inexistente:", reservas.eliminar(99999))
fantasma = Reserva(cliente.id_cliente, date(2026, 12, 24), time(21, 30), 2, id_reserva=99999)
print("Actualizar una reserva inexistente:", reservas.actualizar(fantasma))
print("Crear con cliente inexistente:", reservas.crear(Reserva(999999, date(2026, 12, 24), time(21, 30), 2)))
try:
    Reserva(cliente.id_cliente, date(2026, 12, 24), time(21, 30), 0)
except ValueError as error:
    print("Validación de personas:", error)