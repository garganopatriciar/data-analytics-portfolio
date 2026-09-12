# Ejemplos de conversación — DataMentor AR

Transcripciones reales probando los 3 modos del Gem, tal como quedó configurado en `instrucciones_gem.md`.

---

## Modo 1: Revisor de consultas SQL

**Prompt:** "dame una consulta sql optimizada para un sitio de ventas que quiero saber las ventas en un mes especifico"

**Respuesta del Gem:**

> Como tu pedido entra en la revisión y optimización de consultas SQL (Modo 1), acá tenés la estructura recomendada para este caso.
>
> Para saber las ventas de un mes específico en una tabla transaccional grande de e-commerce, lo ideal es evitar funciones sobre las columnas en la cláusula `WHERE` (como `MONTH(fecha) = 3`) porque anulan los índices o el particionado de la tabla y obligan a escanear todo de punta a punta.
>
> **1. Qué hacer y por qué**
> - **Filtrar por rango exacto de fechas (SARGable):** usá `<` y `>=` con las fechas de inicio y fin del mes. Esto le permite al motor (PostgreSQL, MySQL, BigQuery o Snowflake) usar índices o poda de particiones (*partition pruning*) para leer únicamente los datos de ese mes.
> - **Seleccionar solo los agregados necesarios:** evitá el `SELECT *` y agrupá directamente lo que necesitás sumar o contar.
>
> **2. Consulta optimizada (fragmento base)**
> ```sql
> SELECT
>     COUNT(order_id) AS total_pedidos,
>     SUM(monto_total) AS facturacion_total
> FROM
>     ventas
> WHERE
>     fecha_venta >= '2026-03-01'
>     AND fecha_venta < '2026-04-01';
> ```
>
> **3. Ajuste por motor (si aplica)**
> - Si usás BigQuery o Snowflake: asegurate de que la tabla `ventas` esté particionada por el campo `fecha_venta`. Al hacer el filtro por rango con las fechas exactas, la consulta va a escanear solo la partición del mes elegido, bajando drásticamente el costo de procesamiento.

**Por qué funciona:** el agente no solo optimiza — explica el mecanismo (consultas *SARGables*, cómo las funciones sobre columnas anulan el particionado) en vez de dar una respuesta de caja negra. Esto refuerza directamente el mismo concepto de particionado documentado en `03-analisis-masivo-datos`, mostrando coherencia técnica en todo el portfolio.

---

## Modo 2: Selector de visualización

**Prompt:** "que grafico me sugieres para evaluar las finanzas de un negocio de ventas a lo largo del tiempo"

**Respuesta del Gem:**

> Te sugiero un gráfico de líneas múltiples (o un gráfico combinado de líneas y barras si querés contrastar volumen de ventas con margen).
>
> - **Eje X (horizontal):** El tiempo, agrupado por la frecuencia de análisis adecuada (días, semanas o meses).
> - **Eje Y (vertical):** El monto en dinero (ingresos, costos y ganancia neta).
> - **Por qué:** Es el estándar para ver evolución temporal. Podés superponer dos o tres líneas (ej: Ingresos Totales vs. Costos Totales) para identificar rápido tendencias, estacionalidad y puntos donde se reduce el margen operativo.
> - **Error común a evitar:** Cortar el eje Y en un valor distinto de cero o mezclar métricas de distintas escalas (como volumen de transacciones con ingresos monetarios) en un solo eje sin usar un eje secundario, ya que distorsiona la percepción real del crecimiento.

**Por qué funciona:** respeta el formato pedido (gráfico recomendado + qué va en cada eje + un error común a evitar) y da una recomendación aplicable directamente al proyecto `01-data-analysis` (ventas/ganancia a lo largo del tiempo) y a `04-analytics-engineering` (el modelo `fct_ventas` con métricas de ingresos, costos y ganancia ya modeladas para este tipo de gráfico).

---

## Modo 3: Explicador de conceptos

**Prompt:** "que es clusterizacion en tablas"

**Respuesta del Gem:**

> En una frase: es guardar los datos de una tabla ordenados físicamente en el disco según los valores de una o más columnas para que las búsquedas sobre esas columnas sean ultra rápidas y baratas.
>
> Pensalo como el archivador de una oficina: si guardás las facturas ordenadas por apellido del cliente, cuando busques las de "García" vas directo al cajón de la G en vez de revolver todas las cajas de la oficina.
>
> En la práctica, lo usás en motores como BigQuery o Snowflake. Por ejemplo, en una tabla gigante de eventos web, particionás por `fecha` y clusterizás por `user_id` y `event_name`. Cuando filtrás por un usuario puntual en un día específico, el motor lee únicamente los bloques de disco donde están esos datos, reduciendo drásticamente los bytes escaneados y los costos.

**Por qué funciona:** cumple exactamente el formato pedido en las instrucciones — frase simple, analogía cotidiana, ejemplo concreto de uso real — y conecta directamente con la explicación de particionado/clustering documentada en el proyecto `03-analisis-masivo-datos`, mostrando consistencia entre lo que el agente explica y lo que se aplicó a mano en ese proyecto.
