"""Interfaz web (Flask) para probar el sistema de reservas en localhost."""
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash

from datos.conexion import db
from datos.modelos.orm_models import crear_tablas

from dominio.cliente import Cliente
from dominio.empleado import Empleado
from dominio.restaurant import Restaurant
from dominio.zona import Zona
from dominio.mesa import Mesa
from dominio.reserva import Reserva
from dominio.disponibilidad import Disponibilidad

from repositorios.cliente_repositorio import ClienteRepositorio
from repositorios.empleado_repositorio import EmpleadoRepositorio
from repositorios.restaurant_repositorio import RestaurantRepositorio
from repositorios.zona_repositorio import ZonaRepositorio
from repositorios.mesa_repositorio import MesaRepositorio
from repositorios.disponibilidad_repositorio import DisponibilidadRepositorio
from repositorios.reserva_repositorio import ReservaRepositorio

from negocio.servicios.disponibilidad_servicio import DisponibilidadServicio
from negocio.servicios.reserva_servicio import ReservaServicio


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-secreta-dev-reservas")


@app.before_request
def _antes_de_peticion():
    if db.is_closed():
        db.connect(reuse_if_open=True)


@app.teardown_request
def _despues_de_peticion(exc):
    if not db.is_closed():
        db.close()


# ---------------------- Dashboard ----------------------

@app.route("/")
def index():
    contexto = {
        "total_clientes": ClienteRepositorio.contar(),
        "total_empleados": EmpleadoRepositorio.contar(),
        "total_restaurantes": RestaurantRepositorio.contar(),
        "total_reservas": ReservaRepositorio.contar(),
    }
    return render_template("index.html", **contexto)


# ---------------------- Reservar mesa (vista cliente) ----------------------

@app.route("/reservar", methods=["GET", "POST"])
def reservar_mesa():
    clientes_lista = ClienteRepositorio.listar_todos()

    if request.method == "POST":
        try:
            id_cliente = int(request.form["id_cliente"])
            cant_personas = int(request.form["cant_personas"])
            fecha_txt = request.form["fecha"]
            hora_inicio_txt = request.form["hora_inicio"]
            hora_fin_txt = request.form["hora_fin"]
            observaciones = request.form.get("observaciones", "")

            if not fecha_txt or not hora_inicio_txt or not hora_fin_txt:
                flash("Debes indicar fecha, hora de inicio y hora de termino.", "danger")
                return redirect(url_for("reservar_mesa"))

            fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
            hora_inicio = _a_hora(hora_inicio_txt)
            hora_fin = _a_hora(hora_fin_txt)

            if hora_fin <= hora_inicio:
                flash("La hora de termino debe ser posterior a la hora de inicio.", "danger")
                return redirect(url_for("reservar_mesa"))

            mesas_candidatas = sorted(
                MesaRepositorio.listar_disponibles(cant_personas),
                key=lambda m: m.capacidad,
            )

            mesa_asignada = None
            franja_asignada = None

            for mesa in mesas_candidatas:
                try:
                    franja = DisponibilidadServicio.buscar_franja(
                        id_mesa=mesa.id_mesa,
                        fecha=fecha,
                        hora_inicio=hora_inicio,
                        hora_fin=hora_fin,
                    )
                except ValueError:
                    continue

                if franja is not None:
                    mesa_asignada = mesa
                    franja_asignada = franja
                    break

            if mesa_asignada is None:
                flash(
                    f"No hay mesas disponibles para {cant_personas} persona(s) "
                    f"el {fecha_txt} entre las {hora_inicio_txt} y las {hora_fin_txt}. "
                    "Intenta con otra fecha u horario.",
                    "warning",
                )
                return redirect(url_for("reservar_mesa"))

            reserva_creada = ReservaServicio.crear_reserva(
                id_cliente=id_cliente,
                id_disponibilidad=franja_asignada.id_disponibilidad,
                cant_personas=cant_personas,
                observaciones=observaciones,
            )

            flash(
                f"Reserva #{reserva_creada.id_reserva} confirmada: Mesa "
                f"#{mesa_asignada.numero_mesa} (capacidad {mesa_asignada.capacidad}) "
                f"el {fecha_txt} de {hora_inicio_txt} a {hora_fin_txt}.",
                "success",
            )
            return redirect(url_for("reservar_mesa"))

        except ValueError as error:
            flash(f"No se pudo crear la reserva: {error}", "danger")
            return redirect(url_for("reservar_mesa"))
        except Exception as error:
            flash(f"Error al procesar la reserva: {error}", "danger")
            return redirect(url_for("reservar_mesa"))

    return render_template("reservar.html", clientes=clientes_lista)


