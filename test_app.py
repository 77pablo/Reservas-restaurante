"""
Pruebas automáticas de la aplicación de reservas.

Cubren el camino feliz (registro, login, CRUD de reservas, logout)
y los caminos de error (datos inválidos, credenciales incorrectas,
reservas inexistentes, reservas de otro cliente).

Cómo ejecutarlas (con el venv activo y MySQL encendido en XAMPP):
    python -m unittest test_app -v

Las respuestas del teclado se simulan, así que no tienes que escribir nada.
Cada prueba crea sus propios usuarios con correos únicos y los borra al terminar.
"""
import io
import re
import unittest
import uuid
from contextlib import redirect_stdout
from datetime import date, time, timedelta
from unittest.mock import patch

from app import AplicacionReservas
from conexion.conexion_bd import ConexionBD
from modelos.reserva import Reserva

FECHA_FUTURA = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
CLAVE = "clave123"


def correo_unico():
    return f"test_{uuid.uuid4().hex[:8]}@mail.com"


class PruebaBase(unittest.TestCase):
    """Pruebas que necesitan MySQL. Si no responde, se omiten con un aviso."""

    @classmethod
    def setUpClass(cls):
        if not ConexionBD().probar_conexion():
            raise unittest.SkipTest("MySQL no responde. Enciende XAMPP y vuelve a intentar.")

    def setUp(self):
        self.app = AplicacionReservas()
        self.correos_creados = []

    def tearDown(self):
        # Al borrar el usuario, MySQL borra también su cliente y sus reservas (ON DELETE CASCADE)
        for correo in self.correos_creados:
            self.app._clientes._ejecutar_consulta(
                "DELETE FROM usuario WHERE correo = %s", (correo,)
            )

    def correr(self, funcion, *respuestas):
        """Ejecuta una acción de la app simulando lo que escribe el usuario.
        Devuelve (resultado, texto impreso en pantalla)."""
        with patch("builtins.input", side_effect=list(respuestas)):
            with redirect_stdout(io.StringIO()) as salida:
                resultado = funcion()
        return resultado, salida.getvalue()

    def registrar(self):
        correo = correo_unico()
        self.correos_creados.append(correo)
        _, salida = self.correr(self.app.registrarse, "Persona Prueba", correo, "+56900000000", CLAVE)
        self.assertIn("[OK] Cuenta creada", salida)
        return correo

    def registrar_e_iniciar(self):
        correo = self.registrar()
        _, salida = self.correr(self.app.iniciar_sesion, correo, CLAVE)
        self.assertIn("[OK] Bienvenida/o", salida)
        return correo

    def crear_reserva(self, fecha=FECHA_FUTURA, hora="20:00", personas="2", observaciones=""):
        _, salida = self.correr(self.app.nueva_reserva, fecha, hora, personas, observaciones)
        self.assertIn("[OK] Reserva #", salida)
        return int(re.search(r"Reserva #(\d+)", salida).group(1))


# ============================================================
#  CAMINO FELIZ
# ============================================================

