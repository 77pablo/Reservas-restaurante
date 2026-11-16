from datetime import date, datetime

from conexion.conexion_bd import ConexionBD
from modelos.cliente import Cliente
from modelos.reserva import Reserva
from repositorios.cliente_repositorio import ClienteRepositorio
from repositorios.reserva_repositorio import ReservaRepositorio


# ---------- Funciones para pedir datos ----------

def pedir(texto):
    return input(texto).strip()


def pedir_fecha(actual=None):
    sugerencia = f" [{actual}]" if actual else ""
    while True:
        valor = pedir(f"Fecha AAAA-MM-DD{sugerencia}: ")
        if not valor and actual:
            return actual
        try:
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            print("  [ERROR] Formato inválido. Ejemplo: 2026-12-31")
            continue
        if fecha < date.today():
            print("  [ERROR] La fecha no puede ser anterior a hoy.")
            continue
        return fecha


def pedir_hora(actual=None):
    sugerencia = f" [{actual:%H:%M}]" if actual else ""
    while True:
        valor = pedir(f"Hora HH:MM{sugerencia}: ")
        if not valor and actual:
            return actual
        try:
            return datetime.strptime(valor, "%H:%M").time()
        except ValueError:
            print("  [ERROR] Formato inválido. Ejemplo: 21:30")


def pedir_personas(actual=None):
    sugerencia = f" [{actual}]" if actual else ""
    while True:
        valor = pedir(f"Personas (1-{Reserva.MAX_PERSONAS}){sugerencia}: ")
        if not valor and actual:
            return actual
        if not valor.isdigit():
            print("  [ERROR] Debes escribir un número.")
            continue
        personas = int(valor)
        if 1 <= personas <= Reserva.MAX_PERSONAS:
            return personas
        print(f"  [ERROR] Debe estar entre 1 y {Reserva.MAX_PERSONAS}.")


# ---------- Aplicación ----------

