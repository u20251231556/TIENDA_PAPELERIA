from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint, render_template, abort,
    request, redirect, url_for, flash
)
from db import query, transaction, DatabaseError, error_message

bp = Blueprint(
    "detalle_surtido",
    __name__,
    url_prefix="/detalle_surtido"
)


@bp.route("/<int:id_surtido>")
def listar(id_surtido):
    entrada = query(
        "SELECT * FROM surtido WHERE id_surtido = %s",
        (id_surtido,),
        one=True
    )

    if entrada is None:
        abort(404)

    registros = query(
        """
        SELECT
            d.id_detalle_surtido,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion,
            d.cantidad,
            d.precio_compra,
            d.subtotal
        FROM detalle_surtido d
        JOIN presentacion pr
            ON pr.id_presentacion = d.id_presentacion
        JOIN producto p
            ON p.id_producto = pr.id_producto
        JOIN marca m
            ON m.id_marca = p.id_marca
        WHERE d.id_surtido = %s
        ORDER BY d.id_detalle_surtido
        """,
        (id_surtido,)
    )

    return render_template(
        "detalle_surtido/list.html",
        entrada=entrada,
        registros=registros
    )
@bp.route("/<int:id_surtido>/nuevo", methods=["GET", "POST"])
def crear(id_surtido):
    entrada = query(
        "SELECT * FROM surtido WHERE id_surtido = %s",
        (id_surtido,),
        one=True
    )

    if entrada is None:
        abort(404)

    item = {
        "id_presentacion": "",
        "cantidad": "1",
        "precio_compra": ""
    }
    errores = []

    if request.method == "POST":
        item = {
            "id_presentacion": request.form.get("id_presentacion", ""),
            "cantidad": request.form.get("cantidad", ""),
            "precio_compra": request.form.get("precio_compra", "").strip()
        }

        try:
            id_presentacion = int(item["id_presentacion"])

            if not 1 <= id_presentacion <= 2147483647:
                errores.append("Seleccione una presentación válida.")
        except ValueError:
            errores.append("Seleccione una presentación válida.")

        try:
            cantidad = int(item["cantidad"])

            if not 1 <= cantidad <= 2147483647:
                errores.append(
                    "La cantidad debe estar entre 1 y 2.147.483.647."
                )
        except ValueError:
            errores.append("La cantidad debe ser un número entero.")

        try:
            precio = Decimal(item["precio_compra"])

            if not precio.is_finite():
                errores.append("Ingrese un precio válido.")
            elif precio < 0 or precio > Decimal("9999999999.99"):
                errores.append(
                    "El precio debe estar entre 0 y 9.999.999.999,99."
                )
            elif precio != precio.quantize(Decimal("0.01")):
                errores.append("El precio admite máximo dos decimales.")
        except InvalidOperation:
            errores.append("Ingrese un precio de compra válido.")

        if not errores:
            try:
                with transaction() as cursor:
                    cursor.execute(
                        """
                        SELECT id_producto, unidades_por_presentacion
                        FROM presentacion
                        WHERE id_presentacion = %s
                        FOR SHARE
                        """,
                        (id_presentacion,)
                    )

                    presentacion = cursor.fetchone()

                    if presentacion is None:
                        raise ValueError(
                            "La presentación seleccionada ya no existe."
                        )

                    id_producto, unidades_por_presentacion = presentacion
                    unidades_recibidas = cantidad * unidades_por_presentacion

                    if unidades_recibidas > 2147483647:
                        raise ValueError(
                            "La cantidad de unidades recibidas es demasiado grande."
                        )

                    cursor.execute(
                        """
                        INSERT INTO detalle_surtido (
                            id_surtido,
                            id_presentacion,
                            cantidad,
                            precio_compra
                        )
                        VALUES (%s, %s, %s, %s)
                        """,
                        (id_surtido, id_presentacion, cantidad, precio)
                    )

                    cursor.execute(
                        """
                        INSERT INTO inventario (
                            id_producto,
                            cantidad_disponible
                        )
                        VALUES (%s, %s)
                        ON CONFLICT (id_producto)
                        DO UPDATE SET cantidad_disponible =
                            inventario.cantidad_disponible
                            + EXCLUDED.cantidad_disponible
                        """,
                        (id_producto, unidades_recibidas)
                    )

                flash(
                    "Artículo agregado e inventario actualizado.",
                    "success"
                )

                return redirect(url_for(
                    "detalle_surtido.listar",
                    id_surtido=id_surtido
                ))

            except DatabaseError as exc:
                errores.append(error_message(exc))
            except ValueError as exc:
                errores.append(str(exc))

    presentaciones = query("""
        SELECT
            pr.id_presentacion,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion
        FROM presentacion pr
        JOIN producto p ON p.id_producto = pr.id_producto
        JOIN marca m ON m.id_marca = p.id_marca
        ORDER BY p.nombre_producto, m.nombre_marca,
                 pr.unidades_por_presentacion
    """)

    return render_template(
        "detalle_surtido/form.html",
        entrada=entrada,
        item=item,
        presentaciones=presentaciones,
        errores=errores
    )

