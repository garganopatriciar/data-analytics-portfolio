#!/usr/bin/env python3
"""Mapper compatible con Hadoop Streaming.
Entrada: líneas CSV crudas (ambas series, ; o ,). Salida: 'anio|nivel_icsap \t cantidad'."""
import sys, re, csv, unicodedata

RX = [("estricto", r"^ASMA$|BRONQUITIS, ENFISEMA|CRONICAS DE LAS VIAS RESPIRATORIAS INFERIORES|^DIABETES|"
                   r"HIPERTENSIVAS|INFECCIOSAS INTESTINALES|PREVENIBLES POR VACUNAS|SARAMPION|TOS FERINA|"
                   r"PAROTIDITIS|VARICELA|^TUBERCULOSIS|^DESNUTRICION|^EPILEPSIA"),
      ("ampliado", r"INFLUENZA Y NEUMONIA|NEUMONIA E INFLUENZA|^ENFERMEDADES DEL SISTEMA URINARIO$|"
                   r"^IRA SUPERIORES$|INFECCIONES AGUDAS DE LA VIAS RESPIRATORIAS SUPERIORES")]
RX = [(n, re.compile(r)) for n, r in RX]

def norm(t):
    t = unicodedata.normalize("NFKD", t.strip().upper())
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", t)

for line in sys.stdin:
    if line.startswith("anio"):                       # encabezado de cada archivo
        continue
    sep = ";" if line.count(";") > line.count(",") else ","
    f = next(csv.reader([line], delimiter=sep))
    if len(f) != 10 or not f[9].strip():              # filas vacías / corruptas (serie 2016)
        continue
    anio, cap, agr, q = f[0], norm(f[6]), norm(f[7]), int(f[9])
    causa = cap if agr == "TODOS" else agr
    nivel = "otro"
    for n, rx in RX:
        if rx.search(causa):
            nivel = n
            break
    print(f"{anio}|{nivel}\t{q}")
