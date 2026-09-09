# Limpieza de datos y tablero interactivo — Clima Argentina 2024

Proyecto de práctica que recorre el flujo completo de un análisis de datos: generación de un dataset con errores típicos del mundo real, limpieza documentada paso a paso, y un tablero final interactivo.

Datos diarios simulados de tres ciudades argentinas (Buenos Aires, Córdoba y Bariloche) durante 2024: temperatura, humedad, precipitación y viento.

## 🔎 Vista previa del tablero

![Tablero de clima](screenshot.png)

*(reemplazar `screenshot.png` por una captura del tablero — ver sección "Cómo agregar la captura" más abajo)*

## 📁 Estructura del repositorio

| Archivo | Descripción |
|---|---|
| `01_generar_dataset_sucio.py` | Genera `clima_sucio.csv`: dataset sintético con errores intencionales (fechas en formatos mixtos, texto con unidades, comas decimales, duplicados, outliers, faltantes) |
| `clima_sucio.csv` | Dataset crudo, tal como "llegaría" desde una fuente real |
| `02_limpieza_datos.py` | Limpieza completa: normalización de texto y fechas, tipado correcto, eliminación de duplicados, imputación por interpolación temporal, columnas derivadas (mes, estación, si llovió) |
| `log_limpieza.txt` | Resumen de cada corrección aplicada (cuántas fechas, duplicados y faltantes se corrigieron) |
| `clima_limpio.csv` / `clima_limpio.xlsx` | Dataset final, listo para análisis. El Excel incluye una hoja adicional con resumen mensual por ciudad |
| `tablero_clima.html` | Tablero interactivo (KPIs, temperatura, precipitación, humedad y viento por ciudad) |

## 🧹 Qué problemas tenía el dataset original

- Fechas mezcladas en 4 formatos distintos (`2024-06-15`, `15/06/2024`, `15-06-2024`, `15 de Jun de 2024`)
- Nombres de ciudad inconsistentes (`buenos aires`, `BUENOS AIRES`, `Bs As`, `Buenos  Aires`)
- Temperatura guardada como texto con unidad (`"21.5 C"`)
- Humedad con coma decimal en vez de punto (`"68,7"`)
- Valores faltantes representados de 5 formas distintas (`NaN`, `""`, `"N/A"`, `"-"`, `"s/d"`)
- Filas duplicadas (exactas y por fecha+ciudad)
- Outliers imposibles por error de sensor (temperaturas de 300°C o -99°C)

## ✅ Criterios de limpieza aplicados

- **Fechas**: parseo con múltiples formatos y validación de que todas queden en `datetime`
- **Texto**: normalización de mayúsculas, tildes y espacios, mapeadas a un catálogo único de ciudades
- **Valores numéricos fuera de rango físico** (temperatura, humedad): descartados como faltantes en vez de conservarlos
- **Imputación de faltantes**: interpolación temporal por ciudad para variables continuas (temperatura, humedad, viento); la precipitación se completa con `0` bajo el criterio conservador de "sin dato = sin lluvia registrada", documentado explícitamente en el script
- **Duplicados**: se eliminan tanto los exactos como los repetidos por `fecha + ciudad`, quedándose con el primer registro

## 📊 Tablero

El tablero (`tablero_clima.html`) es un archivo autocontenido (HTML + JS, sin dependencias de servidor) que muestra:

- KPIs por ciudad: temperatura promedio, máxima/mínima, precipitación total, días de lluvia, humedad promedio
- Evolución mensual de temperatura, precipitación, humedad y viento
- Selector para comparar Buenos Aires, Córdoba y Bariloche

Se puede abrir directamente en el navegador, o publicarlo con **GitHub Pages** para tener un link compartible (ver más abajo).

## 🛠️ Herramientas usadas

Python (pandas, numpy, openpyxl), HTML/CSS/JavaScript, Chart.js

## ▶️ Cómo reproducirlo

```bash
pip install pandas numpy openpyxl
python 01_generar_dataset_sucio.py   # genera clima_sucio.csv
python 02_limpieza_datos.py          # genera clima_limpio.csv / clima_limpio.xlsx
```

Luego abrir `tablero_clima.html` en el navegador.

## 🌐 Publicar el tablero con GitHub Pages

1. En el repo, ir a **Settings → Pages**
2. En "Branch", elegir `main` y carpeta `/ (root)`
3. Guardar. GitHub va a dar un link tipo `https://tu-usuario.github.io/nombre-repo/tablero_clima.html`

## 📌 Nota

El dataset es sintético (generado con `01_generar_dataset_sucio.py`), pensado para practicar y mostrar el proceso completo de limpieza de datos con un ejemplo no vinculado a mi trabajo actual en el sector salud.

---
Patricia Raquel Gargano · [LinkedIn](https://linkedin.com/in/patriciargargano) · garganopatriciar@gmail.com
