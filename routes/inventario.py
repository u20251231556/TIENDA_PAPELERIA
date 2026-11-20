from flask import Blueprint, render_template
from db import query

bp = Blueprint(
    "inventario",
    __name__,
    url_prefix="/inventario"
)


@bp.route("/")
def listar():
    registros = query("""
        SELECT
            i.id_inventario,
            p.nombre_producto,
            m.nombre_marca,
            i.cantidad_disponible
        FROM inventario i
        JOIN producto p ON p.id_producto = i.id_producto
        JOIN marca m ON m.id_marca = p.id_marca
        ORDER BY p.nombre_producto, m.nombre_marca
    """)

    return render_template(
        "inventario/list.html",
        registros=registros
    )