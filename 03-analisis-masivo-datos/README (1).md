# Análisis masivo de datos — Viajes de taxi en Nueva York (BigQuery)

Análisis de escala sobre uno de los datasets públicos más usados para practicar big data: los registros de viajes de taxi amarillo de Nueva York. El foco de este proyecto no es solo "sacar insights", sino **mostrar criterio de optimización de consultas SQL sobre volúmenes grandes** — una habilidad que se nota poco en portfolios pero pesa mucho en roles de analytics engineer.

## 📊 El dataset

- **Fuente:** `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016` (dataset público de Google BigQuery)
- **Volumen:** 131.131.794 viajes — un año completo (2016-01-01 a 2016-12-31)
- **Motor:** Google BigQuery (procesamiento columnar, serverless, capa gratuita de 1 TB de consultas/mes)

## 🧠 La pregunta de negocio

¿Cómo varía la demanda de viajes, la tarifa promedio y la distancia promedio según la hora del día? Útil, por ejemplo, para decisiones de dotación de flota u horarios de tarifa dinámica.

## ⚡ Lo importante: optimización de consultas

Antes de responder la pregunta, comparé dos formas de escribir la misma consulta — una "ingenua" y una optimizada — para mostrar el impacto real en costo/performance.

| Consulta | Qué hace | GB procesados | Diferencia |
|---|---|---:|---:|
| `02_consulta_no_optimizada.sql` | `SELECT *` (trae todas las columnas) | 23.15 GB | — |
| `03_consulta_optimizada_tarifas_por_hora.sql` | Selecciona solo 3 columnas necesarias | 4.89 GB | **-79%** |

**Por qué pasa esto:** BigQuery es un motor de almacenamiento **columnar** — solo lee del disco las columnas que mencionás en el `SELECT`/`WHERE`/`GROUP BY`, no la fila completa. Pedir `SELECT *` fuerza a leer las ~18 columnas de la tabla aunque el análisis solo necesite 3. En un motor que cobra por bytes procesados (y en cualquier motor, por tiempo de I/O), esto es la primera y más simple optimización a aplicar.

### Sobre particionado y clustering

Esta tabla pública **no está particionada ni clusterizada**, así que filtrar por fecha no reduce más el costo (igual escanea la tabla completa). Si este fuera un pipeline propio en producción, la recomendación sería materializar una versión de la tabla:

```sql
CREATE TABLE mi_dataset.viajes_particionados
PARTITION BY DATE(pickup_datetime)
CLUSTER BY pickup_location_id
AS SELECT * FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2016`
```

- **Particionar por fecha**: la mayoría de las consultas de negocio filtran por rango de fechas (ej: "último mes"); con la tabla particionada, BigQuery salta directo a los días relevantes en vez de escanear el año completo.
- **Clusterizar por zona**: dentro de cada partición, ordena los datos por `pickup_location_id`, acelerando además las consultas que comparan o filtran por zona.

## 📈 Resultado y hallazgos

Ver `resultados_tarifas_por_hora.csv` para el detalle completo (24 filas, una por hora).

- **Pico de demanda a las 19hs** (~8,0 millones de viajes en el año), con el valle más marcado a las 5am (~1,37 millones).
- **Hallazgo más interesante:** a las 4am la distancia promedio salta a **18,3 millas**, muy por encima del resto del día (2,8 a 7,2 millas). Con pocos viajes a esa hora, es consistente con traslados al aeropuerto en vuelos tempraneros, no con viajes urbanos típicos.
- La tarifa promedio se mantiene relativamente estable (entre $12 y $16) a lo largo del día, sin variar tanto como el volumen de viajes.

## 📁 Archivos

| Archivo | Contenido |
|---|---|
| `01_exploracion_volumen.sql` | Dimensiona el dataset: cantidad de filas y rango de fechas |
| `02_consulta_no_optimizada.sql` | Versión con `SELECT *`, usada solo para medir el costo de referencia |
| `03_consulta_optimizada_tarifas_por_hora.sql` | Consulta final, optimizada, que responde la pregunta de negocio |
| `resultados_tarifas_por_hora.csv` | Resultado de la consulta 03: 24 filas (una por hora del día) |

## 🛠️ Herramientas

Google BigQuery (SQL estándar), capa gratuita "Sandbox" (sin facturación habilitada)

## ▶️ Cómo reproducirlo

1. Crear un proyecto gratis en [Google Cloud Console](https://console.cloud.google.com) (no requiere tarjeta para el nivel Sandbox)
2. Abrir BigQuery, agregar el dataset público `bigquery-public-data.new_york_taxi_trips`
3. Ejecutar los archivos `.sql` de este repo, en orden, desde el editor de consultas
