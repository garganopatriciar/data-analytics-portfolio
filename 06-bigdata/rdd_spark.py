"""Mismo cálculo con el paradigma MapReduce sobre RDD de Spark (map + reduceByKey) y
validación cruzada contra la tabla gold generada con DataFrames."""
import os, sys, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from common import spark_session, RAW, GOLD, OUT

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
spark = spark_session(); sc = spark.sparkContext
sc.addPyFile(os.path.join(here, "mapper_lib.py"))
import mapper_lib
t0 = time.time()
res = (sc.textFile(os.path.join(RAW, "*.csv"))
         .map(mapper_lib.map_line).filter(lambda kv: kv is not None)
         .reduceByKey(lambda a, b: a + b).collect())
t_rdd = time.time() - t0
rdd = {k: v for k, v in res}
mr = dict(l.strip().split("\t") for l in open(os.path.join(OUT, "mapreduce_resultado.tsv")))
mr = {k: int(v) for k, v in mr.items()}
g = spark.read.parquet(os.path.join(GOLD, "anual")).toPandas().set_index("anio")
ok = True
for a in g.index:
    for nivel, col in (("estricto", "icsap_estricto"),):
        v_df, v_mr, v_rdd = int(g.loc[a, col]), mr.get(f"{a}|{nivel}"), rdd.get(f"{a}|{nivel}")
        print(a, nivel, "DataFrame:", v_df, "MR-streaming:", v_mr, "RDD:", v_rdd)
        ok &= (v_df == v_mr == v_rdd)
    tot = sum(v for k, v in mr.items() if k.startswith(str(a)))
    ok &= tot == int(g.loc[a, "egresos"])
print("VALIDACION CRUZADA OK" if ok else "DIFERENCIAS DETECTADAS", "| RDD seg:", round(t_rdd, 1))
spark.stop()
