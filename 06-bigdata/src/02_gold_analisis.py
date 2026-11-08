"""Silver -> Gold.
Clasifica cada causa de egreso según el marco de Internaciones por Condiciones
Sensibles al cuidado Ambulatorio (ICSAP; Caminal et al., 2001), adaptado a los
agrupamientos publicados, y genera tablas analíticas con Spark SQL y funciones ventana.
"""
import json, os, time
from pyspark.sql import functions as F, Window as W
from common import spark_session, SILVER, GOLD, OUT

t0 = time.time()
spark = spark_session()
s = spark.read.parquet(SILVER)

# ---------- Diccionario ICSAP (regex sobre la causa normalizada) ----------
ICSAP = [  # (condicion, regex, nivel)
    ("Asma", r"^ASMA$", "estricto"),
    ("EPOC", r"BRONQUITIS, ENFISEMA|CRONICAS DE LAS VIAS RESPIRATORIAS INFERIORES", "estricto"),
    ("Diabetes", r"^DIABETES", "estricto"),
    ("Hipertension", r"HIPERTENSIVAS", "estricto"),
    ("Gastroenteritis", r"INFECCIOSAS INTESTINALES", "estricto"),
    ("Inmunoprevenibles", r"PREVENIBLES POR VACUNAS|SARAMPION|TOS FERINA|PAROTIDITIS|VARICELA", "estricto"),
    ("Tuberculosis", r"^TUBERCULOSIS", "estricto"),
    ("Desnutricion", r"^DESNUTRICION", "estricto"),
    ("Epilepsia", r"^EPILEPSIA", "estricto"),
    ("Neumonia/Influenza", r"INFLUENZA Y NEUMONIA|NEUMONIA E INFLUENZA", "ampliado"),
    ("Sist. urinario (proxy ITU)", r"^ENFERMEDADES DEL SISTEMA URINARIO$", "ampliado"),
    ("IRA superiores", r"^IRA SUPERIORES$|INFECCIONES AGUDAS DE LA VIAS RESPIRATORIAS SUPERIORES", "ampliado"),
]
cond = F.lit(None).cast("string"); nivel = F.lit(None).cast("string")
for c, rx, nv in reversed(ICSAP):
    cond = F.when(F.col("causa").rlike(rx), c).otherwise(cond)
    nivel = F.when(F.col("causa").rlike(rx), nv).otherwise(nivel)

df = (s.withColumn("icsap_condicion", cond)
       .withColumn("icsap_nivel", nivel)
       .withColumn("obstetrico", F.col("capitulo").rlike("EMBARAZO|PARTO|PUERPERIO") |
                                  F.col("causa").rlike("^PARTO$|^ABORTO$|OBSTETRIC"))
       .withColumn("covid", F.col("causa").rlike("COVID"))
       .cache())
df.createOrReplaceTempView("egresos")

# Auditoría del mapeo: qué causas originales cayeron en cada condición
mapeo = (df.filter("icsap_condicion IS NOT NULL")
           .groupBy("icsap_nivel", "icsap_condicion", "causa").agg(F.sum("cantidad").alias("egresos"))
           .orderBy("icsap_nivel", "icsap_condicion"))

# ---------- 1. Serie anual (Spark SQL) ----------
anual = spark.sql("""
SELECT anio,
       SUM(cantidad)                                             AS egresos,
       SUM(CASE WHEN NOT obstetrico THEN cantidad END)           AS egresos_no_obst,
       SUM(CASE WHEN covid THEN cantidad ELSE 0 END)             AS egresos_covid,
       SUM(CASE WHEN icsap_nivel='estricto' THEN cantidad ELSE 0 END) AS icsap_estricto,
       SUM(CASE WHEN icsap_nivel IS NOT NULL THEN cantidad ELSE 0 END) AS icsap_ampliado,
       SUM(CASE WHEN tipo_egreso='DEFUNCION' THEN cantidad ELSE 0 END) AS defunciones,
       SUM(CASE WHEN tipo_egreso='DEFUNCION' AND icsap_nivel IS NOT NULL THEN cantidad ELSE 0 END) AS defunciones_icsap
FROM egresos GROUP BY anio ORDER BY anio""")
anual = (anual
    .withColumn("pct_icsap_estricto", F.round(100 * F.col("icsap_estricto") / F.col("egresos_no_obst"), 2))
    .withColumn("pct_icsap_ampliado", F.round(100 * F.col("icsap_ampliado") / F.col("egresos_no_obst"), 2))
    .withColumn("var_interanual_pct", F.round(100 * (F.col("egresos") / F.lag("egresos").over(W.orderBy("anio")) - 1), 1)))

# ---------- 2. Condición x año ----------
cond_anio = (df.filter("icsap_condicion IS NOT NULL")
               .groupBy("anio", "icsap_nivel", "icsap_condicion").agg(F.sum("cantidad").alias("egresos")))

# ---------- 3. Edad x condición (todo el período) ----------
edad_tot = df.filter("NOT obstetrico").groupBy("grupo_edad").agg(F.sum("cantidad").alias("egresos_no_obst"))
edad_cond = (df.filter("icsap_condicion IS NOT NULL").groupBy("grupo_edad", "icsap_condicion")
               .agg(F.sum("cantidad").alias("egresos"))
               .join(edad_tot, "grupo_edad")
               .withColumn("pct_sobre_edad", F.round(100 * F.col("egresos") / F.col("egresos_no_obst"), 2)))

