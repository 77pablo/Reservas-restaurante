from peewee import MySQLDatabase
from decouple import config 

def conectar_base_datos():
    database = MySQLDatabase(config('database'), **{'charset': 'utf8mb4',
                                                    'host': config('host'),
                                                    'port': config('port'),
                                                    'user': config('user'),
                                                    'password': config('password')})
    
    return database