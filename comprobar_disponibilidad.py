from datetime import date, time

from datos.conexion import database
from datos.modelos.models import Disponibilidad, Mesa

with database.connection_context():
    franjas = (
        Disponibilidad
        .select(Disponibilidad, Mesa)
        .join(Mesa, on=(Disponibilidad.id_mesa == Mesa.id_mesa))
        .where(
            (Disponibilidad.fecha == date(2026, 10, 17))
            & (Disponibilidad.hora_inicio <= time(14, 0))
            & (Disponibilidad.hora_fin >= time(16, 0))
            & (Disponibilidad.estado_franja == "Disponible")
            & (Mesa.activa == True)
            & (Mesa.capacidad_comensales >= 2)
        )
    )

    encontradas = list(franjas)

    if encontradas:
        for franja in encontradas:
            print(
                f"ID de mesa: {franja.id_mesa} | "
                f"Fecha: {franja.fecha} | "
                f"Inicio: {franja.hora_inicio} | "
                f"Fin: {franja.hora_fin} | "
                f"Estado: {franja.estado_franja}"
            )
    else:
        print("No se encontraron franjas disponibles para ese horario.")
