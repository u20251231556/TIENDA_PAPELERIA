from decimal import Decimal

from db import query


def crear_producto(client, app):
    # Crear la marca.
    client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "PELIKAN"}
    )

    with app.app_context():
        marca = query(
            "SELECT id_marca FROM marca WHERE nombre_marca = %s",
            ("PELIKAN",),
            one=True
        )

    assert marca is not None

    # Crear el producto.
    client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "LAPIZ PRUEBA",
            "id_marca": str(marca["id_marca"])
        }
    )

    with app.app_context():
        producto = query(
            """
            SELECT id_producto
            FROM producto
            WHERE nombre_producto = %s
            """,
            ("LAPIZ PRUEBA",),
            one=True
        )

    assert producto is not None
    return producto["id_producto"]


def consultar_presentaciones(app):
    with app.app_context():
        return query(
            """
            SELECT *
            FROM presentacion
            ORDER BY id_presentacion
            """
        )


def test_crear_editar_eliminar_presentacion(client, app):
    id_producto = crear_producto(client, app)

    # Crear una caja de 12 unidades.
    respuesta = client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "12",
            "precio_venta": "10000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    presentaciones = consultar_presentaciones(app)

    assert len(presentaciones) == 1
    assert presentaciones[0]["id_producto"] == id_producto
    assert presentaciones[0]["tipo_presentacion"] == "caja"
    assert presentaciones[0]["unidades_por_presentacion"] == 12
    assert presentaciones[0]["precio_venta"] == Decimal("10000")

    id_presentacion = presentaciones[0]["id_presentacion"]

    # Comprobar el listado.
    respuesta = client.get("/presentaciones/")
    html = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200
    assert "LAPIZ PRUEBA" in html
    assert "PELIKAN" in html

    # Editar: no tiene entradas ni ventas, por eso se puede cambiar.
    respuesta = client.post(
        f"/presentaciones/{id_presentacion}/editar",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "24",
            "precio_venta": "18000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    presentaciones = consultar_presentaciones(app)

    assert len(presentaciones) == 1
    assert presentaciones[0]["id_presentacion"] == id_presentacion
    assert presentaciones[0]["unidades_por_presentacion"] == 24
    assert presentaciones[0]["precio_venta"] == Decimal("18000")

    # Eliminar.
    respuesta = client.post(
        f"/presentaciones/{id_presentacion}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert consultar_presentaciones(app) == []


def test_presentacion_unidad_debe_contener_una(client, app):
    id_producto = crear_producto(client, app)

    # Una presentación "unidad" no puede contener 12 unidades.
    respuesta = client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "unidad",
            "unidades_por_presentacion": "12",
            "precio_venta": "1000"
        }
    )

    assert respuesta.status_code == 200
    assert consultar_presentaciones(app) == []
    assert "debe contener 1" in respuesta.get_data(as_text=True).lower()


def test_presentacion_duplicada(client, app):
    id_producto = crear_producto(client, app)

    datos = {
        "id_producto": str(id_producto),
        "tipo_presentacion": "caja",
        "unidades_por_presentacion": "12",
        "precio_venta": "10000"
    }

    # Guardar la primera presentación.
    client.post(
        "/presentaciones/nuevo",
        data=datos
    )

    assert len(consultar_presentaciones(app)) == 1

    # Intentar guardar la misma presentación.
    respuesta = client.post(
        "/presentaciones/nuevo",
        data=datos,
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert len(consultar_presentaciones(app)) == 1
    assert "existe" in respuesta.get_data(as_text=True).lower()

def test_presentacion_utilizada_solo_permite_cambiar_precio(client, app):
    id_producto = crear_producto(client, app)

    # Crear una caja de 12 unidades.
    client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "12",
            "precio_venta": "10000"
        }
    )

    presentaciones = consultar_presentaciones(app)
    assert len(presentaciones) == 1

    id_presentacion = presentaciones[0]["id_presentacion"]

    # Registrar una entrada para que tenga movimientos.
    client.post(
        "/surtido/nuevo",
        data={
            "fecha_surtido": "2026-11-18T10:00:00",
            "id_presentacion": str(id_presentacion),
            "cantidad": "2",
            "precio_compra": "7000"
        }
    )

    with app.app_context():
        detalles = query("SELECT * FROM detalle_surtido")

    assert len(detalles) == 1

    # Intentar cambiar la caja de 12 a 24 unidades.
    respuesta = client.post(
        f"/presentaciones/{id_presentacion}/editar",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "24",
            "precio_venta": "10000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert "solo puede actualizar" in (
        respuesta.get_data(as_text=True).lower()
    )

    presentaciones = consultar_presentaciones(app)

    # Debe conservar las 12 unidades.
    assert presentaciones[0]["unidades_por_presentacion"] == 12

    # Ahora cambiar únicamente el precio.
    respuesta = client.post(
        f"/presentaciones/{id_presentacion}/editar",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "12",
            "precio_venta": "11000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    presentaciones = consultar_presentaciones(app)

    assert presentaciones[0]["precio_venta"] == Decimal("11000")
    assert presentaciones[0]["unidades_por_presentacion"] == 12

    # El inventario debe seguir teniendo las 24 unidades recibidas.
    with app.app_context():
        inventario = query(
            """
            SELECT cantidad_disponible
            FROM inventario
            WHERE id_producto = %s
            """,
            (id_producto,),
            one=True
        )

    assert inventario is not None
    assert inventario["cantidad_disponible"] == 24