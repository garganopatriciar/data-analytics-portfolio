"""Segmentación de municipios con Spark MLlib (K-Means) según su perfil de
internaciones evitables, para priorizar intervenciones de telemedicina/APS."""
import json, os
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from common import spark_session, SILVER, GOLD, OUT

spark = spark_session()
mun = spark.read.parquet(os.path.join(GOLD, "municipios"))
s = spark.read.parquet(SILVER).filter("anio IN (2017,2018,2019,2022)")

# participación de cada condición crónica / aguda sobre egresos no obstétricos
cron = {"Asma": "^ASMA$", "EPOC": "BRONQUITIS, ENFISEMA|CRONICAS DE LAS VIAS RESP",
        "Diabetes": "^DIABETES", "Hipertension": "HIPERTENSIVAS", "Gastroenteritis": "INFECCIOSAS INTESTINALES"}
aggs = [F.sum(F.when(F.col("causa").rlike(rx), F.col("cantidad")).otherwise(0)).alias(f"n_{k}")
        for k, rx in cron.items()]
perfil = (s.filter(~F.col("capitulo").rlike("EMBARAZO|PARTO|PUERPERIO") & ~F.col("causa").rlike("COVID"))
           .groupBy("municipio_id").agg(F.sum("cantidad").alias("n"), *aggs))
for k in cron:
    perfil = perfil.withColumn(f"pct_{k}", 100 * F.col(f"n_{k}") / F.col("n"))
feat_cols = [f"pct_{k}" for k in cron] + ["pct_65mas", "letalidad_pct", "razon_oe"]
data = mun.join(perfil, "municipio_id").select("region_sanitaria", "municipio", "egresos", *feat_cols).cache()

assembler = VectorAssembler(inputCols=feat_cols, outputCol="raw")
scaler = StandardScaler(inputCol="raw", outputCol="features", withMean=True, withStd=True)
ev = ClusteringEvaluator(featuresCol="features", metricName="silhouette")
sil = {}
for k in range(2, 9):
    m = Pipeline(stages=[assembler, scaler, KMeans(k=k, seed=42, featuresCol="features")]).fit(data)
    sil[k] = round(ev.evaluate(m.transform(data)), 4)
print("silhouette por k:", sil)
# k elegido: máximo silhouette con k>=3 (k=2 suele separar sólo AMBA vs interior, poco accionable)
k_best = max((k for k in sil if k >= 3), key=lambda k: sil[k])
model = Pipeline(stages=[assembler, scaler, KMeans(k=k_best, seed=42, featuresCol="features")]).fit(data)
pred = model.transform(data).withColumnRenamed("prediction", "cluster")

resumen = (pred.groupBy("cluster")
             .agg(F.count("*").alias("municipios"), F.sum("egresos").alias("egresos"),
                  *[F.round(F.avg(c), 2).alias(c) for c in feat_cols])
             .orderBy("cluster"))
resumen.show(truncate=False)
resumen.toPandas().to_csv(os.path.join(OUT, "clusters_resumen.csv"), index=False)
pred.select("cluster", "region_sanitaria", "municipio", "egresos", *feat_cols).toPandas() \
    .sort_values(["cluster", "egresos"], ascending=[True, False]) \
    .to_csv(os.path.join(OUT, "clusters_municipios.csv"), index=False)
with open(os.path.join(OUT, "clusters_silhouette.json"), "w") as fh:
    json.dump({"silhouette": sil, "k_elegido": k_best}, fh, indent=2)
for c in range(k_best):
    print(c, [r.municipio for r in pred.filter(F.col("cluster") == c).orderBy(F.desc("egresos")).limit(6).collect()])
spark.stop()
