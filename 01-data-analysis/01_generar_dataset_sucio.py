"""
01_generar_dataset_sucio.py
----------------------------
Genera un dataset de clima "sucio" (con errores tipicos del mundo real)
para practicar limpieza de datos. Simula registros diarios de 3 ciudades
argentinas durante 2024, con los defectos mas comunes que se encuentran
en datasets reales:

- Fechas en formatos distintos dentro de la misma columna
- Nombres de ciudad con mayusculas/minusculas y espacios inconsistentes
- Temperatura guardada como texto con unidades ("21.5 C")
- Valores faltantes (NaN, "", "N/A", "-")
- Filas duplicadas
- Outliers imposibles (ej: temperatura de 300 grados por error de sensor)
- Columna de humedad con comas en vez de puntos decimales
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

CIUDADES = {
    "Buenos Aires": {"temp_base": 18, "amp": 9, "humedad_base": 68, "lluvia_prob": 0.30},
    "Cordoba":      {"temp_base": 17, "amp": 11, "humedad_base": 55, "lluvia_prob": 0.22},
    "Bariloche":    {"temp_base": 9,  "amp": 8,  "humedad_base": 72, "lluvia_prob": 0.35},
}

start = date(2024, 1, 1)
n_days = 366  # 2024 es bisiesto

rows = []
for city, params in CIUDADES.items():
    for i in range(n_days):
        d = start + timedelta(days=i)
        # temperatura estacional (hemisferio sur: pico de calor en enero, frio en julio)
        day_of_year = d.timetuple().tm_yday
        seasonal = np.cos((day_of_year - 15) / 365 * 2 * np.pi)
        temp = params["temp_base"] + params["amp"] * seasonal + np.random.normal(0, 2.2)
        humedad = params["humedad_base"] + np.random.normal(0, 8) - seasonal * 5
        humedad = np.clip(humedad, 15, 100)
        llovio = np.random.random() < params["lluvia_prob"]
        precipitacion = round(np.random.exponential(8), 1) if llovio else 0.0
        viento = max(0, np.random.normal(14, 6))

        rows.append({
            "fecha": d,
            "ciudad": city,
            "temperatura": round(temp, 1),
            "humedad": round(humedad, 1),
            "precipitacion_mm": precipitacion,
            "viento_kmh": round(viento, 1),
        })

df = pd.DataFrame(rows)

# ---------------------------------------------------------------
# A partir de aca ensuciamos el dataset a proposito
# ---------------------------------------------------------------
n = len(df)
dirty = df.copy()

# 1) Formatos de fecha mezclados
def fecha_random_formato(d):
    fmt = np.random.choice(["iso", "dmy_slash", "dmy_dash", "texto"])
    if fmt == "iso":
        return d.isoformat()
    elif fmt == "dmy_slash":
        return d.strftime("%d/%m/%Y")
    elif fmt == "dmy_dash":
        return d.strftime("%d-%m-%Y")
    else:
        return d.strftime("%d de %b de %Y")

idx_fecha_rara = np.random.choice(n, size=int(n * 0.4), replace=False)
dirty["fecha"] = dirty["fecha"].astype(object)
for i in idx_fecha_rara:
    dirty.at[i, "fecha"] = fecha_random_formato(df.at[i, "fecha"])
# el resto lo dejamos como date object (tambien "sucio" porque mezcla tipos)

# 2) Nombre de ciudad inconsistente (mayusculas, espacios, acentos)
variantes_ciudad = {
    "Buenos Aires": ["buenos aires", "BUENOS AIRES", " Buenos Aires", "Bs As", "Buenos  Aires"],
    "Cordoba": ["cordoba", "CÓRDOBA", "Córdoba ", "cordoba "],
    "Bariloche": ["bariloche", "BARILOCHE", " Bariloche", "San Carlos de Bariloche"],
}
idx_ciudad_rara = np.random.choice(n, size=int(n * 0.35), replace=False)
for i in idx_ciudad_rara:
    original = df.at[i, "ciudad"]
    dirty.at[i, "ciudad"] = np.random.choice(variantes_ciudad[original])

# 3) Temperatura como texto con unidades, y algunos outliers de sensor
dirty["temperatura"] = dirty["temperatura"].astype(object)
idx_temp_texto = np.random.choice(n, size=int(n * 0.25), replace=False)
for i in idx_temp_texto:
    val = df.at[i, "temperatura"]
    dirty.at[i, "temperatura"] = f"{val} C"

idx_outlier = np.random.choice(n, size=6, replace=False)
for i in idx_outlier:
    dirty.at[i, "temperatura"] = np.random.choice([300.0, -99.0, 999])

# 4) Humedad con coma decimal (formato europeo/latam) como texto
dirty["humedad"] = dirty["humedad"].astype(object)
idx_humedad_coma = np.random.choice(n, size=int(n * 0.3), replace=False)
for i in idx_humedad_coma:
    val = df.at[i, "humedad"]
    dirty.at[i, "humedad"] = str(val).replace(".", ",")

# 5) Valores faltantes representados de formas distintas
faltantes_posibles = [np.nan, "", "N/A", "-", "s/d"]
dirty["precipitacion_mm"] = dirty["precipitacion_mm"].astype(object)
dirty["viento_kmh"] = dirty["viento_kmh"].astype(object)
for col in ["temperatura", "humedad", "precipitacion_mm", "viento_kmh"]:
    idx_faltante = np.random.choice(n, size=int(n * 0.05), replace=False)
    for i in idx_faltante:
        dirty.at[i, col] = np.random.choice(faltantes_posibles)

# 6) Filas duplicadas (algunas exactas, otras casi exactas)
duplicados = dirty.sample(n=25, random_state=1)
dirty = pd.concat([dirty, duplicados], ignore_index=True)

# 7) Desordenamos las filas para que no se note el patron
dirty = dirty.sample(frac=1, random_state=7).reset_index(drop=True)

out_path = "/mnt/user-data/outputs/clima_sucio.csv"
dirty.to_csv(out_path, index=False)
print(f"Dataset sucio generado: {out_path}")
print(f"Filas: {len(dirty)} | Columnas: {list(dirty.columns)}")
print(dirty.head(8).to_string())
