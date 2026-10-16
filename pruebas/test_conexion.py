
import unittest

from datos.conexion import database


class PruebasConexion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Abre la conexión antes de ejecutar las pruebas."""
        database.connect(reuse_if_open=True)

    @classmethod
    def tearDownClass(cls):
        """Cierra la conexión al finalizar las pruebas."""
        if not database.is_closed():
            database.close()

    def test_conexion_a_mysql(self):
        """Comprueba que MySQL responde a una consulta."""
        resultado = database.execute_sql("SELECT 1").fetchone()

        self.assertEqual(resultado[0], 1)

    def test_tablas_principales_existen(self):
        """Comprueba que existen las tablas del modelo."""
        tablas_esperadas = {
            "usuario",
            "cliente",
            "empleado",
            "restaurant",
            "zona",
            "mesa",
            "reserva",
            "disponibilidad",
            "empleado_restaurant",
        }

        tablas_existentes = set(database.get_tables())
        tablas_faltantes = tablas_esperadas - tablas_existentes

        self.assertFalse(
            tablas_faltantes,
            f"Faltan tablas en MySQL: {sorted(tablas_faltantes)}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
