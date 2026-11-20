from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from db import query, transaction, DatabaseError, error_message

bp = Blueprint("surtido", __name__, url_prefix="/surtido")


def leer_articulos(formulario):
    presentaciones = formulario.getlist("id_presentacion")
    cantidades = formulario.getlist("cantidad")
    precios = formulario.getlist("precio_compra")

    articulos = []
    datos = []
    errores = []

    if not presentaciones:
        errores.append("Agregue al menos un artículo.")
        return articulos, datos, errores

    if not (
        len(presentaciones) == len(cantidades) == len(precios)
    ):
        errores.append("Los datos de los artículos están incompletos.")
        return articulos, datos, errores

    for numero, (presentacion, cantidad, precio_texto) in enumerate(
        zip(presentaciones, cantidades, precios),
        start=1
    ):
        articulos.append({
            "id_presentacion": presentacion,
            "cantidad": cantidad,
            "precio_compra": precio_texto
        })

        errores_antes = len(errores)
        id_presentacion = None
        cantidad_validada = None
        precio = None

        try:
            id_presentacion = int(presentacion)

            if not 1 <= id_presentacion <= 2147483647:
                raise ValueError

        except ValueError:
            errores.append(
                f"Artículo {numero}: seleccione una presentación válida."
            )

        try:
            cantidad_validada = int(cantidad)

            if not 1 <= cantidad_validada <= 2147483647:
                raise ValueError

        except ValueError:
            errores.append(
                f"Artículo {numero}: ingrese una cantidad entera "
                "entre 1 y 2.147.483.647."
            )

        try:
            precio = Decimal(precio_texto.strip())

            if not precio.is_finite():
                raise InvalidOperation

            if not Decimal("0") <= precio <= Decimal("9999999999.99"):
                raise InvalidOperation

            if precio != precio.quantize(Decimal("0.01")):
                raise InvalidOperation

        except InvalidOperation:
            errores.append(
                f"Artículo {numero}: ingrese un precio entre "
                "0 y 9.999.999.999,99, con máximo dos decimales."
            )

        if len(errores) == errores_antes:
            subtotal = cantidad_validada * precio

            if subtotal > Decimal("999999999999.99"):
                errores.append(
                    f"Artículo {numero}: el subtotal supera "
                    "el límite permitido."
                )
            else:
                datos.append((
                    id_presentacion,
                    cantidad_validada,
                    precio
                ))

    return articulos, datos, errores


