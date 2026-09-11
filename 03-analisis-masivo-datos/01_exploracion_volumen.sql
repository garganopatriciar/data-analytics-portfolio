-- 01_exploracion_volumen.sql
-- ---------------------------------------------------------------
-- Objetivo: dimensionar el dataset antes de trabajar con él.
-- Cuenta la cantidad total de viajes y el rango de fechas cubierto.
--
-- Bytes procesados: ~1 GB (1,000.46 MB)
-- Resultado: 131,131,794 viajes en 2016 (1 enero 2016 - 31 dic 2016)
-- ---------------------------------------------------------------

SELECT
  COUNT(*) AS cantidad_viajes,
  MIN(pickup_datetime) AS primer_viaje,
  MAX(pickup_datetime) AS ultimo_viaje
FROM
  `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
