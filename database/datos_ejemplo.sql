-- Clientes ficticios para la demostración del proyecto.

INSERT INTO cliente (
    nombre_cliente,
    identificacion,
    telefono,
    correo_electronico
)
VALUES
    ('ANA TORRES', 6279449554, 3000000001, 'ana.torres@example.com'),
    ('CARLOS RAMIREZ', 6148485616, 3000000002, 'carlos.ramirez@example.com'),
    ('LAURA GOMEZ', 2238574330, 3000000003, 'laura.gomez@example.com'),
    ('JUAN PEREZ', 5357839696, 3000000004, 'juan.perez@example.com'),
    ('DIANA LOPEZ', 7692673727, 3000000005, 'diana.lopez@example.com'),
    ('ANDRES ROJAS', 9881145774, 3000000006, 'andres.rojas@example.com'),
    ('PAULA CASTRO', 9486330676, 3000000007, 'paula.castro@example.com'),
    ('DIEGO VARGAS', 4143227142, 3000000008, 'diego.vargas@example.com'),
    ('LUISA MORENO', 4358673108, 3000000009, 'luisa.moreno@example.com'),
    ('MATEO RUIZ', 8434960195, 3000000010, 'mateo.ruiz@example.com');

-- Marcas para los productos de la papelería.

INSERT INTO marca (nombre_marca)
VALUES
    ('NORMA'),
    ('PELIKAN'),
    ('FABER-CASTELL'),
    ('STAEDTLER'),
    ('BIC'),
    ('PAPER MATE'),
    ('SHARPIE'),
    ('SCRIBE'),
    ('KORES'),
    ('PRISMACOLOR')
ON CONFLICT (nombre_marca) DO NOTHING;


-- Productos de la papelería.
-- Se busca la marca por su nombre para no depender de sus ID.

INSERT INTO producto (nombre_producto, id_marca)
VALUES
    (
        'CUADERNO CUADRICULADO 100 HOJAS',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'NORMA')
    ),
    (
        'BORRADOR DE NATA',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'PELIKAN')
    ),
    (
        'COLORES ESCOLARES',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'FABER-CASTELL')
    ),
    (
        'LAPIZ HB',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'STAEDTLER')
    ),
    (
        'BOLIGRAFO AZUL',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'BIC')
    ),
    (
        'PORTAMINAS 0.7 MM',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'PAPER MATE')
    ),
    (
        'MARCADOR PERMANENTE NEGRO',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'SHARPIE')
    ),
    (
        'CUADERNO RAYADO 100 HOJAS',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'SCRIBE')
    ),
    (
        'PEGANTE EN BARRA 20 G',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'KORES')
    ),
    (
        'LAPIZ DE COLOR ROJO',
        (SELECT id_marca FROM marca WHERE nombre_marca = 'PRISMACOLOR')
    )
ON CONFLICT DO NOTHING;

-- Presentaciones por unidad con precios de ejemplo.

INSERT INTO presentacion (
    id_producto,
    tipo_presentacion,
    unidades_por_presentacion,
    precio_venta
)
SELECT
    p.id_producto,
    'unidad',
    1,
    datos.precio
FROM (
    VALUES
        ('CUADERNO CUADRICULADO 100 HOJAS', 'NORMA', 6500),
        ('BORRADOR DE NATA', 'PELIKAN', 1500),
        ('COLORES ESCOLARES', 'FABER-CASTELL', 1200),
        ('LAPIZ HB', 'STAEDTLER', 2000),
        ('BOLIGRAFO AZUL', 'BIC', 1500),
        ('PORTAMINAS 0.7 MM', 'PAPER MATE', 5000),
        ('MARCADOR PERMANENTE NEGRO', 'SHARPIE', 5500),
        ('CUADERNO RAYADO 100 HOJAS', 'SCRIBE', 6000),
        ('PEGANTE EN BARRA 20 G', 'KORES', 3500),
        ('LAPIZ DE COLOR ROJO', 'PRISMACOLOR', 4500)
) AS datos(producto, marca, precio)
JOIN marca m
    ON m.nombre_marca = datos.marca
JOIN producto p
    ON p.nombre_producto = datos.producto
    AND p.id_marca = m.id_marca
ON CONFLICT (
    id_producto,
    tipo_presentacion,
    unidades_por_presentacion
) DO NOTHING;

-- Diez entradas de mercancía para los productos de ejemplo.
-- Ejecutar este bloque una sola vez.

WITH datos (
    nombre_producto,
    nombre_marca,
    cantidad,
    precio_compra,
    fecha
) AS (
    VALUES
        ('CUADERNO CUADRICULADO 100 HOJAS', 'NORMA',
            20, 4500, '2026-11-18 08:00:00'),

        ('BORRADOR DE NATA', 'PELIKAN',
            20, 800, '2026-11-18 08:10:00'),

        ('COLORES ESCOLARES', 'FABER-CASTELL',
            20, 700, '2026-11-18 08:20:00'),

        ('LAPIZ HB', 'STAEDTLER',
            20, 1200, '2026-11-18 08:30:00'),

        ('BOLIGRAFO AZUL', 'BIC',
            20, 800, '2026-11-18 08:40:00'),

        ('PORTAMINAS 0.7 MM', 'PAPER MATE',
            20, 3000, '2026-11-18 08:50:00'),

        ('MARCADOR PERMANENTE NEGRO', 'SHARPIE',
            20, 3500, '2026-11-18 09:00:00'),

        ('CUADERNO RAYADO 100 HOJAS', 'SCRIBE',
            20, 4000, '2026-11-18 09:10:00'),

        ('PEGANTE EN BARRA 20 G', 'KORES',
            20, 2000, '2026-11-18 09:20:00'),

        ('LAPIZ DE COLOR ROJO', 'PRISMACOLOR',
            20, 2800, '2026-11-18 09:30:00')
),

