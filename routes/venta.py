from datetime import datetime
from decimal import Decimal

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from db import query, transaction, DatabaseError, error_message

bp = Blueprint("venta", __name__, url_prefix="/venta")


def leer_articulos(formulario):
    presentaciones = formulario.getlist("id_presentacion")
    cantidades = formulario.getlist("cantidad")

    articulos = []
    datos = []
    errores = []

    if not presentaciones:
        errores.append("Agregue al menos un artículo.")
        return articulos, datos, errores

    if len(presentaciones) != len(cantidades):
        errores.append("Los datos de los artículos están incompletos.")
        return articulos, datos, errores

    for numero, (presentacion, cantidad) in enumerate(
        zip(presentaciones, cantidades),
        start=1
    ):
        articulos.append({
            "id_presentacion": presentacion,
            "cantidad": cantidad
        })

        errores_antes = len(errores)
        id_presentacion = None
        cantidad_validada = None

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

        if len(errores) == errores_antes:
            datos.append((id_presentacion, cantidad_validada))

    return articulos, datos, errores


@bp.route("/")
def listar():
    registros = query("""
        SELECT
            v.id_venta,
            v.fecha_venta,
            COALESCE(
                c.nombre_cliente,
                'Venta de mostrador'
            ) AS nombre_cliente,
            COALESCE(
                (
                    SELECT SUM(d.subtotal)
                    FROM detalle_venta d
                    WHERE d.id_venta = v.id_venta
                ),
                0
            ) AS total
        FROM venta v
        LEFT JOIN cliente c ON c.id_cliente = v.id_cliente
        ORDER BY v.fecha_venta DESC, v.id_venta DESC
    """)

    return render_template(
        "venta/list.html",
        registros=registros
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    item = {
        "fecha_venta": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "id_cliente": ""
    }

    articulos = [{
        "id_presentacion": "",
        "cantidad": "1"
    }]

    errores = []

    if request.method == "POST":
        item = {
            "fecha_venta": request.form.get(
                "fecha_venta", ""
            ).strip(),

            "id_cliente": request.form.get(
                "id_cliente", ""
            ).strip()
        }

        articulos, datos, errores = leer_articulos(request.form)

        fecha = None
        id_cliente = None

        try:
            fecha = datetime.fromisoformat(item["fecha_venta"])

            if fecha.tzinfo is not None:
                raise ValueError

        except ValueError:
            errores.append("Ingrese una fecha y hora válidas.")

        if item["id_cliente"]:
            try:
                id_cliente = int(item["id_cliente"])

                if not 1 <= id_cliente <= 2147483647:
                    raise ValueError

            except ValueError:
                errores.append("Seleccione un cliente válido.")

        if not errores:
            try:
                with transaction() as cursor:
                    ids = sorted({
                        id_presentacion
                        for id_presentacion, cantidad in datos
                    })

                    cursor.execute(
                        """
                        SELECT
                            pr.id_presentacion,
                            pr.id_producto,
                            pr.unidades_por_presentacion,
                            pr.precio_venta,
                            p.nombre_producto
                        FROM presentacion pr
                        JOIN producto p
                            ON p.id_producto = pr.id_producto
                        WHERE pr.id_presentacion = ANY(%s)
                        ORDER BY pr.id_presentacion
                        FOR SHARE OF pr
                        """,
                        (ids,)
                    )

                    catalogo = {
                        fila[0]: {
                            "id_producto": fila[1],
                            "unidades": fila[2],
                            "precio": fila[3],
                            "nombre": fila[4]
                        }
                        for fila in cursor.fetchall()
                    }

                    unidades_por_producto = {}
                    nombres = {}
                    detalles = []

                    for id_presentacion, cantidad in datos:
                        if id_presentacion not in catalogo:
                            raise ValueError(
                                "Una presentación seleccionada ya no existe."
                            )

                        presentacion = catalogo[id_presentacion]
                        id_producto = presentacion["id_producto"]
                        precio = presentacion["precio"]

                        if (
                            not precio.is_finite()
                            or precio < 0
                            or precio > Decimal("9999999999.99")
                        ):
                            raise ValueError(
                                "Una presentación tiene un precio inválido. "
                                "Revíselo antes de vender."
                            )

                        if cantidad * precio > Decimal("999999999999.99"):
                            raise ValueError(
                                "El subtotal de un artículo supera "
                                "el límite permitido."
                            )

                        unidades_por_producto[id_producto] = (
                            unidades_por_producto.get(id_producto, 0)
                            + cantidad * presentacion["unidades"]
                        )

                        nombres[id_producto] = presentacion["nombre"]

                        detalles.append((
                            id_presentacion,
                            cantidad,
                            precio
                        ))

                    for unidades in unidades_por_producto.values():
                        if unidades > 2147483647:
                            raise ValueError(
                                "La cantidad solicitada supera "
                                "el máximo de existencias permitido."
                            )

                    cursor.execute(
                        """
                        INSERT INTO venta (fecha_venta, id_cliente)
                        VALUES (%s, %s)
                        RETURNING id_venta
                        """,
                        (fecha, id_cliente)
                    )

                    id_venta = cursor.fetchone()[0]

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
                                "Existencias insuficientes para el producto: "
                                + nombres[id_producto]
                            )

                    for id_presentacion, cantidad, precio in detalles:
                        cursor.execute(
                            """
                            INSERT INTO detalle_venta (
                                id_venta,
                                id_presentacion,
                                cantidad,
                                precio_unitario
                            )
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                id_venta,
                                id_presentacion,
                                cantidad,
                                precio
                            )
                        )

                flash(
                    "Venta registrada e inventario actualizado.",
                    "success"
                )

                return redirect(url_for(
                    "detalle_venta.listar",
                    id_venta=id_venta
                ))

            except DatabaseError as exc:
                errores.append(error_message(exc))
            except ValueError as exc:
                errores.append(str(exc))

    clientes = query("""
        SELECT id_cliente, nombre_cliente, identificacion
        FROM cliente
        ORDER BY nombre_cliente, identificacion
    """)

    presentaciones = query("""
        SELECT
            pr.id_presentacion,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion,
            pr.precio_venta,
            COALESCE(
                i.cantidad_disponible, 0
            ) AS unidades_disponibles
        FROM presentacion pr
        JOIN producto p ON p.id_producto = pr.id_producto
        JOIN marca m ON m.id_marca = p.id_marca
        LEFT JOIN inventario i ON i.id_producto = p.id_producto
        ORDER BY p.nombre_producto, m.nombre_marca,
                pr.unidades_por_presentacion
    """)

    return render_template(
        "venta/form.html",
        item=item,
        clientes=clientes,
        presentaciones=presentaciones,
        articulos=articulos,
        errores=errores,
        titulo="Nueva venta"
    )

