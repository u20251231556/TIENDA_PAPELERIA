--
-- PostgreSQL database dump
--

\restrict ByElU3FdV9QNX07FbmmPKG6B75XZVwzVFhPvF9M2FkQ9bObOhX9THQKdcsErzjP

-- Dumped from database version 17.11
-- Dumped by pg_dump version 17.11

-- Started on 2026-11-19 15:47:22

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 16502)
-- Name: cliente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cliente (
    id_cliente integer NOT NULL,
    nombre_cliente character varying(100) NOT NULL,
    telefono bigint,
    correo_electronico character varying(100),
    identificacion bigint NOT NULL,
    CONSTRAINT chk_cliente_identificacion_positiva CHECK ((identificacion > 0)),
    CONSTRAINT chk_cliente_telefono_positivo CHECK ((telefono > 0))
);


--
-- TOC entry 217 (class 1259 OID 16501)
-- Name: cliente_id_cliente_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cliente_id_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5012 (class 0 OID 0)
-- Dependencies: 217
-- Name: cliente_id_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cliente_id_cliente_seq OWNED BY public.cliente.id_cliente;


--
-- TOC entry 234 (class 1259 OID 16608)
-- Name: detalle_surtido; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_surtido (
    id_detalle_surtido integer NOT NULL,
    id_surtido integer NOT NULL,
    id_presentacion integer NOT NULL,
    cantidad integer NOT NULL,
    precio_compra numeric(12,2) NOT NULL,
    subtotal numeric(14,2) GENERATED ALWAYS AS (((cantidad)::numeric * precio_compra)) STORED,
    CONSTRAINT chk_cantidad_surtido CHECK ((cantidad > 0)),
    CONSTRAINT chk_precio_compra CHECK ((precio_compra >= (0)::numeric))
);


--
-- TOC entry 233 (class 1259 OID 16607)
-- Name: detalle_surtido_id_detalle_surtido_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_surtido_id_detalle_surtido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5013 (class 0 OID 0)
-- Dependencies: 233
-- Name: detalle_surtido_id_detalle_surtido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_surtido_id_detalle_surtido_seq OWNED BY public.detalle_surtido.id_detalle_surtido;


--
-- TOC entry 230 (class 1259 OID 16580)
-- Name: detalle_venta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_venta (
    id_detalle_venta integer NOT NULL,
    id_venta integer NOT NULL,
    id_presentacion integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(12,2) NOT NULL,
    subtotal numeric(14,2) GENERATED ALWAYS AS (((cantidad)::numeric * precio_unitario)) STORED,
    CONSTRAINT chk_cantidad_venta CHECK ((cantidad > 0)),
    CONSTRAINT chk_precio_venta CHECK ((precio_unitario >= (0)::numeric))
);


--
-- TOC entry 229 (class 1259 OID 16579)
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_venta_id_detalle_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5014 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_venta_id_detalle_venta_seq OWNED BY public.detalle_venta.id_detalle_venta;


--
-- TOC entry 226 (class 1259 OID 16551)
-- Name: inventario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventario (
    id_inventario integer NOT NULL,
    id_producto integer NOT NULL,
    cantidad_disponible integer DEFAULT 0 NOT NULL,
    CONSTRAINT chk_cantidad_inventario CHECK ((cantidad_disponible >= 0))
);


--
-- TOC entry 225 (class 1259 OID 16550)
-- Name: inventario_id_inventario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventario_id_inventario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5015 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_inventario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventario_id_inventario_seq OWNED BY public.inventario.id_inventario;


--
-- TOC entry 220 (class 1259 OID 16511)
-- Name: marca; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.marca (
    id_marca integer NOT NULL,
    nombre_marca character varying(80) NOT NULL
);


--
-- TOC entry 219 (class 1259 OID 16510)
-- Name: marca_id_marca_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.marca_id_marca_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5016 (class 0 OID 0)
-- Dependencies: 219
-- Name: marca_id_marca_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.marca_id_marca_seq OWNED BY public.marca.id_marca;


