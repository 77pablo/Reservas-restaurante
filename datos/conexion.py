from peewee import MySQLDatabase
from decouple import config

database = MySQLDatabase(
    config('database'), 
    **{
        'charset': 'utf8mb4',
        'host': config('host'),
        'port': int(config('port')),  
        'user': config('user'),
        'password': config('password')
    }
)