from db import query


def datos_cliente():
    return {
        "nombre_cliente": "CLIENTE PRUEBA",
        "identificacion": "10000001",
        "telefono": "3001234567",
        "correo_electronico": "cliente@ejemplo.com"
    }


def consultar_clientes(app):
    with app.app_context():
        return query(
            """
            SELECT *
            FROM cliente
            ORDER BY id_cliente
            """
        )


def test_crear_editar_eliminar_cliente(client, app):
    # Crear.
    respuesta = client.post(
        "/clientes/nuevo",
        data=datos_cliente(),
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    clientes = consultar_clientes(app)

    assert len(clientes) == 1
    assert clientes[0]["nombre_cliente"] == "CLIENTE PRUEBA"
    assert clientes[0]["identificacion"] == "10000001"

    id_cliente = clientes[0]["id_cliente"]

    # Comprobar el listado.
    respuesta = client.get("/clientes/")
    html = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200
    assert "CLIENTE PRUEBA" in html
    assert "10000001" in html

    # Editar.
    datos = datos_cliente()
    datos["nombre_cliente"] = "CLIENTE EDITADO"
    datos["telefono"] = "3117654321"

    respuesta = client.post(
        f"/clientes/{id_cliente}/editar",
        data=datos,
        follow_redirects=True
    )

    assert respuesta.status_code == 200

    clientes = consultar_clientes(app)

    assert len(clientes) == 1
    assert clientes[0]["id_cliente"] == id_cliente
    assert clientes[0]["nombre_cliente"] == "CLIENTE EDITADO"
    assert clientes[0]["telefono"] == "3117654321"

    # Eliminar.
    respuesta = client.post(
        f"/clientes/{id_cliente}/eliminar",
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert consultar_clientes(app) == []


def test_identificacion_obligatoria(client, app):
    datos = datos_cliente()
    datos["identificacion"] = "   "

    respuesta = client.post(
        "/clientes/nuevo",
        data=datos
    )

    assert respuesta.status_code == 200
    assert consultar_clientes(app) == []
    assert "obligatoria" in respuesta.get_data(as_text=True).lower()


def test_identificacion_repetida(client, app):
    # Guardar el primer cliente.
    client.post(
        "/clientes/nuevo",
        data=datos_cliente()
    )

    assert len(consultar_clientes(app)) == 1

    # Repetir identificación, pero usar otro correo.
    datos = datos_cliente()
    datos["nombre_cliente"] = "OTRO CLIENTE"
    datos["correo_electronico"] = "otro@ejemplo.com"

    respuesta = client.post(
        "/clientes/nuevo",
        data=datos,
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert len(consultar_clientes(app)) == 1
    assert "identificación" in respuesta.get_data(as_text=True).lower()
    assert "existe" in respuesta.get_data(as_text=True).lower()


def test_correo_repetido(client, app):
    client.post(
        "/clientes/nuevo",
        data=datos_cliente()
    )

    assert len(consultar_clientes(app)) == 1

    # Usar otra identificación, pero repetir el correo.
    datos = datos_cliente()
    datos["nombre_cliente"] = "OTRO CLIENTE"
    datos["identificacion"] = "10000002"

    respuesta = client.post(
        "/clientes/nuevo",
        data=datos,
        follow_redirects=True
    )

    assert respuesta.status_code == 200
    assert len(consultar_clientes(app)) == 1
    assert "correo" in respuesta.get_data(as_text=True).lower()
    assert "existe" in respuesta.get_data(as_text=True).lower()


def test_correo_invalido(client, app):
    datos = datos_cliente()
    datos["correo_electronico"] = "correo-sin-arroba"

    respuesta = client.post(
        "/clientes/nuevo",
        data=datos
    )

    assert respuesta.status_code == 200
    assert consultar_clientes(app) == []
    assert "correo" in respuesta.get_data(as_text=True).lower()


def test_telefono_invalido(client, app):
    datos = datos_cliente()
    datos["telefono"] = "abc123"

    respuesta = client.post(
        "/clientes/nuevo",
        data=datos
    )

    assert respuesta.status_code == 200
    assert consultar_clientes(app) == []
    assert "teléfono" in respuesta.get_data(as_text=True).lower()