-- Buscar la presentación por unidad de cada producto.
seleccion AS (
    SELECT
        pr.id_presentacion,
        pr.id_producto,
        pr.unidades_por_presentacion,
        d.cantidad,
        d.precio_compra,
        d.fecha::timestamp AS fecha
    FROM datos d
    JOIN marca m
        ON m.nombre_marca = d.nombre_marca
    JOIN producto p
        ON p.nombre_producto = d.nombre_producto
        AND p.id_marca = m.id_marca
    JOIN presentacion pr
        ON pr.id_producto = p.id_producto
        AND pr.tipo_presentacion = 'unidad'
        AND pr.unidades_por_presentacion = 1
),

-- Crear los encabezados de las entradas.
entradas AS (
    INSERT INTO surtido (fecha_surtido)
    SELECT fecha
    FROM seleccion
    RETURNING id_surtido, fecha_surtido
),

-- Guardar el artículo de cada entrada.
detalles AS (
    INSERT INTO detalle_surtido (
        id_surtido,
        id_presentacion,
        cantidad,
        precio_compra
    )
    SELECT
        e.id_surtido,
        s.id_presentacion,
        s.cantidad,
        s.precio_compra
    FROM seleccion s
    JOIN entradas e
        ON e.fecha_surtido = s.fecha
    RETURNING id_presentacion, cantidad
)

-- Agregar las unidades recibidas al inventario.
INSERT INTO inventario (
    id_producto,
    cantidad_disponible
)
SELECT
    pr.id_producto,
    SUM(d.cantidad * pr.unidades_por_presentacion)::integer
FROM detalles d
JOIN presentacion pr
    ON pr.id_presentacion = d.id_presentacion
GROUP BY pr.id_producto
ON CONFLICT (id_producto)
DO UPDATE SET cantidad_disponible =
    inventario.cantidad_disponible
    + EXCLUDED.cantidad_disponible;

-- Diez ventas de ejemplo.
-- Ejecutar una sola vez, después de cargar las entradas.

WITH datos (
    identificacion,
    nombre_producto,
    nombre_marca,
    cantidad,
    fecha
) AS (
    VALUES
        (6279449554, 'CUADERNO CUADRICULADO 100 HOJAS',
            'NORMA', 2, '2026-11-18 10:00:00'),

        (6148485616, 'BORRADOR DE NATA',
            'PELIKAN', 3, '2026-11-18 10:10:00'),

        (2238574330, 'COLORES ESCOLARES',
            'FABER-CASTELL', 4, '2026-11-18 10:20:00'),

        (5357839696, 'LAPIZ HB',
            'STAEDTLER', 2, '2026-11-18 10:30:00'),

        (7692673727, 'BOLIGRAFO AZUL',
            'BIC', 5, '2026-11-18 10:40:00'),

        (9881145774, 'PORTAMINAS 0.7 MM',
            'PAPER MATE', 1, '2026-11-18 10:50:00'),

        (9486330676, 'MARCADOR PERMANENTE NEGRO',
            'SHARPIE', 2, '2026-11-18 11:00:00'),

        (4143227142, 'CUADERNO RAYADO 100 HOJAS',
            'SCRIBE', 3, '2026-11-18 11:10:00'),

        (4358673108, 'PEGANTE EN BARRA 20 G',
            'KORES', 2, '2026-11-18 11:20:00'),

        (8434960195, 'LAPIZ DE COLOR ROJO',
            'PRISMACOLOR', 4, '2026-11-18 11:30:00')
),

-- Buscar clientes y presentaciones, tomando el precio del catálogo.
seleccion AS (
    SELECT
        c.id_cliente,
        pr.id_presentacion,
        pr.precio_venta,
        d.cantidad,
        d.fecha::timestamp AS fecha
    FROM datos d
    JOIN cliente c
        ON c.identificacion = d.identificacion
    JOIN marca m
        ON m.nombre_marca = d.nombre_marca
    JOIN producto p
        ON p.nombre_producto = d.nombre_producto
        AND p.id_marca = m.id_marca
    JOIN presentacion pr
        ON pr.id_producto = p.id_producto
        AND pr.tipo_presentacion = 'unidad'
        AND pr.unidades_por_presentacion = 1
),

-- Crear las ventas.
ventas_nuevas AS (
    INSERT INTO venta (id_cliente, fecha_venta)
    SELECT id_cliente, fecha
    FROM seleccion
    RETURNING id_venta, id_cliente, fecha_venta
),

-- Guardar los artículos y sus precios al momento de la venta.
detalles AS (
    INSERT INTO detalle_venta (
        id_venta,
        id_presentacion,
        cantidad,
        precio_unitario
    )
    SELECT
        v.id_venta,
        s.id_presentacion,
        s.cantidad,
        s.precio_venta
    FROM seleccion s
    JOIN ventas_nuevas v
        ON v.id_cliente = s.id_cliente
        AND v.fecha_venta = s.fecha
    RETURNING id_presentacion, cantidad
),

-- Calcular las unidades vendidas por producto.
unidades_vendidas AS (
    SELECT
        pr.id_producto,
        SUM(
            d.cantidad * pr.unidades_por_presentacion
        )::integer AS unidades
    FROM detalles d
    JOIN presentacion pr
        ON pr.id_presentacion = d.id_presentacion
    GROUP BY pr.id_producto
)

-- Descontar del inventario.
UPDATE inventario i
SET cantidad_disponible =
    i.cantidad_disponible - u.unidades
FROM unidades_vendidas u
WHERE i.id_producto = u.id_producto
RETURNING i.id_producto, i.cantidad_disponible;