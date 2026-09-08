"""
02_limpieza_datos.py
---------------------
Limpieza completa del dataset clima_sucio.csv.
Cada paso esta comentado para que el proceso sirva como pieza de
portfolio (mostrar el "antes / despues" y el razonamiento).
"""

import pandas as pd
import numpy as np
import re

IN_PATH = "/mnt/user-data/outputs/clima_sucio.csv"
OUT_CSV = "/mnt/user-data/outputs/clima_limpio.csv"
LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)

df = pd.read_csv(IN_PATH, dtype=str)  # todo como texto: lo tipamos nosotros a mano
log(f"Filas cargadas: {len(df)}")

# 1) Normalizar nombres de columnas (por si vinieran con espacios/mayusculas)
df.columns = [c.strip().lower() for c in df.columns]

# 2) Estandarizar la columna 'ciudad'
#    - sacar espacios, pasar a un catalogo unico, sin importar mayusculas/acentos
def normalizar_ciudad(valor):
    if pd.isna(valor):
        return np.nan
    v = valor.strip().lower()
    v = (v.replace("á", "a").replace("é", "e").replace("í", "i")
           .replace("ó", "o").replace("ú", "o" if False else "u"))
    v = re.sub(r"\s+", " ", v)
    mapa = {
        "buenos aires": "Buenos Aires",
        "bs as": "Buenos Aires",
        "cordoba": "Cordoba",
        "bariloche": "Bariloche",
        "san carlos de bariloche": "Bariloche",
    }
    return mapa.get(v, valor.strip())

df["ciudad"] = df["ciudad"].apply(normalizar_ciudad)
log(f"Ciudades unicas tras normalizar: {sorted(df['ciudad'].dropna().unique())}")

# 3) Parsear fechas con formatos mixtos
MESES = {"ene":1,"feb":2,"mar":3,"abr":4,"may":5,"jun":6,"jul":7,"ago":8,
          "sep":9,"oct":10,"nov":11,"dic":12}

def parsear_fecha(valor):
    if pd.isna(valor):
        return pd.NaT
    v = valor.strip()
    # formato "20 de Sep de 2024"
    m = re.match(r"(\d{1,2}) de (\w{3})\w* de (\d{4})", v, flags=re.IGNORECASE)
    if m:
        dia, mes_txt, anio = m.groups()
        mes = MESES.get(mes_txt.lower()[:3])
        if mes:
            return pd.Timestamp(year=int(anio), month=mes, day=int(dia))
    # intentos estandar: ISO, dd/mm/yyyy, dd-mm-yyyy
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return pd.to_datetime(v, format=fmt)
        except ValueError:
            continue
    return pd.to_datetime(v, errors="coerce", dayfirst=True)

df["fecha"] = df["fecha"].apply(parsear_fecha)
sin_fecha = df["fecha"].isna().sum()
log(f"Fechas que no se pudieron interpretar: {sin_fecha}")

# 4) Limpiar 'temperatura': sacar la unidad " C", pasar a float, marcar outliers imposibles
def limpiar_temperatura(valor):
    if pd.isna(valor):
        return np.nan
    v = str(valor).strip().upper().replace("C", "").strip()
    try:
        num = float(v)
    except ValueError:
        return np.nan
    # rango fisicamente posible para Argentina: -25 a 50 C
    if num < -25 or num > 50:
        return np.nan
    return num

df["temperatura"] = df["temperatura"].apply(limpiar_temperatura)

# 5) Limpiar 'humedad': coma decimal -> punto, rango 0-100
def limpiar_humedad(valor):
    if pd.isna(valor):
        return np.nan
    v = str(valor).strip().replace(",", ".")
    try:
        num = float(v)
    except ValueError:
        return np.nan
    if num < 0 or num > 100:
        return np.nan
    return num

df["humedad"] = df["humedad"].apply(limpiar_humedad)

# 6) Precipitacion y viento: solo castear a numero, no pueden ser negativos
for col in ["precipitacion_mm", "viento_kmh"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df.loc[df[col] < 0, col] = np.nan

# 7) Eliminar duplicados exactos (misma fecha + ciudad + variables)
antes = len(df)
df = df.drop_duplicates()
log(f"Duplicados exactos eliminados: {antes - len(df)}")

# También puede haber duplicados de "misma fecha+ciudad" con valores levemente
# distintos (doble carga del sensor). Nos quedamos con el primer registro.
antes = len(df)
df = df.sort_values(["ciudad", "fecha"]).drop_duplicates(subset=["ciudad", "fecha"], keep="first")
log(f"Duplicados por fecha+ciudad eliminados: {antes - len(df)}")

# 8) Descartar filas sin fecha o sin ciudad (no se pueden ubicar en el tiempo/espacio)
antes = len(df)
df = df.dropna(subset=["fecha", "ciudad"])
log(f"Filas sin fecha o ciudad descartadas: {antes - len(df)}")

# 9) Imputar valores faltantes de las variables numericas
#    Estrategia: interpolar en el tiempo dentro de cada ciudad (el clima es
#    una serie continua, tiene mas sentido que usar la media general).
df = df.sort_values(["ciudad", "fecha"]).reset_index(drop=True)
faltantes_antes = df[["temperatura", "humedad", "precipitacion_mm", "viento_kmh"]].isna().sum()

for col in ["temperatura", "humedad", "viento_kmh"]:
    df[col] = df.groupby("ciudad")[col].transform(lambda s: s.interpolate(limit_direction="both"))

# la precipitacion no se interpola (no es una variable "suave"): un dia sin
# dato se asume sin lluvia registrada = 0, criterio conservador y documentado
df["precipitacion_mm"] = df["precipitacion_mm"].fillna(0)

faltantes_despues = df[["temperatura", "humedad", "precipitacion_mm", "viento_kmh"]].isna().sum()
log("Valores faltantes por columna (antes -> despues de imputar):")
for col in faltantes_antes.index:
    log(f"  {col}: {faltantes_antes[col]} -> {faltantes_despues[col]}")

# 10) Redondear y tipar columnas finales
df["temperatura"] = df["temperatura"].round(1)
df["humedad"] = df["humedad"].round(1)
df["precipitacion_mm"] = df["precipitacion_mm"].round(1)
df["viento_kmh"] = df["viento_kmh"].round(1)

# 11) Columnas derivadas utiles para el tablero
df["anio"] = df["fecha"].dt.year
df["mes"] = df["fecha"].dt.month
df["mes_nombre"] = df["fecha"].dt.strftime("%b")

def estacion(mes):
    # hemisferio sur
    if mes in (12, 1, 2):
        return "Verano"
    if mes in (3, 4, 5):
        return "Otonio"
    if mes in (6, 7, 8):
        return "Invierno"
    return "Primavera"

df["estacion"] = df["mes"].apply(estacion)
df["llovio"] = df["precipitacion_mm"] > 0

df = df[["fecha", "anio", "mes", "mes_nombre", "estacion", "ciudad",
         "temperatura", "humedad", "precipitacion_mm", "viento_kmh", "llovio"]]

df.to_csv(OUT_CSV, index=False)
log(f"\nDataset limpio guardado en: {OUT_CSV}")
log(f"Filas finales: {len(df)} | Columnas: {list(df.columns)}")

with open("/mnt/user-data/outputs/log_limpieza.txt", "w") as f:
    f.write("\n".join(LOG))

print("\n--- Muestra del dataset limpio ---")
print(df.head(10).to_string())
