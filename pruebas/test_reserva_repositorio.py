
import unittest
from datetime import date, datetime, time, timedelta, timezone

from datos.repositorio.reserva_repositorio import ReservaRepositorio


class PruebasValidacionesReserva(unittest.TestCase):

    def test_convertir_fecha_desde_texto(self):
        resultado = ReservaRepositorio._convertir_fecha("2027-01-15")

        self.assertEqual(resultado, date(2027, 1, 15))

    def test_convertir_fecha_desde_datetime(self):
        valor = datetime(2027, 1, 15, 12, 30)

        resultado = ReservaRepositorio._convertir_fecha(valor)

        self.assertEqual(resultado, date(2027, 1, 15))

    def test_rechazar_fecha_invalida(self):
        with self.assertRaises(ValueError):
            ReservaRepositorio._convertir_fecha("2027-99-45")

    def test_convertir_hora_desde_texto(self):
        resultado = ReservaRepositorio._convertir_hora("14:30")

        self.assertEqual(resultado, time(14, 30))

    def test_rechazar_hora_invalida(self):
        with self.assertRaises(ValueError):
            ReservaRepositorio._convertir_hora("hora incorrecta")

    def test_rechazar_hora_con_zona_horaria(self):
        hora = time(14, 30, tzinfo=timezone.utc)

        with self.assertRaises(ValueError):
            ReservaRepositorio._convertir_hora(hora)

    def test_pendiente_puede_confirmarse_o_cancelarse(self):
        permitidos = ReservaRepositorio.TRANSICIONES_PERMITIDAS["Pendiente"]

        self.assertIn("Confirmada", permitidos)
        self.assertIn("Cancelada", permitidos)
        self.assertNotIn("Completada", permitidos)

    def test_confirmada_puede_completarse_o_cancelarse(self):
        permitidos = ReservaRepositorio.TRANSICIONES_PERMITIDAS["Confirmada"]

        self.assertIn("Completada", permitidos)
        self.assertIn("Cancelada", permitidos)

    def test_reserva_cancelada_no_admite_transiciones(self):
        permitidos = ReservaRepositorio.TRANSICIONES_PERMITIDAS["Cancelada"]

        self.assertEqual(permitidos, set())

    def test_rechazar_cantidad_cero(self):
        resultado = ReservaRepositorio.crear_reserva(
            id_cliente=1,
            cantidad_personas=0,
            fecha=date.today() + timedelta(days=2),
            hora_inicio="12:00",
            hora_fin="13:00",
        )

        self.assertIsNone(resultado)

    def test_rechazar_horario_invertido(self):
        resultado = ReservaRepositorio.crear_reserva(
            id_cliente=1,
            cantidad_personas=2,
            fecha=date.today() + timedelta(days=2),
            hora_inicio="15:00",
            hora_fin="14:00",
        )

        self.assertIsNone(resultado)

    def test_rechazar_fecha_pasada(self):
        resultado = ReservaRepositorio.crear_reserva(
            id_cliente=1,
            cantidad_personas=2,
            fecha=date.today() - timedelta(days=1),
            hora_inicio="12:00",
            hora_fin="13:00",
        )

        self.assertIsNone(resultado)


if __name__ == "__main__":
    unittest.main(verbosity=2)