--
-- TOC entry 224 (class 1259 OID 16533)
-- Name: presentacion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.presentacion (
    id_presentacion integer NOT NULL,
    id_producto integer NOT NULL,
    tipo_presentacion character varying(20) NOT NULL,
    unidades_por_presentacion integer NOT NULL,
    precio_venta numeric(12,2) NOT NULL,
    CONSTRAINT chk_precio_presentacion CHECK ((precio_venta >= (0)::numeric)),
    CONSTRAINT chk_presentacion_unidad CHECK ((((tipo_presentacion)::text <> 'unidad'::text) OR (unidades_por_presentacion = 1))),
    CONSTRAINT chk_tipo_presentacion CHECK (((tipo_presentacion)::text = ANY ((ARRAY['unidad'::character varying, 'caja'::character varying])::text[]))),
    CONSTRAINT chk_unidades_presentacion CHECK ((unidades_por_presentacion > 0))
);


--
-- TOC entry 223 (class 1259 OID 16532)
-- Name: presentacion_id_presentacion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.presentacion_id_presentacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5017 (class 0 OID 0)
-- Dependencies: 223
-- Name: presentacion_id_presentacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.presentacion_id_presentacion_seq OWNED BY public.presentacion.id_presentacion;


--
-- TOC entry 222 (class 1259 OID 16520)
-- Name: producto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.producto (
    id_producto integer NOT NULL,
    nombre_producto character varying(100) NOT NULL,
    id_marca integer NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 16519)
-- Name: producto_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.producto_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5018 (class 0 OID 0)
-- Dependencies: 221
-- Name: producto_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.producto_id_producto_seq OWNED BY public.producto.id_producto;


