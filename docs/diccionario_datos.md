# Diccionario de datos — Tienda Papelería

**Asignatura:** Programación Web  
**Integrantes:** Manuel Alejandro Cardona, Sergio Alejandro Osso y Martin Murcia  
**Base de datos:** `tienda`  
**Motor:** PostgreSQL  

En este diccionario explicamos qué guarda cada tabla de la papelería, para qué sirve cada campo y qué reglas debe cumplir.

## Significado de las restricciones

| Restricción | Significado |
|---|---|
| PK | Identifica cada registro. No se repite ni puede quedar nula. |
| FK | Relaciona un registro con otra tabla. |
| NOT NULL | El campo es obligatorio. |
| UNIQUE | El valor o la combinación de campos no se puede repetir. |
| CHECK | El dato debe cumplir una condición. |
| DEFAULT | Valor que se usa si no se indica otro. |
| GENERATED | PostgreSQL calcula el campo automáticamente. |

La columna «Tipo declarado» muestra cómo definimos los campos en `Tienda.sql`. Usamos `SERIAL` para el ID propio de cada tabla, que se genera automáticamente. Las llaves foráneas son `INTEGER` porque guardan el ID de un registro que ya existe en otra tabla.

En PostgreSQL, `SERIAL` crea un campo entero con una secuencia. Por eso en `backup.sql` puede aparecer como `INTEGER` junto con su secuencia; corresponde al mismo campo.

Los precios están en pesos colombianos. Los campos `NUMERIC(12,2)` y `NUMERIC(14,2)` permiten guardar valores con dos decimales.

## 1. Tabla `marca`

Guarda las marcas de los productos.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_marca` | SERIAL | PK, NOT NULL | Identificador de la marca. Se genera automáticamente. |
| `nombre_marca` | VARCHAR(80) | NOT NULL, UNIQUE | Nombre de la marca, por ejemplo NORMA o PELIKAN. |

## 2. Tabla `producto`

Guarda el nombre de cada producto y su marca. Las presentaciones y sus precios se registran en otra tabla.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_producto` | SERIAL | PK, NOT NULL | Identificador del producto. Se genera automáticamente. |
| `nombre_producto` | VARCHAR(100) | NOT NULL; índice UNIQUE con la marca | Nombre del producto. |
| `id_marca` | INTEGER | NOT NULL, FK a `marca.id_marca` | Marca del producto. |

No se puede repetir un producto con el mismo nombre y marca. Para comprobarlo, el índice `uq_producto_nombre_marca` usa `UPPER(TRIM(nombre_producto))`, que convierte el nombre a mayúsculas y quita los espacios de los extremos. Un producto con ese nombre sí puede tener otra marca.

## 3. Tabla `presentacion`

Define cómo se vende o recibe un producto: por unidad o por caja.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_presentacion` | SERIAL | PK, NOT NULL | Identificador de la presentación. Se genera automáticamente. |
| `id_producto` | INTEGER | NOT NULL, FK a `producto.id_producto` | Producto al que pertenece. |
| `tipo_presentacion` | VARCHAR(20) | NOT NULL, CHECK: `unidad` o `caja` | Tipo de presentación. |
| `unidades_por_presentacion` | INTEGER | NOT NULL, CHECK: mayor que 0 | Unidades individuales que contiene una presentación. |
| `precio_venta` | NUMERIC(12,2) | NOT NULL, CHECK: mayor o igual a 0 | Precio de venta por unidad o por caja, según la presentación. |

Otras reglas de esta tabla:

- Si el tipo es `unidad`, `unidades_por_presentacion` debe ser 1.
- La combinación de producto, tipo y unidades es UNIQUE. Por ejemplo, no se pueden registrar dos veces cajas de 12 para el mismo producto.

## 4. Tabla `cliente`

Guarda la identificación y los datos de contacto de los clientes.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_cliente` | SERIAL | PK, NOT NULL | Identificador interno del cliente. Se genera automáticamente. |
| `nombre_cliente` | VARCHAR(100) | NOT NULL | Nombre del cliente. |
| `telefono` | BIGINT | Permite NULL; no es UNIQUE; CHECK: mayor que 0 | Teléfono de contacto. Puede compartirse entre clientes. |
| `correo_electronico` | VARCHAR(100) | UNIQUE, permite NULL | Correo opcional. Los valores registrados no pueden repetirse. |
| `identificacion` | BIGINT | NOT NULL, UNIQUE, CHECK: mayor que 0 | Documento numérico del cliente. Es obligatorio, debe ser positivo y no puede repetirse. |

El teléfono y la identificación se guardan como valores numéricos de tipo `BIGINT`. `id_cliente` es el número interno del registro; `identificacion` corresponde al documento del cliente.

## 5. Tabla `inventario`

Guarda las existencias actuales por producto en unidades individuales.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_inventario` | SERIAL | PK, NOT NULL | Identificador del registro de inventario. Se genera automáticamente. |
| `id_producto` | INTEGER | NOT NULL, UNIQUE, FK a `producto.id_producto` | Producto al que corresponden las existencias. Solo puede tener un registro de inventario. |
| `cantidad_disponible` | INTEGER | NOT NULL, DEFAULT 0, CHECK: mayor o igual a 0 | Unidades individuales disponibles para vender. |

Las cajas y las unidades de un producto usan el mismo inventario. Por ejemplo, al recibir dos cajas de 12 se suman 24 unidades. Las entradas aumentan las existencias y las ventas las descuentan.

## 6. Tabla `surtido`

Guarda el número y la fecha de cada entrada de mercancía. Los artículos de esa entrada se guardan en `detalle_surtido`.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_surtido` | SERIAL | PK, NOT NULL | Identificador de la entrada de mercancía. Se genera automáticamente. |
| `fecha_surtido` | TIMESTAMP WITHOUT TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Fecha y hora en que se registra la entrada. |

