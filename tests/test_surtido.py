from db import query


def preparar_presentacion(client, app):
    # Crear una marca.
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

    # Crear un producto.
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

    # Crear una caja de 12 unidades.
    client.post(
        "/presentaciones/nuevo",
        data={
            "id_producto": str(producto["id_producto"]),
            "tipo_presentacion": "caja",
            "unidades_por_presentacion": "12",
            "precio_venta": "10000"
        }
    )

    with app.app_context():
        presentacion = query(
            """
            SELECT id_presentacion
            FROM presentacion
            WHERE id_producto = %s
            """,
            (producto["id_producto"],),
            one=True
        )

    assert presentacion is not None

    return producto["id_producto"], presentacion["id_presentacion"]


def test_entrada_aumenta_inventario(client, app):
    id_producto, id_presentacion = preparar_presentacion(client, app)

    # Recibir 2 cajas de 12 unidades.
    respuesta = client.post(
        "/surtido/nuevo",
        data={
            "fecha_surtido": "2026-11-18T10:00:00",
            "id_presentacion": str(id_presentacion),
            "cantidad": "2",
            "precio_compra": "7000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    with app.app_context():
        entradas = query("SELECT * FROM surtido")
        detalles = query("SELECT * FROM detalle_surtido")
        inventario = query(
            """
            SELECT cantidad_disponible
            FROM inventario
            WHERE id_producto = %s
            """,
            (id_producto,),
            one=True
        )

    # Debe guardar la entrada y su artículo.
    assert len(entradas) == 1
    assert len(detalles) == 1
    assert detalles[0]["id_surtido"] == entradas[0]["id_surtido"]
    assert detalles[0]["id_presentacion"] == id_presentacion
    assert detalles[0]["cantidad"] == 2
    assert detalles[0]["precio_compra"] == 7000
    assert detalles[0]["subtotal"] == 14000

    # 2 cajas × 12 unidades = 24 unidades.
    assert inventario is not None
    assert inventario["cantidad_disponible"] == 24

    # Comprobar que el artículo aparezca en el detalle.
    id_surtido = entradas[0]["id_surtido"]
    respuesta = client.get(f"/detalle_surtido/{id_surtido}")

    assert respuesta.status_code == 200
    assert "LAPIZ PRUEBA" in respuesta.get_data(as_text=True)


def test_entrada_con_cantidad_cero_no_se_guarda(client, app):
    id_producto, id_presentacion = preparar_presentacion(client, app)

    respuesta = client.post(
        "/surtido/nuevo",
        data={
            "fecha_surtido": "2026-11-18T10:00:00",
            "id_presentacion": str(id_presentacion),
            "cantidad": "0",
            "precio_compra": "7000"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert "cantidad" in respuesta.get_data(as_text=True).lower()

    with app.app_context():
        entradas = query("SELECT * FROM surtido")
        detalles = query("SELECT * FROM detalle_surtido")
        inventario = query(
            "SELECT * FROM inventario WHERE id_producto = %s",
            (id_producto,)
        )

    # No debe guardar una entrada incompleta ni agregar existencias.
    assert entradas == []
    assert detalles == []
    assert inventario == []


def test_eliminar_entrada_descuenta_inventario(client, app):
    id_producto, id_presentacion = preparar_presentacion(client, app)

    # Registrar primero una entrada.
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
        entradas = query("SELECT * FROM surtido")
        inventario = query(
            """
            SELECT cantidad_disponible
            FROM inventario
            WHERE id_producto = %s
            """,
            (id_producto,),
            one=True
        )

    assert len(entradas) == 1
    assert inventario is not None
    assert inventario["cantidad_disponible"] == 24

    id_surtido = entradas[0]["id_surtido"]

    # Eliminar la entrada completa.
    respuesta = client.post(
        f"/surtido/{id_surtido}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    with app.app_context():
        entradas = query("SELECT * FROM surtido")
        detalles = query("SELECT * FROM detalle_surtido")
        inventario = query(
            """
            SELECT cantidad_disponible
            FROM inventario
            WHERE id_producto = %s
            """,
            (id_producto,),
            one=True
        )

    assert entradas == []
    assert detalles == []
    assert inventario is not None
    assert inventario["cantidad_disponible"] == 0