@bp.route(
    "/<int:id_surtido>/<int:id>/eliminar",
    methods=["POST"]
)
def eliminar(id_surtido, id):
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                SELECT
                    d.cantidad,
                    pr.id_producto,
                    pr.unidades_por_presentacion
                FROM detalle_surtido d
                JOIN presentacion pr
                    ON pr.id_presentacion = d.id_presentacion
                WHERE d.id_detalle_surtido = %s
                  AND d.id_surtido = %s
                FOR UPDATE OF d
                FOR SHARE OF pr
                """,
                (id, id_surtido)
            )

            detalle = cursor.fetchone()

            if detalle is None:
                raise ValueError("El artículo ya no existe en esta entrada.")

            cantidad, id_producto, unidades_por_presentacion = detalle
            unidades = cantidad * unidades_por_presentacion

            cursor.execute(
                """
                UPDATE inventario
                SET cantidad_disponible = cantidad_disponible - %s
                WHERE id_producto = %s
                  AND cantidad_disponible >= %s
                RETURNING id_inventario
                """,
                (unidades, id_producto, unidades)
            )

            if cursor.fetchone() is None:
                raise ValueError(
                    "No se puede eliminar: no hay suficientes "
                    "existencias para descontar esta entrada."
                )

            cursor.execute(
                """
                DELETE FROM detalle_surtido
                WHERE id_detalle_surtido = %s
                  AND id_surtido = %s
                """,
                (id, id_surtido)
            )

        flash("Artículo eliminado e inventario actualizado.", "success")

    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for(
        "detalle_surtido.listar",
        id_surtido=id_surtido
    ))
@bp.route(
    "/<int:id_surtido>/<int:id>/editar",
    methods=["GET", "POST"]
)
def editar(id_surtido, id):
    entrada = query(
        "SELECT * FROM surtido WHERE id_surtido = %s",
        (id_surtido,),
        one=True
    )

    if entrada is None:
        abort(404)

    item = query(
        """
        SELECT *
        FROM detalle_surtido
        WHERE id_detalle_surtido = %s
          AND id_surtido = %s
        """,
        (id, id_surtido),
        one=True
    )

    if item is None:
        abort(404)

    errores = []

    if request.method == "POST":
        item["cantidad"] = request.form.get("cantidad", "")
        item["precio_compra"] = request.form.get(
            "precio_compra", ""
        ).strip()

        try:
            cantidad = int(item["cantidad"])

            if not 1 <= cantidad <= 2147483647:
                errores.append(
                    "La cantidad debe estar entre 1 y 2.147.483.647."
                )
        except ValueError:
            errores.append("La cantidad debe ser un número entero.")

        try:
            precio = Decimal(item["precio_compra"])

            if not precio.is_finite():
                errores.append("Ingrese un precio válido.")
            elif precio < 0 or precio > Decimal("9999999999.99"):
                errores.append(
                    "El precio debe estar entre 0 y 9.999.999.999,99."
                )
            elif precio != precio.quantize(Decimal("0.01")):
                errores.append("El precio admite máximo dos decimales.")
        except InvalidOperation:
            errores.append("Ingrese un precio de compra válido.")

        if not errores:
            try:
                with transaction() as cursor:
                    cursor.execute(
                        """
                        SELECT
                            d.cantidad,
                            pr.id_producto,
                            pr.unidades_por_presentacion
                        FROM detalle_surtido d
                        JOIN presentacion pr
                            ON pr.id_presentacion = d.id_presentacion
                        WHERE d.id_detalle_surtido = %s
                          AND d.id_surtido = %s
                        FOR UPDATE OF d
                        FOR SHARE OF pr
                        """,
                        (id, id_surtido)
                    )

                    anterior = cursor.fetchone()

                    if anterior is None:
                        raise ValueError(
                            "El artículo ya no existe en esta entrada."
                        )

                    cantidad_anterior, id_producto, unidades = anterior
                    diferencia = (cantidad - cantidad_anterior) * unidades

                    if diferencia != 0:
                        cursor.execute(
                            """
                            UPDATE inventario
                            SET cantidad_disponible =
                                cantidad_disponible::bigint + %s
                            WHERE id_producto = %s
                              AND cantidad_disponible::bigint + %s
                                  BETWEEN 0 AND 2147483647
                            RETURNING id_inventario
                            """,
                            (diferencia, id_producto, diferencia)
                        )

                        if cursor.fetchone() is None:
                            raise ValueError(
                                "No se puede ajustar la cantidad: "
                                "el inventario no existe o el cambio "
                                "dejaría las existencias fuera del rango permitido."
                            )

                    cursor.execute(
                        """
                        UPDATE detalle_surtido
                        SET cantidad = %s,
                            precio_compra = %s
                        WHERE id_detalle_surtido = %s
                          AND id_surtido = %s
                        """,
                        (cantidad, precio, id, id_surtido)
                    )

                flash(
                    "Artículo actualizado e inventario ajustado.",
                    "success"
                )

                return redirect(url_for(
                    "detalle_surtido.listar",
                    id_surtido=id_surtido
                ))

            except DatabaseError as exc:
                errores.append(error_message(exc))
            except ValueError as exc:
                errores.append(str(exc))

    presentaciones = query(
        """
        SELECT
            pr.id_presentacion,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion
        FROM presentacion pr
        JOIN producto p ON p.id_producto = pr.id_producto
        JOIN marca m ON m.id_marca = p.id_marca
        WHERE pr.id_presentacion = %s
        """,
        (item["id_presentacion"],)
    )

    return render_template(
        "detalle_surtido/form.html",
        entrada=entrada,
        item=item,
        presentaciones=presentaciones,
        errores=errores,
        editando=True
    )