--
-- TOC entry 232 (class 1259 OID 16600)
-- Name: surtido; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.surtido (
    id_surtido integer NOT NULL,
    fecha_surtido timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- TOC entry 231 (class 1259 OID 16599)
-- Name: surtido_id_surtido_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.surtido_id_surtido_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5019 (class 0 OID 0)
-- Dependencies: 231
-- Name: surtido_id_surtido_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.surtido_id_surtido_seq OWNED BY public.surtido.id_surtido;


--
-- TOC entry 228 (class 1259 OID 16567)
-- Name: venta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.venta (
    id_venta integer NOT NULL,
    id_cliente integer,
    fecha_venta timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- TOC entry 227 (class 1259 OID 16566)
-- Name: venta_id_venta_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.venta_id_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 5020 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.venta_id_venta_seq OWNED BY public.venta.id_venta;


--
-- TOC entry 4782 (class 2604 OID 16505)
-- Name: cliente id_cliente; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id_cliente SET DEFAULT nextval('public.cliente_id_cliente_seq'::regclass);


--
-- TOC entry 4794 (class 2604 OID 16611)
-- Name: detalle_surtido id_detalle_surtido; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_surtido ALTER COLUMN id_detalle_surtido SET DEFAULT nextval('public.detalle_surtido_id_detalle_surtido_seq'::regclass);


--
-- TOC entry 4790 (class 2604 OID 16583)
-- Name: detalle_venta id_detalle_venta; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_venta ALTER COLUMN id_detalle_venta SET DEFAULT nextval('public.detalle_venta_id_detalle_venta_seq'::regclass);


--
-- TOC entry 4786 (class 2604 OID 16554)
-- Name: inventario id_inventario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventario ALTER COLUMN id_inventario SET DEFAULT nextval('public.inventario_id_inventario_seq'::regclass);


--
-- TOC entry 4783 (class 2604 OID 16514)
-- Name: marca id_marca; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marca ALTER COLUMN id_marca SET DEFAULT nextval('public.marca_id_marca_seq'::regclass);


--
-- TOC entry 4785 (class 2604 OID 16536)
-- Name: presentacion id_presentacion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.presentacion ALTER COLUMN id_presentacion SET DEFAULT nextval('public.presentacion_id_presentacion_seq'::regclass);


--
-- TOC entry 4784 (class 2604 OID 16523)
-- Name: producto id_producto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto ALTER COLUMN id_producto SET DEFAULT nextval('public.producto_id_producto_seq'::regclass);


--
-- TOC entry 4792 (class 2604 OID 16603)
-- Name: surtido id_surtido; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.surtido ALTER COLUMN id_surtido SET DEFAULT nextval('public.surtido_id_surtido_seq'::regclass);


--
-- TOC entry 4788 (class 2604 OID 16570)
-- Name: venta id_venta; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venta ALTER COLUMN id_venta SET DEFAULT nextval('public.venta_id_venta_seq'::regclass);


--
-- TOC entry 4990 (class 0 OID 16502)
-- Dependencies: 218
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cliente (id_cliente, nombre_cliente, telefono, correo_electronico, identificacion) FROM stdin;
11	ANA TORRES	3000000001	ana.torres@example.com	6279449554
12	CARLOS RAMIREZ	3000000002	carlos.ramirez@example.com	6148485616
13	LAURA GOMEZ	3000000003	laura.gomez@example.com	2238574330
14	JUAN PEREZ	3000000004	juan.perez@example.com	5357839696
15	DIANA LOPEZ	3000000005	diana.lopez@example.com	7692673727
16	ANDRES ROJAS	3000000006	andres.rojas@example.com	9881145774
17	PAULA CASTRO	3000000007	paula.castro@example.com	9486330676
18	DIEGO VARGAS	3000000008	diego.vargas@example.com	4143227142
19	LUISA MORENO	3000000009	luisa.moreno@example.com	4358673108
20	MATEO RUIZ	3000000010	mateo.ruiz@example.com	8434960195
\.


--
-- TOC entry 5006 (class 0 OID 16608)
-- Dependencies: 234
-- Data for Name: detalle_surtido; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_surtido (id_detalle_surtido, id_surtido, id_presentacion, cantidad, precio_compra) FROM stdin;
11	11	11	20	4500.00
12	12	12	20	800.00
13	13	13	20	700.00
14	14	14	20	1200.00
15	15	15	20	800.00
16	16	16	20	3000.00
17	17	17	20	3500.00
18	18	18	20	4000.00
19	19	19	20	2000.00
20	20	20	20	2800.00
\.


--
-- TOC entry 5002 (class 0 OID 16580)
-- Dependencies: 230
-- Data for Name: detalle_venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_venta (id_detalle_venta, id_venta, id_presentacion, cantidad, precio_unitario) FROM stdin;
1	1	11	2	6500.00
2	2	12	3	1500.00
3	3	13	4	1200.00
4	4	14	2	2000.00
5	5	15	5	1500.00
6	6	16	1	5000.00
7	7	17	2	5500.00
8	8	18	3	6000.00
9	9	19	2	3500.00
10	10	20	4	4500.00
\.


--
-- TOC entry 4998 (class 0 OID 16551)
-- Dependencies: 226
-- Data for Name: inventario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventario (id_inventario, id_producto, cantidad_disponible) FROM stdin;
11	11	18
12	12	17
13	13	16
14	14	18
15	15	15
16	16	19
17	17	18
18	18	17
19	19	18
20	20	16
\.


--
-- TOC entry 4992 (class 0 OID 16511)
-- Dependencies: 220
-- Data for Name: marca; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.marca (id_marca, nombre_marca) FROM stdin;
11	NORMA
12	PELIKAN
13	FABER-CASTELL
14	STAEDTLER
15	BIC
16	PAPER MATE
17	SHARPIE
18	SCRIBE
19	KORES
20	PRISMACOLOR
\.


--
-- TOC entry 4996 (class 0 OID 16533)
-- Dependencies: 224
-- Data for Name: presentacion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.presentacion (id_presentacion, id_producto, tipo_presentacion, unidades_por_presentacion, precio_venta) FROM stdin;
11	11	unidad	1	6500.00
12	12	unidad	1	1500.00
13	13	unidad	1	1200.00
14	14	unidad	1	2000.00
15	15	unidad	1	1500.00
16	16	unidad	1	5000.00
17	17	unidad	1	5500.00
18	18	unidad	1	6000.00
19	19	unidad	1	3500.00
20	20	unidad	1	4500.00
\.


--
-- TOC entry 4994 (class 0 OID 16520)
-- Dependencies: 222
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.producto (id_producto, nombre_producto, id_marca) FROM stdin;
11	CUADERNO CUADRICULADO 100 HOJAS	11
12	BORRADOR DE NATA	12
13	COLORES ESCOLARES	13
14	LAPIZ HB	14
15	BOLIGRAFO AZUL	15
16	PORTAMINAS 0.7 MM	16
17	MARCADOR PERMANENTE NEGRO	17
18	CUADERNO RAYADO 100 HOJAS	18
19	PEGANTE EN BARRA 20 G	19
20	LAPIZ DE COLOR ROJO	20
\.


--
-- TOC entry 5004 (class 0 OID 16600)
-- Dependencies: 232
-- Data for Name: surtido; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.surtido (id_surtido, fecha_surtido) FROM stdin;
11	2026-11-18 08:00:00
12	2026-11-18 08:10:00
13	2026-11-18 08:20:00
14	2026-11-18 08:30:00
15	2026-11-18 08:40:00
16	2026-11-18 08:50:00
17	2026-11-18 09:00:00
18	2026-11-18 09:10:00
19	2026-11-18 09:20:00
20	2026-11-18 09:30:00
\.


--
-- TOC entry 5000 (class 0 OID 16567)
-- Dependencies: 228
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.venta (id_venta, id_cliente, fecha_venta) FROM stdin;
1	11	2026-11-18 10:00:00
2	12	2026-11-18 10:10:00
3	13	2026-11-18 10:20:00
4	14	2026-11-18 10:30:00
5	15	2026-11-18 10:40:00
6	16	2026-11-18 10:50:00
7	17	2026-11-18 11:00:00
8	18	2026-11-18 11:10:00
9	19	2026-11-18 11:20:00
10	20	2026-11-18 11:30:00
\.


--
-- TOC entry 5021 (class 0 OID 0)
-- Dependencies: 217
-- Name: cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cliente_id_cliente_seq', 20, true);


--
-- TOC entry 5022 (class 0 OID 0)
-- Dependencies: 233
-- Name: detalle_surtido_id_detalle_surtido_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_surtido_id_detalle_surtido_seq', 20, true);


--
-- TOC entry 5023 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_venta_id_detalle_venta_seq', 10, true);


--
-- TOC entry 5024 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_inventario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventario_id_inventario_seq', 20, true);


--
-- TOC entry 5025 (class 0 OID 0)
-- Dependencies: 219
-- Name: marca_id_marca_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.marca_id_marca_seq', 20, true);


--
-- TOC entry 5026 (class 0 OID 0)
-- Dependencies: 223
-- Name: presentacion_id_presentacion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.presentacion_id_presentacion_seq', 20, true);


--
-- TOC entry 5027 (class 0 OID 0)
-- Dependencies: 221
-- Name: producto_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.producto_id_producto_seq', 20, true);


--
-- TOC entry 5028 (class 0 OID 0)
-- Dependencies: 231
-- Name: surtido_id_surtido_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.surtido_id_surtido_seq', 20, true);


--
-- TOC entry 5029 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.venta_id_venta_seq', 10, true);


--
-- TOC entry 4808 (class 2606 OID 16509)
-- Name: cliente cliente_correo_electronico_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_correo_electronico_key UNIQUE (correo_electronico);


--
-- TOC entry 4810 (class 2606 OID 25144)
-- Name: cliente cliente_identificacion_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_identificacion_key UNIQUE (identificacion);


--
-- TOC entry 4812 (class 2606 OID 16507)
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id_cliente);


--
-- TOC entry 4835 (class 2606 OID 16616)
-- Name: detalle_surtido detalle_surtido_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_surtido
    ADD CONSTRAINT detalle_surtido_pkey PRIMARY KEY (id_detalle_surtido);


--
-- TOC entry 4831 (class 2606 OID 16588)
-- Name: detalle_venta detalle_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_pkey PRIMARY KEY (id_detalle_venta);


--
-- TOC entry 4825 (class 2606 OID 16560)
-- Name: inventario inventario_id_producto_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_id_producto_key UNIQUE (id_producto);


--
-- TOC entry 4827 (class 2606 OID 16558)
-- Name: inventario inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_pkey PRIMARY KEY (id_inventario);


--
-- TOC entry 4814 (class 2606 OID 16518)
-- Name: marca marca_nombre_marca_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marca
    ADD CONSTRAINT marca_nombre_marca_key UNIQUE (nombre_marca);


--
-- TOC entry 4816 (class 2606 OID 16516)
-- Name: marca marca_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.marca
    ADD CONSTRAINT marca_pkey PRIMARY KEY (id_marca);


--
-- TOC entry 4821 (class 2606 OID 16542)
-- Name: presentacion presentacion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.presentacion
    ADD CONSTRAINT presentacion_pkey PRIMARY KEY (id_presentacion);


--
-- TOC entry 4818 (class 2606 OID 16526)
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id_producto);