class AplicacionReservas:
    def __init__(self):
        self._clientes = ClienteRepositorio()
        self._reservas = ReservaRepositorio()
        self._sesion = None  # Cliente con sesión iniciada, o None

    # ----- Cuenta -----

    def registrarse(self):
        print("\n--- Registro ---")
        nombre = pedir("Nombre completo: ")
        correo = pedir("Correo: ")
        telefono = pedir("Teléfono: ")
        clave = pedir("Contraseña (mínimo 6 caracteres): ")

        if not nombre or not correo or not clave:
            print("[ERROR] Nombre, correo y contraseña son obligatorios.")
            return
        if "@" not in correo:
            print("[ERROR] El correo no tiene un formato válido.")
            return
        if self._clientes.buscar_por_correo(correo) is not None:
            print("[ERROR] Ese correo ya está registrado. Inicia sesión.")
            return

        cliente = Cliente(nombre, correo, telefono)
        try:
            cliente.establecer_contrasena(clave)
        except ValueError as error:
            print(f"[ERROR] {error}")
            return

        if self._clientes.crear(cliente):
            print(f"[OK] Cuenta creada. Ya puedes iniciar sesión, {cliente.nombre_completo}.")
        else:
            print("[ERROR] No se pudo crear la cuenta.")

    def iniciar_sesion(self):
        print("\n--- Inicio de sesión ---")
        correo = pedir("Correo: ")
        clave = pedir("Contraseña: ")

        cliente = self._clientes.buscar_por_correo(correo)
        if cliente is None or not cliente.iniciar_sesion(clave):
            # No se indica cuál dato falla, para no revelar si un correo existe
            print("[ERROR] Correo o contraseña incorrectos.")
            return

        self._sesion = cliente
        print(f"[OK] Bienvenida/o, {cliente.nombre_completo}.")

    def cerrar_sesion(self):
        self._sesion.cerrar_sesion()
        self._sesion = None
        print("[OK] Sesión cerrada.")

    # ----- Reservas (solo con sesión iniciada) -----

    def ver_reservas(self):
        lista = self._reservas.listar_por_cliente(self._sesion.id_cliente)
        if lista is None:
            print("[ERROR] No se pudieron cargar las reservas. Revisa la conexión a MySQL.")
            return None
        if not lista:
            print("No tienes reservas todavía.")
            return []

        print(f"\n  {'ID':<4}{'Fecha':<12}{'Hora':<7}{'Personas':<10}{'Estado':<12}Observaciones")
        for r in lista:
            hora = f"{r.hora:%H:%M}"
            print(f"  {r.id_reserva:<4}{str(r.fecha):<12}{hora:<7}{r.cant_personas:<10}{r.estado:<12}{r.observaciones}")
        return lista

    def _elegir_reserva(self):
        """Muestra solo las reservas del cliente con sesión y pide una por ID."""
        lista = self.ver_reservas()
        if not lista:
            return None

        id_texto = pedir("ID de la reserva: ")
        if not id_texto.isdigit():
            print("[ERROR] El ID debe ser un número.")
            return None

        id_buscado = int(id_texto)
        for reserva in lista:
            if reserva.id_reserva == id_buscado:
                return reserva

        print("[ERROR] No existe una reserva con ese ID en tu cuenta.")
        return None

    def nueva_reserva(self):
        print("\n--- Nueva reserva ---")
        fecha = pedir_fecha()
        hora = pedir_hora()
        personas = pedir_personas()
        observaciones = pedir("Observaciones (opcional): ")

        reserva = Reserva(self._sesion.id_cliente, fecha, hora, personas, observaciones=observaciones)
        if self._reservas.crear(reserva):
            print(f"[OK] Reserva #{reserva.id_reserva} creada para el {fecha} a las {hora:%H:%M}.")
        else:
            print("[ERROR] No se pudo guardar la reserva.")

    def editar_reserva(self):
        reserva = self._elegir_reserva()
        if reserva is None:
            return
        if reserva.estado in ("Cancelada", "Completada"):
            print(f"[ERROR] No se puede editar una reserva {reserva.estado.lower()}.")
            return

        print("Presiona Enter para mantener el valor actual.")
        reserva.fecha = pedir_fecha(reserva.fecha)
        reserva.hora = pedir_hora(reserva.hora)
        reserva.cant_personas = pedir_personas(reserva.cant_personas)
        nuevas_observaciones = pedir(f"Observaciones [{reserva.observaciones}]: ")
        if nuevas_observaciones:
            reserva.observaciones = nuevas_observaciones

        if self._reservas.actualizar(reserva):
            print("[OK] Reserva actualizada.")
        else:
            print("[ERROR] No se pudo actualizar la reserva.")

    def eliminar_reserva(self):
        reserva = self._elegir_reserva()
        if reserva is None:
            return

        confirmacion = pedir(f"¿Eliminar la reserva #{reserva.id_reserva}? (s/n): ").lower()
        if confirmacion != "s":
            print("Operación cancelada.")
            return

        if self._reservas.eliminar(reserva.id_reserva):
            print("[OK] Reserva eliminada.")
        else:
            print("[ERROR] No se pudo eliminar la reserva.")

    # ----- Menús -----

    def _menu_visitante(self):
        print("\n=== EcoTech Reservas ===")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("0. Salir")
        opcion = pedir("Opción: ")

        if opcion == "1":
            self.registrarse()
        elif opcion == "2":
            self.iniciar_sesion()
        elif opcion == "0":
            return False
        else:
            print("[ERROR] Opción no válida.")
        return True

    def _menu_cliente(self):
        print(f"\n=== Sesión: {self._sesion.nombre_completo} ===")
        print("1. Ver mis reservas")
        print("2. Nueva reserva")
        print("3. Editar reserva")
        print("4. Eliminar reserva")
        print("5. Cerrar sesión")
        opcion = pedir("Opción: ")

        acciones = {
            "1": self.ver_reservas,
            "2": self.nueva_reserva,
            "3": self.editar_reserva,
            "4": self.eliminar_reserva,
        }
        if opcion in acciones:
            acciones[opcion]()
        elif opcion == "5":
            self.cerrar_sesion()
        else:
            print("[ERROR] Opción no válida.")
        return True

    def ejecutar(self):
        if not ConexionBD().probar_conexion():
            print("Revisa que MySQL esté encendido en XAMPP y que el archivo .env sea correcto.")
            return

        while True:
            if self._sesion is None:
                continuar = self._menu_visitante()
            else:
                continuar = self._menu_cliente()
            if not continuar:
                break
        print("¡Hasta luego!")


if __name__ == "__main__":
    AplicacionReservas().ejecutar()