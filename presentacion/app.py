
import os
import re
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_wtf.csrf import CSRFProtect

from datos.repositorio.cliente_repositorio import ClienteRepositorio
from negocio.servicios.reserva_servicio import ReservaServicio


# =========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "No se encontró SECRET_KEY en el archivo .env."
    )

csrf = CSRFProtect(app)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def validar_correo(correo):
    """Comprueba que el correo tenga un formato básico válido."""
    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(patron, correo))


def convertir_fecha(fecha_texto):
    """Convierte una fecha YYYY-MM-DD en un objeto date."""
    try:
        return date.fromisoformat(fecha_texto)
    except (TypeError, ValueError):
        return None


def convertir_hora(hora_texto):
    """Convierte una hora HH:MM en un objeto time."""
    try:
        return datetime.strptime(hora_texto, "%H:%M").time()
    except (TypeError, ValueError):
        return None


# =========================================================
# INICIO
# =========================================================

@app.route("/")
def inicio():
    """Muestra la página principal."""
    return render_template("index.html")


# =========================================================
# COMPROBACIÓN DE SALUD
# =========================================================

@app.route("/salud")
def salud():
    """Permite comprobar que Flask está respondiendo."""
    return {
        "estado": "correcto",
        "aplicacion": "Reservas Restaurante",
    }, 200


# =========================================================
# FORMULARIO DE RESERVA
# =========================================================

@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    """
    Permite realizar una reserva usando nombre y correo.
    Si el cliente no existe, se crea automáticamente.
    """

    if request.method == "GET":
        return render_template("reservar.html")

    # -----------------------------------------------------
    # 1. Obtener los datos enviados desde el formulario
    # -----------------------------------------------------

    nombre = request.form.get("nombre", "").strip()
    correo = request.form.get("correo", "").strip().lower()
    cantidad_personas_texto = request.form.get(
        "cantidad_personas", ""
    ).strip()
    fecha_texto = request.form.get("fecha", "").strip()
    hora_inicio_texto = request.form.get(
        "hora_inicio", ""
    ).strip()
    hora_fin_texto = request.form.get(
        "hora_fin", ""
    ).strip()
    observaciones = request.form.get(
        "observaciones", ""
    ).strip()

    # -----------------------------------------------------
    # 2. Validar los campos obligatorios
    # -----------------------------------------------------

    if not all([
        nombre,
        correo,
        cantidad_personas_texto,
        fecha_texto,
        hora_inicio_texto,
        hora_fin_texto,
    ]):
        flash(
            "Completa todos los campos obligatorios.",
            "error",
        )
        return redirect(url_for("reservar"))

    if len(nombre) > 150:
        flash(
            "El nombre no puede superar los 150 caracteres.",
            "error",
        )
        return redirect(url_for("reservar"))

    if len(correo) > 100 or not validar_correo(correo):
        flash(
            "Introduce un correo electrónico válido.",
            "error",
        )
        return redirect(url_for("reservar"))

    # -----------------------------------------------------
    # 3. Validar cantidad de personas, fecha y horario
    # -----------------------------------------------------

    try:
        cantidad_personas = int(cantidad_personas_texto)
    except (TypeError, ValueError):
        flash(
            "La cantidad de personas debe ser un número entero.",
            "error",
        )
        return redirect(url_for("reservar"))

    if cantidad_personas < 1:
        flash(
            "La reserva debe ser para al menos una persona.",
            "error",
        )
        return redirect(url_for("reservar"))

    fecha = convertir_fecha(fecha_texto)
    hora_inicio = convertir_hora(hora_inicio_texto)
    hora_fin = convertir_hora(hora_fin_texto)

    if fecha is None:
        flash(
            "La fecha indicada no es válida.",
            "error",
        )
        return redirect(url_for("reservar"))

    if hora_inicio is None or hora_fin is None:
        flash(
            "Las horas indicadas no son válidas.",
            "error",
        )
        return redirect(url_for("reservar"))

    if fecha < date.today():
        flash(
            "No puedes reservar para una fecha pasada.",
            "error",
        )
        return redirect(url_for("reservar"))

    if hora_inicio >= hora_fin:
        flash(
            "La hora de término debe ser posterior a la hora de inicio.",
            "error",
        )
        return redirect(url_for("reservar"))

    if fecha == date.today():
        ahora = datetime.now().time()

        if hora_inicio <= ahora:
            flash(
                "La hora de inicio debe ser posterior a la hora actual.",
                "error",
            )
            return redirect(url_for("reservar"))

    # -----------------------------------------------------
    # 4. Obtener o crear al cliente automáticamente
    # -----------------------------------------------------

    try:
        cliente = (
            ClienteRepositorio.obtener_o_crear_por_nombre_y_correo(
                nombre,
                correo,
            )
        )
    except Exception:
        app.logger.exception(
            "Error al obtener o crear el cliente."
        )
        flash(
            "No fue posible registrar tus datos. "
            "Inténtalo nuevamente.",
            "error",
        )
        return redirect(url_for("reservar"))

    if cliente is None:
        flash(
            "No fue posible registrar tus datos. "
            "Verifica tu nombre y correo e inténtalo nuevamente.",
            "error",
        )
        return redirect(url_for("reservar"))

    # -----------------------------------------------------
    # 5. Crear la reserva usando el servicio
    # -----------------------------------------------------

    try:
        reserva_creada = ReservaServicio.crear_reserva(
            id_cliente=cliente.id_cliente,
            cantidad_personas=cantidad_personas,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            observaciones=observaciones or None,
        )
    except Exception:
        app.logger.exception(
            "Error al crear la reserva."
        )
        flash(
            "Ocurrió un error al procesar la reserva. "
            "Inténtalo nuevamente.",
            "error",
        )
        return redirect(url_for("reservar"))

    if reserva_creada is None or reserva_creada is False:
        flash(
            "No encontramos una mesa disponible para la fecha, "
            "el horario y la cantidad de personas seleccionados.",
            "error",
        )
        return redirect(url_for("reservar"))

    # -----------------------------------------------------
    # 6. Confirmar el resultado
    # -----------------------------------------------------

    app.logger.info(
        "Reserva creada correctamente. ID=%s, cliente=%s",
        getattr(reserva_creada, "id_reserva", "desconocido"),
        cliente.id_cliente,
    )

    flash(
        "¡Tu reserva fue registrada correctamente! "
        "Quedó pendiente de confirmación.",
        "success",
    )

    return redirect(url_for("reservar"))


