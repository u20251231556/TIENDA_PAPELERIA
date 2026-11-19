import pytest

from app import create_app
from config import Config
from db import get_db


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "clave-exclusiva-para-pruebas"
    DB_NAME = "tienda_test"


def limpiar_base(app):
    with app.app_context():
        conexion = get_db()

        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                nombre_base = cursor.fetchone()[0]

                # Impide limpiar una base diferente.
                if nombre_base != "tienda_test":
                    raise RuntimeError(
                        "Las pruebas solo pueden limpiar tienda_test."
                    )

                cursor.execute("""
                    TRUNCATE TABLE
                        detalle_venta,
                        detalle_surtido,
                        venta,
                        surtido,
                        inventario,
                        presentacion,
                        producto,
                        marca,
                        cliente
                    RESTART IDENTITY
                """)


@pytest.fixture()
def app():
    aplicacion = create_app(TestConfig)

    limpiar_base(aplicacion)

    try:
        yield aplicacion
    finally:
        limpiar_base(aplicacion)


@pytest.fixture()
def client(app):
    with app.test_client() as cliente:
        yield cliente