def _a_hora(valor):
    """Convierte 'HH:MM' o 'HH:MM:SS' en un objeto time."""
    for formato in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(valor, formato).time()
        except ValueError:
            continue
    raise ValueError(f"Hora invalida: {valor}")

# ---------------------- Clientes (CRUD completo) ----------------------

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if request.method == "POST":
        try:
            cliente = Cliente(
                nombre_completo=request.form["nombre_completo"],
                correo=request.form["correo"],
                telefono=request.form["telefono"],
                contrasena=request.form["contrasena"],
                preferencias=request.form.get("preferencias", ""),
                puntos_fidelidad=int(request.form.get("puntos_fidelidad") or 0),
            )
            ClienteRepositorio.crear(cliente)
            flash(f"Cliente '{cliente.nombre_completo}' registrado correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar cliente: {error}", "danger")
        return redirect(url_for("clientes"))

    lista = ClienteRepositorio.listar_todos()
    return render_template("clientes.html", clientes=lista)


@app.route("/clientes/<int:id_cliente>/puntos", methods=["POST"])
def actualizar_puntos(id_cliente):
    try:
        nuevos_puntos = int(request.form["puntos_fidelidad"])
        if ClienteRepositorio.actualizar_puntos(id_cliente, nuevos_puntos):
            flash("Puntos de fidelidad actualizados.", "success")
        else:
            flash("No se encontro el cliente indicado.", "warning")
    except ValueError:
        flash("El valor de puntos debe ser un numero entero.", "danger")
    return redirect(url_for("clientes"))


@app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    cliente = ClienteRepositorio.obtener_por_id(id_cliente)
    if cliente is None:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes"))

    if request.method == "POST":
        try:
            cliente.nombre_completo = request.form["nombre_completo"]
            cliente.correo = request.form["correo"]
            cliente.telefono = request.form["telefono"]
            cliente.contrasena = request.form["contrasena"]
            cliente.preferencias = request.form.get("preferencias", "")
            cliente.puntos_fidelidad = int(request.form.get("puntos_fidelidad") or 0)

            if ClienteRepositorio.actualizar(cliente):
                flash("Cliente actualizado correctamente.", "success")
            else:
                flash("No se pudo actualizar el cliente.", "danger")
            return redirect(url_for("clientes"))
        except Exception as error:
            flash(f"Error al actualizar cliente: {error}", "danger")
            return redirect(url_for("editar_cliente", id_cliente=id_cliente))

    return render_template("editar_cliente.html", cliente=cliente)


@app.route("/clientes/<int:id_cliente>/eliminar", methods=["POST"])
def eliminar_cliente(id_cliente):
    if ClienteRepositorio.eliminar(id_cliente):
        flash("Cliente eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el cliente.", "danger")
    return redirect(url_for("clientes"))


# ---------------------- Empleados (CRUD completo) ----------------------

