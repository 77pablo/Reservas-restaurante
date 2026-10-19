"""Paquete de conexion a la base de datos.

Reexporta el contenido de conexion.py para mantener compatibilidad
con 'from datos.conexion import db' en el resto del proyecto.
"""

from .conexion import *  # noqa: F401,F403
from .conexion import db  # noqa: F401