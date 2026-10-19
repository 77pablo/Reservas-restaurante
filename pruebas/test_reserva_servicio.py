"""Pruebas de las reglas de negocio del servicio de reservas."""

import unittest

from datos.conexion import db
from datos.modelos.orm_models import crear_tablas
from negocio.servicios.reserva_servicio import ReservaServicio
from negocio.servicios.disponibilidad_servicio import DisponibilidadServicio


class TestReservaServicio(unittest.TestCase):
    """Verifica validaciones basicas sin modificar datos reales."""

    @classmethod
    def setUpClass(cls):
        if db.is_closed():
            db.connect()
        crear_tablas()

    @classmethod
    def tearDownClass(cls):
        if not db.is_closed():
            db.close()

    def test_cantidad_personas_invalida_lanza_error(self):
        """Una cantidad de personas no positiva debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            ReservaServicio.crear_reserva(
                id_cliente=1,
                id_disponibilidad=1,
                cant_personas=0,
            )

    def test_cantidad_personas_no_entera_lanza_error(self):
        """Una cantidad de personas no entera debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            ReservaServicio.crear_reserva(
                id_cliente=1,
                id_disponibilidad=1,
                cant_personas="dos",
            )

    def test_cliente_inexistente_lanza_error(self):
        """Un id de cliente que no existe debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            ReservaServicio.crear_reserva(
                id_cliente=999999,
                id_disponibilidad=1,
                cant_personas=2,
            )

    def test_mesa_inexistente_lanza_error_en_disponibilidad(self):
        """Buscar franja de una mesa inexistente debe lanzar ValueError."""
        from datetime import date, time

        with self.assertRaises(ValueError):
            DisponibilidadServicio.buscar_franja(
                id_mesa=999999,
                fecha=date(2030, 1, 1),
                hora_inicio=time(19, 0),
                hora_fin=time(20, 0),
            )

    def test_hora_inicio_mayor_a_hora_fin_lanza_error(self):
        """La hora de inicio debe ser anterior a la hora de fin."""
        from datetime import date, time

        with self.assertRaises(ValueError):
            DisponibilidadServicio.buscar_franja(
                id_mesa=1,
                fecha=date(2030, 1, 1),
                hora_inicio=time(21, 0),
                hora_fin=time(19, 0),
            )


if __name__ == "__main__":
    unittest.main()