@app.route("/empleados", methods=["GET", "POST"])
def empleados():
    if request.method == "POST":
        try:
            empleado = Empleado(
                nombre_completo=request.form["nombre_completo"],
                correo=request.form["correo"],
                telefono=request.form["telefono"],
                contrasena=request.form["contrasena"],
                cargo=request.form["cargo"],
                turno=request.form["turno"],
            )
            EmpleadoRepositorio.crear(empleado)
            flash(f"Empleado '{empleado.nombre_completo}' registrado correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar empleado: {error}", "danger")
        return redirect(url_for("empleados"))

    lista = EmpleadoRepositorio.listar_todos()
    return render_template("empleados.html", empleados=lista)


@app.route("/empleados/<int:id_empleado>/editar", methods=["GET", "POST"])
def editar_empleado(id_empleado):
    empleado = EmpleadoRepositorio.obtener_por_id(id_empleado)
    if empleado is None:
        flash("Empleado no encontrado.", "danger")
        return redirect(url_for("empleados"))

    if request.method == "POST":
        try:
            empleado.nombre_completo = request.form["nombre_completo"]
            empleado.correo = request.form["correo"]
            empleado.telefono = request.form["telefono"]
            empleado.contrasena = request.form["contrasena"]
            empleado.cargo = request.form["cargo"]
            empleado.turno = request.form["turno"]

            if EmpleadoRepositorio.actualizar(empleado):
                flash("Empleado actualizado correctamente.", "success")
            else:
                flash("No se pudo actualizar el empleado.", "danger")
            return redirect(url_for("empleados"))
        except Exception as error:
            flash(f"Error al actualizar empleado: {error}", "danger")
            return redirect(url_for("editar_empleado", id_empleado=id_empleado))

    return render_template("editar_empleado.html", empleado=empleado)


@app.route("/empleados/<int:id_empleado>/eliminar", methods=["POST"])
def eliminar_empleado(id_empleado):
    if EmpleadoRepositorio.eliminar(id_empleado):
        flash("Empleado eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el empleado.", "danger")
    return redirect(url_for("empleados"))


# ---------------------- Restaurantes (CRUD completo) ----------------------

@app.route("/restaurantes", methods=["GET", "POST"])
def restaurantes():
    if request.method == "POST":
        try:
            restaurant = Restaurant(
                nombre=request.form["nombre"],
                direccion=request.form["direccion"],
                telefono=request.form["telefono"],
                horario_apertura=request.form["horario_apertura"],
                horario_cierre=request.form["horario_cierre"],
            )
            RestaurantRepositorio.crear(restaurant)
            flash(f"Restaurant '{restaurant.nombre}' registrado correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar restaurant: {error}", "danger")
        return redirect(url_for("restaurantes"))

    lista = RestaurantRepositorio.listar_todos()
    return render_template("restaurantes.html", restaurantes=lista)


@app.route("/restaurantes/<int:id_restaurant>/editar", methods=["GET", "POST"])
def editar_restaurante(id_restaurant):
    restaurant = RestaurantRepositorio.obtener_por_id(id_restaurant)
    if restaurant is None:
        flash("Restaurant no encontrado.", "danger")
        return redirect(url_for("restaurantes"))

    if request.method == "POST":
        try:
            restaurant.nombre = request.form["nombre"]
            restaurant.direccion = request.form["direccion"]
            restaurant.telefono = request.form["telefono"]
            restaurant.horario_apertura = request.form["horario_apertura"]
            restaurant.horario_cierre = request.form["horario_cierre"]

            if RestaurantRepositorio.actualizar(restaurant):
                flash("Restaurant actualizado correctamente.", "success")
            else:
                flash("No se pudo actualizar el restaurant.", "danger")
            return redirect(url_for("restaurantes"))
        except Exception as error:
            flash(f"Error al actualizar restaurant: {error}", "danger")
            return redirect(url_for("editar_restaurante", id_restaurant=id_restaurant))

    return render_template("editar_restaurante.html", restaurant=restaurant)


@app.route("/restaurantes/<int:id_restaurant>/eliminar", methods=["POST"])
def eliminar_restaurante(id_restaurant):
    if RestaurantRepositorio.eliminar(id_restaurant):
        flash("Restaurant eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el restaurant.", "danger")
    return redirect(url_for("restaurantes"))


