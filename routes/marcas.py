from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from db import query, execute, DatabaseError, error_message

bp = Blueprint("marcas", __name__, url_prefix="/marcas")


@bp.route("/")
def listar():
    marcas = query("""
        SELECT id_marca, nombre_marca
        FROM marca
        ORDER BY id_marca
    """)

    return render_template("marcas/list.html", marcas=marcas)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    nombre = ""
    errores = []

    if request.method == "POST":
        nombre = request.form.get("nombre_marca", "").strip().upper()


        if not nombre:
            errores.append("El nombre es obligatorio.")
        elif len(nombre) > 80:
            errores.append("El nombre admite máximo 80 caracteres.")

        if not errores:
            try:
                execute(
                    "INSERT INTO marca (nombre_marca) VALUES (%s)",
                    (nombre,)
                )
                flash("Marca creada correctamente.", "success")

                return redirect(url_for("marcas.listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))

    return render_template(
        "marcas/form.html",
        nombre=nombre,
        errores=errores
    )
@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    marca = query(
        "SELECT * FROM marca WHERE id_marca = %s",
        (id,),
        one=True
    )
    if marca is None:
        abort(404)

    nombre = marca["nombre_marca"]
    errores = []

    if request.method == "POST":
        nombre = request.form.get("nombre_marca", "").strip().upper()

        if not nombre:
            errores.append("El nombre es obligatorio.")
        elif len(nombre) > 80:
            errores.append("El nombre admite máximo 80 caracteres.")

        if not errores:
            try:
                execute(
                    "UPDATE marca SET nombre_marca = %s WHERE id_marca = %s",
                    (nombre, id)
                )
                flash("Marca actualizada correctamente.", "success")
                return redirect(url_for("marcas.listar"))
            except DatabaseError as exc:
                errores.append(error_message(exc))

    return render_template(
        "marcas/form.html",
        nombre=nombre,
        errores=errores,
        titulo="Editar marca"
    )

@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        filas = execute(
            "DELETE FROM marca WHERE id_marca = %s",
            (id,)
        )

        if filas:
            flash("Marca eliminada correctamente.", "success")
        else:
            flash("La marca ya no existe.", "warning")

    except DatabaseError as exc:
        flash(error_message(exc), "danger")

    return redirect(url_for("marcas.listar"))
