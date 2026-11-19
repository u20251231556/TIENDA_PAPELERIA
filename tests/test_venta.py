from db import query


def preparar_mercancia(client, app):
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
    id_producto = producto["id_producto"]

    # Crear la presentación por unidad.
    client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "unidad",
            "unidades_por_presentacion": "1",
            "precio_venta": "1000"
        }
    )

    # Crear la presentación por caja.
    client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(id_producto),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "12",
            "precio_venta": "10000"
        }
    )

    with app.app_context():
        unidad = query(
            """
            SELECT id_presentacion
            FROM presentacion
            WHERE id_producto = %s
              AND tipo_presentacion = %s
            """,
            (id_producto, "unidad"),
            one=True
        )

        caja = query(
            """
            SELECT id_presentacion
            FROM presentacion
            WHERE id_producto = %s
              AND tipo_presentacion = %s
            """,
            (id_producto, "caja"),
            one=True
        )

    assert unidad is not None
    assert caja is not None

    # Recibir 2 cajas: quedan 24 unidades.
    respuesta = client.post(
        "/surtido/nuevo",
        data={
            "fecha_surtido": "2026-11-18T10:00:00",
            "id_presentacion": str(caja["id_presentacion"]),
            "cantidad": "2",
            "precio_compra": "7000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert consultar_stock(app, id_producto) == 24

    return (
        id_producto,
        unidad["id_presentacion"],
        caja["id_presentacion"]
    )


def consultar_stock(app, id_producto):
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
    return inventario["cantidad_disponible"]


def test_venta_de_caja_y_unidades(client, app):
    id_producto, id_unidad, id_caja = preparar_mercancia(client, app)

    # Vender 1 caja y 3 unidades del mismo producto.
    respuesta = client.post(
        "/venta/nuevo",
        data={
            "fecha_venta": "2026-11-18T11:00:00",
            "id_cliente": "",
            "id_presentacion": [str(id_caja), str(id_unidad)],
            "cantidad": ["1", "3"]
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    # Teníamos 24 y vendimos 15: deben quedar 9.
    assert consultar_stock(app, id_producto) == 9

    with app.app_context():
        ventas = query("SELECT * FROM venta")
        detalles = query("SELECT * FROM detalle_venta")

    assert len(ventas) == 1
    assert ventas[0]["id_cliente"] is None
    assert len(detalles) == 2

    # Los artículos deben pertenecer a esa venta.
    assert detalles[0]["id_venta"] == ventas[0]["id_venta"]
    assert detalles[1]["id_venta"] == ventas[0]["id_venta"]

    # Una caja cuesta 10.000 y tres unidades cuestan 3.000.
    total = sum(detalle["subtotal"] for detalle in detalles)
    assert total == 13000

    # Comprobar que se muestra el recibo.
    html = respuesta.get_data(as_text=True)
    assert "LAPIZ PRUEBA" in html
    assert "Venta de mostrador" in html


def test_venta_sin_existencias_suficientes(client, app):
    id_producto, id_unidad, id_caja = preparar_mercancia(client, app)

    # Intentar vender 3 cajas cuando solo hay 2.
    respuesta = client.post(
        "/venta/nuevo",
        data={
            "fecha_venta": "2026-11-18T11:00:00",
            "id_cliente": "",
            "id_presentacion": str(id_caja),
            "cantidad": "3"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert "insuficientes" in respuesta.get_data(as_text=True).lower()

    # No debe descontar ni guardar una venta incompleta.
    assert consultar_stock(app, id_producto) == 24

    with app.app_context():
        ventas = query("SELECT * FROM venta")
        detalles = query("SELECT * FROM detalle_venta")

    assert ventas == []
    assert detalles == []


def test_venta_con_cantidad_cero(client, app):
    id_producto, id_unidad, id_caja = preparar_mercancia(client, app)

    respuesta = client.post(
        "/venta/nuevo",
        data={
            "fecha_venta": "2026-11-18T11:00:00",
            "id_cliente": "",
            "id_presentacion": str(id_unidad),
            "cantidad": "0"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert "cantidad" in respuesta.get_data(as_text=True).lower()
    assert consultar_stock(app, id_producto) == 24

    with app.app_context():
        ventas = query("SELECT * FROM venta")
        detalles = query("SELECT * FROM detalle_venta")

    assert ventas == []
    assert detalles == []