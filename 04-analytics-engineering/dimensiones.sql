-- marts/dim_fecha.sql
-- ---------------------------------------------------------------
-- Dimensión de tiempo: una fila por cada fecha presente en los
-- datos, con atributos derivados listos para filtrar/agrupar sin
-- tener que calcularlos en cada consulta (año, mes, trimestre,
-- nombre de mes, día de la semana, si es fin de semana).
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE dim_fecha AS
SELECT DISTINCT
    fecha                                    AS fecha_id,
    EXTRACT(YEAR FROM fecha)                 AS anio,
    EXTRACT(MONTH FROM fecha)                AS mes,
    EXTRACT(QUARTER FROM fecha)               AS trimestre,
    STRFTIME(fecha, '%B')                    AS mes_nombre,
    STRFTIME(fecha, '%A')                    AS dia_semana_nombre,
    CASE WHEN EXTRACT(DOW FROM fecha) IN (0, 6)
         THEN TRUE ELSE FALSE END            AS es_fin_de_semana
FROM stg_ventas;


-- marts/dim_producto.sql
-- ---------------------------------------------------------------
-- Dimensión de producto: catálogo único de categoría + producto.
-- Se genera una clave sustituta (surrogate key) con ROW_NUMBER,
-- práctica estándar en modelado dimensional para no depender de
-- claves de negocio como identificador único.
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE dim_producto AS
SELECT
    ROW_NUMBER() OVER (ORDER BY categoria, producto) AS producto_key,
    categoria,
    producto
FROM (SELECT DISTINCT categoria, producto FROM stg_ventas);


-- marts/dim_provincia.sql
-- ---------------------------------------------------------------
-- Dimensión geográfica.
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE dim_provincia AS
SELECT
    ROW_NUMBER() OVER (ORDER BY provincia) AS provincia_key,
    provincia
FROM (SELECT DISTINCT provincia FROM stg_ventas);


-- marts/dim_canal_segmento.sql
-- ---------------------------------------------------------------
-- Dimensión de contexto de venta: canal (online/tienda) cruzado
-- con segmento de cliente (consumidor/empresa/mayorista).
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE dim_canal_segmento AS
SELECT
    ROW_NUMBER() OVER (ORDER BY canal, segmento_cliente) AS canal_segmento_key,
    canal,
    segmento_cliente
FROM (SELECT DISTINCT canal, segmento_cliente FROM stg_ventas);
