"""Pruebas de conexion a la base de datos y existencia de tablas."""

import unittest

from datos.conexion import db
from datos.modelos.orm_models import (
    crear_tablas,
    UsuarioORM,
    ClienteORM,
    EmpleadoORM,
    RestaurantORM,
    ZonaORM,
    MesaORM,
    ReservaORM,
    DisponibilidadORM,
)


class TestConexion(unittest.TestCase):
    """Verifica que la conexion a MySQL funcione y las tablas existan."""

    @classmethod
    def setUpClass(cls):
        if db.is_closed():
            db.connect()
        crear_tablas()

    @classmethod
    def tearDownClass(cls):
        if not db.is_closed():
            db.close()

    def test_conexion_abierta(self):
        """La conexion a la base de datos debe permitir ejecutar consultas."""
        if db.is_closed():
            db.connect(reuse_if_open=True)
        resultado = db.execute_sql("SELECT 1").fetchone()
        self.assertEqual(resultado[0], 1)

    def test_nombre_base_de_datos(self):
        """La base de datos debe ser 'reserva-restaurante'."""
        self.assertEqual(db.database, "reserva-restaurante")

    def test_tabla_usuario_existe(self):
        self.assertTrue(UsuarioORM.table_exists())

    def test_tabla_cliente_existe(self):
        self.assertTrue(ClienteORM.table_exists())

    def test_tabla_empleado_existe(self):
        self.assertTrue(EmpleadoORM.table_exists())

    def test_tabla_restaurant_existe(self):
        self.assertTrue(RestaurantORM.table_exists())

    def test_tabla_zona_existe(self):
        self.assertTrue(ZonaORM.table_exists())

    def test_tabla_mesa_existe(self):
        self.assertTrue(MesaORM.table_exists())

    def test_tabla_reserva_existe(self):
        self.assertTrue(ReservaORM.table_exists())

    def test_tabla_disponibilidad_existe(self):
        self.assertTrue(DisponibilidadORM.table_exists())


if __name__ == "__main__":
    unittest.main()