@bp.route("/")
def listar():
    surtido = query("""
        SELECT id_surtido, fecha_surtido
        FROM surtido
        ORDER BY fecha_surtido DESC, id_surtido DESC
    """)

    return render_template(
        "surtido/list.html",
        surtido=surtido
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    fecha = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    articulos = [{
        "id_presentacion": "",
        "cantidad": "1",
        "precio_compra": ""
    }]
    errores = []

    if request.method == "POST":
        fecha = request.form.get("fecha_surtido", "").strip()
        articulos, datos, errores = leer_articulos(request.form)

        fecha_validada = None

        try:
            fecha_validada = datetime.fromisoformat(fecha)

            if fecha_validada.tzinfo is not None:
                raise ValueError

        except ValueError:
            errores.append("Ingrese una fecha y hora válidas.")

        if not errores:
            try:
                with transaction() as cursor:
                    ids = sorted({
                        id_presentacion
                        for id_presentacion, cantidad, precio in datos
                    })

                    cursor.execute(
                        """
                        SELECT
                            id_presentacion,
                            id_producto,
                            unidades_por_presentacion
                        FROM presentacion
                        WHERE id_presentacion = ANY(%s)
                        ORDER BY id_presentacion
                        FOR SHARE
                        """,
                        (ids,)
                    )

                    catalogo = {
                        fila[0]: (fila[1], fila[2])
                        for fila in cursor.fetchall()
                    }

                    unidades_por_producto = {}

                    for id_presentacion, cantidad, precio in datos:
                        if id_presentacion not in catalogo:
                            raise ValueError(
                                "Una presentación seleccionada ya no existe."
                            )

                        id_producto, unidades = catalogo[id_presentacion]

                        unidades_por_producto[id_producto] = (
                            unidades_por_producto.get(id_producto, 0)
                            + cantidad * unidades
                        )

                    for unidades in unidades_por_producto.values():
                        if unidades > 2147483647:
                            raise ValueError(
                                "La cantidad de unidades de un producto "
                                "supera el límite permitido."
                            )

                    cursor.execute(
                        """
                        INSERT INTO surtido (fecha_surtido)
                        VALUES (%s)
                        RETURNING id_surtido
                        """,
                        (fecha_validada,)
                    )

                    id_surtido = cursor.fetchone()[0]

                    for id_presentacion, cantidad, precio in datos:
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
                            (
                                id_surtido,
                                id_presentacion,
                                cantidad,
                                precio
                            )
                        )

                    for id_producto in sorted(unidades_por_producto):
                        unidades = unidades_por_producto[id_producto]

                        cursor.execute(
                            """
                            INSERT INTO inventario (
                                id_producto,
                                cantidad_disponible
                            )
                            VALUES (%s, %s)
                            ON CONFLICT (id_producto)
                            DO UPDATE SET cantidad_disponible =
                                inventario.cantidad_disponible::bigint
                                + EXCLUDED.cantidad_disponible
                            WHERE inventario.cantidad_disponible::bigint
                                + EXCLUDED.cantidad_disponible
                                <= 2147483647
                            RETURNING id_inventario
                            """,
                            (id_producto, unidades)
                        )

                        if cursor.fetchone() is None:
                            raise ValueError(
                                "Las existencias de un producto "
                                "superarían el límite permitido."
                            )

                flash(
                    "Entrada registrada e inventario actualizado.",
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
        "surtido/form.html",
        fecha=fecha,
        articulos=articulos,
        presentaciones=presentaciones,
        errores=errores,
        titulo="Nueva entrada de mercancía"
    )


@bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    try:
        with transaction() as cursor:
            cursor.execute(
                """
                SELECT id_surtido
                FROM surtido
                WHERE id_surtido = %s
                FOR UPDATE
                """,
                (id,)
            )

            if cursor.fetchone() is None:
                raise ValueError("La entrada ya no existe.")

            cursor.execute(
                """
                SELECT
                    d.cantidad,
                    pr.id_producto,
                    pr.unidades_por_presentacion
                FROM detalle_surtido d
                JOIN presentacion pr
                    ON pr.id_presentacion = d.id_presentacion
                WHERE d.id_surtido = %s
                ORDER BY d.id_detalle_surtido
                FOR UPDATE OF d
                FOR SHARE OF pr
                """,
                (id,)
            )

            unidades_por_producto = {}

            for cantidad, id_producto, unidades in cursor.fetchall():
                unidades_por_producto[id_producto] = (
                    unidades_por_producto.get(id_producto, 0)
                    + cantidad * unidades
                )

            for id_producto in sorted(unidades_por_producto):
                unidades = unidades_por_producto[id_producto]

                cursor.execute(
                    """
                    UPDATE inventario
                    SET cantidad_disponible =
                        cantidad_disponible - %s
                    WHERE id_producto = %s
                      AND cantidad_disponible >= %s
                    RETURNING id_inventario
                    """,
                    (unidades, id_producto, unidades)
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        "No se puede eliminar la entrada: "
                        "no hay existencias suficientes para "
                        "descontar toda su mercancía."
                    )

            cursor.execute(
                "DELETE FROM detalle_surtido WHERE id_surtido = %s",
                (id,)
            )

            cursor.execute(
                "DELETE FROM surtido WHERE id_surtido = %s",
                (id,)
            )

        flash(
            "Entrada eliminada e inventario actualizado.",
            "success"
        )

    except DatabaseError as exc:
        flash(error_message(exc), "danger")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("surtido.listar"))