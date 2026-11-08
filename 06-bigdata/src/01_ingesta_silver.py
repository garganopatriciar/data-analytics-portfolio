"""Bronze -> Silver.
Lee los 7 CSV anuales (dos series con esquemas distintos), armoniza esquema y
categorías, aplica controles de calidad y escribe Parquet particionado por año.
"""
import glob, json, os, re, time
from functools import reduce
from pyspark.sql import functions as F, DataFrame
from common import spark_session, RAW, SILVER, OUT, norm

t0 = time.time()
spark = spark_session()
os.makedirs(OUT, exist_ok=True)
calidad = {}
partes = []

for path in sorted(glob.glob(os.path.join(RAW, "*.csv"))):
    with open(path, encoding="utf-8", errors="replace") as fh:
        header = fh.readline()
    sep = ";" if header.count(";") > header.count(",") else ","
    df = (spark.read.option("header", True).option("sep", sep)
          .option("encoding", "UTF-8").csv(path))
    # Corrección de typo en el encabezado de algunas series ("muncipio")
    for c in df.columns:
        if "muncipio" in c:
            df = df.withColumnRenamed(c, c.replace("muncipio", "municipio"))
    serie = "2021-2022" if "hospitalarios" in os.path.basename(path) else "2016-2020"
    df = df.select("anio", "region_sanitaria", "municipio_id", "municipio_nombre", "sexo",
                   "grupo_edad", "causa_egreso_capitulo", "causa_egreso_agrupamiento",
                   "tipo_egreso", "cantidad").withColumn("serie", F.lit(serie))
    n = df.count()
    nulos = df.filter(F.col("cantidad").isNull() | F.col("anio").isNull()).count()
    dups = n - df.dropDuplicates().count()
    calidad[os.path.basename(path)] = {"separador": sep, "filas": n,
                                       "filas_nulas": nulos, "duplicados_exactos": dups}
    partes.append(df)

raw = reduce(DataFrame.unionByName, partes)

# ---- Armonización de grupos de edad (la serie nueva es más granular) ----
ge = norm(F.col("grupo_edad"))
nums = F.regexp_extract(ge, r"^(\d+)\s*(?:-|A)\s*(\d+)", 1)
edad = (F.when(ge.rlike("DIA|MES|^[1-4] ANO"), "00-04")
         .when(ge.rlike("^0-4$|^0 A 4"), "00-04")
         .when(ge.rlike("^(80|85)"), "80+")
         .when(nums != "", F.lpad(nums, 2, "0").cast("string"))
         .otherwise("IGN"))
lim = F.when(edad.rlike(r"^\d\d$"),
             F.concat(edad, F.lit("-"), F.lpad((edad.cast("int") + 4).cast("string"), 2, "0"))
             ).otherwise(edad)

agrup = norm(F.col("causa_egreso_agrupamiento"))
cap = norm(F.col("causa_egreso_capitulo"))
tipo = norm(F.col("tipo_egreso"))

silver = (raw
    .filter(F.col("cantidad").isNotNull() & F.col("anio").isNotNull())
    .dropDuplicates()
    .select(
        F.col("anio").cast("int").alias("anio"),
        norm(F.col("region_sanitaria")).alias("region_sanitaria"),
        F.lpad(F.trim(F.col("municipio_id")), 5, "0").alias("municipio_id"),
        norm(F.col("municipio_nombre")).alias("municipio_nombre"),
        F.when(norm(F.col("sexo")).isin("FEMENINO", "MASCULINO"), norm(F.col("sexo")))
         .otherwise("IGNORADO").alias("sexo"),
        lim.alias("grupo_edad"),
        cap.alias("capitulo"),
        # 'TODOS' en la serie vieja = capítulo sin subagrupamiento
        F.when(agrup == "TODOS", cap).otherwise(agrup).alias("causa"),
        F.regexp_replace(F.regexp_replace(tipo, "TRANSLADO", "TRASLADO"), "DEFUNCION", "DEFUNCION")
         .alias("tipo_egreso"),
        F.col("cantidad").cast("int").alias("cantidad"),
        "serie"))

# Nombre de municipio canónico por código INDEC (difieren mayúsc./tildes entre años)
canon = (silver.groupBy("municipio_id", "municipio_nombre").agg(F.sum("cantidad").alias("q"))
         .orderBy(F.desc("q")).dropDuplicates(["municipio_id"])
         .select("municipio_id", F.col("municipio_nombre").alias("municipio")))
silver = silver.join(F.broadcast(canon), "municipio_id", "left").drop("municipio_nombre")

(silver.repartition("anio").write.mode("overwrite")
       .partitionBy("anio").parquet(SILVER))

s = spark.read.parquet(SILVER)
resumen = {
    "registros_silver": s.count(),
    "egresos_totales": s.agg(F.sum("cantidad")).first()[0],
    "municipios": s.select("municipio_id").distinct().count(),
    "regiones": s.select("region_sanitaria").distinct().count(),
    "causas_distintas": s.select("causa").distinct().count(),
    "grupos_edad": sorted(r[0] for r in s.select("grupo_edad").distinct().collect()),
    "segundos": round(time.time() - t0, 1),
}
calidad["_resumen"] = resumen
with open(os.path.join(OUT, "calidad_ingesta.json"), "w") as fh:
    json.dump(calidad, fh, ensure_ascii=False, indent=2)
print(json.dumps(calidad, ensure_ascii=False, indent=2))
spark.stop()
