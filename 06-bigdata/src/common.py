"""Utilidades compartidas: sesión Spark, rutas y normalización de texto."""
import os
from pyspark.sql import SparkSession, functions as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")          # capa bronze (landing, equivalente a HDFS /raw)
SILVER = os.path.join(BASE, "data", "silver")    # Parquet armonizado, particionado por anio
GOLD = os.path.join(BASE, "data", "gold")        # agregados analíticos
OUT = os.path.join(BASE, "outputs")


def spark_session(app="tp-adm-egresos", cores="*"):
    return (SparkSession.builder.appName(app)
            .master(f"local[{cores}]")
            .config("spark.driver.memory", "4g")
            .config("spark.sql.shuffle.partitions", "8")
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.ansi.enabled", "false")   # Spark 4 lo activa por defecto
            .config("spark.ui.enabled", "false")
            .getOrCreate())


ACC_FROM = "ÁÉÍÓÚÜÑáéíóúüñ"
ACC_TO = "AEIOUUNaeiouun"


def norm(col):
    """Mayúsculas, sin tildes, espacios colapsados. Resuelve la heterogeneidad de rótulos entre series."""
    c = F.translate(F.upper(F.trim(col)), ACC_FROM, ACC_TO)
    return F.regexp_replace(c, r"\s+", " ")
