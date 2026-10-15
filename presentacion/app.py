import os
from datetime import date, time
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)
from flask_wtf.csrf import CSRFProtect

from datos.repositorio.cliente_repositorio import ClienteRepositorio
from negocio.servicios.reserva_servicio import ReservaServicio


# --------------------------------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "Falta SECRET_KEY en el archivo .env. "
        "Configura una clave secreta antes de iniciar Flask."
    )

# Protección CSRF para los formularios POST.
csrf = CSRFProtect(app)


# --------------------------------------------------
# PÁGINA PRINCIPAL
# --------------------------------------------------

@app.route("/")
def inicio():
    return render_template("index.html")


# --------------------------------------------------
# COMPROBACIÓN DEL SERVIDOR
# --------------------------------------------------

@app.route("/salud")
def salud():
    return jsonify({
        "estado": "correcto",
        "aplicacion": "Reservas Restaurante",
    })


# --------------------------------------------------
# ADMINISTRACIÓN DE RESERVAS
# --------------------------------------------------

@app.route("/reservas", methods=["GET"])
def reservas():
    lista_reservas = ReservaServicio.obtener_todas_con_horario()

    return render_template(
        "reservas.html",
        reservas=lista_reservas,
    )


# --------------------------------------------------
# FORMULARIO PARA CREAR UNA RESERVA
# --------------------------------------------------

@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    if request.method == "GET":
        return render_template("reservar.html")

    nombre = request.form.get("nombre", "").strip()
    correo = request.form.get("correo", "").strip().lower()
    cantidad_texto = request.form.get(
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

    # Validar los campos obligatorios.
    if not all([
        nombre,
        correo,
        cantidad_texto,
        fecha_texto,
        hora_inicio_texto,
        hora_fin_texto,
    ]):
        flash(
            "Completa todos los campos obligatorios.",
            "error",
        )
        return redirect(url_for("reservar"))

    # Validar cantidad de personas.
    try:
        cantidad_personas = int(cantidad_texto)

        if cantidad_personas < 1:
            raise ValueError

    except ValueError:
        flash(
            "La cantidad de personas debe ser un entero positivo.",
            "error",
        )
        return redirect(url_for("reservar"))

    # Validar formato de fecha y horas.
    try:
        fecha_reserva = date.fromisoformat(fecha_texto)
        hora_inicio = time.fromisoformat(hora_inicio_texto)
        hora_fin = time.fromisoformat(hora_fin_texto)

    except ValueError:
        flash(
            "La fecha o el horario no tienen un formato válido.",
            "error",
        )
        return redirect(url_for("reservar"))

    if hora_inicio >= hora_fin:
        flash(
            "La hora de término debe ser posterior a la hora de inicio.",
            "error",
        )
        return redirect(url_for("reservar"))

    # Buscar un cliente previamente registrado.
    cliente = ClienteRepositorio.buscar_por_nombre_y_correo(
        nombre,
        correo,
    )

    if cliente is None:
        flash(
            "No encontramos un cliente con ese nombre y correo. "
            "Verifica los datos o registra primero al cliente.",
            "error",
        )
        return redirect(url_for("reservar"))

    # Crear la reserva mediante la capa de servicios.
    reserva_creada = ReservaServicio.crear_reserva(
        id_cliente=cliente.id_cliente,
        cantidad_personas=cantidad_personas,
        fecha=fecha_reserva,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        observaciones=observaciones or None,
    )

    if reserva_creada is None:
        flash(
            "No fue posible crear la reserva. "
            "Comprueba la fecha, el horario, la capacidad "
            "y la disponibilidad de las mesas.",
            "error",
        )
        return redirect(url_for("reservar"))

    flash(
        f"Reserva creada correctamente. "
        f"Número de reserva: {reserva_creada.id_reserva}.",
        "success",
    )

    return redirect(url_for("reservas"))


# --------------------------------------------------
# CAMBIAR EL ESTADO DE UNA RESERVA
# --------------------------------------------------

@app.route(
    "/reservas/<int:id_reserva>/estado",
    methods=["POST"],
)
def cambiar_estado_reserva(id_reserva):
    nuevo_estado = request.form.get(
        "estado", ""
    ).strip()

    estados_permitidos = {
        "Confirmada",
        "Cancelada",
        "Completada",
    }

    if nuevo_estado not in estados_permitidos:
        flash(
            "El estado solicitado no es válido.",
            "error",
        )
        return redirect(url_for("reservas"))

    reserva = ReservaServicio.obtener_por_id(id_reserva)

    if reserva is None:
        flash(
            "No se encontró la reserva solicitada.",
            "error",
        )
        return redirect(url_for("reservas"))

    resultado = ReservaServicio.cambiar_estado(
        id_reserva,
        nuevo_estado,
    )

    if resultado:
        flash(
            f"La reserva {id_reserva} cambió al estado "
            f"{nuevo_estado}.",
            "success",
        )
    else:
        flash(
            "No se pudo cambiar el estado. "
            "Es posible que la transición no esté permitida.",
            "error",
        )

    return redirect(url_for("reservas"))


# --------------------------------------------------
# ERRORES HTTP
# --------------------------------------------------

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return "Página no encontrada.", 404


# --------------------------------------------------
# INICIAR APLICACIÓN
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1",
        port=5055,
    )