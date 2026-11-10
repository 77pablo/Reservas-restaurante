from decouple import config
class Configuracion:
    DB_HOST = config("DB_HOST", default="127.0.0.1")
    DB_PORT = config("DB_PORT", default=3306, cast=int)
    DB_NAME = config("DB_NAME", default="ecotech_reservas")
    DB_USER = config("DB_USER", default="root")
    DB_PASSWORD = config("DB_PASSWORD", default="")
