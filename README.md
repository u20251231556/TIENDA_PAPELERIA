# CRUD ventas_db · Flask + PostgreSQL

Aplicación web para consultar, crear, editar y eliminar registros de las cinco tablas
de la base `ventas_db`: categorias, productos, clientes, vendedores y ventas.

Tecnologías: Python 3.10+, Flask 3, psycopg2, Bootstrap 5 (desde CDN).

## Estructura

```
crud_ventas/
├── app.py               # Punto de entrada: crea la app y registra los blueprints
├── config.py            # Lee la configuración del archivo .env
├── db.py                # Conexión a PostgreSQL y funciones query / execute
├── validators.py        # Validaciones de los formularios
├── routes/              # Un blueprint (CRUD) por tabla
│   ├── categorias.py
│   ├── productos.py
│   ├── clientes.py
│   ├── vendedores.py
│   └── ventas.py
├── templates/
│   ├── base.html        # Plantilla común: menú, mensajes, Bootstrap
│   ├── _macros.html     # Botones y encabezados reutilizables
│   ├── index.html       # Panel de inicio
│   └── <tabla>/list.html, <tabla>/form.html
├── static/css/styles.css
├── tests/test_crud.py   # 32 pruebas automáticas
├── requirements.txt     # Librerías de la aplicación
├── requirements-dev.txt # + pytest
├── .env.example         # Plantilla de configuración
└── setup.sh             # Instalación rápida en macOS / Linux
```

## Instalación en macOS

1. Descomprime el proyecto y abre la Terminal en esa carpeta:
   ```bash
   cd ~/Downloads/crud_ventas
   ```
2. Ejecuta el instalador (crea `.venv`, instala las librerías y crea `.env`):
   ```bash
   bash setup.sh
   ```
   O manualmente:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
3. Edita `.env` con tus datos de PostgreSQL (los mismos que usas en pgAdmin):
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ventas_db
   DB_USER=postgres
   DB_PASSWORD=tu_contraseña
   ```
   Si instalaste PostgreSQL con **Postgres.app**, el usuario suele ser tu usuario de Mac y la
   contraseña va vacía.

## Ejecutar

```bash
source .venv/bin/activate
python app.py
```

Abre **http://127.0.0.1:5001**

> Se usa el puerto **5001** porque en macOS el 5000 lo ocupa el *Receptor AirPlay*.

## Pruebas

```bash
python -m pytest -v
```

Las pruebas trabajan sobre la base real: cada una crea sus propios registros
(con prefijo `ZZ_TEST_`) y los elimina al terminar, así que los datos originales no cambian.

## Qué hace cada pantalla

| Tabla      | Listado muestra                                     | Formulario                         |
|------------|-----------------------------------------------------|------------------------------------|
| categorias | nº de productos por categoría                       | nombre (único), descripción        |
| productos  | categoría, precio en pesos, aviso de agotado        | lista desplegable de categorías    |
| clientes   | segmento con color, nº de compras                   | segmento (lista), email (único)    |
| vendedores | total vendido y % de cumplimiento de la meta        | zona (lista), meta mensual         |
| ventas     | joins con cliente/producto/vendedor y total general | autocompleta precio y calcula total|

Detalles de diseño:

- **Descuento**: en la base se guarda como fracción (`0.10`) y en el formulario se escribe
  como porcentaje entero (`10`). Solo se aceptan enteros porque la columna es `NUMERIC(4,2)`.
- **Integridad referencial**: las llaves foráneas son `ON DELETE RESTRICT`. Si intentas
  eliminar, por ejemplo, un cliente con ventas, la app muestra un mensaje en lugar de fallar.
- **Errores de la base** (duplicados, CHECK, FK) se traducen a mensajes en español en `db.py`.
- **Consultas parametrizadas** (`%s`) en todas las sentencias, para evitar inyección SQL.
- Eliminar siempre usa **POST** y pide confirmación.
