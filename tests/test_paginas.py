import pytest


def test_inicio_carga(client):
    respuesta = client.get("/")

    assert respuesta.status_code == 200
    assert "Papelería" in respuesta.get_data(as_text=True)


def test_pagina_inexistente(client):
    respuesta = client.get("/pagina-que-no-existe")

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "ruta",
    [
        "/marcas/",
        "/productos/",
        "/presentaciones/",
        "/clientes/",
        "/surtido/",
        "/inventario/",
        "/venta/",
    ]
)
def test_listados_cargan_sin_registros(client, ruta):
    respuesta = client.get(ruta)

    assert respuesta.status_code == 200