@app.route("/restaurantes/<int:id_restaurant>/zonas", methods=["GET", "POST"])
def zonas_restaurante(id_restaurant):
    restaurant = RestaurantRepositorio.obtener_por_id(id_restaurant)
    if restaurant is None:
        flash("Restaurant no encontrado.", "danger")
        return redirect(url_for("restaurantes"))

    if request.method == "POST":
        try:
            zona = Zona(
                id_restaurant=id_restaurant,
                nombre_zona=request.form["nombre_zona"],
                permite_fumadores=bool(request.form.get("permite_fumadores")),
            )
            ZonaRepositorio.crear(zona)
            flash(f"Zona '{zona.nombre_zona}' registrada correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar zona: {error}", "danger")
        return redirect(url_for("zonas_restaurante", id_restaurant=id_restaurant))

    zonas = ZonaRepositorio.listar_por_restaurant(id_restaurant)
    return render_template("restaurante_detalle.html", restaurant=restaurant, zonas=zonas)


# ---------------------- Zonas (CRUD completo) / Mesas ----------------------

@app.route("/zonas/<int:id_zona>/editar", methods=["GET", "POST"])
def editar_zona(id_zona):
    zona = ZonaRepositorio.obtener_por_id(id_zona)
    if zona is None:
        flash("Zona no encontrada.", "danger")
        return redirect(url_for("restaurantes"))

    if request.method == "POST":
        try:
            zona.nombre_zona = request.form["nombre_zona"]
            zona.permite_fumadores = bool(request.form.get("permite_fumadores"))

            if ZonaRepositorio.actualizar(zona):
                flash("Zona actualizada correctamente.", "success")
            else:
                flash("No se pudo actualizar la zona.", "danger")
            return redirect(url_for("zonas_restaurante", id_restaurant=zona.id_restaurant))
        except Exception as error:
            flash(f"Error al actualizar zona: {error}", "danger")
            return redirect(url_for("editar_zona", id_zona=id_zona))

    return render_template("editar_zona.html", zona=zona)


@app.route("/zonas/<int:id_zona>/eliminar", methods=["POST"])
def eliminar_zona(id_zona):
    zona = ZonaRepositorio.obtener_por_id(id_zona)
    if zona is None:
        flash("Zona no encontrada.", "danger")
        return redirect(url_for("restaurantes"))

    id_restaurant = zona.id_restaurant
    if ZonaRepositorio.eliminar(id_zona):
        flash("Zona eliminada correctamente.", "success")
    else:
        flash("No se pudo eliminar la zona.", "danger")
    return redirect(url_for("zonas_restaurante", id_restaurant=id_restaurant))


@app.route("/zonas/<int:id_zona>/mesas", methods=["GET", "POST"])
def mesas_zona(id_zona):
    zona = ZonaRepositorio.obtener_por_id(id_zona)
    if zona is None:
        flash("Zona no encontrada.", "danger")
        return redirect(url_for("restaurantes"))

    if request.method == "POST":
        try:
            mesa = Mesa(
                id_zona=id_zona,
                numero_mesa=int(request.form["numero_mesa"]),
                capacidad=int(request.form["capacidad"]),
                activa=bool(request.form.get("activa")),
            )
            MesaRepositorio.crear(mesa)
            flash(f"Mesa N {mesa.numero_mesa} registrada correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar mesa: {error}", "danger")
        return redirect(url_for("mesas_zona", id_zona=id_zona))

    mesas = MesaRepositorio.listar_por_zona(id_zona)
    return render_template("zona_detalle.html", zona=zona, mesas=mesas)