# ---------- 4. Municipios: perfil, ranking intra-región y z-score ----------
mun = spark.sql("""
SELECT region_sanitaria, municipio_id, municipio,
       SUM(cantidad) AS egresos,
       SUM(CASE WHEN NOT obstetrico THEN cantidad END) AS egresos_no_obst,
       SUM(CASE WHEN icsap_nivel='estricto' THEN cantidad ELSE 0 END) AS icsap_estricto,
       SUM(CASE WHEN icsap_nivel IS NOT NULL THEN cantidad ELSE 0 END) AS icsap_ampliado,
       SUM(CASE WHEN grupo_edad IN ('65-69','70-74','75-79','80+') AND NOT obstetrico THEN cantidad ELSE 0 END) AS egresos_65mas,
       SUM(CASE WHEN tipo_egreso='DEFUNCION' THEN cantidad ELSE 0 END) AS defunciones
FROM egresos
WHERE anio IN (2017, 2018, 2019, 2022)      -- excluye años de distorsión pandémica (2020-2021)
  AND NOT covid
GROUP BY region_sanitaria, municipio_id, municipio""")
mun = (mun.filter("egresos >= 1000")       # estabilidad estadística mínima
          .withColumn("pct_icsap", F.round(100 * F.col("icsap_estricto") / F.col("egresos_no_obst"), 2))
          .withColumn("pct_icsap_ampl", F.round(100 * F.col("icsap_ampliado") / F.col("egresos_no_obst"), 2))
          .withColumn("pct_65mas", F.round(100 * F.col("egresos_65mas") / F.col("egresos_no_obst"), 2))
          .withColumn("letalidad_pct", F.round(100 * F.col("defunciones") / F.col("egresos"), 2)))
# Estandarización indirecta por edad: ICSAP esperado = sum_edad(egresos_mun,edad * tasa_provincial_edad)
base = df.filter("anio IN (2017, 2018, 2019, 2022) AND NOT covid AND NOT obstetrico")
tasa_prov = (base.groupBy("grupo_edad")
               .agg((F.sum(F.when(F.col("icsap_nivel") == "estricto", F.col("cantidad")).otherwise(0)) /
                     F.sum("cantidad")).alias("tasa_edad")))
esperado = (base.groupBy("municipio_id", "grupo_edad").agg(F.sum("cantidad").alias("n"))
                .join(F.broadcast(tasa_prov), "grupo_edad")
                .groupBy("municipio_id").agg(F.sum(F.col("n") * F.col("tasa_edad")).alias("icsap_esperado")))
mun = (mun.join(esperado, "municipio_id")
          .withColumn("razon_oe", F.round(F.col("icsap_estricto") / F.col("icsap_esperado"), 3)))
w_all = W.partitionBy(F.lit(1))
mun = (mun.withColumn("z_icsap", F.round((F.col("pct_icsap") - F.avg("pct_icsap").over(w_all)) /
                                         F.stddev("pct_icsap").over(w_all), 2))
          .withColumn("rank_en_region", F.dense_rank().over(
              W.partitionBy("region_sanitaria").orderBy(F.desc("pct_icsap")))))

# ---------- 5. Región x año con variación interanual (ventana LAG) ----------
reg = (df.filter("NOT obstetrico").groupBy("region_sanitaria", "anio")
         .agg(F.sum("cantidad").alias("egresos_no_obst"),
              F.sum(F.when(F.col("icsap_nivel") == "estricto", F.col("cantidad")).otherwise(0)).alias("icsap_estricto"))
         .withColumn("pct_icsap", F.round(100 * F.col("icsap_estricto") / F.col("egresos_no_obst"), 2))
         .withColumn("delta_pp", F.round(F.col("pct_icsap") - F.lag("pct_icsap").over(
              W.partitionBy("region_sanitaria").orderBy("anio")), 2)))

os.makedirs(GOLD, exist_ok=True)
tablas = {"mapeo_icsap": mapeo, "anual": anual, "condicion_anio": cond_anio,
          "edad_condicion": edad_cond, "municipios": mun, "region_anio": reg}
for nombre, t in tablas.items():
    t.write.mode("overwrite").parquet(os.path.join(GOLD, nombre))
    t.toPandas().to_csv(os.path.join(OUT, f"gold_{nombre}.csv"), index=False)

anual.show(truncate=False)
mapeo.show(40, truncate=60)
mun.orderBy(F.desc("razon_oe")).select("region_sanitaria", "municipio", "egresos", "pct_icsap", "z_icsap", "pct_65mas", "razon_oe").show(12, truncate=False)
print("corr(pct_icsap, pct_65mas) =", round(mun.stat.corr("pct_icsap", "pct_65mas"), 3))
print("corr(razon_oe, pct_65mas)  =", round(mun.stat.corr("razon_oe", "pct_65mas"), 3))
print("municipios analizados:", mun.count())
print("segundos:", round(time.time() - t0, 1))
spark.stop()
