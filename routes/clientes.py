import re

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, abort
)
from db import query, execute, DatabaseError, error_message

bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@bp.route("/")
def listar():
    clientes = query("""
        SELECT
            id_cliente,
            nombre_cliente,
            identificacion,
            telefono,
            correo_electronico
        FROM cliente
        ORDER BY id_cliente
    """)

    return render_template(
        "clientes/list.html",
        clientes=clientes
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {
        "nombre_cliente": "",
        "identificacion": "",
        "telefono": "",
        "correo_electronico": ""
    }
    errores = []

    if request.method == "POST":
        item = {
            "nombre_cliente": request.form.get(
                "nombre_cliente", ""
            ).strip().upper(),

            "identificacion": request.form.get(
                "identificacion", ""
            ).strip().upper(),

            "telefono": request.form.get(
                "telefono", ""
            ).strip(),

            "correo_electronico": request.form.get(
                "correo_electronico", ""
            ).strip().lower()
        }

        if not item["nombre_cliente"]:
            errores.append("El nombre del cliente es obligatorio.")
        elif len(item["nombre_cliente"]) > 100:
            errores.append("El nombre admite máximo 100 caracteres.")

        if not item["identificacion"]:
            errores.append("La identificación es obligatoria.")
        elif len(item["identificacion"]) > 30:
            errores.append(
                "La identificación admite máximo 30 caracteres."
            )
        elif not item["identificacion"].strip():
            errores.append("La identificación es obligatoria.")

        telefono = item["telefono"]

        if telefono and not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            errores.append(
                "Ingrese un teléfono de 7 a 15 dígitos, "
                "sin espacios ni guiones. Puede comenzar con +."
            )

        correo = item["correo_electronico"]

        if len(correo) > 100:
            errores.append("El correo admite máximo 100 caracteres.")
        elif correo and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", correo
        ):
            errores.append("Ingrese un correo electrónico válido.")

        if not errores:
            try:
                execute(
                    """
                    INSERT INTO cliente (
                        nombre_cliente,
                        identificacion,
                        telefono,
                        correo_electronico
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        item["nombre_cliente"],
                        item["identificacion"],
                        telefono or None,
                        correo or None
                    )
                )

                flash("Cliente creado correctamente.", "success")
                return redirect(url_for("clientes.listar"))

            except DatabaseError as exc:
                errores.append(error_message(exc))

    return render_template(
        "clientes/form.html",
        item=item,
        errores=errores,
        titulo="Nuevo cliente"
    )

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query(
        "SELECT * FROM cliente WHERE id_cliente = %s",
        (id,),
        one=True
    )

    if item is None:
        abort(404)

    errores = []

    if request.method == "POST":
        item = {
            "nombre_cliente": request.form.get(
                "nombre_cliente", ""
            ).strip().upper(),

            "identificacion": request.form.get(
                "identificacion", ""
            ).strip().upper(),

            "telefono": request.form.get(
                "telefono", ""
            ).strip(),

            "correo_electronico": request.form.get(
                "correo_electronico", ""
            ).strip().lower()
        }

        if not item["nombre_cliente"]:
            errores.append("El nombre del cliente es obligatorio.")
        elif len(item["nombre_cliente"]) > 100:
            errores.append("El nombre admite máximo 100 caracteres.")

        if not item["identificacion"]:
            errores.append("La identificación es obligatoria.")
        elif len(item["identificacion"]) > 30:
            errores.append(
                "La identificación admite máximo 30 caracteres."
            )

        telefono = item["telefono"]

        if telefono and not re.fullmatch(r"\+?[0-9]{7,15}", telefono):
            errores.append(
                "Ingrese un teléfono de 7 a 15 dígitos, "
                "sin espacios ni guiones. Puede comenzar con +."
            )

        correo = item["correo_electronico"]

        if len(correo) > 100:
            errores.append("El correo admite máximo 100 caracteres.")
        elif correo and not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+", correo
        ):
            errores.append("Ingrese un correo electrónico válido.")

        if not errores:
            try:
                execute(
                    """
                    UPDATE cliente
                    SET nombre_cliente = %s,
                        identificacion = %s,
                        telefono = %s,
                        correo_electronico = %s
                    WHERE id_cliente = %s
                    """,
                    (
                        item["nombre_cliente"],
                        item["identificacion"],
                        telefono or None,
                        correo or None,
                        id
                    )
                )

                flash("Cliente actualizado correctamente.", "success")
                return redirect(url_for("clientes.listar"))

            except DatabaseError as exc:
                errores.append(error_message(exc))

    return render_template(
        "clientes/form.html",
        item=item,
        errores=errores,
        titulo="Editar cliente"
    )

@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        filas = execute(
            "DELETE FROM cliente WHERE id_cliente = %s",
            (id,)
        )

        if filas:
            flash("Cliente eliminado correctamente.", "success")
        else:
            flash("El cliente ya no existe.", "warning")

    except DatabaseError as exc:
        flash(error_message(exc), "danger")

    return redirect(url_for("clientes.listar"))