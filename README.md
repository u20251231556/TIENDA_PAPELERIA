# Tienda Papelería

Este es nuestro proyecto final de Programación Web. Escogimos una papelería para trabajar el registro de productos, clientes, entradas de mercancía y ventas. Desde la aplicación se pueden consultar las existencias y registrar los movimientos que las aumentan o disminuyen.

Está pensada para la persona encargada de la papelería y funciona de manera local. En esta versión no incluimos inicio de sesión.

## Integrantes

- Manuel Alejandro Cardona.
- Sergio Alejandro Osso.
- Martin Murcia.

**Repositorio:** [TIENDA_PAPELERIA](https://github.com/u20251231556/TIENDA_PAPELERIA)

## Tecnologías

Usamos Python, Flask, PostgreSQL, psycopg2, HTML, Jinja2, Bootstrap 5.3.3 y JavaScript. Para la configuración usamos python-dotenv y para las pruebas automatizadas usamos pytest.

Las pruebas documentadas se ejecutaron con Python 3.14.7 y pytest 8.4.2. El respaldo se generó con PostgreSQL 17.11.

## Qué permite hacer

| Módulo | Funciones |
|---|---|
| Marcas | Crear, listar, editar y eliminar marcas. |
| Productos | Administrar productos y relacionarlos con su marca. |
| Presentaciones | Registrar unidades o cajas, las unidades que contienen y su precio de venta. |
| Clientes | Crear, listar, editar y eliminar clientes. |
| Entradas de mercancía | Registrar varios artículos en una entrada, consultar su detalle o eliminarla cuando el inventario lo permita. |
| Detalle de surtido | Editar o eliminar artículos de una entrada, ajustando las existencias. |
| Inventario | Consultar las unidades disponibles por producto. |
| Ventas | Registrar una venta con varios artículos y comprobar las existencias. |
| Detalle de venta | Consultar e imprimir el recibo. |

El CRUD completo se trabaja en marcas, productos, presentaciones, clientes y detalle de surtido. Los artículos de una entrada se crean desde Nueva entrada y después se administran desde Ver detalle.

El inventario cambia con los movimientos, por eso su pantalla es de consulta. Las ventas confirmadas quedan como recibos y no tienen botones para editarlas o eliminarlas.

## Estructura del proyecto

```text
TIENDA_PAPELERIA/
├── app.py                       # Inicio de Flask y registro de los Blueprints
├── config.py                    # Configuración desde .env
├── db.py                        # Conexión, consultas y transacciones
├── README.md
├── requirements.txt             # Librerías de la aplicación
├── requirements-dev.txt         # Incluye pytest
├── pytest.ini                   # Configuración de las pruebas
├── .env.example                 # Ejemplo de configuración
├── .gitignore
├── routes/
│   ├── __init__.py
│   ├── marcas.py
│   ├── productos.py
│   ├── presentaciones.py
│   ├── clientes.py
│   ├── surtido.py
│   ├── detalle_surtido.py
│   ├── inventario.py
│   ├── venta.py
│   └── detalle_venta.py
├── templates/
│   ├── base.html                # Menú, mensajes y contenido común
│   ├── index.html               # Página principal
│   ├── 404.html                 # Página no encontrada
│   ├── error_db.html            # Error de conexión
│   ├── marcas/                  # list.html y form.html
│   ├── productos/               # list.html y form.html
│   ├── presentaciones/          # list.html y form.html
│   ├── clientes/                # list.html y form.html
│   ├── surtido/                 # list.html y form.html
│   ├── detalle_surtido/         # list.html y form.html
│   ├── inventario/              # list.html
│   ├── venta/                   # list.html y form.html
│   └── detalle_venta/           # list.html
├── static/
│   └── css/
│       └── styles.css
├── database/
│   ├── Tienda.sql               # Creación de las tablas
│   ├── datos_ejemplo.sql        # Datos de demostración
│   └── backup.sql               # Respaldo con estructura y datos
├── images/
│   ├── database MER.png
│   └── arquitectura.png
├── docs/
│   ├── diccionario_datos.md
│   ├── conteo_registros/        # Captura del conteo por tabla
│   ├── evidencias/              # Capturas y PDF de pruebas manuales
│   └── pytest_pruebas/          # Capturas y PDF de pytest
└── tests/
    ├── conftest.py              # Preparación de tienda_test
    ├── test_paginas.py
    ├── test_marca.py
    ├── test_producto.py
    ├── test_clientes.py
    ├── test_presentaciones.py
    ├── test_surtido.py
    └── test_venta.py
```

Las validaciones están en los archivos de `routes/`. Cada módulo tiene su Blueprint y sus plantillas. `.env` y `.venv` se crean en cada computador y no se suben al repositorio.

## Instalación en Windows

Necesitamos Python, PostgreSQL, pgAdmin y Git instalados. Los siguientes comandos se ejecutan desde PowerShell, dentro de la carpeta del proyecto.

### Descargar el proyecto

```powershell
git clone https://github.com/u20251231556/TIENDA_PAPELERIA.git
cd TIENDA_PAPELERIA
git switch main
```

### Preparar el entorno

Primero permitimos la ejecución de scripts en la terminal actual y luego creamos y activamos el entorno:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Cuando esté activo aparecerá `(.venv)` en la terminal.

### Configurar la conexión

Copiamos el archivo de ejemplo si todavía no existe `.env`:

```powershell
Copy-Item .env.example .env
```

En `.env` colocamos los datos de nuestro PostgreSQL:

```dotenv
SECRET_KEY=una-clave-privada-para-la-aplicacion
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tienda
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

Cada integrante configura sus propias credenciales. `.env` y `.venv` no se suben al repositorio.

### Cargar la base de datos

Creamos una base vacía llamada **`tienda`** en PostgreSQL y usamos una de estas dos alternativas:

- **Con los scripts:** ejecutamos `database/Tienda.sql` y después `database/datos_ejemplo.sql`, una sola vez y en ese orden.
- **Con el respaldo:** restauramos directamente `database/backup.sql` sobre la base vacía. Ya contiene estructura y datos, así que no ejecutamos los otros dos archivos. Este respaldo es Plain y se carga con **psql**, porque contiene instrucciones propias de ese cliente y bloques COPY.

No se deben mezclar ambas alternativas sobre la misma base ya cargada. El archivo de ejemplos se llama `datos_ejemplo.sql`, en singular.

### Abrir la aplicación

Con PostgreSQL funcionando, el entorno activo y `.env` guardado:

```powershell
python app.py
```

Abrimos [http://127.0.0.1:5000](http://127.0.0.1:5000).

Bootstrap se carga desde Internet mediante un CDN. Para detener la aplicación usamos **Ctrl + C**. Para salir del entorno virtual:

```powershell
deactivate
```

Cuando volvamos a trabajar no hace falta reinstalar todo. Desde la carpeta `TIENDA_PAPELERIA` activamos `.venv` y ejecutamos `python app.py`.

## Base de datos

El proyecto tiene nueve tablas: `marca`, `producto`, `presentacion`, `cliente`, `inventario`, `surtido`, `detalle_surtido`, `venta` y `detalle_venta`.

![Modelo de la base de datos](<images/database MER.png>)

Separamos las marcas, productos, presentaciones y clientes para no repetir sus datos en cada movimiento. Las entradas y ventas guardan sus artículos en las tablas de detalle.

- **1FN:** cada campo guarda un valor y cada artículo se registra en una fila del detalle.
- **2FN:** los datos de cada registro corresponden a la entidad o movimiento que identifica su clave.
- **3FN:** los datos de las entidades relacionadas se consultan mediante sus llaves foráneas. Por ejemplo, el nombre de la marca está en `marca`, no se copia en cada producto.

Los campos y sus restricciones se explican en el [diccionario de datos](docs/diccionario_datos.md). La identificación del cliente es obligatoria y no se puede repetir; el teléfono es opcional.

## Inventario y validaciones

Las existencias se manejan en unidades individuales. Si recibimos dos cajas de doce, se agregan 24 unidades. Si después vendemos una caja y tres unidades, quedan nueve.

Las entradas, ventas y ajustes de inventario se guardan con transacciones desde Python. Si una operación falla, sus cambios se revierten. No usamos triggers para actualizar las existencias.

También comprobamos campos obligatorios, duplicados, formatos de correo y teléfono, cantidades positivas y precios válidos. Las consultas SQL usan parámetros `%s` y los errores de la base se muestran con mensajes en español.

Una presentación que ya tenga entradas o ventas solo permite cambiar su precio. Los recibos conservan el precio registrado al vender, aunque después cambie el precio del catálogo. Sus subtotales son calculados por PostgreSQL.

## Pruebas con pytest

Para ejecutar las pruebas necesitamos instalar las dependencias de desarrollo, con el entorno virtual activo:

```powershell
python -m pip install -r requirements-dev.txt
```

Además, creamos una base independiente llamada **`tienda_test`** y ejecutamos sobre ella **`database/Tienda.sql`**. No cargamos datos de ejemplo: las pruebas crean sus propios registros.

`conftest.py` selecciona `tienda_test` y usa el mismo servidor, usuario y contraseña del `.env`. No hay que cambiar `DB_NAME=tienda` en ese archivo. La base de pruebas se limpia antes y después de cada caso, así que no debe contener información que queramos conservar.

Desde la carpeta que contiene `app.py`, ejecutamos:

```powershell
python -m pytest -v
```

No hace falta tener `python app.py` corriendo. Para ejecutar un archivo por separado, por ejemplo clientes:

```powershell
python -m pytest tests/test_clientes.py -v
```

| Archivo | Casos | Qué comprueba |
|---|---:|---|
| `test_paginas.py` | 9 | Inicio, página 404 y listados vacíos. |
| `test_marca.py` | 4 | CRUD, nombre vacío, duplicado y marca relacionada. |
| `test_producto.py` | 3 | CRUD, duplicado y marca inexistente. |
| `test_clientes.py` | 6 | CRUD, identificación obligatoria o repetida, correo repetido o inválido y teléfono inválido. |
| `test_presentaciones.py` | 4 | CRUD, cantidades incompatibles, duplicados y protección de presentaciones utilizadas. |
| `test_surtido.py` | 3 | Entrada, cantidad cero y eliminación con ajuste de inventario. |
| `test_venta.py` | 3 | Venta de caja y unidades, existencias insuficientes y cantidad cero. |
| **Total** | **32** | |

Las capturas incluidas muestran **32 pruebas aprobadas**. Si modificamos el proyecto, volvemos a ejecutarlas sobre la versión actualizada. `tienda_test` debe conservar la misma estructura de tablas que `tienda`.


## Documentación y evidencias

- [Diccionario de datos](docs/diccionario_datos.md).
- [Plan de 15 pruebas manuales con capturas](docs/evidencias/Plan_pruebas_Tienda_Papeleria.pdf).
- [Explicación y resultados de pytest](docs/pytest_pruebas/Pruebas_pytest_Tienda_Papeleria.pdf).
- [Conteo de registros por tabla](docs/conteo_registros/conteo_registros.png).

Las pruebas manuales incluyen tres casos por cada una de las cinco tablas seleccionadas. Las capturas originales están en `docs/evidencias/` y las de pytest en `docs/pytest_pruebas/`.