--
-- TOC entry 4833 (class 2606 OID 16606)
-- Name: surtido surtido_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.surtido
    ADD CONSTRAINT surtido_pkey PRIMARY KEY (id_surtido);


--
-- TOC entry 4823 (class 2606 OID 16544)
-- Name: presentacion uq_presentacion; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.presentacion
    ADD CONSTRAINT uq_presentacion UNIQUE (id_producto, tipo_presentacion, unidades_por_presentacion);


--
-- TOC entry 4829 (class 2606 OID 16573)
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id_venta);


--
-- TOC entry 4819 (class 1259 OID 16629)
-- Name: uq_producto_nombre_marca; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX uq_producto_nombre_marca ON public.producto USING btree (id_marca, upper(TRIM(BOTH FROM nombre_producto)));


--
-- TOC entry 4840 (class 2606 OID 16594)
-- Name: detalle_venta fk_detalle_presentacion; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT fk_detalle_presentacion FOREIGN KEY (id_presentacion) REFERENCES public.presentacion(id_presentacion);


--
-- TOC entry 4842 (class 2606 OID 16617)
-- Name: detalle_surtido fk_detalle_surtido; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_surtido
    ADD CONSTRAINT fk_detalle_surtido FOREIGN KEY (id_surtido) REFERENCES public.surtido(id_surtido);


