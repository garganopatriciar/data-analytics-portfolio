-- staging/stg_ventas.sql
-- ---------------------------------------------------------------
-- Capa STAGING: primer punto de contacto con el dato crudo.
-- Responsabilidad única: limpiar y estandarizar, sin aplicar
-- lógica de negocio todavía (eso vive en marts).
--
--   - Renombra columnas a un estándar consistente
--   - Castea tipos explícitamente (no confiar en inferencia automática)
--   - Normaliza texto (trim, capitalización consistente)
--   - Genera una clave primaria limpia (order_id)
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE stg_ventas AS
SELECT
    CAST(order_id AS BIGINT)                  AS order_id,
    CAST(fecha AS DATE)                       AS fecha,
    TRIM(provincia)                           AS provincia,
    TRIM(categoria)                           AS categoria,
    TRIM(producto)                            AS producto,
    TRIM(canal)                               AS canal,
    TRIM(segmento_cliente)                    AS segmento_cliente,
    CAST(cantidad AS INTEGER)                 AS cantidad,
    ROUND(CAST(precio_unitario AS DOUBLE), 2) AS precio_unitario,
    ROUND(CAST(ventas AS DOUBLE), 2)          AS ventas,
    ROUND(CAST(costo AS DOUBLE), 2)           AS costo,
    ROUND(CAST(ganancia AS DOUBLE), 2)        AS ganancia
FROM raw_ventas
WHERE order_id IS NOT NULL
  AND fecha IS NOT NULL;
