from db import query


def crear_marca(client, app):
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
    return marca["id_marca"]


def buscar_producto(app, nombre):
    with app.app_context():
        return query(
            """
            SELECT id_producto, nombre_producto, id_marca
            FROM producto
            WHERE nombre_producto = %s
            """,
            (nombre,),
            one=True
        )


def test_crear_editar_eliminar_producto(client, app):
    id_marca = crear_marca(client, app)

    # Crear un producto.
    respuesta = client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "  lapiz prueba  ",
            "id_marca": str(id_marca)
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    producto = buscar_producto(app, "LAPIZ PRUEBA")

    assert producto is not None
    assert producto["id_marca"] == id_marca

    id_producto = producto["id_producto"]

    # Revisar que aparezca con su marca en el listado.
    respuesta = client.get("/productos/")
    html = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200
    assert "LAPIZ PRUEBA" in html
    assert "PELIKAN" in html

    # Editar el nombre.
    respuesta = client.post(
        f"/productos/{id_producto}/editar",
        data={
            "nombre_producto": "borrador prueba",
            "id_marca": str(id_marca)
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_producto(app, "LAPIZ PRUEBA") is None

    actualizado = buscar_producto(app, "BORRADOR PRUEBA")

    assert actualizado is not None
    assert actualizado["id_producto"] == id_producto
    assert actualizado["id_marca"] == id_marca

    # Eliminar el producto.
    respuesta = client.post(
        f"/productos/{id_producto}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_producto(app, "BORRADOR PRUEBA") is None


def test_producto_duplicado_no_se_guarda(client, app):
    id_marca = crear_marca(client, app)

    # Registrar el primer producto.
    client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "LAPIZ",
            "id_marca": str(id_marca)
        }
    )

    assert buscar_producto(app, "LAPIZ") is not None

    # Intentar repetirlo con la misma marca.
    respuesta = client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "  lapiz  ",
            "id_marca": str(id_marca)
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert "existe" in respuesta.get_data(as_text=True).lower()

    with app.app_context():
        resultado = query(
            "SELECT COUNT(*) AS cantidad FROM producto",
            one=True
        )

    # Debe conservar únicamente el primer producto.
    assert resultado["cantidad"] == 1


def test_producto_con_marca_inexistente(client, app):
    # La base de prueba comienza vacía.
    respuesta = client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "LAPIZ",
            "id_marca": "999999"
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_producto(app, "LAPIZ") is None
    assert "relacionado" in respuesta.get_data(as_text=True).lower()