## 7. Tabla `detalle_surtido`

Guarda cada artículo recibido dentro de una entrada de mercancía.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_detalle_surtido` | SERIAL | PK, NOT NULL | Identificador del artículo registrado en la entrada. Se genera automáticamente. |
| `id_surtido` | INTEGER | NOT NULL, FK a `surtido.id_surtido` | Entrada a la que pertenece el artículo. |
| `id_presentacion` | INTEGER | NOT NULL, FK a `presentacion.id_presentacion` | Presentación recibida. |
| `cantidad` | INTEGER | NOT NULL, CHECK: mayor que 0 | Cantidad de unidades o cajas recibidas, según la presentación seleccionada. |
| `precio_compra` | NUMERIC(12,2) | NOT NULL, CHECK: mayor o igual a 0 | Cuánto costó cada unidad o caja recibida. |
| `subtotal` | NUMERIC(14,2) | GENERATED ALWAYS AS (`cantidad * precio_compra`) STORED | Cantidad recibida multiplicada por el precio de compra. Se calcula automáticamente. |

Ejemplo: si se reciben 2 cajas de 12 unidades a $7.000 por caja, `cantidad` es 2, `precio_compra` es 7000 y `subtotal` es 14000. Al inventario se agregan 24 unidades.

## 8. Tabla `venta`

Guarda el número, la fecha y el cliente de cada venta. Sus artículos se guardan en `detalle_venta`.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_venta` | SERIAL | PK, NOT NULL | Identificador de la venta. Se genera automáticamente. |
| `id_cliente` | INTEGER | FK a `cliente.id_cliente`, permite NULL | Cliente de la venta. Se puede dejar sin cliente registrado para una venta de mostrador. |
| `fecha_venta` | TIMESTAMP WITHOUT TIME ZONE | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Fecha y hora en que se registra la venta. |

El total se calcula sumando los subtotales de los artículos de la venta.

## 9. Tabla `detalle_venta`

Guarda cada artículo vendido y el precio con el que se realizó la venta.

| Campo | Tipo declarado | Restricciones | Descripción |
|---|---|---|---|
| `id_detalle_venta` | SERIAL | PK, NOT NULL | Identificador del artículo dentro de la venta. Se genera automáticamente. |
| `id_venta` | INTEGER | NOT NULL, FK a `venta.id_venta` | Venta a la que pertenece el artículo. |
| `id_presentacion` | INTEGER | NOT NULL, FK a `presentacion.id_presentacion` | Presentación vendida. |
| `cantidad` | INTEGER | NOT NULL, CHECK: mayor que 0 | Cantidad de unidades o cajas vendidas, según la presentación. |
| `precio_unitario` | NUMERIC(12,2) | NOT NULL, CHECK: mayor o igual a 0 | Precio de cada unidad o caja al momento de venderla. |
| `subtotal` | NUMERIC(14,2) | GENERATED ALWAYS AS (`cantidad * precio_unitario`) STORED | Cantidad vendida multiplicada por el precio registrado. Se calcula automáticamente. |

El precio se guarda en el detalle para que el recibo conserve su valor, aunque después cambie el precio de la presentación.

## Relaciones

| Tabla principal | Tabla relacionada | Relación |
|---|---|---|
| `marca` | `producto` | Una marca puede tener varios productos; cada producto pertenece a una marca. |
| `producto` | `presentacion` | Un producto puede tener varias presentaciones; cada presentación pertenece a un producto. |
| `producto` | `inventario` | Un producto puede tener cero o un registro de inventario; cada inventario corresponde a un producto. |
| `cliente` | `venta` | Un cliente puede tener varias ventas; una venta puede tener un cliente o ninguno. |
| `surtido` | `detalle_surtido` | Una entrada puede tener varios artículos; cada detalle pertenece a una entrada. |
| `presentacion` | `detalle_surtido` | Una presentación puede aparecer en varios artículos de entradas. |
| `venta` | `detalle_venta` | Una venta puede tener varios artículos; cada detalle pertenece a una venta. |
| `presentacion` | `detalle_venta` | Una presentación puede aparecer en varios artículos de ventas. |

No se puede borrar un registro si quedan otros que lo necesitan. Por ejemplo, una marca con productos asociados no se puede eliminar.

## Reglas que comprobamos desde la aplicación

Además de las restricciones de PostgreSQL, en los archivos de `routes/` comprobamos que los datos del formulario sean válidos: campos vacíos, longitud del texto, formato de correo y teléfono, cantidades y precios.

Una presentación que ya tenga entradas o ventas solo permite cambiar su precio. No permite modificar el producto, el tipo ni las unidades que contiene.

El inventario se actualiza desde Python. No usamos triggers. Las entradas, las ventas y sus cambios de existencias se guardan en una transacción para evitar que quede una operación a medias.
