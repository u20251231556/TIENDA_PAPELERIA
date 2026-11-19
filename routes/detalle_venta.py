from decimal import Decimal

from flask import Blueprint, render_template, abort
from db import query

bp = Blueprint(
    "detalle_venta",
    __name__,
    url_prefix="/detalle_venta"
)


@bp.route("/<int:id_venta>")
def listar(id_venta):
    venta = query(
        """
        SELECT
            v.id_venta,
            v.fecha_venta,
            COALESCE(
                c.nombre_cliente,
                'Venta de mostrador'
            ) AS nombre_cliente,
            c.identificacion
        FROM venta v
        LEFT JOIN cliente c ON c.id_cliente = v.id_cliente
        WHERE v.id_venta = %s
        """,
        (id_venta,),
        one=True
    )

    if venta is None:
        abort(404)

    registros = query(
        """
        SELECT
            d.id_detalle_venta,
            p.nombre_producto,
            m.nombre_marca,
            pr.tipo_presentacion,
            pr.unidades_por_presentacion,
            d.cantidad,
            d.precio_unitario,
            d.subtotal
        FROM detalle_venta d
        JOIN presentacion pr
            ON pr.id_presentacion = d.id_presentacion
        JOIN producto p
            ON p.id_producto = pr.id_producto
        JOIN marca m
            ON m.id_marca = p.id_marca
        WHERE d.id_venta = %s
        ORDER BY d.id_detalle_venta
        """,
        (id_venta,)
    )

    total = sum(
        (registro["subtotal"] for registro in registros),
        Decimal("0.00")
    )

    return render_template(
        "detalle_venta/list.html",
        venta=venta,
        registros=registros,
        total=total
    )