@app.route("/mesas/<int:id_mesa>/editar", methods=["GET", "POST"])
def editar_mesa(id_mesa):
    mesa = MesaRepositorio.obtener_por_id(id_mesa)
    if mesa is None:
        flash("Mesa no encontrada.", "danger")
        return redirect(url_for("restaurantes"))

    if request.method == "POST":
        try:
            mesa.numero_mesa = int(request.form["numero_mesa"])
            mesa.capacidad = int(request.form["capacidad"])
            mesa.activa = bool(request.form.get("activa"))

            if MesaRepositorio.actualizar(mesa):
                flash("Mesa actualizada correctamente.", "success")
            else:
                flash("No se pudo actualizar la mesa.", "danger")
            return redirect(url_for("mesas_zona", id_zona=mesa.id_zona))
        except Exception as error:
            flash(f"Error al actualizar mesa: {error}", "danger")
            return redirect(url_for("editar_mesa", id_mesa=id_mesa))

    return render_template("editar_mesa.html", mesa=mesa)


@app.route("/mesas/<int:id_mesa>/eliminar", methods=["POST"])
def eliminar_mesa(id_mesa):
    mesa = MesaRepositorio.obtener_por_id(id_mesa)
    if mesa is None:
        flash("Mesa no encontrada.", "danger")
        return redirect(url_for("restaurantes"))

    id_zona = mesa.id_zona
    if MesaRepositorio.eliminar(id_mesa):
        flash("Mesa eliminada correctamente.", "success")
    else:
        flash("No se pudo eliminar la mesa.", "danger")
    return redirect(url_for("mesas_zona", id_zona=id_zona))


# ---------------------- Disponibilidad (Create, Read, Delete) ----------------------

@app.route("/disponibilidad", methods=["GET", "POST"])
def disponibilidad():
    if request.method == "POST":
        try:
            franja = Disponibilidad(
                id_mesa=int(request.form["id_mesa"]),
                fecha=request.form["fecha"],
                hora_inicio=request.form["hora_inicio"],
                hora_fin=request.form["hora_fin"],
                estado_franja="Disponible",
            )
            DisponibilidadRepositorio.crear(franja)
            flash("Franja de disponibilidad registrada correctamente.", "success")
        except Exception as error:
            flash(f"Error al registrar disponibilidad: {error}", "danger")
        return redirect(url_for("disponibilidad"))

    franjas = [DisponibilidadRepositorio._a_dominio(r) for r in DisponibilidadRepositorio.listar_todos()]
    mesas = [MesaRepositorio._a_dominio(r) for r in MesaRepositorio.listar_todos()]
    return render_template("disponibilidad.html", franjas=franjas, mesas=mesas)


@app.route("/disponibilidad/<int:id_disponibilidad>/eliminar", methods=["POST"])
def eliminar_disponibilidad(id_disponibilidad):
    if DisponibilidadRepositorio.eliminar(id_disponibilidad):
        flash("Franja de disponibilidad eliminada correctamente.", "success")
    else:
        flash("No se pudo eliminar la franja.", "danger")
    return redirect(url_for("disponibilidad"))


# ---------------------- Reservas (CRUD completo, vista staff) ----------------------

@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    if request.method == "POST":
        try:
            id_cliente = int(request.form["id_cliente"])
            cant_personas = int(request.form["cant_personas"])
            observaciones = request.form.get("observaciones", "")

            reserva = Reserva(
                id_cliente=id_cliente,
                cant_personas=cant_personas,
                observaciones=observaciones,
            )
            reserva_creada = ReservaRepositorio.crear(reserva)

            if reserva_creada is None:
                flash("No se pudo crear la reserva: datos invalidos.", "danger")
                return redirect(url_for("reservas"))

            id_mesa = request.form.get("id_mesa")
            fecha = request.form.get("fecha")
            hora_inicio = request.form.get("hora_inicio")
            hora_fin = request.form.get("hora_fin")

            if id_mesa and fecha and hora_inicio and hora_fin:
                franja = DisponibilidadRepositorio.buscar_franja_disponible(
                    int(id_mesa), fecha, hora_inicio, hora_fin
                )
                if franja is not None:
                    DisponibilidadRepositorio.ocupar_franja(
                        franja.id_disponibilidad, reserva_creada.id_reserva
                    )
                    flash("Reserva creada y mesa asignada correctamente.", "success")
                else:
                    flash("Reserva creada, pero no se encontro una franja disponible para esa mesa/horario.", "warning")
            else:
                flash("Reserva creada (pendiente de asignar mesa).", "success")

        except Exception as error:
            flash(f"Error al crear la reserva: {error}", "danger")
        return redirect(url_for("reservas"))

    reservas_lista = ReservaRepositorio.listar_todas()
    clientes_lista = ClienteRepositorio.listar_todos()
    mesas = [MesaRepositorio._a_dominio(r) for r in MesaRepositorio.listar_todos()]
    return render_template(
        "reservas.html",
        reservas=reservas_lista,
        clientes=clientes_lista,
        mesas=mesas,
        estados_posibles=sorted(Reserva.ESTADOS_VALIDOS),
    )