class CaminoFelizTests(PruebaBase):

    def test_flujo_completo_registro_login_crud_logout(self):
        correo = correo_unico()
        self.correos_creados.append(correo)

        # 1. Registro
        _, salida = self.correr(self.app.registrarse, "Luis Test", correo, "+56900000001", CLAVE)
        self.assertIn("[OK] Cuenta creada", salida)

        # 2. Inicio de sesión
        _, salida = self.correr(self.app.iniciar_sesion, correo, CLAVE)
        self.assertIn("[OK] Bienvenida/o", salida)
        self.assertIsNotNone(self.app._sesion)

        # 3. Crear reserva
        id_reserva = self.crear_reserva(personas="2", observaciones="Cumpleaños")

        # 4. Leer
        lista, _ = self.correr(self.app.ver_reservas)
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0].id_reserva, id_reserva)
        self.assertEqual(lista[0].cant_personas, 2)
        self.assertEqual(lista[0].hora, time(20, 0))

        # 5. Editar: ID, Enter en fecha, Enter en hora, 4 personas, observaciones nuevas
        _, salida = self.correr(self.app.editar_reserva, str(id_reserva), "", "", "4", "Cumpleaños con torta")
        self.assertIn("[OK] Reserva actualizada", salida)
        lista, _ = self.correr(self.app.ver_reservas)
        self.assertEqual(lista[0].cant_personas, 4)
        self.assertEqual(lista[0].observaciones, "Cumpleaños con torta")

        # 6. Eliminar
        _, salida = self.correr(self.app.eliminar_reserva, str(id_reserva), "s")
        self.assertIn("[OK] Reserva eliminada", salida)
        lista, salida = self.correr(self.app.ver_reservas)
        self.assertEqual(lista, [])
        self.assertIn("No tienes reservas todavía", salida)

        # 7. Cerrar sesión
        _, salida = self.correr(self.app.cerrar_sesion)
        self.assertIn("[OK] Sesión cerrada", salida)
        self.assertIsNone(self.app._sesion)

    def test_recorrido_completo_por_menus(self):
        """Recorre la aplicación como lo haría una persona, desde el menú principal."""
        correo = correo_unico()
        self.correos_creados.append(correo)
        respuestas = [
            "1", "Mario Test", correo, "+56900000002", CLAVE,  # Visitante: registrarse
            "2", correo, CLAVE,                                # Visitante: iniciar sesión
            "2", FECHA_FUTURA, "19:30", "3", "Mesa junto a la ventana",  # Cliente: nueva reserva
            "1",                                               # Cliente: ver reservas
            "5",                                               # Cliente: cerrar sesión
            "0",                                               # Salir
        ]
        _, salida = self.correr(self.app.ejecutar, *respuestas)
        for texto in [
            "[OK] Cuenta creada",
            "[OK] Bienvenida/o",
            "[OK] Reserva #",
            "Mesa junto a la ventana",
            "[OK] Sesión cerrada",
            "¡Hasta luego!",
        ]:
            self.assertIn(texto, salida)


# ============================================================
#  CAMINOS DE ERROR
# ============================================================

