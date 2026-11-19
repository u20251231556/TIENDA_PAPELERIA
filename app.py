"""Punto de entrada de la aplicación CRUD ventas_db."""
import psycopg2
from flask import Flask, app, redirect, render_template, url_for

import db
from config import Config
from routes.marcas import bp as marcas_bp
from routes.productos import bp as productos_bp
from routes.presentaciones import bp as presentaciones_bp
from routes.clientes import bp as clientes_bp
from routes.surtido import bp as surtido_bp
from routes.detalle_surtido import bp as detalle_surtido_bp
from routes.inventario import bp as inventario_bp
from routes.venta import bp as venta_bp
from routes.detalle_venta import bp as detalle_venta_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Habilita las rutas del módulo de marcas.
    app.register_blueprint(marcas_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(presentaciones_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(surtido_bp)
    app.register_blueprint(detalle_surtido_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(detalle_venta_bp)


    @app.route("/")
    def inicio():
        return render_template("index.html")

    @app.errorhandler(psycopg2.OperationalError)
    def error_conexion(exc):
        return render_template("error_db.html", error=str(exc)), 500

    @app.errorhandler(404)
    def no_encontrado(exc):
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)