@app.route("/reservas/<int:id_reserva>/estado", methods=["POST"])
def cambiar_estado_reserva(id_reserva):
    nuevo_estado = request.form["estado"]
    try:
        if ReservaRepositorio.cambiar_estado(id_reserva, nuevo_estado):
            flash(f"Reserva #{id_reserva} actualizada a '{nuevo_estado}'.", "success")
        else:
            flash("Transicion de estado no permitida o reserva inexistente.", "danger")
    except Exception as error:
        flash(f"Error al cambiar estado: {error}", "danger")
    return redirect(url_for("reservas"))


@app.route("/reservas/<int:id_reserva>/editar", methods=["GET", "POST"])
def editar_reserva(id_reserva):
    reserva = ReservaRepositorio.obtener_por_id(id_reserva)
    if reserva is None:
        flash("Reserva no encontrada.", "danger")
        return redirect(url_for("reservas"))

    if request.method == "POST":
        try:
            cant_personas = int(request.form["cant_personas"])
            observaciones = request.form.get("observaciones", "")

            if ReservaRepositorio.actualizar_datos(
                id_reserva, cant_personas=cant_personas, observaciones=observaciones
            ):
                flash("Reserva actualizada correctamente.", "success")
            else:
                flash("No se pudo actualizar la reserva.", "danger")
            return redirect(url_for("reservas"))
        except Exception as error:
            flash(f"Error al actualizar reserva: {error}", "danger")
            return redirect(url_for("editar_reserva", id_reserva=id_reserva))

    return render_template("editar_reserva.html", reserva=reserva)


@app.route("/reservas/<int:id_reserva>/eliminar", methods=["POST"])
def eliminar_reserva(id_reserva):
    if ReservaRepositorio.eliminar(id_reserva):
        flash("Reserva eliminada correctamente.", "success")
    else:
        flash("No se pudo eliminar la reserva.", "danger")
    return redirect(url_for("reservas"))


# ---------------------- Polimorfismo: vista unificada de usuarios ----------------------

@app.route("/usuarios")
def usuarios_polimorfismo():
    """Trata a Clientes y Empleados de forma uniforme como objetos Usuario,
    pero cada uno responde distinto a la misma llamada de metodo
    (obtener_rol / realizar_accion_principal) segun su tipo real.
    Esto demuestra polimorfismo por sobrescritura en tiempo de ejecucion.
    """
    clientes_lista = ClienteRepositorio.listar_todos()
    empleados_lista = EmpleadoRepositorio.listar_todos()

    usuarios_mixtos = list(clientes_lista) + list(empleados_lista)

    resultados = [
        {
            "nombre": usuario.nombre_completo,
            "correo": usuario.correo,
            "rol": usuario.obtener_rol(),
            "accion": usuario.realizar_accion_principal(),
        }
        for usuario in usuarios_mixtos
    ]

    return render_template("usuarios.html", resultados=resultados)


if __name__ == "__main__":
    crear_tablas()
    app.run(debug=True, port=5000)