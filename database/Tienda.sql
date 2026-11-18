--  TABLA CLIENTE
CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo_electronico VARCHAR(100) UNIQUE,
    identificacion VARCHAR(30) NOT NULL UNIQUE
    CHECK (TRIM(identificacion) <> '')
    );


--  TABLA MARCA
CREATE TABLE marca (
    id_marca SERIAL PRIMARY KEY,
    nombre_marca VARCHAR(80) NOT NULL UNIQUE
);


--  TABLA PRODUCTO
CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre_producto VARCHAR(100) NOT NULL,
    id_marca INTEGER NOT NULL,

    CONSTRAINT fk_producto_marca
        FOREIGN KEY (id_marca)
        REFERENCES marca(id_marca)
);


--  TABLA PRESENTACION
CREATE TABLE presentacion (
    id_presentacion SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL,
    tipo_presentacion VARCHAR(20) NOT NULL,
    unidades_por_presentacion INTEGER NOT NULL,
    precio_venta NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_presentacion_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto),

    CONSTRAINT chk_unidades_presentacion
        CHECK (unidades_por_presentacion > 0),

    CONSTRAINT chk_precio_presentacion
        CHECK (precio_venta >= 0),

    CONSTRAINT chk_tipo_presentacion
        CHECK (
            tipo_presentacion IN ('unidad', 'caja')
        ),

    CONSTRAINT chk_presentacion_unidad
        CHECK (
            tipo_presentacion <> 'unidad'
            OR unidades_por_presentacion = 1
        ),

    CONSTRAINT uq_presentacion
        UNIQUE (
            id_producto,
            tipo_presentacion,
            unidades_por_presentacion
        )
);


--  TABLA INVENTARIO
CREATE TABLE inventario (
    id_inventario SERIAL PRIMARY KEY,
    id_producto INTEGER NOT NULL UNIQUE,
    cantidad_disponible INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT fk_inventario_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto),

    CONSTRAINT chk_cantidad_inventario
        CHECK (cantidad_disponible >= 0)
);


--  TABLA VENTA
CREATE TABLE venta (
    id_venta SERIAL PRIMARY KEY,
    id_cliente INTEGER,
    fecha_venta TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente)
);


--  TABLA DETALLE_VENTA
CREATE TABLE detalle_venta (
    id_detalle_venta SERIAL PRIMARY KEY,
    id_venta INTEGER NOT NULL,
    id_presentacion INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario NUMERIC(12,2) NOT NULL,

    subtotal NUMERIC(14,2)
        GENERATED ALWAYS AS (
            cantidad * precio_unitario
        ) STORED,

    CONSTRAINT fk_detalle_venta
        FOREIGN KEY (id_venta)
        REFERENCES venta(id_venta),

    CONSTRAINT fk_detalle_presentacion
        FOREIGN KEY (id_presentacion)
        REFERENCES presentacion(id_presentacion),

    CONSTRAINT chk_cantidad_venta
        CHECK (cantidad > 0),

    CONSTRAINT chk_precio_venta
        CHECK (precio_unitario >= 0)
);


--  TABLA SURTIDO
CREATE TABLE surtido (
    id_surtido SERIAL PRIMARY KEY,
    fecha_surtido TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


--  TABLA DETALLE_SURTIDO
CREATE TABLE detalle_surtido (
    id_detalle_surtido SERIAL PRIMARY KEY,
    id_surtido INTEGER NOT NULL,
    id_presentacion INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_compra NUMERIC(12,2) NOT NULL,

    subtotal NUMERIC(14,2)
        GENERATED ALWAYS AS (
            cantidad * precio_compra
        ) STORED,

    CONSTRAINT fk_detalle_surtido
        FOREIGN KEY (id_surtido)
        REFERENCES surtido(id_surtido),

    CONSTRAINT fk_surtido_presentacion
        FOREIGN KEY (id_presentacion)
        REFERENCES presentacion(id_presentacion),

    CONSTRAINT chk_cantidad_surtido
        CHECK (cantidad > 0),

    CONSTRAINT chk_precio_compra
        CHECK (precio_compra >= 0)
);