--
-- TOC entry 4841 (class 2606 OID 16589)
-- Name: detalle_venta fk_detalle_venta; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT fk_detalle_venta FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- TOC entry 4838 (class 2606 OID 16561)
-- Name: inventario fk_inventario_producto; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT fk_inventario_producto FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- TOC entry 4837 (class 2606 OID 16545)
-- Name: presentacion fk_presentacion_producto; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.presentacion
    ADD CONSTRAINT fk_presentacion_producto FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- TOC entry 4836 (class 2606 OID 16527)
-- Name: producto fk_producto_marca; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT fk_producto_marca FOREIGN KEY (id_marca) REFERENCES public.marca(id_marca);


--
-- TOC entry 4843 (class 2606 OID 16622)
-- Name: detalle_surtido fk_surtido_presentacion; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_surtido
    ADD CONSTRAINT fk_surtido_presentacion FOREIGN KEY (id_presentacion) REFERENCES public.presentacion(id_presentacion);


--
-- TOC entry 4839 (class 2606 OID 16574)
-- Name: venta fk_venta_cliente; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


-- Completed on 2026-11-19 15:47:22

--
-- PostgreSQL database dump complete
--

\unrestrict ByElU3FdV9QNX07FbmmPKG6B75XZVwzVFhPvF9M2FkQ9bObOhX9THQKdcsErzjP

