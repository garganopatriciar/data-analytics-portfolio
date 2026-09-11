-- marts/fct_ventas.sql
-- ---------------------------------------------------------------
-- Tabla de HECHOS: una fila por transacción de venta, con claves
-- foráneas a cada dimensión y las métricas de negocio.
-- Grano: 1 fila = 1 order_id (una venta).
-- ---------------------------------------------------------------

CREATE OR REPLACE TABLE fct_ventas AS
SELECT
    v.order_id,
    v.fecha                        AS fecha_id,
    p.producto_key,
    prov.provincia_key,
    cs.canal_segmento_key,
    v.cantidad,
    v.precio_unitario,
    v.ventas,
    v.costo,
    v.ganancia
FROM stg_ventas v
LEFT JOIN dim_producto p
    ON v.categoria = p.categoria AND v.producto = p.producto
LEFT JOIN dim_provincia prov
    ON v.provincia = prov.provincia
LEFT JOIN dim_canal_segmento cs
    ON v.canal = cs.canal AND v.segmento_cliente = cs.segmento_cliente;