# =========================================================
# ADMINISTRACIÓN DE RESERVAS
# =========================================================

@app.route("/reservas")
def reservas():
    """Muestra las reservas registradas para su administración."""

    try:
        reservas_registradas = (
            ReservaServicio.obtener_todas_con_horario()
        )
    except Exception:
        app.logger.exception(
            "Error al cargar las reservas."
        )
        flash(
            "No fue posible cargar las reservas.",
            "error",
        )
        reservas_registradas = []

    return render_template(
        "reservas.html",
        reservas=reservas_registradas,
    )


# =========================================================
# CAMBIAR ESTADO DE UNA RESERVA
# =========================================================

@app.route(
    "/reservas/<int:id_reserva>/estado",
    methods=["POST"],
)
def cambiar_estado_reserva(id_reserva):
    """Permite confirmar, cancelar o completar una reserva."""

    nuevo_estado = request.form.get(
        "estado", ""
    ).strip()

    estados_validos = {
        "Confirmada",
        "Cancelada",
        "Completada",
    }

    if nuevo_estado not in estados_validos:
        flash(
            "El estado solicitado no es válido.",
            "error",
        )
        return redirect(url_for("reservas"))

    try:
        resultado = ReservaServicio.cambiar_estado(
            id_reserva,
            nuevo_estado,
        )
    except Exception:
        app.logger.exception(
            "Error al cambiar el estado de la reserva %s.",
            id_reserva,
        )
        flash(
            "Ocurrió un error al actualizar la reserva.",
            "error",
        )
        return redirect(url_for("reservas"))

    if resultado:
        flash(
            f"La reserva #{id_reserva} ahora está en estado "
            f"{nuevo_estado}.",
            "success",
        )
    else:
        flash(
            "No se pudo cambiar el estado. "
            "Comprueba que la reserva exista y que la transición "
            "esté permitida.",
            "error",
        )

    return redirect(url_for("reservas"))


# =========================================================
# EJECUCIÓN DIRECTA
# =========================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5055,
        debug=False,
    )
