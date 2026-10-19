"""
Modulo de conexion a MySQL.

Librerias oficiales utilizadas:
- PyMySQL: driver oficial puro-Python para MySQL (cumple PEP 249).
- Peewee: ORM utilizado para mapear las clases Python a tablas MySQL.

Este modulo centraliza la configuracion de conexion y expone
funciones para probar la conectividad desde ambas capas.
"""
from pathlib import Path

import pymysql
pymysql.install_as_MySQLdb()

from peewee import MySQLDatabase
from decouple import Config, RepositoryEnv


# ============================================================
# Carga del archivo .env desde la raiz del proyecto
# (sin importar desde que carpeta se ejecute Python)
# ============================================================
RUTA_ENV = Path(__file__).resolve().parents[1] / ".env"

if not RUTA_ENV.exists():
    raise FileNotFoundError(
        f"No se encontro el archivo .env en la ruta: {RUTA_ENV}\n"
        f"Crea el archivo .env en la raiz del proyecto con las "
        f"variables DB_NAME, DB_HOST, DB_PORT, DB_USER y DB_PASS."
    )

config = Config(RepositoryEnv(str(RUTA_ENV)))


# ============================================================
# Variables de configuracion de la base de datos
# ============================================================
NOMBRE_BD = config("DB_NAME")
HOST_BD = config("DB_HOST", default="127.0.0.1")
PUERTO_BD = config("DB_PORT", default=3306, cast=int)
USUARIO_BD = config("DB_USER")

# Compatible con ambos nombres de variable: DB_PASSWORD o DB_PASS
PASSWORD_BD = config(
    "DB_PASSWORD",
    default=config("DB_PASS", default="")
)


# ============================================================
# Instancia unica de conexion Peewee (ORM)
# Todos los modelos del sistema comparten esta misma conexion.
# ============================================================
db = MySQLDatabase(
    NOMBRE_BD,
    host=HOST_BD,
    port=PUERTO_BD,
    user=USUARIO_BD,
    password=PASSWORD_BD,
    charset="utf8mb4",
)


# ============================================================
# Funciones de prueba de conexion
# ============================================================
def probar_conexion_pymysql():
    """
    Prueba de conexion directa usando PyMySQL (libreria oficial).
    Retorna True si la conexion fue exitosa, False en caso contrario.
    """
    try:
        conexion = pymysql.connect(
            host=HOST_BD,
            port=PUERTO_BD,
            user=USUARIO_BD,
            password=PASSWORD_BD,
            database=NOMBRE_BD,
            charset="utf8mb4",
        )
        with conexion.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
        conexion.close()
        print(f"[OK] PyMySQL conectado correctamente. MySQL version: {version[0]}")
        return True
    except Exception as error:
        print(f"[ERROR] Fallo la conexion con PyMySQL: {error}")
        return False


def probar_conexion():
    """
    Prueba de conexion a traves de Peewee (capa ORM).
    Retorna True si la conexion fue exitosa, False en caso contrario.
    """
    try:
        db.connect(reuse_if_open=True)
        db.execute_sql("SELECT 1")
        print(
            f"[OK] Peewee conectado correctamente a '{NOMBRE_BD}' "
            f"en {HOST_BD}:{PUERTO_BD}"
        )
        return True
    except Exception as error:
        print(f"[ERROR] Fallo la conexion con Peewee: {error}")
        return False
    finally:
        if not db.is_closed():
            db.close()