from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from db import query, execute, DatabaseError, error_message

bp = Blueprint("productos", __name__, url_prefix="/productos")


@bp.route("/")
def listar():
    productos = query("""
        SELECT
            p.id_producto,
            p.nombre_producto,
            m.nombre_marca
        FROM producto p
        JOIN marca m ON m.id_marca = p.id_marca
        ORDER BY p.id_producto
    """)

    return render_template(
        "productos/list.html",
        productos=productos
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {
        "nombre_producto": "",
        "id_marca": ""
    }
    errores = []

    if request.method == "POST":
        item = {
            "nombre_producto": request.form.get(
                "nombre_producto", ""
            ).strip().upper(),
            "id_marca": request.form.get("id_marca", "")
        }

        if not item["nombre_producto"]:
            errores.append("El nombre del producto es obligatorio.")
        elif len(item["nombre_producto"]) > 100:
            errores.append("El nombre admite máximo 100 caracteres.")

        try:
            id_marca = int(item["id_marca"])
            if id_marca <= 0:
                errores.append("Seleccione una marca válida.")
        except ValueError:
            errores.append("Seleccione una marca válida.")

        if not errores:
            try:
                execute(
                    """
                    INSERT INTO producto (nombre_producto, id_marca)
                    VALUES (%s, %s)
                    """,
                    (item["nombre_producto"], id_marca)
                )

                flash("Producto creado correctamente.", "success")
                return redirect(url_for("productos.listar"))

            except DatabaseError as exc:
                errores.append(error_message(exc))

    marcas = query("""
        SELECT id_marca, nombre_marca
        FROM marca
        ORDER BY nombre_marca
    """)

    return render_template(
        "productos/form.html",
        item=item,
        marcas=marcas,
        errores=errores
    )

@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query(
        "SELECT * FROM producto WHERE id_producto = %s",
        (id,),
        one=True
    )

    if item is None:
        abort(404)

    errores = []

    if request.method == "POST":
        item = {
            "nombre_producto": request.form.get(
                "nombre_producto", ""
            ).strip().upper(),
            "id_marca": request.form.get("id_marca", "")
        }

        if not item["nombre_producto"]:
            errores.append("El nombre del producto es obligatorio.")
        elif len(item["nombre_producto"]) > 100:
            errores.append("El nombre admite máximo 100 caracteres.")

        try:
            id_marca = int(item["id_marca"])
            if id_marca <= 0:
                errores.append("Seleccione una marca válida.")
        except ValueError:
            errores.append("Seleccione una marca válida.")

        if not errores:
            try:
                execute(
                    """
                    UPDATE producto
                    SET nombre_producto = %s, id_marca = %s
                    WHERE id_producto = %s
                    """,
                    (item["nombre_producto"], id_marca, id)
                )

                flash("Producto actualizado correctamente.", "success")
                return redirect(url_for("productos.listar"))

            except DatabaseError as exc:
                errores.append(error_message(exc))

    marcas = query("""
        SELECT id_marca, nombre_marca
        FROM marca
        ORDER BY nombre_marca
    """)

    return render_template(
        "productos/form.html",
        item=item,
        marcas=marcas,
        errores=errores,
        titulo="Editar producto"
    )

@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        filas = execute(
            "DELETE FROM producto WHERE id_producto = %s",
            (id,)
        )

        if filas:
            flash("Producto eliminado correctamente.", "success")
        else:
            flash("El producto ya no existe.", "warning")

    except DatabaseError as exc:
        flash(error_message(exc), "danger")

    return redirect(url_for("productos.listar"))