class CaminoDeErrorTests(PruebaBase):

    # ----- Registro -----

    def test_registro_con_correo_repetido(self):
        correo = self.registrar()
        _, salida = self.correr(self.app.registrarse, "Otra Persona", correo, "+56900000003", "clave456")
        self.assertIn("Ese correo ya está registrado", salida)

    def test_registro_con_clave_corta_no_guarda_nada(self):
        correo = correo_unico()
        self.correos_creados.append(correo)
        _, salida = self.correr(self.app.registrarse, "Clave Corta", correo, "+56900000004", "123")
        self.assertIn("Mínimo 6 caracteres", salida)
        self.assertIsNone(self.app._clientes.buscar_por_correo(correo))

    def test_registro_con_campos_vacios(self):
        _, salida = self.correr(self.app.registrarse, "", "", "", "")
        self.assertIn("son obligatorios", salida)

    def test_registro_con_correo_sin_arroba(self):
        _, salida = self.correr(self.app.registrarse, "Sin Arroba", "correo.malo", "+56900000005", CLAVE)
        self.assertIn("formato válido", salida)

    # ----- Login -----

    def test_login_con_clave_incorrecta(self):
        correo = self.registrar()
        _, salida = self.correr(self.app.iniciar_sesion, correo, "clave_mala")
        self.assertIn("Correo o contraseña incorrectos", salida)
        self.assertIsNone(self.app._sesion)

    def test_login_con_correo_inexistente(self):
        _, salida = self.correr(self.app.iniciar_sesion, correo_unico(), CLAVE)
        self.assertIn("Correo o contraseña incorrectos", salida)
        self.assertIsNone(self.app._sesion)

    def test_opcion_de_menu_invalida(self):
        _, salida = self.correr(self.app._menu_visitante, "9")
        self.assertIn("Opción no válida", salida)

    # ----- Datos de la reserva -----

    def test_fecha_pasada_se_vuelve_a_pedir(self):
        self.registrar_e_iniciar()
        _, salida = self.correr(self.app.nueva_reserva, "2020-01-01", FECHA_FUTURA, "20:00", "2", "")
        self.assertIn("no puede ser anterior a hoy", salida)
        self.assertIn("[OK] Reserva #", salida)

    def test_formato_de_fecha_invalido(self):
        self.registrar_e_iniciar()
        _, salida = self.correr(self.app.nueva_reserva, "31/12/2026", FECHA_FUTURA, "20:00", "2", "")
        self.assertIn("Formato inválido", salida)
        self.assertIn("[OK] Reserva #", salida)

    def test_hora_invalida_se_vuelve_a_pedir(self):
        self.registrar_e_iniciar()
        _, salida = self.correr(self.app.nueva_reserva, FECHA_FUTURA, "25:00", "20:00", "2", "")
        self.assertIn("Formato inválido", salida)
        self.assertIn("[OK] Reserva #", salida)

    def test_personas_no_numericas_y_fuera_de_rango(self):
        self.registrar_e_iniciar()
        _, salida = self.correr(self.app.nueva_reserva, FECHA_FUTURA, "20:00", "abc", "0", "25", "2", "")
        self.assertIn("Debes escribir un número", salida)
        self.assertEqual(salida.count("Debe estar entre 1 y 20"), 2)
        self.assertIn("[OK] Reserva #", salida)

    # ----- Editar y eliminar -----

    def test_editar_sin_reservas(self):
        self.registrar_e_iniciar()
        _, salida = self.correr(self.app.editar_reserva)
        self.assertIn("No tienes reservas todavía", salida)

    def test_editar_con_id_inexistente(self):
        self.registrar_e_iniciar()
        self.crear_reserva()
        _, salida = self.correr(self.app.editar_reserva, "999999")
        self.assertIn("No existe una reserva con ese ID en tu cuenta", salida)

    def test_id_no_numerico(self):
        self.registrar_e_iniciar()
        self.crear_reserva()
        _, salida = self.correr(self.app.eliminar_reserva, "abc")
        self.assertIn("El ID debe ser un número", salida)

    def test_no_se_puede_editar_reserva_cancelada(self):
        self.registrar_e_iniciar()
        id_reserva = self.crear_reserva()
        reserva = self.app._reservas.buscar_por_id(id_reserva)
        reserva.estado = "Cancelada"
        self.app._reservas.actualizar(reserva)

        _, salida = self.correr(self.app.editar_reserva, str(id_reserva))
        self.assertIn("No se puede editar una reserva cancelada", salida)

    def test_eliminar_cancelado_conserva_la_reserva(self):
        self.registrar_e_iniciar()
        id_reserva = self.crear_reserva()
        _, salida = self.correr(self.app.eliminar_reserva, str(id_reserva), "n")
        self.assertIn("Operación cancelada", salida)
        self.assertIsNotNone(self.app._reservas.buscar_por_id(id_reserva))

    # ----- Seguridad entre clientes -----

    def test_cliente_no_puede_tocar_reservas_de_otro(self):
        # Ana crea una reserva y cierra sesión
        self.registrar_e_iniciar()
        id_ana = self.crear_reserva()
        self.correr(self.app.cerrar_sesion)

        # Beto inicia sesión y tiene su propia reserva (sin ella no se pediría ningún ID)
        self.registrar_e_iniciar()
        self.crear_reserva()

        # Beto intenta eliminar la reserva de Ana
        _, salida = self.correr(self.app.eliminar_reserva, str(id_ana), "s")
        self.assertIn("No existe una reserva con ese ID en tu cuenta", salida)
        self.assertIsNotNone(self.app._reservas.buscar_por_id(id_ana))


# ============================================================
#  REGLAS DEL MODELO (no necesitan MySQL)
# ============================================================

class ValidacionesDelModeloTests(unittest.TestCase):

    def test_estado_invalido_se_rechaza(self):
        reserva = Reserva(1, date(2026, 12, 1), time(20, 0), 2)
        with self.assertRaises(ValueError):
            reserva.estado = "Inventado"

    def test_personas_fuera_de_rango_se_rechazan(self):
        for personas in (0, -1, 21):
            with self.subTest(personas=personas):
                with self.assertRaises(ValueError):
                    Reserva(1, date(2026, 12, 1), time(20, 0), personas)

    def test_fecha_y_hora_deben_ser_del_tipo_correcto(self):
        with self.assertRaises(ValueError):
            Reserva(1, "2026-12-01", time(20, 0), 2)
        with self.assertRaises(ValueError):
            Reserva(1, date(2026, 12, 1), "20:00", 2)

    def test_estados_validos_se_aceptan(self):
        reserva = Reserva(1, date(2026, 12, 1), time(20, 0), 2)
        for estado in Reserva.ESTADOS_VALIDOS:
            with self.subTest(estado=estado):
                reserva.estado = estado
                self.assertEqual(reserva.estado, estado)


if __name__ == "__main__":
    unittest.main(verbosity=2)