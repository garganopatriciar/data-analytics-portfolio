-- 02_consulta_no_optimizada.sql
-- ---------------------------------------------------------------
-- Versión "ingenua" de la consulta: pide todas las columnas con
-- SELECT *, aunque el análisis solo necesita 3 de ellas.
--
-- Se incluye a modo comparativo, NO se llegó a ejecutar (se dejó
-- solo en fase de estimación) para no gastar cuota de más.
--
-- Bytes que BigQuery estimó procesar: 23.15 GB
-- ---------------------------------------------------------------

SELECT *
FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
