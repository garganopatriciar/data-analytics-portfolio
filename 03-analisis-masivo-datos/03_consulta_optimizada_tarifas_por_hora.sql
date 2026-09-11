-- 03_consulta_optimizada_tarifas_por_hora.sql
-- ---------------------------------------------------------------
-- Pregunta de negocio: ¿cómo varía la demanda, la tarifa promedio
-- y la distancia promedio de los viajes según la hora del día?
--
-- Optimización aplicada frente a la versión "ingenua" (02):
--  - Se seleccionan solo las 3 columnas necesarias
--    (pickup_datetime, fare_amount, trip_distance) en vez de SELECT *.
--    BigQuery es un motor columnar: solo lee del disco las columnas
--    mencionadas en la consulta, así que menos columnas = menos bytes.
--  - Se filtran valores inválidos (tarifas o distancias <= 0) antes
--    de agregar, para no distorsionar los promedios.
--
-- Bytes procesados: 4.89 GB  (vs. 23.15 GB de la versión con SELECT *)
-- Reducción: ~79%
--
-- Nota sobre particionado/clustering: esta tabla pública no está
-- particionada por fecha, por lo que un WHERE por rango de fechas
-- no reduciría más el costo (igual escanea la tabla completa). Si
-- este fuera un pipeline propio, convendría materializar la tabla
-- particionada por DATE(pickup_datetime) y clusterizada por
-- pickup_location_id, ya que la mayoría de las consultas de negocio
-- filtran por rango de fechas y comparan zonas.
-- ---------------------------------------------------------------

SELECT
  EXTRACT(HOUR FROM pickup_datetime) AS hora_del_dia,
  COUNT(*) AS cantidad_viajes,
  ROUND(AVG(fare_amount), 2) AS tarifa_promedio,
  ROUND(AVG(trip_distance), 2) AS distancia_promedio
FROM
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
WHERE
  fare_amount > 0
  AND trip_distance > 0
GROUP BY
  hora_del_dia
ORDER BY
  hora_del_dia
