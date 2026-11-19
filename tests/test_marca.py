from db import query


def buscar_marca(app, nombre):
    with app.app_context():
        return query(
            """
            SELECT id_marca, nombre_marca
            FROM marca
            WHERE nombre_marca = %s
            """,
            (nombre,),
            one=True
        )


def test_crear_editar_eliminar_marca(client, app):
    # Crear.
    respuesta = client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "  pelikan  "},
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    marca = buscar_marca(app, "PELIKAN")
    assert marca is not None

    id_marca = marca["id_marca"]

    # Verificar que aparece en el listado.
    respuesta = client.get("/marcas/")

    assert "PELIKAN" in respuesta.get_data(as_text=True)

    # Editar.
    respuesta = client.post(
        f"/marcas/{id_marca}/editar",
        data={"nombre_marca": "norma"},
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_marca(app, "PELIKAN") is None

    marca_editada = buscar_marca(app, "NORMA")

    assert marca_editada is not None
    assert marca_editada["id_marca"] == id_marca

    # Eliminar.
    respuesta = client.post(
        f"/marcas/{id_marca}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_marca(app, "NORMA") is None


def test_marca_vacia_no_se_guarda(client, app):
    respuesta = client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "   "}
    )

    assert respuesta.status_code == 200

    with app.app_context():
        resultado = query(
            "SELECT COUNT(*) AS cantidad FROM marca",
            one=True
        )

    assert resultado["cantidad"] == 0
    assert "obligatorio" in respuesta.get_data(as_text=True).lower()


def test_marca_duplicada_no_se_guarda(client, app):
    client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "PELIKAN"}
    )

    respuesta = client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "  pelikan  "},
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    with app.app_context():
        resultado = query(
            "SELECT COUNT(*) AS cantidad FROM marca",
            one=True
        )

    assert resultado["cantidad"] == 1
    assert "existe" in respuesta.get_data(as_text=True).lower()


def test_no_eliminar_marca_con_producto(client, app):
    # Crear la marca.
    client.post(
        "/marcas/nuevo",
        data={"nombre_marca": "PELIKAN"}
    )

    marca = buscar_marca(app, "PELIKAN")
    assert marca is not None

    id_marca = marca["id_marca"]

    # Crear un producto asociado.
    respuesta = client.post(
        "/productos/nuevo",
        data={
            "nombre_producto": "LAPIZ PRUEBA",
            "id_marca": str(id_marca)
        },
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    with app.app_context():
        producto = query(
            """
            SELECT id_producto
            FROM producto
            WHERE id_marca = %s
            """,
            (id_marca,),
            one=True
        )

    assert producto is not None

    # Intentar eliminar la marca utilizada.
    respuesta = client.post(
        f"/marcas/{id_marca}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert buscar_marca(app, "PELIKAN") is not None
    assert "relacionado" in respuesta.get_data(as_text=True).lower()