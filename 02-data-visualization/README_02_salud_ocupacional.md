# Tablero de Salud Ocupacional

Dashboard interactivo de indicadores de salud y seguridad en el trabajo (SST), con datos mensuales simulados de una empresa de 5 áreas durante 2023-2024. Combina criterio clínico/epidemiológico con visualización de datos — un cruce poco común en portfolios de analytics, pero directamente relevante dada mi formación en Medicina (UBA) junto con mi trabajo actual en salud digital.

## 🎯 Qué mide

| Indicador | Qué representa | Por qué importa |
|---|---|---|
| **Índice de incidencia** | Accidentes con lesión por cada 200.000 horas trabajadas (metodología estándar OSHA) | Permite comparar el riesgo entre áreas de distinto tamaño de forma justa — un área de 80 personas y una de 15 no se pueden comparar solo por cantidad de accidentes |
| **Tasa de ausentismo** | % de días hábiles perdidos sobre el total posible | Indicador agregado de bienestar/salud de la fuerza laboral |
| **Días perdidos por causa** | Desglose entre accidentes laborales, enfermedad común, salud mental y trastornos musculoesqueléticos | Distingue causas prevenibles (ergonomía, seguridad) de las que no lo son, orientando dónde intervenir |
| **Cumplimiento de capacitación en seguridad** | % de dotación con capacitación al día | Indicador líder (predictivo), a diferencia de los anteriores que son indicadores rezagados (miden lo que ya pasó) |
| **Casi-accidentes (near-misses)** | Eventos sin lesión pero con potencial de haberla causado | En SST, se monitorean porque anticipan accidentes reales — una tasa alta de casi-accidentes con pocos accidentes reales puede ser "suerte", no seguridad real |

## 📊 Hallazgos principales

- **Producción y Logística concentran el riesgo real**: índice de incidencia promedio de 37,8 y 39,5 respectivamente, muy por encima de Administración (9,4), Ventas (13,3) e IT (7,9) — coherente con la naturaleza física del trabajo en esas áreas.
- **La enfermedad común, no los accidentes, es la principal causa de días perdidos** (1.609 de 2.717 días totales, ~59%) — un recordatorio de que la gestión de ausentismo no puede enfocarse solo en seguridad física.
- **Los trastornos musculoesqueléticos están concentrados en Producción y Logística**, consistente con tareas de esfuerzo físico repetitivo — sugiere una intervención ergonómica específica en esas áreas, no una política genérica para toda la empresa.

## 🛠️ Cómo se construyó

1. Generación de un dataset sintético mensual (`salud_ocupacional.csv`) con parámetros de riesgo realistas y diferenciados por área
2. Cálculo del índice de incidencia con la fórmula estándar OSHA: `(accidentes × 200.000) / horas trabajadas`
3. Agregación de datos y construcción del tablero interactivo en HTML/JavaScript (Chart.js), autocontenido — no depende de ningún servicio externo, corre abriendo el archivo directamente en cualquier navegador

## 📁 Archivos

| Archivo | Contenido |
|---|---|
| `salud_ocupacional.csv` | Dataset mensual, 120 filas (24 meses × 5 áreas) |
| `tablero_salud_ocupacional.html` | Tablero interactivo con selector por área |

## 🛠️ Herramientas

Python (pandas, numpy), HTML/CSS/JavaScript, Chart.js

## 📌 Nota

Los datos son sintéticos, generados para este proyecto de portfolio — no corresponden a ninguna organización real, en línea con el resto de los proyectos de este repositorio que evitan usar información vinculada a mi trabajo actual.
