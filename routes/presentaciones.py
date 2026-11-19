from decimal import Decimal, InvalidOperation


from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, abort
)
from db import query, execute, DatabaseError, error_message


bp = Blueprint(
    "presentaciones",
    __name__,
    url_prefix="/presentaciones"
)




def leer_formulario(formulario):
    item = {
        "id_producto": formulario.get("id_producto", ""),
        "tipo_presentacion": formulario.get("tipo_presentacion", ""),
        "unidades_por_presentacion": formulario.get(
            "unidades_por_presentacion", ""
        ),
        "precio_venta": formulario.get("precio_venta", "").strip()
    }


    errores = []
    id_producto = None
    unidades = None
    precio = None


    try:
        id_producto = int(item["id_producto"])


        if not 1 <= id_producto <= 2147483647:
            errores.append("Seleccione un producto válido.")
    except ValueError:
        errores.append("Seleccione un producto válido.")


    tipo = item["tipo_presentacion"]


    if tipo not in ("unidad", "caja"):
        errores.append("Seleccione unidad o caja.")


    try:
        unidades = int(item["unidades_por_presentacion"])


        if not 1 <= unidades <= 2147483647:
            errores.append(
                "La cantidad debe estar entre 1 y 2.147.483.647."
            )
        elif tipo == "unidad" and unidades != 1:
            errores.append(
                "La presentación unidad debe contener 1 unidad."
            )
    except ValueError:
        errores.append(
            "La cantidad de unidades debe ser un número entero."
        )


    try:
        precio = Decimal(item["precio_venta"])


        if not precio.is_finite():
            errores.append("Ingrese un precio válido.")
        elif precio < 0 or precio > Decimal("9999999999.99"):
            errores.append(
                "El precio debe estar entre 0 y 9.999.999.999,99."
            )
        elif precio != precio.quantize(Decimal("0.01")):
            errores.append("El precio admite máximo dos decimales.")
    except InvalidOperation:
        errores.append("Ingrese un precio válido.")


    datos = (id_producto, tipo, unidades, precio)


    return item, datos, errores




def mostrar_formulario(item, errores, titulo):
    productos = query("""
        SELECT
            p.id_producto,
            p.nombre_producto,
            m.nombre_marca
        FROM producto p
        JOIN marca m ON m.id_marca = p.id_marca
        ORDER BY p.nombre_producto, m.nombre_marca
    """)


    return render_template(
        "presentaciones/form.html",
        item=item,
        productos=productos,
        errores=errores,
        titulo=titulo
    )




@bp.route("/")
def listar():
    presentaciones = query("""
        SELECT
            pr.id_presentacion,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion,
            pr.precio_venta
        FROM presentacion pr
        JOIN producto p ON p.id_producto = pr.id_producto
        JOIN marca m ON m.id_marca = p.id_marca
        ORDER BY pr.id_presentacion
    """)


    return render_template(
        "presentaciones/list.html",
        presentaciones=presentaciones
    )




@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {
        "id_producto": "",
        "tipo_presentacion": "unidad",
        "unidades_por_presentacion": "1",
        "precio_venta": ""
    }
    errores = []


    if request.method == "POST":
        item, datos, errores = leer_formulario(request.form)


        if not errores:
            try:
                execute(
                    """
                    INSERT INTO presentacion (
                        id_producto,
                        tipo_presentacion,
                        unidades_por_presentacion,
                        precio_venta
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    datos
                )


                flash("Presentación creada correctamente.", "success")
                return redirect(url_for("presentaciones.listar"))


            except DatabaseError as exc:
                errores.append(error_message(exc))


    return mostrar_formulario(item, errores, "Nueva presentación")




@bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    item = query(
        "SELECT * FROM presentacion WHERE id_presentacion = %s",
        (id,),
        one=True
    )


    if item is None:
        abort(404)


    errores = []


    if request.method == "POST":
        item, datos, errores = leer_formulario(request.form)


        if not errores:
            try:
                execute(
                    """
                    UPDATE presentacion
                    SET id_producto = %s,
                        tipo_presentacion = %s,
                        unidades_por_presentacion = %s,
                        precio_venta = %s
                    WHERE id_presentacion = %s
                    """,
                    datos + (id,)
                )


                flash(
                    "Presentación actualizada correctamente.",
                    "success"
                )
                return redirect(url_for("presentaciones.listar"))


            except DatabaseError as exc:
                errores.append(error_message(exc))


    return mostrar_formulario(item, errores, "Editar presentación")


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        filas = execute(
            "DELETE FROM presentacion WHERE id_presentacion = %s",
            (id,)
        )


        if filas:
            flash("Presentación eliminada correctamente.", "success")
        else:
            flash("La presentación ya no existe.", "warning")


    except DatabaseError as exc:
        flash(error_message(exc), "danger")


    return redirect(url_for("presentaciones.listar"))
