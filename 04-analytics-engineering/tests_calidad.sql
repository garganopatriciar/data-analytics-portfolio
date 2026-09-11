-- tests/tests_calidad.sql
-- ---------------------------------------------------------------
-- Tests de calidad de datos, estilo dbt: cada uno debería devolver
-- CERO filas si el modelo está sano. Si devuelven filas, hay un
-- problema que investigar antes de confiar en el modelo.
-- ---------------------------------------------------------------

-- TEST 1: unicidad de la clave primaria en la tabla de hechos
-- (no debería haber order_id repetidos)
SELECT order_id, COUNT(*) AS repeticiones
FROM fct_ventas
GROUP BY order_id
HAVING COUNT(*) > 1;

-- TEST 2: integridad referencial — todo producto_key en fct_ventas
-- debe existir en dim_producto (ningún JOIN debería haber fallado)
SELECT f.order_id
FROM fct_ventas f
LEFT JOIN dim_producto p ON f.producto_key = p.producto_key
WHERE p.producto_key IS NULL;

-- TEST 3: integridad referencial — provincia
SELECT f.order_id
FROM fct_ventas f
LEFT JOIN dim_provincia p ON f.provincia_key = p.provincia_key
WHERE p.provincia_key IS NULL;

-- TEST 4: no debería haber ventas negativas o en cero
SELECT order_id, ventas
FROM fct_ventas
WHERE ventas <= 0;

-- TEST 5: la ganancia nunca debería superar a la venta
-- (costo no puede ser negativo en este negocio)
SELECT order_id, ventas, costo, ganancia
FROM fct_ventas
WHERE ganancia > ventas;

-- TEST 6: conservación del total — la suma de ventas en el mart
-- final debe coincidir con la suma en el dato crudo (nada se
-- perdió ni se duplicó en las transformaciones)
SELECT
    (SELECT ROUND(SUM(ventas), 2) FROM raw_ventas)    AS total_raw,
    (SELECT ROUND(SUM(ventas), 2) FROM fct_ventas)    AS total_mart,
    (SELECT ROUND(SUM(ventas), 2) FROM raw_ventas)
      - (SELECT ROUND(SUM(ventas), 2) FROM fct_ventas) AS diferencia;
