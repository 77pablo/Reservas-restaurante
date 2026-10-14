
import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect

from negocio.servicios.cliente_servicio import ClienteServicio
from negocio.servicios.reserva_servicio import ReservaServicio


load_dotenv()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "Falta configurar SECRET_KEY en el archivo .env"
    )

app.config["WTF_CSRF_ENABLED"] = True
csrf = CSRFProtect(app)


@app.route("/", methods=["GET"])
def inicio():
    return render_template("index.html")


@app.route("/salud", methods=["GET"])
def salud():
    return {
        "estado": "correcto",
        "mensaje": "La aplicación está funcionando.",
    }


@app.route("/reservas", methods=["GET"])
def listar_reservas():
    try:
        reservas = (
            ReservaServicio.obtener_todas_con_horario()
        )

        return render_template(
            "reservas.html",
            reservas=reservas,
        )

    except Exception:
        app.logger.exception(
            "Error al obtener las reservas."
        )
        return "No se pudieron cargar las reservas.", 500


@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    if request.method == "GET":
        return render_template(
            "reservar.html",
            fecha_minima=date.today().isoformat(),
        )

    try:
        nombre_completo = request.form.get(
            "nombre_completo", ""
        ).strip()

        correo_electronico = request.form.get(
            "correo_electronico", ""
        ).strip().lower()

        fecha_reserva = request.form.get(
            "fecha", ""
        ).strip()

        hora_inicio = request.form.get(
            "hora_inicio", ""
        ).strip()

        hora_fin = request.form.get(
            "hora_fin", ""
        ).strip()

        cantidad_texto = request.form.get(
            "cantidad_personas", ""
        ).strip()

        observaciones = request.form.get(
            "observaciones", ""
        ).strip()

        if not all([
            nombre_completo,
            correo_electronico,
            fecha_reserva,
            hora_inicio,
            hora_fin,
            cantidad_texto,
        ]):
            return (
                "Completa todos los campos obligatorios.",
                400,
            )

        try:
            cantidad_personas = int(cantidad_texto)
        except ValueError:
            return (
                "La cantidad de personas debe ser un número.",
                400,
            )

        if cantidad_personas < 1:
            return (
                "La cantidad de personas debe ser al menos 1.",
                400,
            )

        if len(nombre_completo) > 150:
            return "El nombre es demasiado largo.", 400

        if len(correo_electronico) > 100:
            return "El correo es demasiado largo.", 400

        cliente = (
            ClienteServicio.buscar_por_nombre_y_correo(
                nombre_completo,
                correo_electronico,
            )
        )

        if cliente is None:
            return (
                "No encontramos un cliente registrado con "
                "ese nombre y correo. Verifica los datos.",
                400,
            )

        reserva_creada = ReservaServicio.crear_reserva(
            id_cliente=cliente.id_cliente,
            cantidad_personas=cantidad_personas,
            fecha=fecha_reserva,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            observaciones=observaciones or None,
        )

        if reserva_creada is None:
            return (
                "No se pudo crear la reserva. Comprueba la "
                "fecha, el horario, la capacidad y la "
                "disponibilidad de las mesas.",
                400,
            )

        return render_template(
            "reservar.html",
            fecha_minima=date.today().isoformat(),
            exito=True,
            numero_reserva=reserva_creada.id_reserva,
            nombre_cliente=nombre_completo,
        )

    except (TypeError, ValueError):
        return (
            "Hay datos con un formato incorrecto. "
            "Revisa la fecha, las horas y la cantidad.",
            400,
        )

    except Exception:
        app.logger.exception(
            "Error al procesar la reserva."
        )
        return (
            "Ocurrió un error interno al crear la reserva.",
            500,
        )


if __name__ == "__main__":
    modo_debug = (
        os.environ.get("FLASK_DEBUG", "0") == "1"
    )

    app.run(debug=modo_debug)
